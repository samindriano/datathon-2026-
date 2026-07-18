from run_diststate_experiment import acceptance_gate


def _summary(mean, folds, horizons, std):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"h5": horizons[0], "h10": horizons[1], "h15": horizons[2]},
        "worst_fold_mse": max(folds),
        "std_mse": std,
    }


def test_diststate_gate_requires_material_broad_conservative_gain():
    candidates = {
        "stableblend": _summary(36.56, [41.75, 38.41, 29.52], [31.29, 37.06, 41.33], 5.16),
        "distblend": _summary(36.0, [41.1, 37.9, 29.0], [30.9, 36.5, 40.6], 5.0),
    }
    stress = {
        "block_fold_horizon_cells_improved": 18,
        "temporal_chunks_improved": 35,
        "temporal_chunk_gain_median": 0.4,
        "temporal_chunk_gain_min": -0.1,
    }
    diagnostics = {
        "distblend_m2_mean_correction_vs_ridge": -0.2,
        "distblend_vs_e013_rms": 0.5,
        "prediction_values_valid": True,
        "all_zero_history_guard_valid": True,
    }
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "KEEP"
    stress["temporal_chunks_improved"] = 33
    assert acceptance_gate(candidates, stress, diagnostics)["status"] == "REJECT"
