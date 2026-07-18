"""Per-road ridge augmented with sparse road-neighbor history summaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from multifold import HORIZONS, windows_at_origins
from ridge_model import FEATURE_NAMES as LOCAL_FEATURE_NAMES
from ridge_model import history_features as local_history_features


FEATURE_NAMES = (*LOCAL_FEATURE_NAMES, *(f"neighbor_{name}" for name in LOCAL_FEATURE_NAMES))


def build_neighbor_edges(adjacency: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return row-normalized undirected external-neighbor edges."""
    adjacency = np.asarray(adjacency)
    if adjacency.ndim != 2 or adjacency.shape[0] != adjacency.shape[1]:
        raise ValueError(f"Expected square adjacency, got {adjacency.shape}")
    if not np.isfinite(adjacency).all():
        raise ValueError("adjacency must be finite")
    connected = (adjacency != 0) | (adjacency.T != 0)
    np.fill_diagonal(connected, False)
    rows, columns = np.nonzero(connected)
    degree = np.bincount(rows, minlength=len(adjacency))
    weights = 1.0 / degree[rows]
    return (
        rows.astype(np.int64),
        columns.astype(np.int64),
        weights.astype(np.float32),
    )


def graph_history_features(
    history: np.ndarray,
    edge_rows: np.ndarray,
    edge_columns: np.ndarray,
    edge_weights: np.ndarray,
    edge_chunk_size: int = 1024,
) -> np.ndarray:
    """Append neighbor means of the five local ridge features."""
    local = local_history_features(history)
    neighbor = np.zeros_like(local)
    for start in range(0, len(edge_rows), edge_chunk_size):
        stop = min(start + edge_chunk_size, len(edge_rows))
        rows = edge_rows[start:stop]
        columns = edge_columns[start:stop]
        contribution = local[:, columns, :] * edge_weights[None, start:stop, None]
        np.add.at(neighbor, (slice(None), rows, slice(None)), contribution)
    return np.concatenate((local, neighbor), axis=2).astype(np.float32, copy=False)


@dataclass(frozen=True)
class GraphRidgeModel:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    coefficients: np.ndarray
    edge_rows: np.ndarray
    edge_columns: np.ndarray
    edge_weights: np.ndarray
    alpha: float

    def predict(self, history: np.ndarray) -> np.ndarray:
        features = graph_history_features(
            history, self.edge_rows, self.edge_columns, self.edge_weights
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


def fit_graph_ridge(
    block: np.ndarray,
    adjacency: np.ndarray,
    origin_start: int,
    origin_end: int,
    alpha: float = 0.1,
    chunk_size: int = 256,
) -> GraphRidgeModel:
    """Fit per-road ridge using local and neighbor summaries on train origins."""
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if alpha <= 0 or chunk_size < 1:
        raise ValueError("alpha and chunk_size must be positive")
    if adjacency.shape != (block.shape[1], block.shape[1]):
        raise ValueError("adjacency road count does not match the speed block")

    edge_rows, edge_columns, edge_weights = build_neighbor_edges(adjacency)
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
        x = graph_history_features(
            histories, edge_rows, edge_columns, edge_weights
        ).astype(np.float64)
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
    return GraphRidgeModel(
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        target_mean=target_mean,
        coefficients=coefficients,
        edge_rows=edge_rows,
        edge_columns=edge_columns,
        edge_weights=edge_weights,
        alpha=float(alpha),
    )
