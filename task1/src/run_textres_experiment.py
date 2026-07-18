"""Run d1-e006-textres on the frozen Task 1 validation folds."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import predict as baseline_predict
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
from text_residual_model import FEATURE_NAMES, fit_text_residual, load_aligned_texts


EXPERIMENT_ID = "d1-e006-textres"


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
    ridge: dict[str, object], textres: dict[str, object]
) -> dict[str, object]:
    ridge_folds = np.asarray(ridge["fold_mse"], dtype=np.float64)
    text_folds = np.asarray(textres["fold_mse"], dtype=np.float64)
    ridge_horizons = np.asarray(list(ridge["mse_by_horizon"].values()))
    text_horizons = np.asarray(list(textres["mse_by_horizon"].values()))
    checks = {
        "mean_improves_by_at_least_0_5_percent": float(textres["mean_mse"])
        <= 0.995 * float(ridge["mean_mse"]),
        "improves_at_least_two_folds": int((text_folds < ridge_folds).sum()) >= 2,
        "improves_at_least_two_horizons": int(
            (text_horizons < ridge_horizons).sum()
        )
        >= 2,
        "worst_fold_within_one_percent": float(textres["worst_fold_mse"])
        <= 1.01 * float(ridge["worst_fold_mse"]),
    }
    return {
        "checks": checks,
        "folds_improved": int((text_folds < ridge_folds).sum()),
        "horizons_improved": int((text_horizons < ridge_horizons).sum()),
        "status": "KEEP" if all(checks.values()) else "REJECT",
    }


def load_train_text_blocks(data_root: Path, blocks: list[np.ndarray]) -> list[list[str]]:
    paths = sorted((data_root / "train").glob("train_text_*.json"))
    if len(paths) != 2:
        raise ValueError(f"Expected two train text blocks, found {len(paths)}")
    result = []
    for index, (path, block) in enumerate(zip(paths, blocks, strict=True), start=1):
        keys = [f"m{index}_{position}" for position in range(1, len(block) + 1)]
        result.append(load_aligned_texts(path, keys))
    return result


def evaluate_candidates(
    blocks: list[np.ndarray],
    text_blocks: list[list[str]],
    fold_sets: list[list],
    args: argparse.Namespace,
) -> dict[str, dict[str, object]]:
    methods = ("mean15", "ridge-history", "textres")
    scores: dict[str, list[np.ndarray]] = {method: [] for method in methods}
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores: dict[str, list[np.ndarray]] = {method: [] for method in methods}
        for fold in folds:
            origins = np.arange(
                fold.validation_origin_start, fold.validation_origin_end + 1
            )
            histories, targets = windows_at_origins(block, origins)
            model = fit_text_residual(
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
                "mean15": baseline_predict(histories, "mean15"),
                "ridge-history": model.base_model.predict(histories),
                "textres": model.predict(histories, validation_texts),
            }
            for method in methods:
                block_scores[method].append(
                    mse_by_horizon(targets, predictions[method])
                )
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))
    return {
        method: summarize_fold_scores(scores[method])
        for method in methods
    }


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
    candidates = evaluate_candidates(blocks, text_blocks, fold_sets, args)
    gate = acceptance_gate(candidates["ridge-history"], candidates["textres"])

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = load_aligned_texts(data_root / "test" / "test_texts.json", test_keys)
    regimes = classify_test_regime(test_history)
    final_models = [
        fit_text_residual(
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
    test_prediction = np.empty(
        (len(test_history), len(HORIZONS), test_history.shape[2]), dtype=np.float32
    )
    ridge_test_prediction = np.empty_like(test_prediction)
    test_text_array = np.asarray(test_texts, dtype=object)
    for regime_index, model in enumerate(final_models):
        mask = regimes == regime_index
        ridge_test_prediction[mask] = model.base_model.predict(test_history[mask])
        test_prediction[mask] = model.predict(
            test_history[mask], test_text_array[mask].tolist()
        )

    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(
            data_root / "sample_submission.csv", test_prediction, submission_path
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
        },
        "hypothesis": "Fixed global event-type counts explain per-road residuals beyond causal speed history.",
        "preregistered_parameters": {
            "features": list(FEATURE_NAMES),
            "base_alpha": args.base_alpha,
            "residual_alpha": args.residual_alpha,
            "zero_history_guard": True,
            "seed": None,
            "uses_external_model": False,
        },
        "candidates": candidates,
        "acceptance_gate": gate,
        "textres_improvement_vs_ridge_mse": float(
            candidates["ridge-history"]["mean_mse"]
            - candidates["textres"]["mean_mse"]
        ),
        "textres_improvement_vs_ridge_percent": float(
            100.0
            * (
                candidates["ridge-history"]["mean_mse"]
                - candidates["textres"]["mean_mse"]
            )
            / candidates["ridge-history"]["mean_mse"]
        ),
        "test_regime_counts": {
            "m1": int((regimes == 0).sum()),
            "m2": int((regimes == 1).sum()),
        },
        "prediction": {
            "shape": list(test_prediction.shape),
            "min": float(test_prediction.min()),
            "max": float(test_prediction.max()),
            "mean": float(test_prediction.mean()),
            "submission_rows": int(test_prediction.size),
        },
        "prediction_delta_vs_ridge": {
            "mean": float((test_prediction - ridge_test_prediction).mean()),
            "mean_absolute": float(
                np.abs(test_prediction - ridge_test_prediction).mean()
            ),
            "root_mean_square": float(
                np.sqrt(np.square(test_prediction - ridge_test_prediction).mean())
            ),
            "max_absolute": float(
                np.abs(test_prediction - ridge_test_prediction).max()
            ),
            "changed_fraction": float(
                np.mean(test_prediction != ridge_test_prediction)
            ),
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
