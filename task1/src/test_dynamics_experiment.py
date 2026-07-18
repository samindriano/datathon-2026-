import numpy as np

from run_dynamics_experiment import acceptance_gate, dynamics_blend


def _summary(mean, folds, horizons, std):
    return {"mean_mse": mean, "fold_mse": folds,
            "mse_by_horizon": {"5": horizons[0], "10": horizons[1], "15": horizons[2]},
            "worst_fold_mse": max(folds), "std_mse": std}


def test_fixed_blend_and_gate():
    np.testing.assert_allclose(
        dynamics_blend(np.asarray([0.0, 8.0]), np.asarray([0.0, 4.0])), [0.0, 7.0]
    )
    candidates = {
        "stableblend": _summary(40.0, [45.0, 40.0, 35.0], [35.0, 40.0, 45.0], 4.1),
        "dynamicsblend": _summary(39.0, [44.0, 39.0, 34.0], [34.0, 39.0, 44.0], 4.0),
    }
    stress = {"block_fold_horizon_cells_improved": 18, "temporal_chunks_improved": 36,
              "temporal_chunk_gain_median": 0.5, "temporal_chunk_gain_min": 0.0}
    diagnostics = {"prediction_values_valid": True, "all_zero_history_guard_valid": True}
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "KEEP"
    stress["temporal_chunks_improved"] = 30
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"

