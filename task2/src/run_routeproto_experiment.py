"""Run the frozen d2-e008-routeproto experiment on official Task 2 folds."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from baseline import CurrentModeBaseline
from routeproto import RouteProtoRanker
from submission_validator import validate_submission
from validation import DEFAULT_FOLD_COUNT, DEFAULT_SEED, accuracy, make_target_group_folds


EXPERIMENT_ID = "d2-e008-routeproto"
VALIDATION_VERSION = "d2-targetgroup-v1"
AUDIT_REFERENCE_MEAN = 0.2853333333333333
E002_FOLD_SCORES = [0.29055555555555557, 0.2827777777777778, 0.2783333333333333, 0.28055555555555556, 0.29444444444444445]
MINIMUM_MEAN = 0.290333
MINIMUM_WORST = 0.273333
MINIMUM_CURRENT_UNSEEN = 0.118539
MINIMUM_CATEGORY_OOD = 0.310200
MAXIMUM_TEST_TOP_SHARE = 0.3252
MINIMUM_TEST_UNIQUE = 337
MAXIMUM_RUNTIME_SECONDS = 300.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=DEFAULT_FOLD_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def target_hash(targets: set[int]) -> str:
    ordered = sorted(int(target) for target in targets)
    payload = json.dumps(ordered, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def subset_accuracy(
    truth: np.ndarray, prediction: np.ndarray, mask: np.ndarray
) -> float | None:
    if not mask.any():
        return None
    return accuracy(truth[mask], prediction[mask])


def aggregate_accuracy(correct: int, rows: int) -> float:
    if rows <= 0:
        raise ValueError("cannot aggregate an empty subset")
    return correct / rows


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    baseline_dir = args.baseline_dir.resolve()
    experiment_dir = args.experiment_dir.resolve()
    if experiment_dir.name != EXPERIMENT_ID:
        raise ValueError(f"experiment directory must be named {EXPERIMENT_ID}")
    experiment_dir.mkdir(parents=True, exist_ok=True)

    train = pd.read_csv(data_root / "states_train.csv")
    test = pd.read_csv(data_root / "states_test.csv")
    articles = pd.read_csv(data_root / "articles.csv")
    categories = pd.read_csv(data_root / "categories.csv")
    sample = pd.read_csv(data_root / "sample_submission.csv")
    baseline_metrics = json.loads(
        (baseline_dir / "metrics.json").read_text(encoding="utf-8")
    )
    baseline_manifest = json.loads(
        (baseline_dir / "validation_manifest.json").read_text(encoding="utf-8")
    )
    if baseline_manifest["version"] != VALIDATION_VERSION:
        raise ValueError("baseline validation version does not match frozen harness")
    if baseline_manifest["seed"] != args.seed:
        raise ValueError("seed differs from the frozen baseline manifest")
    if baseline_manifest["fold_count"] != args.fold_count:
        raise ValueError("fold count differs from the frozen baseline manifest")

    folds = make_target_group_folds(
        train, categories, fold_count=args.fold_count, seed=args.seed
    )
    categories_by_article = {
        int(article_id): frozenset(group["category"].astype(str))
        for article_id, group in categories.groupby("article_id", sort=True)
    }
    expected_hashes = {
        int(fold["fold"]): fold["target_sha256"]
        for fold in baseline_manifest["folds"]
    }

    method_scores: dict[str, list[float]] = {
        "current_mode": [],
        "routeproto": [],
    }
    aggregate = {
        "current_unseen": {
            "rows": 0,
            "current_mode_correct": 0,
            "routeproto_correct": 0,
        },
        "category_entirely_unseen": {
            "rows": 0,
            "current_mode_correct": 0,
            "routeproto_correct": 0,
        },
    }
    fold_metrics = []
    for fold in range(args.fold_count):
        training = train.loc[folds != fold]
        validation = train.loc[folds == fold]
        training_targets = set(training["target_article_id"].astype(np.int64))
        validation_targets = set(validation["target_article_id"].astype(np.int64))
        if training_targets & validation_targets:
            raise RuntimeError("target leakage between training and validation")
        fold_hash = target_hash(validation_targets)
        if fold_hash != expected_hashes[fold]:
            raise RuntimeError(f"fold {fold} target hash differs from frozen manifest")

        baseline = CurrentModeBaseline.fit(training)
        ranker = RouteProtoRanker.fit(training, articles)
        truth = validation["next_article_id"].to_numpy(dtype=np.int64)
        baseline_prediction = baseline.predict(validation)
        ranker_prediction = ranker.predict(validation)
        method_scores["current_mode"].append(accuracy(truth, baseline_prediction))
        method_scores["routeproto"].append(accuracy(truth, ranker_prediction))

        stored_baseline_score = baseline_metrics["validation"]["folds"][fold][
            "scores"
        ]["current_mode"]
        if not np.isclose(
            method_scores["current_mode"][-1], stored_baseline_score, atol=0.0, rtol=0.0
        ):
            raise RuntimeError(f"fold {fold} baseline score does not reproduce exactly")

        current_seen = ranker.seen_current_mask(validation)
        current_unseen = ~current_seen
        training_next_labels = set(training["next_article_id"].astype(np.int64))
        next_label_seen = validation["next_article_id"].astype(np.int64).isin(
            training_next_labels
        ).to_numpy()
        training_target_categories = set().union(
            *(
                categories_by_article.get(int(target), frozenset())
                for target in training_targets
            )
        )
        category_entirely_unseen = np.fromiter(
            (
                bool(categories_by_article.get(int(target), frozenset()))
                and categories_by_article.get(int(target), frozenset()).isdisjoint(
                    training_target_categories
                )
                for target in validation["target_article_id"]
            ),
            dtype=bool,
            count=len(validation),
        )
        state_id_ablated = validation.copy()
        state_id_ablated["state_id"] = -1
        state_id_ablation_match = bool(
            np.array_equal(ranker.predict(state_id_ablated), ranker_prediction)
        )
        label_ablated = validation.copy()
        label_ablated["next_article_id"] = -999999
        label_ablation_match = bool(
            np.array_equal(ranker.predict(label_ablated), ranker_prediction)
        )
        prediction_counts = pd.Series(ranker_prediction).value_counts(normalize=True)

        for subset_name, mask in (
            ("current_unseen", current_unseen),
            ("category_entirely_unseen", category_entirely_unseen),
        ):
            aggregate[subset_name]["rows"] += int(mask.sum())
            aggregate[subset_name]["current_mode_correct"] += int(
                np.sum(baseline_prediction[mask] == truth[mask])
            )
            aggregate[subset_name]["routeproto_correct"] += int(
                np.sum(ranker_prediction[mask] == truth[mask])
            )

        fold_metrics.append(
            {
                "fold": fold,
                "rows": int(len(validation)),
                "targets": int(len(validation_targets)),
                "target_sha256": fold_hash,
                "target_seen_rate": float(
                    validation["target_article_id"].isin(training_targets).mean()
                ),
                "current_seen_rate": float(current_seen.mean()),
                "current_seen_accuracy": subset_accuracy(
                    truth, ranker_prediction, current_seen
                ),
                "current_unseen_accuracy": subset_accuracy(
                    truth, ranker_prediction, current_unseen
                ),
                "baseline_current_unseen_accuracy": subset_accuracy(
                    truth, baseline_prediction, current_unseen
                ),
                "next_label_seen_rate": float(next_label_seen.mean()),
                "observed_candidate_coverage": ranker.candidate_coverage(validation),
                "entirely_unseen_target_category_rate": float(
                    category_entirely_unseen.mean()
                ),
                "category_seen_accuracy": subset_accuracy(
                    truth, ranker_prediction, ~category_entirely_unseen
                ),
                "category_entirely_unseen_accuracy": subset_accuracy(
                    truth, ranker_prediction, category_entirely_unseen
                ),
                "baseline_category_entirely_unseen_accuracy": subset_accuracy(
                    truth, baseline_prediction, category_entirely_unseen
                ),
                "state_id_feature_used": False,
                "state_id_ablation_exact_match": state_id_ablation_match,
                "heldout_label_ablation_exact_match": label_ablation_match,
                "unique_predictions": int(prediction_counts.size),
                "top_prediction_share": float(prediction_counts.iloc[0]),
                "prediction_change_rate_from_baseline": float(
                    np.mean(ranker_prediction != baseline_prediction)
                ),
                "scores": {
                    "current_mode": method_scores["current_mode"][-1],
                    "routeproto": method_scores["routeproto"][-1],
                    "e002_reference": E002_FOLD_SCORES[fold],
                },
            }
        )

    score_summary = {
        method: {
            "mean_accuracy": float(np.mean(values)),
            "fold_accuracy": [float(value) for value in values],
            "worst_fold_accuracy": float(np.min(values)),
            "std_accuracy": float(np.std(values)),
        }
        for method, values in method_scores.items()
    }
    baseline_summary = score_summary["current_mode"]
    ranker_summary = score_summary["routeproto"]
    fold_wins = int(
        sum(
            ranker > baseline
            for ranker, baseline in zip(
                method_scores["routeproto"], method_scores["current_mode"], strict=True
            )
        )
    )
    e002_fold_wins = int(sum(route > ref for route, ref in zip(method_scores["routeproto"], E002_FOLD_SCORES, strict=True)))
    subset_summary = {}
    for subset_name, values in aggregate.items():
        baseline_accuracy = aggregate_accuracy(
            values["current_mode_correct"], values["rows"]
        )
        ranker_accuracy = aggregate_accuracy(values["routeproto_correct"], values["rows"])
        subset_summary[subset_name] = {
            "rows": values["rows"],
            "current_mode_accuracy": baseline_accuracy,
            "routeproto_accuracy": ranker_accuracy,
            "accuracy_delta": ranker_accuracy - baseline_accuracy,
        }

    full_ranker = RouteProtoRanker.fit(train, articles)
    full_baseline = CurrentModeBaseline.fit(train)
    test_prediction = full_ranker.predict(test)
    baseline_test_prediction = full_baseline.predict(test)
    submission = sample.copy()
    if not sample["state_id"].equals(test["state_id"]):
        raise ValueError("sample and test state order differ")
    submission["predicted_next_article_id"] = test_prediction
    submission_path = experiment_dir / "submission.csv"
    submission.to_csv(submission_path, index=False)
    submission_result = validate_submission(submission_path, data_dir=data_root)
    csv_sha256 = hashlib.sha256(submission_path.read_bytes()).hexdigest()
    prediction_sha256 = hashlib.sha256(
        test_prediction.astype("<i8", copy=False).tobytes()
    ).hexdigest()
    elapsed = float(time.perf_counter() - started)

    gate_checks = {
        "audit_reference_reproduced": bool(
            np.isclose(
                ranker_summary["mean_accuracy"],
                AUDIT_REFERENCE_MEAN,
                atol=0.0,
                rtol=0.0,
            )
        ),
        "mean_at_least_0_290333": ranker_summary["mean_accuracy"] >= MINIMUM_MEAN,
        "wins_vs_e002_at_least_4_of_5_folds": e002_fold_wins >= 4,
        "worst_fold_at_least_0_273333": ranker_summary["worst_fold_accuracy"] >= MINIMUM_WORST,
        "current_unseen_at_least_0_118539": subset_summary["current_unseen"]["routeproto_accuracy"] >= MINIMUM_CURRENT_UNSEEN,
        "category_ood_at_least_0_310200": subset_summary["category_entirely_unseen"]["routeproto_accuracy"] >= MINIMUM_CATEGORY_OOD,
        "target_seen_rate_is_zero": all(
            fold["target_seen_rate"] == 0.0 for fold in fold_metrics
        ),
        "state_id_ablation_is_exact": all(
            fold["state_id_ablation_exact_match"] for fold in fold_metrics
        ),
        "heldout_label_ablation_is_exact": all(
            fold["heldout_label_ablation_exact_match"] for fold in fold_metrics
        ),
        "test_top_share_at_most_0_3252": float(pd.Series(test_prediction).value_counts(normalize=True).iloc[0]) <= MAXIMUM_TEST_TOP_SHARE,
        "test_unique_at_least_337": int(pd.Series(test_prediction).nunique()) >= MINIMUM_TEST_UNIQUE,
        "runtime_under_300_seconds": elapsed < MAXIMUM_RUNTIME_SECONDS,
        "submission_is_ready": submission_result.row_count == len(sample),
    }
    gate_status = "KEEP" if all(gate_checks.values()) else "INVESTIGATE"
    prediction_counts = pd.Series(test_prediction).value_counts(normalize=True)
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "owner": "MAIN",
        "branch": "exp/d2-e008-routeproto",
        "baseline_tag": "d2-baseline-v1",
        "baseline_commit": "0f94a1cdb8da4929520fce80a64e5203947ed4d9",
        "metric": "accuracy",
        "validation": {
            "version": VALIDATION_VERSION,
            "fold_count": args.fold_count,
            "seed": args.seed,
            "group": "target_article_id",
            "folds": fold_metrics,
        },
        "hypothesis": "Training target-title prototypes select observed next-click routes by cosine similarity.",
        "model": {
            "vectorizer": "word TF-IDF lowercase ngram_range=(1,2), sublinear_tf=True, min_df=1, norm=l2",
            "prototype": "mean target vectors per current->next edge then l2 normalize",
            "candidate_source": "fold-training current-to-next labels",
            "unseen_current_fallback": "fold-training global mode",
            "weight_search": False,
        },
        "candidates": score_summary,
        "comparison": {
            "mean_accuracy_gain": ranker_summary["mean_accuracy"]
            - baseline_summary["mean_accuracy"],
            "fold_wins": fold_wins,
            "e002_reference_fold_wins": e002_fold_wins,
            "subset_accuracy": subset_summary,
        },
        "test_diagnostics": {
            "rows": int(len(test)),
            "current_seen_rate": float(full_ranker.seen_current_mask(test).mean()),
            "unique_predictions": int(prediction_counts.size),
            "top_prediction_share": float(prediction_counts.iloc[0]),
            "prediction_min": int(test_prediction.min()),
            "prediction_max": int(test_prediction.max()),
            "prediction_change_rate_from_baseline": float(
                np.mean(test_prediction != baseline_test_prediction)
            ),
        },
        "acceptance_gate": {
            "checks": gate_checks,
            "status": gate_status,
        },
        "leakage_check": {
            "static_metadata_available_at_test": True,
            "label_derived_candidates_fit_per_fold": True,
            "state_id_used": False,
            "external_data_or_api": False,
        },
        "submission_validation": {
            "status": "READY",
            "rows": submission_result.row_count,
            "unique_predictions": submission_result.unique_prediction_count,
            "csv_sha256": csv_sha256,
            "int64_prediction_sha256": prediction_sha256,
        },
        "submission": str(submission_path),
        "runtime_seconds": elapsed,
        "recommendation": gate_status,
        "submission_verdict": "INVESTIGATE_PENDING_INDEPENDENT_AUDIT",
    }
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

