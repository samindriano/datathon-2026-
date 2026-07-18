"""Training-only novelty guard for the frozen E016 low-rank correction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lowrank_state_model import LowRankStateRidgeModel
from multifold import windows_at_origins
from ridge_model import history_features


DEFAULT_Z_THRESHOLD = 3.0


def novelty_features(
    history: np.ndarray, model: LowRankStateRidgeModel
) -> np.ndarray:
    """Return latent temporal summaries plus reconstruction-error RMS."""
    history64 = np.asarray(history, dtype=np.float64)
    standardized = (history64 - model.road_mean[None, None, :]) / model.road_scale[
        None, None, :
    ]
    factors = np.einsum(
        "ntr,kr->ntk", standardized, model.basis, optimize=True
    )
    factor_features = history_features(factors.astype(np.float32)).reshape(
        len(history64), -1
    )
    reconstruction = np.einsum(
        "ntk,kr->ntr", factors, model.basis, optimize=True
    )
    reconstruction_rms = np.sqrt(
        np.mean(np.square(standardized - reconstruction), axis=(1, 2))
    )
    return np.concatenate(
        (factor_features.astype(np.float64), reconstruction_rms[:, None]), axis=1
    )


@dataclass(frozen=True)
class LowRankNoveltyGuard:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    z_threshold: float = DEFAULT_Z_THRESHOLD

    def trusted(self, history: np.ndarray, model: LowRankStateRidgeModel) -> np.ndarray:
        features = novelty_features(history, model)
        z = np.abs((features - self.feature_mean[None, :]) / self.feature_scale[None, :])
        return np.max(z, axis=1) <= self.z_threshold


def fit_lowrank_novelty_guard(
    block: np.ndarray,
    model: LowRankStateRidgeModel,
    origin_start: int,
    origin_end: int,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
    chunk_size: int = 256,
) -> LowRankNoveltyGuard:
    """Fit novelty standardization on training origins only."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if z_threshold <= 0 or chunk_size < 1:
        raise ValueError("z_threshold and chunk_size must be positive")
    total = None
    total_square = None
    count = 0
    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        histories, _ = windows_at_origins(block, np.arange(start, stop))
        features = novelty_features(histories, model)
        if total is None:
            total = np.zeros(features.shape[1], dtype=np.float64)
            total_square = np.zeros(features.shape[1], dtype=np.float64)
        total += features.sum(axis=0)
        total_square += np.square(features).sum(axis=0)
        count += len(features)
    mean = total / count
    variance = np.maximum(total_square / count - np.square(mean), 0.0)
    scale = np.sqrt(variance)
    scale = np.where(scale > 1e-6, scale, 1.0)
    return LowRankNoveltyGuard(mean, scale, float(z_threshold))


def apply_lowrank_novelty_guard(
    reference_prediction: np.ndarray,
    lowrank_prediction: np.ndarray,
    trusted: np.ndarray,
) -> np.ndarray:
    """Use E016 only for trusted origins and otherwise revert exactly to E013."""
    reference = np.asarray(reference_prediction, dtype=np.float32)
    lowrank = np.asarray(lowrank_prediction, dtype=np.float32)
    trusted = np.asarray(trusted, dtype=bool)
    if reference.shape != lowrank.shape or trusted.shape != (len(reference),):
        raise ValueError("prediction or trust-mask shape mismatch")
    return np.where(trusted[:, None, None], lowrank, reference).astype(
        np.float32, copy=False
    )
