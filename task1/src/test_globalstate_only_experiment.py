from run_globalstate_only_experiment import acceptance_gate


def _summary(mean, folds, horizons, std):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"h5": horizons[0], "h10": horizons[1], "h15": horizons[2]},
        "worst_fold_mse": max(folds),
        "std_mse": std,
    }


def _passing_inputs():
    candidates = {
        "graphtextblend": _summary(
            37.9, [43.4, 40.0, 30.3], [32.1, 38.5, 43.1], 5.6
        ),
        "globalstate": _summary(
            35.4, [40.1, 36.5, 29.6], [30.8, 35.8, 39.6], 4.3
        ),
    }
    stress = {
        "block_fold_horizon_cells_improved": 18,
        "temporal_chunks_improved": 36,
        "temporal_chunk_gain_median": 2.0,
        "temporal_chunk_gain_min": 0.1,
    }
    diagnostics = {
        "global_m2_mean_correction_vs_ridge": -0.4,
        "prediction_values_valid": True,
        "all_zero_history_guard_valid": True,
    }
    return candidates, stress, diagnostics


def test_acceptance_gate_keeps_only_broad_safe_stress_result():
    result = acceptance_gate(*_passing_inputs())
    assert result["status"] == "KEEP"
    assert all(result["checks"].values())


def test_acceptance_gate_rejects_one_bad_unseen_chunk_gate():
    candidates, stress, diagnostics = _passing_inputs()
    stress["temporal_chunks_improved"] = 33
    result = acceptance_gate(candidates, stress, diagnostics)
    assert result["status"] == "REJECT"
    assert not result["checks"]["at_least_34_of_36_temporal_chunks_improve"]
