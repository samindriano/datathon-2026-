import numpy as np

from lowrank_novelty_guard import apply_lowrank_novelty_guard


def test_guard_reverts_untrusted_origins_to_reference():
    reference = np.zeros((3, 3, 2), dtype=np.float32)
    lowrank = np.ones_like(reference)
    result = apply_lowrank_novelty_guard(
        reference, lowrank, np.array([True, False, True])
    )
    assert np.all(result[0] == 1)
    assert np.all(result[1] == 0)
    assert np.all(result[2] == 1)


def test_guard_rejects_shape_mismatch():
    prediction = np.zeros((2, 3, 4), dtype=np.float32)
    try:
        apply_lowrank_novelty_guard(prediction, prediction, np.array([True]))
    except ValueError as error:
        assert "shape" in str(error)
    else:
        raise AssertionError("shape mismatch must fail")
