import numpy as np
import pytest

from graphtext_blend import blend_predictions


def test_blend_is_exact_equal_average_and_preserves_zeros():
    graph = np.asarray([[[0.0, 2.0], [4.0, 6.0]]], dtype=np.float32)
    text = np.asarray([[[0.0, 4.0], [2.0, 10.0]]], dtype=np.float32)
    result = blend_predictions(graph, text)
    np.testing.assert_allclose(result, [[[0.0, 3.0], [3.0, 8.0]]])
    assert result.dtype == np.float32


def test_blend_rejects_mismatched_or_nonfinite_components():
    with pytest.raises(ValueError, match="shapes must match"):
        blend_predictions(np.zeros((1, 2)), np.zeros((2, 1)))
    with pytest.raises(ValueError, match="must be finite"):
        blend_predictions(np.asarray([np.nan]), np.asarray([0.0]))
