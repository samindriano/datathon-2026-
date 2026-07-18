"""Shared convex lag-weight forecaster for Task 1 traffic speeds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HISTORY_LENGTH, HORIZONS, windows_at_origins


def project_simplex(values: np.ndarray) -> np.ndarray:
    """Project a one-dimensional vector onto the probability simplex."""
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("values must be a non-empty one-dimensional array")
    ordered = np.sort(values)[::-1]
    cumulative = np.cumsum(ordered)
    indices = np.arange(1, values.size + 1)
    positive = ordered - (cumulative - 1.0) / indices > 0
    if not positive.any():
        raise ValueError("simplex projection failed")
    rho = int(np.flatnonzero(positive)[-1])
    threshold = (cumulative[rho] - 1.0) / float(rho + 1)
    projected = np.maximum(values - threshold, 0.0)
    return projected / projected.sum()


@dataclass(frozen=True)
class LagBlendModel:
    weights: np.ndarray
    alpha: float
    active_pair_count: int

    def predict(self, history: np.ndarray) -> np.ndarray:
        history = np.asarray(history, dtype=np.float32)
        if history.ndim != 3 or history.shape[1] != HISTORY_LENGTH:
            raise ValueError(f"Expected (samples, 15, roads), got {history.shape}")
        prediction = np.einsum(
            "ntr,ht->nhr", history.astype(np.float64), self.weights, optimize=True
        )
        zero_history = np.all(history == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def _solve_convex_weights(
    gram: np.ndarray,
    cross: np.ndarray,
    alpha: float,
    max_iterations: int,
    tolerance: float,
) -> np.ndarray:
    prior = np.full(HISTORY_LENGTH, 1.0 / HISTORY_LENGTH, dtype=np.float64)
    system = gram + alpha * np.eye(HISTORY_LENGTH, dtype=np.float64)
    right = cross + alpha * prior[:, None]
    lipschitz = float(np.linalg.eigvalsh(system).max())
    if not np.isfinite(lipschitz) or lipschitz <= 0:
        raise ValueError("lag-weight system is not positive definite")

    result = np.empty((len(HORIZONS), HISTORY_LENGTH), dtype=np.float64)
    for horizon_index in range(len(HORIZONS)):
        weights = prior.copy()
        accelerated = weights.copy()
        momentum = 1.0
        for _ in range(max_iterations):
            gradient = system @ accelerated - right[:, horizon_index]
            updated = project_simplex(accelerated - gradient / lipschitz)
            if np.max(np.abs(updated - weights)) <= tolerance:
                weights = updated
                break
            next_momentum = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * momentum**2))
            accelerated = updated + (
                (momentum - 1.0) / next_momentum
            ) * (updated - weights)
            weights = updated
            momentum = next_momentum
        result[horizon_index] = weights
    return result


def fit_lagblend(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    alpha: float = 1.0,
    chunk_size: int = 256,
    max_iterations: int = 5000,
    tolerance: float = 1e-12,
) -> LagBlendModel:
    """Fit one convex 15-lag weight vector per horizon for a train regime."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if alpha <= 0 or chunk_size < 1 or max_iterations < 1 or tolerance <= 0:
        raise ValueError("fit parameters must be positive")

    gram = np.zeros((HISTORY_LENGTH, HISTORY_LENGTH), dtype=np.float64)
    cross = np.zeros((HISTORY_LENGTH, len(HORIZONS)), dtype=np.float64)
    active_pair_count = 0
    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        histories, targets = windows_at_origins(block, np.arange(start, stop))
        lag_rows = histories.transpose(0, 2, 1).reshape(-1, HISTORY_LENGTH)
        target_rows = targets.transpose(0, 2, 1).reshape(-1, len(HORIZONS))
        active = np.any(lag_rows != 0, axis=1)
        x = lag_rows[active].astype(np.float64)
        y = target_rows[active].astype(np.float64)
        gram += x.T @ x
        cross += x.T @ y
        active_pair_count += len(x)

    if active_pair_count == 0:
        raise ValueError("training range contains no active history pairs")
    weights = _solve_convex_weights(
        gram / active_pair_count,
        cross / active_pair_count,
        alpha=alpha,
        max_iterations=max_iterations,
        tolerance=tolerance,
    )
    return LagBlendModel(
        weights=weights,
        alpha=float(alpha),
        active_pair_count=active_pair_count,
    )
