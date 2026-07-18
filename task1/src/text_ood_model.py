"""OOD-guarded inference for the fixed Task 1 text residual model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from text_residual_model import (
    EVENT_PATTERNS,
    TextResidualModel,
    fit_text_residual,
    text_features,
)


GUARDED_FEATURE = "prohibit left turn"
GUARDED_FEATURE_INDEX = EVENT_PATTERNS.index(GUARDED_FEATURE)


def guarded_standardized_features(
    raw_features: np.ndarray,
    feature_mean: np.ndarray,
    feature_scale: np.ndarray,
    guard_index: int,
    training_minimum: float,
    training_maximum: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Neutralize one feature to its training mean only when out of range."""
    standardized = (raw_features - feature_mean) / feature_scale
    guard_mask = (raw_features[:, guard_index] < training_minimum) | (
        raw_features[:, guard_index] > training_maximum
    )
    standardized[guard_mask, guard_index] = 0.0
    return standardized, guard_mask


@dataclass(frozen=True)
class TextOODModel:
    base: TextResidualModel
    guard_index: int
    training_minimum: float
    training_maximum: float

    def guard_mask(self, texts: Sequence[str]) -> np.ndarray:
        raw = text_features(texts)
        return (raw[:, self.guard_index] < self.training_minimum) | (
            raw[:, self.guard_index] > self.training_maximum
        )

    def predict(self, history: np.ndarray, texts: Sequence[str]) -> np.ndarray:
        if len(history) != len(texts):
            raise ValueError("history and texts must have the same sample count")
        ridge_prediction = self.base.base_model.predict(history).astype(np.float64)
        raw = text_features(texts)
        standardized, _ = guarded_standardized_features(
            raw,
            self.base.feature_mean,
            self.base.feature_scale,
            self.guard_index,
            self.training_minimum,
            self.training_maximum,
        )
        residual = self.base.residual_mean[None, :, :] + np.einsum(
            "nf,rfh->nrh", standardized, self.base.coefficients, optimize=True
        )
        prediction = ridge_prediction + residual.transpose(0, 2, 1)
        zero_history = np.all(np.asarray(history) == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def fit_text_ood(
    block: np.ndarray,
    texts: Sequence[str],
    origin_start: int,
    origin_end: int,
    base_alpha: float = 0.1,
    residual_alpha: float = 1.0,
    chunk_size: int = 256,
) -> TextOODModel:
    """Fit the unchanged text model and record train range for one feature."""
    base = fit_text_residual(
        block,
        texts,
        origin_start,
        origin_end,
        base_alpha=base_alpha,
        residual_alpha=residual_alpha,
        chunk_size=chunk_size,
    )
    origins = np.arange(origin_start, origin_end + 1, dtype=np.int64)
    raw = text_features([texts[index] for index in origins])
    values = raw[:, GUARDED_FEATURE_INDEX]
    return TextOODModel(
        base=base,
        guard_index=GUARDED_FEATURE_INDEX,
        training_minimum=float(values.min()),
        training_maximum=float(values.max()),
    )
