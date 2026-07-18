from run_tristate_experiment import acceptance_gate


def _summary(mean, folds, horizons, std):
    return {"mean_mse": mean, "fold_mse": folds,
            "mse_by_horizon": {"5": horizons[0], "10": horizons[1], "15": horizons[2]},
            "worst_fold_mse": max(folds), "std_mse": std}


def _passing_inputs():
    candidates = {
        "stableblend": _summary(40.0, [45.0, 40.0, 35.0], [35.0, 40.0, 45.0], 4.1),
        "tristate": _summary(39.0, [44.0, 39.0, 34.0], [34.0, 39.0, 44.0], 4.0),
    }
    stress = {"block_fold_horizon_cells_improved": 18, "temporal_chunks_improved": 36,
              "temporal_chunk_gain_median": 0.6, "temporal_chunk_gain_min": -0.05}
    diagnostics = {"tristate_m2_mean_correction_vs_ridge": -0.1,
                   "tristate_vs_e013_rms": 0.4,
                   "prediction_values_valid": True, "all_zero_history_guard_valid": True}
    return candidates, stress, diagnostics


def test_gate_passes_only_complete_frozen_evidence():
    candidates, stress, diagnostics = _passing_inputs()
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "KEEP"


def test_gate_rejects_cell_chunk_and_worst_chunk_failures():
    candidates, stress, diagnostics = _passing_inputs()
    stress["block_fold_horizon_cells_improved"] = 17
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"
    stress["block_fold_horizon_cells_improved"] = 18
    stress["temporal_chunks_improved"] = 34
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"
    stress["temporal_chunks_improved"] = 35
    stress["temporal_chunk_gain_min"] = -0.11
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"

