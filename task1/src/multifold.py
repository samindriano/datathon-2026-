"""Leakage-safe chronological folds and scoring for Task 1."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


HISTORY_LENGTH = 15
HORIZONS = np.array([5, 10, 15], dtype=np.int64)
REGIME_WEIGHTS = np.array([372.0, 168.0], dtype=np.float64) / 540.0


@dataclass(frozen=True)
class Fold:
    block: int
    fold: int
    train_origin_start: int
    train_origin_end: int
    validation_origin_start: int
    validation_origin_end: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def build_folds(
    block_length: int,
    block_index: int,
    fold_count: int = 3,
    validation_size: int = 720,
    min_train_origins: int = 1440,
) -> list[Fold]:
    """Create expanding folds spread across a block with a 15-origin purge."""
    if fold_count < 1 or validation_size < 1 or min_train_origins < 1:
        raise ValueError("fold_count, validation_size, and min_train_origins must be positive")

    max_horizon = int(HORIZONS.max())
    first_origin = HISTORY_LENGTH - 1
    earliest_validation_start = first_origin + min_train_origins + max_horizon
    latest_validation_start = block_length - max_horizon - validation_size
    if earliest_validation_start > latest_validation_start:
        raise ValueError(
            f"Block length {block_length} cannot support {fold_count} folds with "
            f"validation_size={validation_size} and min_train_origins={min_train_origins}"
        )

    starts = np.rint(
        np.linspace(earliest_validation_start, latest_validation_start, fold_count)
    ).astype(int)
    if len(np.unique(starts)) != fold_count:
        raise ValueError("Fold starts are not unique; reduce fold_count or validation_size")

    folds = []
    for fold_index, validation_start in enumerate(starts, start=1):
        folds.append(
            Fold(
                block=block_index,
                fold=fold_index,
                train_origin_start=first_origin,
                train_origin_end=int(validation_start - max_horizon - 1),
                validation_origin_start=int(validation_start),
                validation_origin_end=int(validation_start + validation_size - 1),
            )
        )
    return folds


def windows_at_origins(
    block: np.ndarray, origins: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return histories and future targets for explicit origins."""
    origins = np.asarray(origins, dtype=np.int64)
    offsets = np.arange(HISTORY_LENGTH - 1, -1, -1, dtype=np.int64)
    histories = np.asarray(block[origins[:, None] - offsets[None, :]], dtype=np.float32)
    targets = np.asarray(block[origins[:, None] + HORIZONS[None, :]], dtype=np.float32)
    return histories, targets


def mse_by_horizon(target: np.ndarray, prediction: np.ndarray) -> np.ndarray:
    if target.shape != prediction.shape:
        raise ValueError(f"Target {target.shape} and prediction {prediction.shape} differ")
    errors = np.square(prediction.astype(np.float64) - target.astype(np.float64))
    return errors.mean(axis=(0, 2))


def summarize_fold_scores(per_block: list[np.ndarray]) -> dict[str, object]:
    """Aggregate arrays shaped (fold, horizon) using observed test-regime weights."""
    scores = np.asarray(per_block, dtype=np.float64)
    if scores.ndim != 3 or scores.shape[0] != 2 or scores.shape[2] != len(HORIZONS):
        raise ValueError(f"Expected (2, folds, 3) scores, got {scores.shape}")
    weighted = np.tensordot(REGIME_WEIGHTS, scores, axes=(0, 0))
    fold_means = weighted.mean(axis=1)
    return {
        "mean_mse": float(fold_means.mean()),
        "std_mse": float(fold_means.std()),
        "worst_fold_mse": float(fold_means.max()),
        "fold_mse": [float(value) for value in fold_means],
        "mse_by_horizon": {
            str(int(horizon)): float(value)
            for horizon, value in zip(HORIZONS, weighted.mean(axis=0), strict=True)
        },
        "fold_horizon_mse": weighted.tolist(),
        "block_fold_horizon_mse": scores.tolist(),
    }
