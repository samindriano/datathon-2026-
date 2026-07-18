"""Causal daily-phase traffic prototype for Task 1."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HISTORY_LENGTH, HORIZONS, windows_at_origins


PERIOD = 360
ROAD_GROUPS = 4


def _history_signature(history: np.ndarray, groups: tuple[np.ndarray, ...]) -> np.ndarray:
    history = np.asarray(history, dtype=np.float32)
    if history.ndim != 3 or history.shape[1] != HISTORY_LENGTH:
        raise ValueError(f"Expected (samples, 15, roads), got {history.shape}")
    values = []
    for group in groups:
        if len(group) == 0:
            values.append(np.zeros((len(history), HISTORY_LENGTH), dtype=np.float32))
        else:
            values.append(history[:, :, group].mean(axis=2))
    return np.concatenate(values, axis=1).astype(np.float32, copy=False)


@dataclass(frozen=True)
class SeasonalPhaseModel:
    groups: tuple[np.ndarray, ...]
    signature_mean: np.ndarray
    signature_scale: np.ndarray
    phase_templates: np.ndarray
    phase_delta: np.ndarray
    period: int

    def infer_phase(self, history: np.ndarray) -> np.ndarray:
        signature = _history_signature(history, self.groups).astype(np.float64)
        standardized = (signature - self.signature_mean) / self.signature_scale
        distance = (
            np.square(standardized).sum(axis=1, keepdims=True)
            + np.square(self.phase_templates).sum(axis=1)[None, :]
            - 2.0 * standardized @ self.phase_templates.T
        )
        return np.argmin(distance, axis=1).astype(np.int64)

    def predict(self, history: np.ndarray) -> np.ndarray:
        history = np.asarray(history, dtype=np.float32)
        phase = self.infer_phase(history)
        prediction = history[:, -1, None, :] + self.phase_delta[phase]
        zero_history = np.all(history == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def fit_seasonal_phase(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    period: int = PERIOD,
    road_groups: int = ROAD_GROUPS,
    chunk_size: int = 256,
) -> SeasonalPhaseModel:
    """Fit phase templates and per-road future deltas from training origins only."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if period < 2 or road_groups < 1 or chunk_size < 1:
        raise ValueError("period, road_groups, and chunk_size must be positive")

    training_slice = np.asarray(
        block[max(0, origin_start - HISTORY_LENGTH + 1) : origin_end + 1],
        dtype=np.float32,
    )
    active = np.any(training_slice != 0, axis=0)
    active_indices = np.flatnonzero(active)
    road_mean = training_slice[:, active_indices].mean(axis=0)
    ordered = active_indices[np.argsort(road_mean, kind="stable")]
    groups = tuple(np.asarray(group, dtype=np.int64) for group in np.array_split(ordered, road_groups))

    feature_count = HISTORY_LENGTH * road_groups
    road_count = block.shape[1]
    signature_sum = np.zeros((period, feature_count), dtype=np.float64)
    delta_sum = np.zeros((period, len(HORIZONS), road_count), dtype=np.float64)
    phase_count = np.zeros(period, dtype=np.int64)
    all_signature_sum = np.zeros(feature_count, dtype=np.float64)
    all_signature_sq_sum = np.zeros(feature_count, dtype=np.float64)
    sample_count = 0

    for start in range(origin_start, origin_end + 1, chunk_size):
        stop = min(start + chunk_size, origin_end + 1)
        origins = np.arange(start, stop, dtype=np.int64)
        history, targets = windows_at_origins(block, origins)
        signature = _history_signature(history, groups).astype(np.float64)
        delta = targets.astype(np.float64) - history[:, -1, None, :].astype(np.float64)
        phases = origins % period
        np.add.at(signature_sum, phases, signature)
        np.add.at(delta_sum, phases, delta)
        np.add.at(phase_count, phases, 1)
        all_signature_sum += signature.sum(axis=0)
        all_signature_sq_sum += np.square(signature).sum(axis=0)
        sample_count += len(origins)

    if np.any(phase_count == 0):
        missing = np.flatnonzero(phase_count == 0)
        raise ValueError(f"Training fold does not cover all phases: {missing.tolist()}")

    signature_mean = all_signature_sum / sample_count
    signature_var = np.maximum(
        all_signature_sq_sum / sample_count - np.square(signature_mean), 0.0
    )
    signature_scale = np.where(np.sqrt(signature_var) > 1e-6, np.sqrt(signature_var), 1.0)
    phase_signature = signature_sum / phase_count[:, None]
    phase_templates = (phase_signature - signature_mean) / signature_scale
    phase_delta = delta_sum / phase_count[:, None, None]
    return SeasonalPhaseModel(
        groups=groups,
        signature_mean=signature_mean,
        signature_scale=signature_scale,
        phase_templates=phase_templates,
        phase_delta=phase_delta.astype(np.float32),
        period=int(period),
    )

