"""Per-road ridge augmented with causal citywide traffic-state summaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HORIZONS, windows_at_origins
from ridge_model import FEATURE_NAMES as LOCAL_FEATURE_NAMES
from ridge_model import history_features as local_history_features


FEATURE_NAMES = (*LOCAL_FEATURE_NAMES, *(f"city_{name}" for name in LOCAL_FEATURE_NAMES))


def global_state_history_features(history: np.ndarray) -> np.ndarray:
    """Append five active-road city summaries to every road's local features."""
    history = np.asarray(history, dtype=np.float32)
    local = local_history_features(history)
    active = np.any(history != 0, axis=1)
    active_count = active.sum(axis=1, keepdims=True)
    safe_count = np.maximum(active_count, 1)
    city_history = (history * active[:, None, :]).sum(axis=2) / safe_count
    city_features = local_history_features(city_history[:, :, None])[:, 0, :]
    city_features = np.broadcast_to(
        city_features[:, None, :], (len(history), history.shape[2], len(LOCAL_FEATURE_NAMES))
    )
    return np.concatenate((local, city_features), axis=2).astype(np.float32, copy=False)


@dataclass(frozen=True)
class GlobalStateRidgeModel:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    coefficients: np.ndarray
    alpha: float

    def predict(self, history: np.ndarray) -> np.ndarray:
        features = global_state_history_features(history).astype(np.float64)
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


def fit_global_state_ridge(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    alpha: float = 0.1,
    chunk_size: int = 256,
) -> GlobalStateRidgeModel:
    """Fit per-road ridge using local and active-road city summaries."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if alpha <= 0 or chunk_size < 1:
        raise ValueError("alpha and chunk_size must be positive")

    road_count = block.shape[1]
    feature_count = len(FEATURE_NAMES)
    horizon_count = len(HORIZONS)
    sum_x = np.zeros((road_count, feature_count), dtype=np.float64)
    sum_y = np.zeros((road_count, horizon_count), dtype=np.float64)
    sum_xx = np.zeros((road_count, feature_count, feature_count), dtype=np.float64)
    sum_xy = np.zeros((road_count, feature_count, horizon_count), dtype=np.float64)
    sample_count = 0

    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        histories, targets = windows_at_origins(block, np.arange(start, stop))
        x = global_state_history_features(histories).astype(np.float64)
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
    return GlobalStateRidgeModel(
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        target_mean=target_mean,
        coefficients=coefficients,
        alpha=float(alpha),
    )
