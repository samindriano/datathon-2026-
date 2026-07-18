"""Three-sigma inference guard for one Task 1 text residual feature."""

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
DEFAULT_Z_THRESHOLD = 3.0


def z_guarded_features(
    raw_features: np.ndarray,
    feature_mean: np.ndarray,
    feature_scale: np.ndarray,
    guard_index: int,
    z_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Neutralize one feature when its fitted-train z-score exceeds a limit."""
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")
    standardized = (raw_features - feature_mean) / feature_scale
    guard_mask = np.abs(standardized[:, guard_index]) > z_threshold
    standardized[guard_mask, guard_index] = 0.0
    return standardized, guard_mask


@dataclass(frozen=True)
class TextZGuardModel:
    base: TextResidualModel
    guard_index: int = GUARDED_FEATURE_INDEX
    z_threshold: float = DEFAULT_Z_THRESHOLD

    def guard_mask(self, texts: Sequence[str]) -> np.ndarray:
        raw = text_features(texts)
        standardized = (raw - self.base.feature_mean) / self.base.feature_scale
        return np.abs(standardized[:, self.guard_index]) > self.z_threshold

    def predict(self, history: np.ndarray, texts: Sequence[str]) -> np.ndarray:
        if len(history) != len(texts):
            raise ValueError("history and texts must have the same sample count")
        ridge_prediction = self.base.base_model.predict(history).astype(np.float64)
        standardized, _ = z_guarded_features(
            text_features(texts),
            self.base.feature_mean,
            self.base.feature_scale,
            self.guard_index,
            self.z_threshold,
        )
        residual = self.base.residual_mean[None, :, :] + np.einsum(
            "nf,rfh->nrh", standardized, self.base.coefficients, optimize=True
        )
        prediction = ridge_prediction + residual.transpose(0, 2, 1)
        zero_history = np.all(np.asarray(history) == 0, axis=1)
        prediction = np.where(zero_history[:, None, :], 0.0, prediction)
        return np.maximum(prediction, 0.0).astype(np.float32)


def fit_text_zguard(
    block: np.ndarray,
    texts: Sequence[str],
    origin_start: int,
    origin_end: int,
    base_alpha: float = 0.1,
    residual_alpha: float = 1.0,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
    chunk_size: int = 256,
) -> TextZGuardModel:
    """Fit unchanged textres and attach the fixed standardized guard."""
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")
    base = fit_text_residual(
        block,
        texts,
        origin_start,
        origin_end,
        base_alpha=base_alpha,
        residual_alpha=residual_alpha,
        chunk_size=chunk_size,
    )
    return TextZGuardModel(base=base, z_threshold=float(z_threshold))
