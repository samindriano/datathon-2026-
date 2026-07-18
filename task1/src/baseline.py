"""Chronological no-training baselines for Task 1 traffic forecasting."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd


HORIZONS = np.array([5, 10, 15], dtype=np.int64)
HISTORY_LENGTH = 15
ROAD_COUNT = 1260
SPEED_MIN = 0.0
SPEED_MAX = 160.0


def predict(history: np.ndarray, method: str) -> np.ndarray:
    """Return predictions shaped (samples, horizons, roads)."""
    history = np.asarray(history, dtype=np.float32)
    if history.ndim != 3 or history.shape[1] != HISTORY_LENGTH:
        raise ValueError(f"Expected (samples, 15, roads), got {history.shape}")

    if method == "persist":
        base = history[:, -1]
        result = np.repeat(base[:, None, :], len(HORIZONS), axis=1)
    elif method.startswith("mean"):
        window = int(method.removeprefix("mean"))
        base = history[:, -window:].mean(axis=1)
        result = np.repeat(base[:, None, :], len(HORIZONS), axis=1)
    elif method.startswith("trend"):
        # Format: trend<window>-a<alpha*1000>, e.g. trend5-a250.
        window_part, alpha_part = method.split("-")
        window = int(window_part.removeprefix("trend"))
        alpha = int(alpha_part.removeprefix("a")) / 1000.0
        values = history[:, -window:]
        x = np.arange(window, dtype=np.float32)
        centered = x - x.mean()
        denominator = float(np.square(centered).sum())
        slope = np.einsum("str,t->sr", values, centered) / denominator
        result = history[:, -1, None, :] + (
            alpha * HORIZONS[None, :, None] * slope[:, None, :]
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    return np.clip(result, SPEED_MIN, SPEED_MAX).astype(np.float32, copy=False)


def validation_windows(block: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray]:
    """Build a contiguous tail-origin backtest without crossing block boundaries."""
    max_horizon = int(HORIZONS.max())
    last_origin = len(block) - max_horizon - 1
    first_origin = last_origin - count + 1
    if first_origin < HISTORY_LENGTH - 1:
        raise ValueError(f"Block of length {len(block)} is too short for {count} windows")

    origins = np.arange(first_origin, last_origin + 1)
    offsets = np.arange(HISTORY_LENGTH - 1, -1, -1)
    histories = np.asarray(block[origins[:, None] - offsets[None, :]], dtype=np.float32)
    targets = np.asarray(block[origins[:, None] + HORIZONS[None, :]], dtype=np.float32)
    return histories, targets


def mse_by_horizon(target: np.ndarray, prediction: np.ndarray) -> list[float]:
    errors = np.square(prediction.astype(np.float64) - target.astype(np.float64))
    return [float(value) for value in errors.mean(axis=(0, 2))]


def evaluate(
    blocks: list[np.ndarray], methods: list[str], validation_count: int
) -> tuple[dict, dict[int, str]]:
    block_windows = [validation_windows(block, validation_count) for block in blocks]
    metrics: dict[str, dict] = {}

    for method in methods:
        squared_error_sums = np.zeros(len(HORIZONS), dtype=np.float64)
        scored_values = np.zeros(len(HORIZONS), dtype=np.int64)
        per_block = []
        for histories, targets in block_windows:
            predictions = predict(histories, method)
            errors = np.square(
                predictions.astype(np.float64) - targets.astype(np.float64)
            )
            squared_error_sums += errors.sum(axis=(0, 2))
            scored_values += np.array(
                [errors.shape[0] * errors.shape[2]] * len(HORIZONS), dtype=np.int64
            )
            per_block.append(mse_by_horizon(targets, predictions))

        per_horizon = squared_error_sums / scored_values
        metrics[method] = {
            "mse": float(squared_error_sums.sum() / scored_values.sum()),
            "mse_by_horizon": {
                str(int(horizon)): float(score)
                for horizon, score in zip(HORIZONS, per_horizon, strict=True)
            },
            "mse_by_block_and_horizon": per_block,
        }

    selected = {
        int(horizon): min(
            methods, key=lambda method: metrics[method]["mse_by_horizon"][str(int(horizon))]
        )
        for horizon in HORIZONS
    }
    return metrics, selected


def predict_selected(history: np.ndarray, selected: dict[int, str]) -> np.ndarray:
    result = np.empty((len(history), len(HORIZONS), history.shape[2]), dtype=np.float32)
    cache: dict[str, np.ndarray] = {}
    for index, horizon in enumerate(HORIZONS):
        method = selected[int(horizon)]
        if method not in cache:
            cache[method] = predict(history, method)
        result[:, index] = cache[method][:, index]
    return result


def write_submission(template_path: Path, predictions: np.ndarray, output_path: Path) -> None:
    template = pd.read_csv(template_path)
    expected_rows = predictions.size
    if list(template.columns) != ["id", "speed"]:
        raise ValueError(f"Unexpected submission columns: {template.columns.tolist()}")
    if len(template) != expected_rows:
        raise ValueError(f"Template has {len(template)} rows, expected {expected_rows}")

    expected_ids = [
        f"test_{sample:05d}_h{int(horizon)}_r{road}"
        for sample in range(predictions.shape[0])
        for horizon in HORIZONS
        for road in range(predictions.shape[2])
    ]
    if template["id"].tolist() != expected_ids:
        raise ValueError("Template ID order does not match sample-horizon-road order")

    template["speed"] = predictions.reshape(-1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output_path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--validation-count", type=int, default=540)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    experiment_dir = args.experiment_dir.resolve()
    experiment_dir.mkdir(parents=True, exist_ok=True)

    train_paths = sorted((data_root / "train").glob("train_speed_*.npy"))
    blocks = [np.load(path, mmap_mode="r") for path in train_paths]
    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    methods = [
        "persist",
        "mean3",
        "mean5",
        "mean15",
        "trend5-a250",
        "trend5-a500",
        "trend10-a250",
        "trend10-a500",
        "trend15-a250",
    ]

    metrics, selected = evaluate(blocks, methods, args.validation_count)
    test_prediction = predict_selected(test_history, selected)
    submission_path = experiment_dir / "submission.csv"
    write_submission(data_root / "sample_submission.csv", test_prediction, submission_path)

    selected_scores = [
        metrics[selected[int(horizon)]]["mse_by_horizon"][str(int(horizon))]
        for horizon in HORIZONS
    ]
    summary = {
        "experiment_id": experiment_dir.name,
        "metric": "mse",
        "validation": {
            "scheme": "contiguous_tail_origins_per_train_block",
            "windows_per_block": args.validation_count,
            "history_steps": HISTORY_LENGTH,
            "horizons": HORIZONS.tolist(),
        },
        "candidates": metrics,
        "selected_method_by_horizon": {str(key): value for key, value in selected.items()},
        "selected_mse_by_horizon": {
            str(int(horizon)): float(score)
            for horizon, score in zip(HORIZONS, selected_scores, strict=True)
        },
        "selected_mean_mse": float(np.mean(selected_scores)),
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
    config = {
        "experiment_id": experiment_dir.name,
        "seed": None,
        "training": "none",
        "uses_event_text": False,
        "uses_road_graph": False,
        "speed_clip": [SPEED_MIN, SPEED_MAX],
        "validation_count_per_block": args.validation_count,
    }
    (experiment_dir / "config.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print(f"submission={submission_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
