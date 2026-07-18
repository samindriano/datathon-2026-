import numpy as np

from run_phase_experiment import acceptance_gate, phase_blend


def _summary(mean, folds, horizons, std):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"5": horizons[0], "10": horizons[1], "15": horizons[2]},
        "worst_fold_mse": max(folds),
        "std_mse": std,
    }


def test_phase_blend_uses_fixed_weights_and_preserves_joint_zero():
    anchor = np.asarray([0.0, 8.0], dtype=np.float32)
    seasonal = np.asarray([0.0, 4.0], dtype=np.float32)
    result = phase_blend(anchor, seasonal)
    np.testing.assert_allclose(result, [0.0, 7.0])


def test_gate_requires_broad_improvement():
    candidates = {
        "stableblend": _summary(40.0, [45.0, 40.0, 35.0], [35.0, 40.0, 45.0], 4.1),
        "phaseblend": _summary(39.0, [44.0, 39.0, 34.0], [34.0, 39.0, 44.0], 4.0),
    }
    stress = {
        "block_fold_horizon_cells_improved": 18,
        "temporal_chunks_improved": 36,
        "temporal_chunk_gain_median": 0.5,
        "temporal_chunk_gain_min": 0.0,
    }
    diagnostics = {"prediction_values_valid": True, "all_zero_history_guard_valid": True}
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "KEEP"
    stress["temporal_chunks_improved"] = 33
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"

