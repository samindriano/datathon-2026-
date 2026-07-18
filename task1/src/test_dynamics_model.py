import numpy as np

from dynamics_model import dynamics_features, fit_dynamics_ridge


def test_features_split_positive_and_negative_slope():
    up = np.arange(15, dtype=np.float32)
    down = up[::-1]
    history = np.stack((up, down), axis=1)[None]
    features = dynamics_features(history)
    assert features.shape == (1, 2, 10)
    assert features[0, 0, 4] > 0 and features[0, 0, 5] == 0
    assert features[0, 1, 4] == 0 and features[0, 1, 5] < 0


def test_model_is_finite_and_preserves_structural_zero():
    time = np.arange(100, dtype=np.float32)
    block = np.stack((30.0 + np.sin(time / 5.0), np.zeros_like(time)), axis=1)
    model = fit_dynamics_ridge(block, 14, 70, chunk_size=16)
    prediction = model.predict(block[56:71][None])
    assert prediction.shape == (1, 3, 2)
    assert np.isfinite(prediction).all()
    assert np.all(prediction[:, :, 1] == 0)

