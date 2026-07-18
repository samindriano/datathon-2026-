"""Fixed equal blend of frozen E013, E014, and E016 predictions."""

from __future__ import annotations

import numpy as np


COMPONENT_WEIGHT = 1.0 / 3.0


def tristate_blend_predictions(
    stableblend: np.ndarray,
    distblend: np.ndarray,
    lowrankblend: np.ndarray,
) -> np.ndarray:
    arrays = tuple(np.asarray(value) for value in (stableblend, distblend, lowrankblend))
    if arrays[0].shape != arrays[1].shape or arrays[0].shape != arrays[2].shape:
        raise ValueError("all tristate components must have identical shapes")
    if any(not np.isfinite(value).all() for value in arrays):
        raise ValueError("all tristate components must be finite")
    prediction = COMPONENT_WEIGHT * (arrays[0] + arrays[1] + arrays[2])
    joint_zero = (arrays[0] == 0) & (arrays[1] == 0) & (arrays[2] == 0)
    return np.where(joint_zero, 0.0, np.maximum(prediction, 0.0)).astype(np.float32)

