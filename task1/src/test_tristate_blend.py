import numpy as np
import pytest

from tristate_blend import tristate_blend_predictions


def test_tristate_is_exact_equal_average_and_preserves_joint_zero():
    stable = np.asarray([0.0, 3.0, 9.0], dtype=np.float32)
    dist = np.asarray([0.0, 6.0, 3.0], dtype=np.float32)
    lowrank = np.asarray([0.0, 9.0, 6.0], dtype=np.float32)
    np.testing.assert_allclose(
        tristate_blend_predictions(stable, dist, lowrank), [0.0, 6.0, 6.0]
    )


def test_tristate_rejects_shape_mismatch_and_nonfinite_input():
    with pytest.raises(ValueError, match="identical shapes"):
        tristate_blend_predictions(np.zeros(2), np.zeros(3), np.zeros(2))
    with pytest.raises(ValueError, match="finite"):
        tristate_blend_predictions(np.zeros(2), np.asarray([0.0, np.nan]), np.zeros(2))

