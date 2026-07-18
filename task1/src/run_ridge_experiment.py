"""Run d1-e002-ridge with purged multi-fold chronological validation."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import predict as baseline_predict
from baseline import write_submission
from multifold import HORIZONS, REGIME_WEIGHTS, build_folds, mse_by_horizon, summarize_fold_scores, windows_at_origins
from ridge_model import FEATURE_NAMES, classify_test_regime, fit_road_ridge


EXPERIMENT_ID = "d1-e002-ridge"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=3)
    parser.add_argument("--validation-size", type=int, default=720)
    parser.add_argument("--min-train-origins", type=int, default=1440)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def evaluate_candidate(
    blocks: list[np.ndarray],
    fold_sets: list[list],
    method: str,
    alpha: float,
    chunk_size: int,
) -> dict[str, object]:
    per_block: list[np.ndarray] = []
    for block, folds in zip(blocks, fold_sets, strict=True):
        fold_scores = []
        for fold in folds:
            origins = np.arange(
                fold.validation_origin_start, fold.validation_origin_end + 1
            )
            histories, targets = windows_at_origins(block, origins)
            if method == "mean15":
                predictions = baseline_predict(histories, "mean15")
            elif method == "ridge-history":
                model = fit_road_ridge(
                    block,
                    fold.train_origin_start,
                    fold.train_origin_end,
                    alpha=alpha,
                    chunk_size=chunk_size,
                )
                predictions = model.predict(histories)
            else:
                raise ValueError(f"Unknown method: {method}")
            fold_scores.append(mse_by_horizon(targets, predictions))
        per_block.append(np.asarray(fold_scores))
    return summarize_fold_scores(per_block)


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

    candidates = {
        method: evaluate_candidate(
            blocks, fold_sets, method, alpha=args.alpha, chunk_size=args.chunk_size
        )
        for method in ("mean15", "ridge-history")
    }
    baseline_mse = float(candidates["mean15"]["mean_mse"])
    ridge_mse = float(candidates["ridge-history"]["mean_mse"])

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    regimes = classify_test_regime(test_history)
    final_models = [
        fit_road_ridge(
            block,
            origin_start=14,
            origin_end=len(block) - int(HORIZONS.max()) - 1,
            alpha=args.alpha,
            chunk_size=args.chunk_size,
        )
        for block in blocks
    ]
    test_prediction = np.empty(
        (len(test_history), len(HORIZONS), test_history.shape[2]), dtype=np.float32
    )
    for regime_index, model in enumerate(final_models):
        mask = regimes == regime_index
        test_prediction[mask] = model.predict(test_history[mask])
    submission_path = experiment_dir / "submission.csv"
    write_submission(data_root / "sample_submission.csv", test_prediction, submission_path)

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "metric": "mse",
        "validation": {
            "scheme": "expanding_chronological_multifold",
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
        "hypothesis": "Fixed per-road ridge on causal history summaries improves mean15 across purged folds.",
        "preregistered_parameters": {
            "features": list(FEATURE_NAMES),
            "alpha": args.alpha,
            "zero_history_guard": True,
            "upper_speed_clip": None,
            "seed": None,
        },
        "candidates": candidates,
        "ridge_improvement_mse": baseline_mse - ridge_mse,
        "ridge_improvement_percent": 100.0 * (baseline_mse - ridge_mse) / baseline_mse,
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
