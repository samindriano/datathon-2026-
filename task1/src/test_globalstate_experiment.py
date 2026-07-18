from run_globalstate_experiment import acceptance_gate


def _summary(mean, folds, horizons, worst=None):
    return {
        "mean_mse": mean,
        "fold_mse": folds,
        "mse_by_horizon": {"h5": horizons[0], "h10": horizons[1], "h15": horizons[2]},
        "worst_fold_mse": max(folds) if worst is None else worst,
    }


def test_acceptance_gate_requires_material_broad_gain_and_safe_m2_direction():
    candidates = {
        "graphres": _summary(38.2, [43.7, 40.0, 30.9], [32.4, 38.8, 43.3]),
        "globalstate": _summary(37.8, [43.2, 39.7, 30.5], [32.0, 38.4, 42.9]),
        "textzguard": _summary(38.3, [44.0, 40.6, 30.3], [32.4, 38.9, 43.5]),
        "graphtextblend": _summary(37.9, [43.4, 40.0, 30.3], [32.1, 38.5, 43.1]),
        "globaltextblend": _summary(37.6, [43.0, 39.8, 30.0], [31.9, 38.2, 42.7]),
    }
    diagnostics = {"blend_m2_mean_correction_vs_ridge": -0.1}

    result = acceptance_gate(candidates, diagnostics)

    assert result["status"] == "KEEP"
    assert result["folds_improved_vs_e010"] == 3
    assert result["horizons_improved_vs_e010"] == 3


def test_acceptance_gate_rejects_sub_half_percent_gain():
    candidates = {
        "graphres": _summary(38.2, [43.7, 40.0, 30.9], [32.4, 38.8, 43.3]),
        "globalstate": _summary(37.8, [43.2, 39.7, 30.5], [32.0, 38.4, 42.9]),
        "textzguard": _summary(38.3, [44.0, 40.6, 30.3], [32.4, 38.9, 43.5]),
        "graphtextblend": _summary(37.9, [43.4, 40.0, 30.3], [32.1, 38.5, 43.1]),
        "globaltextblend": _summary(37.75, [43.2, 39.9, 30.1], [32.0, 38.4, 42.9]),
    }
    diagnostics = {"blend_m2_mean_correction_vs_ridge": -0.1}

    result = acceptance_gate(candidates, diagnostics)

    assert result["status"] == "REJECT"
    assert not result["checks"]["blend_mean_improves_e010_by_at_least_0_5_percent"]
