"""Per-road ridge forecaster using all 15 causal speed lags."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HISTORY_LENGTH, HORIZONS, windows_at_origins


FEATURE_NAMES = tuple(f"lag{lag}" for lag in range(HISTORY_LENGTH - 1, -1, -1))


def history_features(history: np.ndarray) -> np.ndarray:
    """Return raw lag features shaped (samples, roads, 15)."""
    history = np.asarray(history, dtype=np.float32)
    if history.ndim != 3 or history.shape[1] != HISTORY_LENGTH:
        raise ValueError(f"Expected (samples, 15, roads), got {history.shape}")
    return history.transpose(0, 2, 1).astype(np.float32, copy=False)


@dataclass(frozen=True)
class RoadAR15Model:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    coefficients: np.ndarray
    alpha: float

    def predict(self, history: np.ndarray) -> np.ndarray:
        features = history_features(history).astype(np.float64)
        standardized = (features - self.feature_mean[None, :, :]) / self.feature_scale[
            None, :, :
        ]
        prediction = self.target_mean[None, :, :] + np.einsum(
            "nrf,rfh->nrh", standardized, self.coefficients, optimize=True
        )
        prediction = prediction.transpose(0, 2, 1)
        zero_history = np.all(np.asarray(history) == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def fit_road_ar15(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    alpha: float = 0.1,
    chunk_size: int = 256,
) -> RoadAR15Model:
    """Fit independent standardized ridge coefficients for all 15 lags."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if alpha <= 0 or chunk_size < 1:
        raise ValueError("alpha and chunk_size must be positive")

    road_count = block.shape[1]
    feature_count = HISTORY_LENGTH
    horizon_count = len(HORIZONS)
    sum_x = np.zeros((road_count, feature_count), dtype=np.float64)
    sum_y = np.zeros((road_count, horizon_count), dtype=np.float64)
    sum_xx = np.zeros((road_count, feature_count, feature_count), dtype=np.float64)
    sum_xy = np.zeros((road_count, feature_count, horizon_count), dtype=np.float64)
    sample_count = 0

    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        histories, targets = windows_at_origins(block, np.arange(start, stop))
        x = history_features(histories).astype(np.float64)
        y = targets.transpose(0, 2, 1).astype(np.float64)
        sum_x += x.sum(axis=0)
        sum_y += y.sum(axis=0)
        sum_xx += np.einsum("nrf,nrg->rfg", x, x, optimize=True)
        sum_xy += np.einsum("nrf,nrh->rfh", x, y, optimize=True)
        sample_count += len(x)

    feature_mean = sum_x / sample_count
    target_mean = sum_y / sample_count
    covariance = sum_xx / sample_count - np.einsum(
        "rf,rg->rfg", feature_mean, feature_mean
    )
    cross_covariance = sum_xy / sample_count - np.einsum(
        "rf,rh->rfh", feature_mean, target_mean
    )
    variance = np.maximum(np.diagonal(covariance, axis1=1, axis2=2), 0.0)
    feature_scale = np.sqrt(variance)
    feature_scale = np.where(feature_scale > 1e-6, feature_scale, 1.0)
    standardized_covariance = covariance / (
        feature_scale[:, :, None] * feature_scale[:, None, :]
    )
    standardized_cross_covariance = cross_covariance / feature_scale[:, :, None]
    system = standardized_covariance + alpha * np.eye(feature_count)[None, :, :]
    coefficients = np.linalg.solve(system, standardized_cross_covariance)
    return RoadAR15Model(
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        target_mean=target_mean,
        coefficients=coefficients,
        alpha=float(alpha),
    )
