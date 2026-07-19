"""Run the preregistered d2-e003-routeknn experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from baseline import CurrentModeBaseline
from metarank import MetaRanker
from routeknn import RouteKNN
from submission_validator import validate_submission
from validation import DEFAULT_FOLD_COUNT, DEFAULT_SEED, accuracy, make_target_group_folds


EXPERIMENT_ID = "d2-e003-routeknn"
VALIDATION_VERSION = "d2-targetgroup-v1"
MINIMUM_MEAN_GAIN = 0.015
MINIMUM_SEEN_CURRENT_GAIN = 0.010
MAXIMUM_WORST_FOLD_DROP = 0.005
MAXIMUM_CATEGORY_OOD_DROP = 0.005
MAXIMUM_RUNTIME_SECONDS = 600.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--e002-dir", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=DEFAULT_FOLD_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def target_hash(targets: set[int]) -> str:
    payload = json.dumps(
        sorted(int(target) for target in targets), separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def subset_accuracy(
    truth: np.ndarray, prediction: np.ndarray, mask: np.ndarray
) -> float | None:
    if not mask.any():
        return None
    return accuracy(truth[mask], prediction[mask])


def add_subset_counts(
    aggregate: dict[str, dict[str, int]],
    name: str,
    mask: np.ndarray,
    truth: np.ndarray,
    predictions: dict[str, np.ndarray],
) -> None:
    aggregate[name]["rows"] += int(mask.sum())
    for method, prediction in predictions.items():
        aggregate[name][f"{method}_correct"] += int(
            np.sum(prediction[mask] == truth[mask])
        )


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    baseline_dir = args.baseline_dir.resolve()
    e002_dir = args.e002_dir.resolve()
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
    e002_metrics = json.loads((e002_dir / "metrics.json").read_text(encoding="utf-8"))
    if baseline_manifest["version"] != VALIDATION_VERSION:
        raise ValueError("baseline validation version does not match frozen harness")
    if baseline_manifest["seed"] != args.seed:
        raise ValueError("seed differs from frozen manifest")
    if baseline_manifest["fold_count"] != args.fold_count:
        raise ValueError("fold count differs from frozen manifest")

    folds = make_target_group_folds(
        train, categories, fold_count=args.fold_count, seed=args.seed
    )
    expected_hashes = {
        int(fold["fold"]): fold["target_sha256"]
        for fold in baseline_manifest["folds"]
    }
    categories_by_article = {
        int(article_id): frozenset(group["category"].astype(str))
        for article_id, group in categories.groupby("article_id", sort=True)
    }
    scores: dict[str, list[float]] = {
        "current_mode": [],
        "metarank": [],
        "routeknn": [],
    }
    subset_names = ("current_seen", "current_unseen", "category_entirely_unseen")
    aggregate = {
        name: {
            "rows": 0,
            "current_mode_correct": 0,
            "metarank_correct": 0,
            "routeknn_correct": 0,
        }
        for name in subset_names
    }
    diversity = {
        "rows": 0,
        "disagreements": 0,
        "routeknn_correct_metarank_wrong": 0,
        "metarank_correct_routeknn_wrong": 0,
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
        metarank = MetaRanker.fit(training, articles, categories)
        routeknn = RouteKNN.fit(training, articles, categories)
        truth = validation["next_article_id"].to_numpy(dtype=np.int64)
        predictions = {
            "current_mode": baseline.predict(validation),
            "metarank": metarank.predict(validation),
            "routeknn": routeknn.predict(validation),
        }
        for method, prediction in predictions.items():
            scores[method].append(accuracy(truth, prediction))

        stored_baseline = baseline_metrics["validation"]["folds"][fold]["scores"][
            "current_mode"
        ]
        stored_e002 = e002_metrics["validation"]["folds"][fold]["scores"]["metarank"]
        if scores["current_mode"][-1] != stored_baseline:
            raise RuntimeError(f"fold {fold} baseline does not reproduce exactly")
        if scores["metarank"][-1] != stored_e002:
            raise RuntimeError(f"fold {fold} E002 does not reproduce exactly")

        current_seen = routeknn.seen_current_mask(validation)
        current_unseen = ~current_seen
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
        for name, mask in (
            ("current_seen", current_seen),
            ("current_unseen", current_unseen),
            ("category_entirely_unseen", category_entirely_unseen),
        ):
            add_subset_counts(aggregate, name, mask, truth, predictions)

        disagreement = predictions["routeknn"] != predictions["metarank"]
        route_correct = predictions["routeknn"] == truth
        meta_correct = predictions["metarank"] == truth
        diversity["rows"] += int(len(validation))
        diversity["disagreements"] += int(disagreement.sum())
        diversity["routeknn_correct_metarank_wrong"] += int(
            np.sum(route_correct & ~meta_correct)
        )
        diversity["metarank_correct_routeknn_wrong"] += int(
            np.sum(meta_correct & ~route_correct)
        )
        state_id_ablated = validation.copy()
        state_id_ablated["state_id"] = -1
        prediction_counts = pd.Series(predictions["routeknn"]).value_counts(
            normalize=True
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
                    truth, predictions["routeknn"], current_seen
                ),
                "baseline_current_seen_accuracy": subset_accuracy(
                    truth, predictions["current_mode"], current_seen
                ),
                "current_unseen_accuracy": subset_accuracy(
                    truth, predictions["routeknn"], current_unseen
                ),
                "category_entirely_unseen_accuracy": subset_accuracy(
                    truth, predictions["routeknn"], category_entirely_unseen
                ),
                "state_id_feature_used": False,
                "state_id_ablation_exact_match": bool(
                    np.array_equal(
                        routeknn.predict(state_id_ablated), predictions["routeknn"]
                    )
                ),
                "unique_predictions": int(prediction_counts.size),
                "top_prediction_share": float(prediction_counts.iloc[0]),
                "prediction_change_rate_from_metarank": float(disagreement.mean()),
                "scores": {
                    method: values[-1] for method, values in scores.items()
                },
            }
        )

    candidate_summary = {
        method: {
            "mean_accuracy": float(np.mean(values)),
            "fold_accuracy": [float(value) for value in values],
            "worst_fold_accuracy": float(np.min(values)),
            "std_accuracy": float(np.std(values)),
        }
        for method, values in scores.items()
    }
    subset_summary = {}
    for name, values in aggregate.items():
        rows = values["rows"]
        subset_summary[name] = {
            "rows": rows,
            **{
                f"{method}_accuracy": values[f"{method}_correct"] / rows
                for method in scores
            },
        }
        subset_summary[name]["routeknn_delta_vs_baseline"] = (
            subset_summary[name]["routeknn_accuracy"]
            - subset_summary[name]["current_mode_accuracy"]
        )
        subset_summary[name]["routeknn_delta_vs_metarank"] = (
            subset_summary[name]["routeknn_accuracy"]
            - subset_summary[name]["metarank_accuracy"]
        )

    full_routeknn = RouteKNN.fit(train, articles, categories)
    full_metarank = MetaRanker.fit(train, articles, categories)
    full_baseline = CurrentModeBaseline.fit(train)
    test_prediction = full_routeknn.predict(test)
    e002_test_prediction = full_metarank.predict(test)
    baseline_test_prediction = full_baseline.predict(test)
    if not sample["state_id"].equals(test["state_id"]):
        raise ValueError("sample and test state order differ")
    submission = sample.copy()
    submission["predicted_next_article_id"] = test_prediction
    submission_path = experiment_dir / "submission.csv"
    submission.to_csv(submission_path, index=False)
    validation_result = validate_submission(submission_path, data_dir=data_root)
    elapsed = float(time.perf_counter() - started)

    baseline_summary = candidate_summary["current_mode"]
    route_summary = candidate_summary["routeknn"]
    baseline_fold_wins = int(
        sum(
            route > baseline
            for route, baseline in zip(
                scores["routeknn"], scores["current_mode"], strict=True
            )
        )
    )
    gate_checks = {
        "mean_gain_at_least_0_015": route_summary["mean_accuracy"]
        - baseline_summary["mean_accuracy"]
        >= MINIMUM_MEAN_GAIN,
        "wins_at_least_4_of_5_folds": baseline_fold_wins >= 4,
        "seen_current_gain_at_least_0_010": subset_summary["current_seen"][
            "routeknn_delta_vs_baseline"
        ]
        >= MINIMUM_SEEN_CURRENT_GAIN,
        "worst_fold_drop_within_0_005": route_summary["worst_fold_accuracy"]
        >= baseline_summary["worst_fold_accuracy"] - MAXIMUM_WORST_FOLD_DROP,
        "category_ood_drop_within_0_005": subset_summary[
            "category_entirely_unseen"
        ]["routeknn_delta_vs_baseline"]
        >= -MAXIMUM_CATEGORY_OOD_DROP,
        "target_seen_rate_is_zero": all(
            fold["target_seen_rate"] == 0.0 for fold in fold_metrics
        ),
        "state_id_ablation_is_exact": all(
            fold["state_id_ablation_exact_match"] for fold in fold_metrics
        ),
        "runtime_under_600_seconds": elapsed < MAXIMUM_RUNTIME_SECONDS,
        "submission_is_ready": validation_result.row_count == len(sample),
    }
    gate_status = "KEEP" if all(gate_checks.values()) else "REJECT"
    test_counts = pd.Series(test_prediction).value_counts(normalize=True)
    e002_disagreement = test_prediction != e002_test_prediction
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "owner": "MAIN",
        "branch": "exp/d2-e003-routeknn",
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
        "hypothesis": "One nearest fold-local route transfers across unseen targets using exact current and static target metadata.",
        "model": {
            "neighbor_count": 1,
            "category_weight": 2.0,
            "title_weight": 1.0,
            "seen_current_rule": "exact current only",
            "unseen_current_rule": "one metadata-nearest training current",
            "parameter_search": False,
        },
        "candidates": candidate_summary,
        "comparison": {
            "mean_gain_vs_baseline": route_summary["mean_accuracy"]
            - baseline_summary["mean_accuracy"],
            "mean_gain_vs_metarank": route_summary["mean_accuracy"]
            - candidate_summary["metarank"]["mean_accuracy"],
            "fold_wins_vs_baseline": baseline_fold_wins,
            "fold_wins_vs_metarank": int(
                sum(
                    route > meta
                    for route, meta in zip(
                        scores["routeknn"], scores["metarank"], strict=True
                    )
                )
            ),
            "subset_accuracy": subset_summary,
            "oof_diversity_vs_metarank": {
                **diversity,
                "disagreement_rate": diversity["disagreements"] / diversity["rows"],
            },
        },
        "test_diagnostics": {
            "rows": int(len(test)),
            "current_seen_rate": float(full_routeknn.seen_current_mask(test).mean()),
            "unique_predictions": int(test_counts.size),
            "top_prediction_share": float(test_counts.iloc[0]),
            "prediction_min": int(test_prediction.min()),
            "prediction_max": int(test_prediction.max()),
            "change_rate_from_baseline": float(
                np.mean(test_prediction != baseline_test_prediction)
            ),
            "disagreement_rate_from_metarank": float(e002_disagreement.mean()),
        },
        "acceptance_gate": {"checks": gate_checks, "status": gate_status},
        "leakage_check": {
            "static_metadata_available_at_test": True,
            "route_index_fit_per_fold": True,
            "state_id_used": False,
            "external_data_or_api": False,
        },
        "submission_validation": {
            "status": "READY",
            "rows": validation_result.row_count,
            "unique_predictions": validation_result.unique_prediction_count,
            "csv_sha256": hashlib.sha256(submission_path.read_bytes()).hexdigest(),
            "int64_prediction_sha256": hashlib.sha256(
                test_prediction.astype("<i8", copy=False).tobytes()
            ).hexdigest(),
        },
        "submission": str(submission_path),
        "runtime_seconds": elapsed,
        "recommendation": gate_status,
        "submission_verdict": "DO_NOT_SUBMIT_PENDING_INDEPENDENT_REVIEW"
        if gate_status == "KEEP"
        else "DO_NOT_SUBMIT",
    }
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
