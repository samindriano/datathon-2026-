"""Fixed conservative shrinkage blend for Task 1."""

from __future__ import annotations

import numpy as np


ANCHOR_WEIGHT = 0.75
GLOBALSTATE_WEIGHT = 0.25


def stable_blend_predictions(
    anchor_prediction: np.ndarray, globalstate_prediction: np.ndarray
) -> np.ndarray:
    """Blend the audited e010 anchor with a quarter globalstate signal."""
    anchor = np.asarray(anchor_prediction)
    globalstate = np.asarray(globalstate_prediction)
    if anchor.shape != globalstate.shape:
        raise ValueError(
            f"prediction shapes must match, got {anchor.shape} and {globalstate.shape}"
        )
    if not np.isfinite(anchor).all() or not np.isfinite(globalstate).all():
        raise ValueError("component predictions must be finite")
    prediction = (
        ANCHOR_WEIGHT * anchor.astype(np.float64)
        + GLOBALSTATE_WEIGHT * globalstate.astype(np.float64)
    )
    return np.maximum(prediction, 0.0).astype(np.float32)
