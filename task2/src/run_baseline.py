"""Run target-group validation and create the Task 2 current-mode baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from baseline import CurrentModeBaseline, deterministic_mode
from submission_validator import validate_submission
from validation import DEFAULT_FOLD_COUNT, DEFAULT_SEED, accuracy, make_target_group_folds


EXPERIMENT_ID = "d2-e001-baseline"
VALIDATION_VERSION = "d2-targetgroup-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=DEFAULT_FOLD_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    experiment_dir = args.experiment_dir.resolve()
    if experiment_dir.name != EXPERIMENT_ID:
        raise ValueError(f"experiment directory must be named {EXPERIMENT_ID}")
    experiment_dir.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(data_root / "states_train.csv")
    test = pd.read_csv(data_root / "states_test.csv")
    categories = pd.read_csv(data_root / "categories.csv")
    sample = pd.read_csv(data_root / "sample_submission.csv")
    folds = make_target_group_folds(
        train, categories, fold_count=args.fold_count, seed=args.seed
    )

    categories_by_article = {
        int(article_id): frozenset(group["category"].astype(str))
        for article_id, group in categories.groupby("article_id", sort=True)
    }
    fold_metrics = []
    manifest_folds = []
    methods = {"sample_current": [], "global_mode": [], "current_mode": []}
    for fold in range(args.fold_count):
        training = train.loc[folds != fold]
        validation = train.loc[folds == fold]
        training_targets = set(training["target_article_id"])
        validation_targets = set(validation["target_article_id"])
        if training_targets & validation_targets:
            raise RuntimeError("target leakage between training and validation")
        ordered_targets = sorted(int(target) for target in validation_targets)
        target_payload = json.dumps(
            ordered_targets, separators=(",", ":")
        ).encode("utf-8")
        target_sha256 = hashlib.sha256(target_payload).hexdigest()
        manifest_folds.append(
            {
                "fold": fold,
                "targets": ordered_targets,
                "target_sha256": target_sha256,
            }
        )
        model = CurrentModeBaseline.fit(training)
        truth = validation["next_article_id"].to_numpy(dtype=np.int64)
        predictions = {
            "sample_current": validation["current_article_id"].to_numpy(
                dtype=np.int64
            ),
            "global_mode": np.full(
                len(validation), model.global_next_article_id, dtype=np.int64
            ),
            "current_mode": model.predict(validation),
        }
        for method, prediction in predictions.items():
            methods[method].append(accuracy(truth, prediction))
        seen = model.seen_current_mask(validation)
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
            np.array_equal(model.predict(state_id_ablated), predictions["current_mode"])
        )
        prediction_counts = pd.Series(predictions["current_mode"]).value_counts(
            normalize=True
        )
        fold_metrics.append(
            {
                "fold": fold,
                "rows": int(len(validation)),
                "targets": int(len(validation_targets)),
                "target_sha256": target_sha256,
                "target_seen_rate": float(
                    validation["target_article_id"].isin(training_targets).mean()
                ),
                "current_seen_rate": float(np.mean(seen)),
                "current_seen_accuracy": accuracy(truth[seen], predictions["current_mode"][seen])
                if seen.any()
                else None,
                "current_unseen_accuracy": accuracy(
                    truth[~seen], predictions["current_mode"][~seen]
                )
                if (~seen).any()
                else None,
                "next_label_seen_rate": float(np.mean(next_label_seen)),
                "observed_candidate_coverage": model.candidate_coverage(validation),
                "entirely_unseen_target_category_rate": float(
                    np.mean(category_entirely_unseen)
                ),
                "category_seen_accuracy": accuracy(
                    truth[~category_entirely_unseen],
                    predictions["current_mode"][~category_entirely_unseen],
                )
                if (~category_entirely_unseen).any()
                else None,
                "category_entirely_unseen_accuracy": accuracy(
                    truth[category_entirely_unseen],
                    predictions["current_mode"][category_entirely_unseen],
                )
                if category_entirely_unseen.any()
                else None,
                "state_id_feature_used": False,
                "state_id_ablation_exact_match": state_id_ablation_match,
                "unique_predictions": int(prediction_counts.size),
                "top_prediction_share": float(prediction_counts.iloc[0]),
                "scores": {
                    method: float(values[-1]) for method, values in methods.items()
                },
            }
        )

    full_model = CurrentModeBaseline.fit(train)
    test_prediction = full_model.predict(test)
    submission = sample.copy()
    if not submission["state_id"].equals(test["state_id"]):
        raise ValueError("sample and test state order differ")
    submission["predicted_next_article_id"] = test_prediction
    submission_path = experiment_dir / "submission.csv"
    submission.to_csv(submission_path, index=False)
    submission_result = validate_submission(submission_path, data_dir=data_root)
    validation_report = {
        "status": "READY",
        "rows": int(submission_result.row_count),
        "columns": sample.columns.tolist(),
        "unique_state_ids": int(submission["state_id"].nunique()),
        "unique_predictions": int(submission_result.unique_prediction_count),
        "reference_exact_match": None,
        "errors": [],
    }
    score_summary = {
        method: {
            "mean_accuracy": float(np.mean(values)),
            "fold_accuracy": [float(value) for value in values],
            "worst_fold_accuracy": float(np.min(values)),
            "std_accuracy": float(np.std(values)),
        }
        for method, values in methods.items()
    }
    current_scores = score_summary["current_mode"]
    gate_checks = {
        "target_groups_are_disjoint": True,
        "target_seen_rate_is_zero": all(
            fold["target_seen_rate"] == 0.0 for fold in fold_metrics
        ),
        "state_id_ablation_is_exact": all(
            fold["state_id_ablation_exact_match"] for fold in fold_metrics
        ),
        "fold_hashes_recorded": len({fold["target_sha256"] for fold in fold_metrics})
        == args.fold_count,
        "current_mode_beats_global_mean": current_scores["mean_accuracy"]
        > score_summary["global_mode"]["mean_accuracy"],
        "current_mode_beats_sample_current_mean": current_scores["mean_accuracy"]
        > score_summary["sample_current"]["mean_accuracy"],
        "submission_is_ready": validation_report["status"] == "READY",
    }
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "metric": "accuracy",
        "validation": {
            "version": VALIDATION_VERSION,
            "fold_count": args.fold_count,
            "seed": args.seed,
            "group": "target_article_id",
            "category_balance": "broad target category",
            "folds": fold_metrics,
        },
        "hypothesis": "The per-current most frequent observed next click is the cheapest transferable baseline when test targets are unseen but most current articles recur.",
        "candidates": score_summary,
        "test_diagnostics": {
            "rows": int(len(test)),
            "current_seen_rate": float(full_model.seen_current_mask(test).mean()),
            "global_fallback_article_id": int(full_model.global_next_article_id),
            "unique_predictions": int(np.unique(test_prediction).size),
            "top_prediction_share": float(
                pd.Series(test_prediction).value_counts(normalize=True).iloc[0]
            ),
            "prediction_min": int(test_prediction.min()),
            "prediction_max": int(test_prediction.max()),
        },
        "acceptance_gate": {
            "checks": gate_checks,
            "status": "KEEP" if all(gate_checks.values()) else "INVESTIGATE",
        },
        "submission_validation": validation_report,
        "submission": str(submission_path),
        "runtime_seconds": float(time.perf_counter() - started),
    }
    validation_manifest = {
        "version": VALIDATION_VERSION,
        "fold_count": args.fold_count,
        "seed": args.seed,
        "group": "target_article_id",
        "folds": manifest_folds,
    }
    (experiment_dir / "validation_manifest.json").write_text(
        json.dumps(validation_manifest, indent=2) + "\n", encoding="utf-8"
    )
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
