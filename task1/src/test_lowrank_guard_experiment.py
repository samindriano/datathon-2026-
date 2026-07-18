from run_lowrank_guard_experiment import acceptance_gate


def _candidate(mean, folds, horizons, worst, std):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"5": horizons[0], "10": horizons[1], "15": horizons[2]},
        "worst_fold_mse": worst,
        "std_mse": std,
    }


def test_acceptance_gate_is_fail_closed():
    candidates = {
        "stableblend": _candidate(10.0, [10.0, 10.0, 10.0], [10, 10, 10], 10, 1),
        "lowrankguard": _candidate(9.0, [9.0, 9.0, 9.0], [9, 9, 9], 9, 0.9),
    }
    stress = {
        "block_fold_horizon_cells_improved": 18,
        "temporal_chunks_improved": 35,
        "temporal_chunk_gain_median": 0.6,
        "temporal_chunk_gain_min": -0.11,
    }
    diagnostics = {
        "lowrankguard_m2_mean_correction_vs_ridge": -0.1,
        "lowrankguard_vs_e013_rms": 0.5,
        "test_reversion_rate": 0.1,
        "prediction_values_valid": True,
        "all_zero_history_guard_valid": True,
    }
    result = acceptance_gate(candidates, stress, diagnostics)
    assert result["status"] == "REJECT"
    assert result["checks"]["worst_chunk_gain_not_below_minus_0_10"] is False
