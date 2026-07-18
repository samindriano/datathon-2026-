import numpy as np

from orthogonal_state_model import fit_orthogonal_basis, fit_orthogonal_state_ridge


def test_basis_is_cross_sectionally_orthogonal_on_active_roads():
    rng = np.random.default_rng(7)
    block = rng.normal(40.0, 3.0, size=(100, 6)).astype(np.float32)
    block[:, -1] = 0.0
    _, _, active, basis, _ = fit_orthogonal_basis(block, 80, rank=2, sample_count=40)
    assert not active[-1]
    np.testing.assert_allclose(basis[:, active].sum(axis=1), 0.0, atol=1e-6)


def test_model_is_finite_and_preserves_zero_roads():
    time = np.arange(100, dtype=np.float32)
    block = np.stack(
        (30.0 + np.sin(time / 4), 50.0 + np.cos(time / 7), np.zeros_like(time)),
        axis=1,
    )
    model = fit_orthogonal_state_ridge(
        block, 14, 70, rank=2, pca_sample_count=40, chunk_size=16
    )
    prediction = model.predict(block[56:71][None])
    assert prediction.shape == (1, 3, 3)
    assert np.isfinite(prediction).all()
    assert np.all(prediction[:, :, 2] == 0)

