import numpy as np
import pytest

from global_state_model import (
    FEATURE_NAMES,
    fit_global_state_ridge,
    global_state_history_features,
)
from ridge_model import history_features


def test_global_features_exclude_structural_zero_roads_and_broadcast():
    history = np.zeros((1, 15, 3), dtype=np.float32)
    history[0, :, 0] = np.arange(1, 16)
    history[0, :, 1] = np.arange(3, 18)

    features = global_state_history_features(history)
    expected_city = history[:, :, :2].mean(axis=2, keepdims=True)
    expected_city_features = history_features(expected_city)[0, 0]

    assert features.shape == (1, 3, len(FEATURE_NAMES))
    np.testing.assert_allclose(
        features[0, :, 5:], np.repeat(expected_city_features[None, :], 3, axis=0)
    )
    np.testing.assert_allclose(features[:, :, :5], history_features(history))


def test_global_features_reject_invalid_history_shape():
    with pytest.raises(ValueError, match="Expected"):
        global_state_history_features(np.zeros((2, 14, 3), dtype=np.float32))


def test_fitted_model_is_finite_and_preserves_all_zero_history():
    time = np.arange(80, dtype=np.float32)[:, None]
    road = np.arange(4, dtype=np.float32)[None, :]
    block = 20.0 + 0.1 * time + road
    block[:, 3] = 0.0

    model = fit_global_state_ridge(block, 14, 55, alpha=0.1, chunk_size=16)
    history = np.stack((block[41:56], block[42:57]))
    prediction = model.predict(history)

    assert prediction.shape == (2, 3, 4)
    assert np.isfinite(prediction).all()
    assert (prediction >= 0).all()
    assert np.all(prediction[:, :, 3] == 0)
