import numpy as np

from seasonal_phase_model import fit_seasonal_phase


def test_phase_model_is_finite_and_preserves_zero_roads():
    period = 20
    time = np.arange(160, dtype=np.float32)
    block = np.stack(
        (40.0 + 5.0 * np.sin(2 * np.pi * time / period), np.zeros_like(time)),
        axis=1,
    )
    model = fit_seasonal_phase(block, 14, 120, period=period, road_groups=1)
    history = block[106:121][None, :, :]
    prediction = model.predict(history)
    assert prediction.shape == (1, 3, 2)
    assert np.isfinite(prediction).all()
    assert np.all(prediction[:, :, 1] == 0)


def test_phase_fit_fails_when_training_does_not_cover_period():
    block = np.ones((100, 2), dtype=np.float32)
    try:
        fit_seasonal_phase(block, 14, 70, period=80, road_groups=1)
    except ValueError as error:
        assert "does not cover all phases" in str(error)
    else:
        raise AssertionError("Expected missing-phase failure")

