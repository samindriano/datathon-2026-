"""Fixed ensemble utilities for Task 1 graph and guarded-text forecasts."""

from __future__ import annotations

import numpy as np


GRAPH_WEIGHT = 0.5
TEXT_WEIGHT = 0.5


def blend_predictions(
    graph_prediction: np.ndarray,
    text_prediction: np.ndarray,
) -> np.ndarray:
    """Return the preregistered equal-weight prediction average."""
    graph = np.asarray(graph_prediction)
    text = np.asarray(text_prediction)
    if graph.shape != text.shape:
        raise ValueError(
            f"prediction shapes must match, got {graph.shape} and {text.shape}"
        )
    if not np.isfinite(graph).all() or not np.isfinite(text).all():
        raise ValueError("component predictions must be finite")
    blended = GRAPH_WEIGHT * graph.astype(np.float64) + TEXT_WEIGHT * text.astype(
        np.float64
    )
    return np.maximum(blended, 0.0).astype(np.float32)
