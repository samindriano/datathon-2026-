"""Causal event-count residual corrections for the Task 1 ridge model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from multifold import HORIZONS, windows_at_origins
from ridge_model import RoadRidgeModel, fit_road_ridge


EVENT_PATTERNS = (
    "a general traffic accident",
    "road closure",
    "construction",
    "road traffic control",
    "an announcement",
    "prohibit left turn",
)
FEATURE_NAMES = (*EVENT_PATTERNS, "total_events")


def text_features(texts: Sequence[str]) -> np.ndarray:
    """Count fixed official event types without external language models."""
    rows = []
    for text in texts:
        if not isinstance(text, str):
            raise TypeError("all text entries must be strings")
        lowered = text.lower()
        counts = [lowered.count(pattern) for pattern in EVENT_PATTERNS]
        total_events = sum(bool(part.strip()) for part in lowered.split("."))
        rows.append((*counts, total_events))
    return np.asarray(rows, dtype=np.float64)


def load_aligned_texts(
    path: Path, expected_keys: Sequence[str]
) -> list[str]:
    """Load a JSON mapping only when its keys exactly match expected order."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    expected_keys = list(expected_keys)
    if list(data) != expected_keys:
        raise ValueError(f"Text keys in {path} do not match expected alignment")
    values = list(data.values())
    if not all(isinstance(value, str) for value in values):
        raise ValueError(f"Text values in {path} must all be strings")
    return values


@dataclass(frozen=True)
class TextResidualModel:
    base_model: RoadRidgeModel
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    residual_mean: np.ndarray
    coefficients: np.ndarray
    alpha: float

    def predict(self, history: np.ndarray, texts: Sequence[str]) -> np.ndarray:
        if len(history) != len(texts):
            raise ValueError("history and texts must have the same sample count")
        base = self.base_model.predict(history).astype(np.float64)
        features = text_features(texts)
        standardized = (features - self.feature_mean) / self.feature_scale
        residual = self.residual_mean[None, :, :] + np.einsum(
            "nf,rfh->nrh", standardized, self.coefficients, optimize=True
        )
        prediction = base + residual.transpose(0, 2, 1)
        zero_history = np.all(np.asarray(history) == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def fit_text_residual(
    block: np.ndarray,
    texts: Sequence[str],
    origin_start: int,
    origin_end: int,
    base_alpha: float = 0.1,
    residual_alpha: float = 1.0,
    chunk_size: int = 256,
) -> TextResidualModel:
    """Fit per-road residual coefficients from training-fold origins only."""
    if len(texts) != len(block):
        raise ValueError("texts must align one-to-one with block timesteps")
    if origin_end < origin_start:
        raise ValueError("origin_end must be at least origin_start")
    if base_alpha <= 0 or residual_alpha <= 0 or chunk_size < 1:
        raise ValueError("fit parameters must be positive")

    base_model = fit_road_ridge(
        block,
        origin_start,
        origin_end,
        alpha=base_alpha,
        chunk_size=chunk_size,
    )
    origins = np.arange(origin_start, origin_end + 1, dtype=np.int64)
    raw_features = text_features([texts[index] for index in origins])
    feature_mean = raw_features.mean(axis=0)
    feature_scale = raw_features.std(axis=0)
    feature_scale = np.where(feature_scale > 1e-6, feature_scale, 1.0)
    standardized_features = (raw_features - feature_mean) / feature_scale

    road_count = block.shape[1]
    horizon_count = len(HORIZONS)
    feature_count = len(FEATURE_NAMES)
    sum_residual = np.zeros((road_count, horizon_count), dtype=np.float64)
    sum_cross = np.zeros(
        (feature_count, road_count, horizon_count), dtype=np.float64
    )
    for start in range(0, len(origins), chunk_size):
        chunk_origins = origins[start : start + chunk_size]
        histories, targets = windows_at_origins(block, chunk_origins)
        base_prediction = base_model.predict(histories)
        residual = (
            targets.astype(np.float64) - base_prediction.astype(np.float64)
        ).transpose(0, 2, 1)
        x = standardized_features[start : start + len(chunk_origins)]
        sum_residual += residual.sum(axis=0)
        sum_cross += np.einsum("nf,nrh->frh", x, residual, optimize=True)

    sample_count = len(origins)
    residual_mean = sum_residual / sample_count
    covariance = standardized_features.T @ standardized_features / sample_count
    cross_covariance = sum_cross / sample_count
    system = covariance + residual_alpha * np.eye(feature_count)
    solved = np.linalg.solve(
        system, cross_covariance.reshape(feature_count, -1)
    )
    coefficients = solved.reshape(feature_count, road_count, horizon_count).transpose(
        1, 0, 2
    )
    return TextResidualModel(
        base_model=base_model,
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        residual_mean=residual_mean,
        coefficients=coefficients,
        alpha=float(residual_alpha),
    )
