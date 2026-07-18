import numpy as np

from text_residual_model import TextResidualModel
from text_zguard_model import TextZGuardModel, z_guarded_features


class DummyBase:
    def predict(self, history):
        return np.ones((len(history), 3, history.shape[2]), dtype=np.float32)


def test_z_guard_only_neutralizes_selected_outlier():
    raw = np.asarray([[0.0, 10.0], [4.0, 1.0]])
    guarded, mask = z_guarded_features(
        raw,
        feature_mean=np.asarray([0.0, 1.0]),
        feature_scale=np.asarray([1.0, 1.0]),
        guard_index=0,
        z_threshold=3.0,
    )
    np.testing.assert_array_equal(mask, [False, True])
    np.testing.assert_allclose(guarded, [[0.0, 9.0], [0.0, 0.0]])


def test_prediction_keeps_zero_guard_and_finite_floor():
    base = TextResidualModel(
        base_model=DummyBase(),
        feature_mean=np.zeros(7),
        feature_scale=np.ones(7),
        residual_mean=np.zeros((2, 3)),
        coefficients=np.zeros((2, 7, 3)),
        alpha=1.0,
    )
    model = TextZGuardModel(base=base, guard_index=5, z_threshold=3.0)
    history = np.ones((2, 15, 2), dtype=np.float32)
    history[0, :, 0] = 0.0
    prediction = model.predict(history, ["", "prohibit left turn. " * 5])
    assert np.isfinite(prediction).all()
    assert (prediction >= 0).all()
    assert np.all(prediction[0, :, 0] == 0.0)
    assert model.guard_mask(["", "prohibit left turn. " * 5]).tolist() == [False, True]
