import numpy as np

from distribution_state_model import (
    FEATURE_NAMES,
    distribution_state_history_features,
    fit_distribution_state_ridge,
)
from ridge_model import history_features


def test_distribution_features_exclude_structural_zero_roads():
    history = np.zeros((1, 15, 3), dtype=np.float32)
    history[0, :, 0] = 20.0
    history[0, :, 1] = 60.0
    features = distribution_state_history_features(history)

    assert features.shape == (1, 3, len(FEATURE_NAMES))
    expected_mean = history_features(np.full((1, 15, 1), 40.0, dtype=np.float32))[0, 0]
    expected_std = history_features(np.full((1, 15, 1), 20.0, dtype=np.float32))[0, 0]
    expected_slow30 = history_features(np.full((1, 15, 1), 0.5, dtype=np.float32))[0, 0]
    expected_slow50 = expected_slow30
    expected_state = np.concatenate(
        (expected_mean, expected_std, expected_slow30, expected_slow50)
    )
    np.testing.assert_allclose(features[0, :, 5:], np.repeat(expected_state[None], 3, axis=0))


def test_fitted_distribution_model_is_finite_and_zero_guarded():
    time = np.arange(80, dtype=np.float32)[:, None]
    road = np.arange(4, dtype=np.float32)[None, :]
    block = 20.0 + 0.1 * time + road
    block[:, 3] = 0.0
    model = fit_distribution_state_ridge(block, 14, 55, chunk_size=16)
    history = np.stack((block[41:56], block[42:57]))
    prediction = model.predict(history)
    assert prediction.shape == (2, 3, 4)
    assert np.isfinite(prediction).all()
    assert np.all(prediction[:, :, 3] == 0)
