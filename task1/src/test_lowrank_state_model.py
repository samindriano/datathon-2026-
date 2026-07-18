import numpy as np

from lowrank_state_model import (
    fit_lowrank_basis,
    fit_lowrank_state_ridge,
    lowrank_history_features,
)


def test_basis_is_training_only_deterministic_and_features_have_expected_shape():
    rng = np.random.default_rng(7)
    block = rng.normal(40, 5, size=(100, 8)).astype(np.float32)
    mean1, scale1, basis1, rows1 = fit_lowrank_basis(block, 60, rank=2, sample_count=20)
    mean2, scale2, basis2, rows2 = fit_lowrank_basis(block, 60, rank=2, sample_count=20)
    np.testing.assert_allclose(mean1, mean2)
    np.testing.assert_allclose(scale1, scale2)
    np.testing.assert_allclose(np.abs(basis1), np.abs(basis2))
    np.testing.assert_array_equal(rows1, rows2)
    assert rows1.max() <= 60
    features = lowrank_history_features(block[None, 20:35], mean1, scale1, basis1)
    assert features.shape == (1, 8, 15)


def test_lowrank_model_is_finite_and_zero_guarded():
    rng = np.random.default_rng(11)
    block = rng.normal(45, 4, size=(90, 6)).astype(np.float32)
    block[:, 5] = 0.0
    model = fit_lowrank_state_ridge(
        block, 14, 60, rank=2, pca_sample_count=30, chunk_size=16
    )
    history = np.stack((block[41:56], block[42:57]))
    prediction = model.predict(history)
    assert prediction.shape == (2, 3, 6)
    assert np.isfinite(prediction).all()
    assert np.all(prediction[:, :, 5] == 0)
