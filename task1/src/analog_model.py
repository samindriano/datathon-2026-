"""Nearest-history road-delta forecaster for Task 1 traffic speeds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HISTORY_LENGTH, HORIZONS, windows_at_origins


FEATURE_GROUPS = ("last", "mean5", "slope5")


def state_features(history: np.ndarray, selected_roads: np.ndarray) -> np.ndarray:
    """Create causal network-state features for deterministic selected roads."""
    history = np.asarray(history, dtype=np.float32)
    selected_roads = np.asarray(selected_roads, dtype=np.int64)
    if history.ndim != 3 or history.shape[1] != HISTORY_LENGTH:
        raise ValueError(f"Expected (samples, 15, roads), got {history.shape}")
    if selected_roads.ndim != 1 or selected_roads.size == 0:
        raise ValueError("selected_roads must be a non-empty vector")
    selected = history[:, :, selected_roads]
    recent = selected[:, -5:]
    x = np.arange(5, dtype=np.float32)
    centered = x - x.mean()
    slope = np.einsum("ntr,t->nr", recent, centered) / float(
        np.square(centered).sum()
    )
    return np.concatenate(
        (selected[:, -1], recent.mean(axis=1), slope), axis=1
    ).astype(np.float32, copy=False)


@dataclass(frozen=True)
class AnalogModel:
    block: np.ndarray
    candidate_origins: np.ndarray
    selected_roads: np.ndarray
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    candidate_features: np.ndarray
    neighbor_count: int
    delta_shrinkage: float
    query_chunk_size: int

    def predict(self, history: np.ndarray) -> np.ndarray:
        history = np.asarray(history, dtype=np.float32)
        features = state_features(history, self.selected_roads).astype(np.float64)
        features = (features - self.feature_mean) / self.feature_scale
        candidate = self.candidate_features.astype(np.float64, copy=False)
        candidate_norm = np.square(candidate).sum(axis=1)
        result = np.empty(
            (len(history), len(HORIZONS), history.shape[2]), dtype=np.float32
        )
        for start in range(0, len(history), self.query_chunk_size):
            stop = min(start + self.query_chunk_size, len(history))
            query = features[start:stop]
            distances = (
                np.square(query).sum(axis=1)[:, None]
                + candidate_norm[None, :]
                - 2.0 * query @ candidate.T
            )
            nearest = np.argpartition(
                distances, kth=self.neighbor_count - 1, axis=1
            )[:, : self.neighbor_count]
            origins = self.candidate_origins[nearest]
            future = np.asarray(
                self.block[origins[:, :, None] + HORIZONS[None, None, :]],
                dtype=np.float32,
            )
            anchors = np.asarray(self.block[origins], dtype=np.float32)
            mean_delta = (future - anchors[:, :, None, :]).mean(axis=1)
            result[start:stop] = history[start:stop, -1, None, :] + (
                self.delta_shrinkage * mean_delta
            )
        zero_history = np.all(history == 0, axis=1)
        result = np.where(zero_history[:, None, :], 0.0, result)
        return np.maximum(result, 0.0).astype(np.float32, copy=False)


def fit_analog(
    block: np.ndarray,
    origin_start: int,
    origin_end: int,
    selected_road_count: int = 64,
    neighbor_count: int = 8,
    delta_shrinkage: float = 0.5,
    fit_chunk_size: int = 256,
    query_chunk_size: int = 64,
) -> AnalogModel:
    """Fit a training-only nearest-state library for one temporal regime."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    candidate_origins = np.arange(origin_start, origin_end + 1, dtype=np.int64)
    if not 1 <= neighbor_count <= len(candidate_origins):
        raise ValueError("neighbor_count must fit within candidate origins")
    if selected_road_count < 1 or selected_road_count > block.shape[1]:
        raise ValueError("selected_road_count must fit within the road count")
    if not 0 < delta_shrinkage <= 1:
        raise ValueError("delta_shrinkage must be in (0, 1]")
    if fit_chunk_size < 1 or query_chunk_size < 1:
        raise ValueError("chunk sizes must be positive")

    last_values = np.asarray(block[candidate_origins], dtype=np.float64)
    road_variance = last_values.var(axis=0)
    selected_roads = np.argsort(-road_variance, kind="stable")[:selected_road_count]

    feature_parts = []
    for start in range(0, len(candidate_origins), fit_chunk_size):
        origins = candidate_origins[start : start + fit_chunk_size]
        histories, _ = windows_at_origins(block, origins)
        feature_parts.append(state_features(histories, selected_roads))
    raw_features = np.concatenate(feature_parts, axis=0).astype(np.float64)
    feature_mean = raw_features.mean(axis=0)
    feature_scale = raw_features.std(axis=0)
    feature_scale = np.where(feature_scale > 1e-6, feature_scale, 1.0)
    candidate_features = ((raw_features - feature_mean) / feature_scale).astype(
        np.float32
    )
    return AnalogModel(
        block=block,
        candidate_origins=candidate_origins,
        selected_roads=selected_roads,
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        candidate_features=candidate_features,
        neighbor_count=neighbor_count,
        delta_shrinkage=float(delta_shrinkage),
        query_chunk_size=query_chunk_size,
    )
