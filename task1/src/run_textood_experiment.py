"""Run d1-e008-textood on frozen folds and test-distribution guard checks."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import write_submission
from multifold import (
    HORIZONS,
    REGIME_WEIGHTS,
    build_folds,
    mse_by_horizon,
    summarize_fold_scores,
    windows_at_origins,
)
from ridge_model import classify_test_regime
from run_textres_experiment import load_train_text_blocks
from text_ood_model import GUARDED_FEATURE, fit_text_ood
from text_residual_model import load_aligned_texts


EXPERIMENT_ID = "d1-e008-textood"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=3)
    parser.add_argument("--validation-size", type=int, default=720)
    parser.add_argument("--min-train-origins", type=int, default=1440)
    parser.add_argument("--base-alpha", type=float, default=0.1)
    parser.add_argument("--residual-alpha", type=float, default=1.0)
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def acceptance_gate(
    ridge: dict[str, object],
    textres: dict[str, object],
    textood: dict[str, object],
    test_diagnostics: dict[str, float | int],
) -> dict[str, object]:
    ridge_folds = np.asarray(ridge["fold_mse"], dtype=np.float64)
    guarded_folds = np.asarray(textood["fold_mse"], dtype=np.float64)
    ridge_horizons = np.asarray(list(ridge["mse_by_horizon"].values()))
    guarded_horizons = np.asarray(list(textood["mse_by_horizon"].values()))
    checks = {
        "mean_improves_ridge_by_at_least_0_5_percent": float(textood["mean_mse"])
        <= 0.995 * float(ridge["mean_mse"]),
        "improves_at_least_two_folds_vs_ridge": int(
            (guarded_folds < ridge_folds).sum()
        )
        >= 2,
        "improves_at_least_two_horizons_vs_ridge": int(
            (guarded_horizons < ridge_horizons).sum()
        )
        >= 2,
        "worst_fold_within_one_percent_of_ridge": float(textood["worst_fold_mse"])
        <= 1.01 * float(ridge["worst_fold_mse"]),
        "mean_within_0_1_percent_of_textres": float(textood["mean_mse"])
        <= 1.001 * float(textres["mean_mse"]),
        "test_m2_mean_correction_is_nonpositive": float(
            test_diagnostics["guarded_m2_mean_correction_vs_ridge"]
        )
        <= 0.0,
        "test_m2_correction_reduced": float(
            test_diagnostics["guarded_m2_mean_correction_vs_ridge"]
        )
        < float(test_diagnostics["exact_m2_mean_correction_vs_ridge"]),
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def evaluate_candidates(
    blocks: list[np.ndarray],
    text_blocks: list[list[str]],
    fold_sets: list[list],
    args: argparse.Namespace,
) -> tuple[dict[str, dict[str, object]], list[list[int]]]:
    methods = ("ridge-history", "textres", "textood")
    scores: dict[str, list[np.ndarray]] = {method: [] for method in methods}
    guard_counts: list[list[int]] = []
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores: dict[str, list[np.ndarray]] = {method: [] for method in methods}
        block_guard_counts = []
        for fold in folds:
            origins = np.arange(
                fold.validation_origin_start, fold.validation_origin_end + 1
            )
            histories, targets = windows_at_origins(block, origins)
            model = fit_text_ood(
                block,
                texts,
                fold.train_origin_start,
                fold.train_origin_end,
                base_alpha=args.base_alpha,
                residual_alpha=args.residual_alpha,
                chunk_size=args.chunk_size,
            )
            validation_texts = [texts[index] for index in origins]
            predictions = {
                "ridge-history": model.base.base_model.predict(histories),
                "textres": model.base.predict(histories, validation_texts),
                "textood": model.predict(histories, validation_texts),
            }
            block_guard_counts.append(int(model.guard_mask(validation_texts).sum()))
            for method in methods:
                block_scores[method].append(
                    mse_by_horizon(targets, predictions[method])
                )
        guard_counts.append(block_guard_counts)
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))
    return (
        {method: summarize_fold_scores(scores[method]) for method in methods},
        guard_counts,
    )


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    experiment_dir = args.experiment_dir.resolve()
    if experiment_dir.name != EXPERIMENT_ID:
        raise ValueError(f"Experiment directory must be named {EXPERIMENT_ID}")
    experiment_dir.mkdir(parents=True, exist_ok=True)

    train_paths = sorted((data_root / "train").glob("train_speed_*.npy"))
    if len(train_paths) != 2:
        raise ValueError(f"Expected two train blocks, found {len(train_paths)}")
    blocks = [np.load(path, mmap_mode="r") for path in train_paths]
    text_blocks = load_train_text_blocks(data_root, blocks)
    fold_sets = [
        build_folds(
            len(block),
            block_index=index,
            fold_count=args.fold_count,
            validation_size=args.validation_size,
            min_train_origins=args.min_train_origins,
        )
        for index, block in enumerate(blocks, start=1)
    ]
    candidates, validation_guard_counts = evaluate_candidates(
        blocks, text_blocks, fold_sets, args
    )

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = load_aligned_texts(data_root / "test" / "test_texts.json", test_keys)
    test_text_array = np.asarray(test_texts, dtype=object)
    regimes = classify_test_regime(test_history)
    final_models = [
        fit_text_ood(
            block,
            texts,
            origin_start=14,
            origin_end=len(block) - int(HORIZONS.max()) - 1,
            base_alpha=args.base_alpha,
            residual_alpha=args.residual_alpha,
            chunk_size=args.chunk_size,
        )
        for block, texts in zip(blocks, text_blocks, strict=True)
    ]
    ridge_prediction = np.empty(
        (len(test_history), len(HORIZONS), test_history.shape[2]), dtype=np.float32
    )
    exact_prediction = np.empty_like(ridge_prediction)
    guarded_prediction = np.empty_like(ridge_prediction)
    test_guard_counts = {}
    for regime_index, model in enumerate(final_models):
        mask = regimes == regime_index
        subset_texts = test_text_array[mask].tolist()
        ridge_prediction[mask] = model.base.base_model.predict(test_history[mask])
        exact_prediction[mask] = model.base.predict(test_history[mask], subset_texts)
        guarded_prediction[mask] = model.predict(test_history[mask], subset_texts)
        test_guard_counts[f"m{regime_index + 1}"] = int(
            model.guard_mask(subset_texts).sum()
        )

    m2 = regimes == 1
    diagnostics: dict[str, float | int] = {
        "exact_m2_mean_correction_vs_ridge": float(
            (exact_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "guarded_m2_mean_correction_vs_ridge": float(
            (guarded_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "guarded_vs_exact_m2_mean_change": float(
            (guarded_prediction[m2] - exact_prediction[m2]).mean()
        ),
        "test_m1_guarded_samples": test_guard_counts["m1"],
        "test_m2_guarded_samples": test_guard_counts["m2"],
    }
    gate = acceptance_gate(
        candidates["ridge-history"],
        candidates["textres"],
        candidates["textood"],
        diagnostics,
    )

    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(
            data_root / "sample_submission.csv", guarded_prediction, submission_path
        )

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "metric": "mse",
        "validation": {
            "version": "d1-multifold-v1",
            "fold_count_per_block": args.fold_count,
            "validation_origins_per_fold": args.validation_size,
            "minimum_training_origins": args.min_train_origins,
            "purge_origins": int(HORIZONS.max()),
            "regime_weights": {
                "m1": float(REGIME_WEIGHTS[0]),
                "m2": float(REGIME_WEIGHTS[1]),
            },
            "folds": [[fold.to_dict() for fold in folds] for folds in fold_sets],
            "guarded_validation_samples": validation_guard_counts,
        },
        "hypothesis": "Neutralizing out-of-training-range turn-restriction counts preserves aligned text gain while removing risky test-m2 extrapolation.",
        "preregistered_parameters": {
            "base_alpha": args.base_alpha,
            "residual_alpha": args.residual_alpha,
            "guarded_feature": GUARDED_FEATURE,
            "guard_trigger": "raw value outside training-origin min/max",
            "guard_action": "set standardized feature to zero (training mean)",
            "other_features_unchanged": True,
            "seed": None,
        },
        "candidates": candidates,
        "test_diagnostics": diagnostics,
        "acceptance_gate": gate,
        "test_regime_counts": {
            "m1": int((regimes == 0).sum()),
            "m2": int((regimes == 1).sum()),
        },
        "prediction": {
            "shape": list(guarded_prediction.shape),
            "min": float(guarded_prediction.min()),
            "max": float(guarded_prediction.max()),
            "mean": float(guarded_prediction.mean()),
            "submission_rows": int(guarded_prediction.size),
        },
        "submission": str(submission_path) if submission_path is not None else None,
        "runtime_seconds": float(time.perf_counter() - started),
    }
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print(f"submission={submission_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
