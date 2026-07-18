import numpy as np
import pytest

from run_stableblend_experiment import acceptance_gate
from stable_blend import stable_blend_predictions


def _summary(mean, folds, horizons, std):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"h5": horizons[0], "h10": horizons[1], "h15": horizons[2]},
        "worst_fold_mse": max(folds),
        "std_mse": std,
    }


def test_stable_blend_uses_fixed_75_25_weights():
    anchor = np.asarray([0.0, 4.0, 8.0], dtype=np.float32)
    globalstate = np.asarray([0.0, 8.0, 0.0], dtype=np.float32)
    result = stable_blend_predictions(anchor, globalstate)
    np.testing.assert_allclose(result, [0.0, 5.0, 6.0])


def test_stable_blend_rejects_invalid_components():
    with pytest.raises(ValueError, match="shapes must match"):
        stable_blend_predictions(np.zeros(2), np.zeros(3))
    with pytest.raises(ValueError, match="must be finite"):
        stable_blend_predictions(np.asarray([np.nan]), np.asarray([0.0]))


def test_acceptance_gate_requires_broad_temporal_gain():
    candidates = {
        "graphtextblend": _summary(
            37.9, [43.4, 40.0, 30.3], [32.1, 38.5, 43.1], 5.6
        ),
        "stableblend": _summary(
            37.2, [42.7, 39.3, 29.8], [31.7, 37.8, 42.2], 5.3
        ),
    }
    stress = {
        "block_fold_horizon_cells_improved": 18,
        "temporal_chunks_improved": 35,
        "temporal_chunk_gain_median": 0.7,
        "temporal_chunk_gain_min": -0.1,
    }
    diagnostics = {
        "stableblend_m2_mean_correction_vs_ridge": -0.2,
        "prediction_values_valid": True,
        "all_zero_history_guard_valid": True,
    }
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "KEEP"

    stress["temporal_chunk_gain_min"] = -0.3
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"
