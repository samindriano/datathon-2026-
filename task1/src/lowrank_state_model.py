"""Per-road ridge augmented with training-only low-rank road-network factors."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HORIZONS, windows_at_origins
from ridge_model import FEATURE_NAMES as LOCAL_FEATURE_NAMES
from ridge_model import history_features


DEFAULT_RANK = 4
DEFAULT_PCA_SAMPLES = 360
FEATURE_NAMES = (
    *LOCAL_FEATURE_NAMES,
    *(
        f"factor{factor}_{name}"
        for factor in range(DEFAULT_RANK)
        for name in LOCAL_FEATURE_NAMES
    ),
)


def fit_lowrank_basis(
    block: np.ndarray,
    origin_end: int,
    rank: int = DEFAULT_RANK,
    sample_count: int = DEFAULT_PCA_SAMPLES,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fit a deterministic road basis from evenly spaced causal training rows."""
    if origin_end < 0 or origin_end >= len(block):
        raise ValueError("origin_end is outside the block")
    if rank < 1 or sample_count < rank:
        raise ValueError("rank and sample_count are invalid")
    rows = np.unique(
        np.linspace(0, origin_end, min(sample_count, origin_end + 1), dtype=np.int64)
    )
    sample = np.asarray(block[rows], dtype=np.float64)
    road_mean = sample.mean(axis=0)
    road_scale = sample.std(axis=0)
    road_scale = np.where(road_scale > 1e-6, road_scale, 1.0)
    standardized = (sample - road_mean) / road_scale
    _, _, right = np.linalg.svd(standardized, full_matrices=False)
    basis = right[:rank].astype(np.float64, copy=False)
    return road_mean, road_scale, basis, rows


def lowrank_history_features(
    history: np.ndarray,
    road_mean: np.ndarray,
    road_scale: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    """Append five temporal summaries for each latent spatial factor."""
    history = np.asarray(history, dtype=np.float32)
    local = history_features(history)
    if road_mean.shape != (history.shape[2],) or road_scale.shape != road_mean.shape:
        raise ValueError("road preprocessing shape does not match history")
    if basis.ndim != 2 or basis.shape[1] != history.shape[2]:
        raise ValueError("basis shape does not match history")
    standardized = (history.astype(np.float64) - road_mean[None, None, :]) / road_scale[
        None, None, :
    ]
    factors = np.einsum("ntr,kr->ntk", standardized, basis, optimize=True)
    factor_features = history_features(factors.astype(np.float32)).reshape(
        len(history), -1
    )
    factor_features = np.broadcast_to(
        factor_features[:, None, :],
        (len(history), history.shape[2], factor_features.shape[1]),
    )
    return np.concatenate((local, factor_features), axis=2).astype(np.float32, copy=False)


@dataclass(frozen=True)
class LowRankStateRidgeModel:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    coefficients: np.ndarray
    road_mean: np.ndarray
    road_scale: np.ndarray
    basis: np.ndarray
    pca_rows: np.ndarray
    alpha: float

    def predict(self, history: np.ndarray) -> np.ndarray:
        features = lowrank_history_features(
            history, self.road_mean, self.road_scale, self.basis
        ).astype(np.float64)
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


def fit_lowrank_state_ridge(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    alpha: float = 0.1,
    rank: int = DEFAULT_RANK,
    pca_sample_count: int = DEFAULT_PCA_SAMPLES,
    chunk_size: int = 256,
) -> LowRankStateRidgeModel:
    """Fit per-road ridge using local features and training-only latent factors."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if alpha <= 0 or chunk_size < 1:
        raise ValueError("alpha and chunk_size must be positive")
    road_mean, road_scale, basis, pca_rows = fit_lowrank_basis(
        block, origin_end, rank=rank, sample_count=pca_sample_count
    )
    road_count = block.shape[1]
    feature_count = len(LOCAL_FEATURE_NAMES) + rank * len(LOCAL_FEATURE_NAMES)
    horizon_count = len(HORIZONS)
    sum_x = np.zeros((road_count, feature_count), dtype=np.float64)
    sum_y = np.zeros((road_count, horizon_count), dtype=np.float64)
    sum_xx = np.zeros((road_count, feature_count, feature_count), dtype=np.float64)
    sum_xy = np.zeros((road_count, feature_count, horizon_count), dtype=np.float64)
    sample_count = 0
    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        histories, targets = windows_at_origins(block, np.arange(start, stop))
        x = lowrank_history_features(histories, road_mean, road_scale, basis).astype(
            np.float64
        )
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
    return LowRankStateRidgeModel(
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        target_mean=target_mean,
        coefficients=coefficients,
        road_mean=road_mean,
        road_scale=road_scale,
        basis=basis,
        pca_rows=pca_rows,
        alpha=float(alpha),
    )
