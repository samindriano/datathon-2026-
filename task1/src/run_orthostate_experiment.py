"""Run the preregistered orthogonal global-plus-spatial state experiment."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import write_submission
from global_state_model import fit_global_state_ridge
from graph_model import fit_graph_ridge
from graphtext_blend import blend_predictions
from multifold import HORIZONS, REGIME_WEIGHTS, build_folds, mse_by_horizon, summarize_fold_scores, windows_at_origins
from orthogonal_state_model import DEFAULT_PCA_SAMPLES, DEFAULT_RANK, FEATURE_NAMES, fit_orthogonal_state_ridge
from ridge_model import classify_test_regime
from run_globalstate_only_experiment import TEMPORAL_CHUNK_SIZE
from run_textres_experiment import load_train_text_blocks
from stable_blend import ANCHOR_WEIGHT, GLOBALSTATE_WEIGHT, stable_blend_predictions
from text_residual_model import load_aligned_texts
from text_zguard_model import DEFAULT_Z_THRESHOLD, fit_text_zguard


EXPERIMENT_ID = "d1-e019-orthostate"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=3)
    parser.add_argument("--validation-size", type=int, default=720)
    parser.add_argument("--min-train-origins", type=int, default=1440)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--rank", type=int, default=DEFAULT_RANK)
    parser.add_argument("--pca-samples", type=int, default=DEFAULT_PCA_SAMPLES)
    parser.add_argument("--text-residual-alpha", type=float, default=1.0)
    parser.add_argument("--text-z-threshold", type=float, default=DEFAULT_Z_THRESHOLD)
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def acceptance_gate(candidates, stress, diagnostics):
    reference = candidates["stableblend"]
    candidate = candidates["orthoblend"]
    rf = np.asarray(reference["fold_mse"])
    cf = np.asarray(candidate["fold_mse"])
    rh = np.asarray(list(reference["mse_by_horizon"].values()))
    ch = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "mean_improves_e013_by_at_least_1_percent": candidate["mean_mse"] <= 0.99 * reference["mean_mse"],
        "all_three_folds_improve": int((cf < rf).sum()) == 3,
        "all_three_horizons_improve": int((ch < rh).sum()) == 3,
        "worst_fold_improves": candidate["worst_fold_mse"] < reference["worst_fold_mse"],
        "fold_standard_deviation_not_worse": candidate["std_mse"] <= reference["std_mse"],
        "all_18_cells_improve": stress["block_fold_horizon_cells_improved"] == 18,
        "all_36_chunks_improve": stress["temporal_chunks_improved"] == 36,
        "median_chunk_gain_at_least_0_25": stress["temporal_chunk_gain_median"] >= 0.25,
        "worst_chunk_is_positive": stress["temporal_chunk_gain_min"] > 0.0,
        "test_m2_correction_is_nonpositive": diagnostics["orthoblend_m2_mean_correction_vs_ridge"] <= 0.0,
        "test_change_vs_e013_is_conservative": diagnostics["orthoblend_vs_e013_rms"] <= 1.0,
        "predictions_are_valid_and_zero_guarded": diagnostics["prediction_values_valid"] and diagnostics["all_zero_history_guard_valid"],
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def fit_components(block, texts, adjacency, start, end, args):
    graph = fit_graph_ridge(block, adjacency, start, end, alpha=args.alpha, chunk_size=args.chunk_size)
    globalstate = fit_global_state_ridge(block, start, end, alpha=args.alpha, chunk_size=args.chunk_size)
    orthostate = fit_orthogonal_state_ridge(
        block, start, end, alpha=args.alpha, rank=args.rank,
        pca_sample_count=args.pca_samples, chunk_size=args.chunk_size,
    )
    text = fit_text_zguard(
        block, texts, start, end, base_alpha=args.alpha,
        residual_alpha=args.text_residual_alpha, z_threshold=args.text_z_threshold,
        chunk_size=args.chunk_size,
    )
    return graph, globalstate, orthostate, text


def predict_components(models, history, texts):
    graph, globalstate, orthostate, text = models
    e010 = blend_predictions(graph.predict(history), text.predict(history, texts))
    orthostate_prediction = orthostate.predict(history)
    return (
        stable_blend_predictions(e010, globalstate.predict(history)),
        orthostate_prediction,
        stable_blend_predictions(e010, orthostate_prediction),
    )


def evaluate(blocks, text_blocks, adjacency, fold_sets, args):
    methods = ("stableblend", "orthostate", "orthoblend")
    scores = {name: [] for name in methods}
    chunk_gains = []
    origin_win_rates = []
    pca_ranges = []
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores = {name: [] for name in methods}
        block_ranges = []
        for fold in folds:
            origins = np.arange(fold.validation_origin_start, fold.validation_origin_end + 1)
            history, target = windows_at_origins(block, origins)
            models = fit_components(block, texts, adjacency, fold.train_origin_start, fold.train_origin_end, args)
            e013, orthostate, candidate = predict_components(
                models, history, [texts[index] for index in origins]
            )
            predictions = {"stableblend": e013, "orthostate": orthostate, "orthoblend": candidate}
            block_ranges.append([int(models[2].pca_rows.min()), int(models[2].pca_rows.max())])
            for name in methods:
                block_scores[name].append(mse_by_horizon(target, predictions[name]))
            target64 = target.astype(np.float64)
            reference_error = np.mean(np.square(target64 - e013.astype(np.float64)), axis=(1, 2))
            candidate_error = np.mean(np.square(target64 - candidate.astype(np.float64)), axis=(1, 2))
            origin_win_rates.append(float(np.mean(candidate_error < reference_error)))
            for start in range(0, len(origins), TEMPORAL_CHUNK_SIZE):
                stop = min(start + TEMPORAL_CHUNK_SIZE, len(origins))
                chunk_gains.append(float(reference_error[start:stop].mean() - candidate_error[start:stop].mean()))
        pca_ranges.append(block_ranges)
        for name in methods:
            scores[name].append(np.asarray(block_scores[name]))
    candidates = {name: summarize_fold_scores(scores[name]) for name in methods}
    reference_cells = np.asarray(candidates["stableblend"]["block_fold_horizon_mse"])
    candidate_cells = np.asarray(candidates["orthoblend"]["block_fold_horizon_mse"])
    chunks = np.asarray(chunk_gains)
    stress = {
        "block_fold_horizon_cells_improved": int((candidate_cells < reference_cells).sum()),
        "block_fold_horizon_cell_count": int(candidate_cells.size),
        "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
        "temporal_chunks_improved": int((chunks > 0).sum()),
        "temporal_chunk_count": int(len(chunks)),
        "temporal_chunk_gain_min": float(chunks.min()),
        "temporal_chunk_gain_median": float(np.median(chunks)),
        "temporal_chunk_gain_max": float(chunks.max()),
        "temporal_chunk_gains": chunks.tolist(),
        "per_block_fold_origin_win_rates": origin_win_rates,
        "pca_row_ranges": pca_ranges,
    }
    return candidates, stress


def main():
    args = parse_args()
    started = time.perf_counter()
    data_root = args.data_root.resolve()
    experiment_dir = args.experiment_dir.resolve()
    if experiment_dir.name != EXPERIMENT_ID:
        raise ValueError(f"Experiment directory must be named {EXPERIMENT_ID}")
    experiment_dir.mkdir(parents=True, exist_ok=True)
    train_paths = sorted((data_root / "train").glob("train_speed_*.npy"))
    if len(train_paths) != 2:
        raise ValueError(f"Expected two train blocks, found {len(train_paths)}")
    blocks = [np.load(path, mmap_mode="r") for path in train_paths]
    text_blocks = load_train_text_blocks(data_root, blocks)
    adjacency = np.load(data_root / "static" / "matrix.npy")
    fold_sets = [
        build_folds(len(block), index, args.fold_count, args.validation_size, args.min_train_origins)
        for index, block in enumerate(blocks, start=1)
    ]
    candidates, stress = evaluate(blocks, text_blocks, adjacency, fold_sets, args)

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = np.asarray(load_aligned_texts(data_root / "test" / "test_texts.json", test_keys), dtype=object)
    regimes = classify_test_regime(test_history)
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    ridge_prediction = np.empty(shape, dtype=np.float32)
    e013_prediction = np.empty(shape, dtype=np.float32)
    orthostate_prediction = np.empty(shape, dtype=np.float32)
    candidate_prediction = np.empty(shape, dtype=np.float32)
    for regime, (block, texts) in enumerate(zip(blocks, text_blocks, strict=True)):
        end = len(block) - int(HORIZONS.max()) - 1
        models = fit_components(block, texts, adjacency, 14, end, args)
        mask = regimes == regime
        history = test_history[mask]
        subset_texts = test_texts[mask].tolist()
        e013, orthostate, candidate = predict_components(models, history, subset_texts)
        ridge_prediction[mask] = models[3].base.base_model.predict(history)
        e013_prediction[mask] = e013
        orthostate_prediction[mask] = orthostate
        candidate_prediction[mask] = candidate
    zero_history = np.all(test_history == 0, axis=1)
    zero_values = candidate_prediction[np.broadcast_to(zero_history[:, None, :], candidate_prediction.shape)]
    delta = candidate_prediction.astype(np.float64) - e013_prediction.astype(np.float64)
    m2 = regimes == 1
    diagnostics = {
        "orthoblend_m2_mean_correction_vs_ridge": float((candidate_prediction[m2] - ridge_prediction[m2]).mean()),
        "orthoblend_vs_e013_rms": float(np.sqrt(np.mean(np.square(delta)))),
        "orthoblend_vs_e013_mean": float(delta.mean()),
        "orthoblend_vs_e013_min": float(delta.min()),
        "orthoblend_vs_e013_max": float(delta.max()),
        "prediction_values_valid": bool(np.isfinite(candidate_prediction).all() and (candidate_prediction >= 0).all()),
        "all_zero_history_guard_valid": bool(np.all(zero_values == 0)),
        "all_zero_history_pairs": int(zero_history.sum()),
    }
    gate = acceptance_gate(candidates, stress, diagnostics)
    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(data_root / "sample_submission.csv", candidate_prediction, submission_path)
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "metric": "mse",
        "validation": {
            "version": "d1-multifold-v1", "fold_count_per_block": args.fold_count,
            "validation_origins_per_fold": args.validation_size,
            "minimum_training_origins": args.min_train_origins,
            "purge_origins": int(HORIZONS.max()),
            "regime_weights": {"m1": float(REGIME_WEIGHTS[0]), "m2": float(REGIME_WEIGHTS[1])},
            "folds": [[fold.to_dict() for fold in folds] for folds in fold_sets],
        },
        "hypothesis": "Explicit global summaries plus PCA of cross-sectionally residualized road state separate city level from spatial modes and stabilize E016.",
        "preregistered_parameters": {
            "features": list(FEATURE_NAMES), "anchor_weight": ANCHOR_WEIGHT,
            "orthostate_weight": GLOBALSTATE_WEIGHT, "rank": args.rank,
            "pca_sample_count": args.pca_samples,
            "city_level_residualization": "cross-sectional mean after per-road standardization",
            "alpha": args.alpha, "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
            "weight_search": False, "rank_search": False, "seed": None,
        },
        "candidates": candidates, "stress": stress,
        "test_diagnostics": diagnostics, "acceptance_gate": gate,
        "test_regime_counts": {"m1": int((regimes == 0).sum()), "m2": int((regimes == 1).sum())},
        "prediction": {
            "shape": list(candidate_prediction.shape), "min": float(candidate_prediction.min()),
            "max": float(candidate_prediction.max()), "mean": float(candidate_prediction.mean()),
            "submission_rows": int(candidate_prediction.size),
        },
        "submission": str(submission_path) if submission_path else None,
        "runtime_seconds": float(time.perf_counter() - started),
    }
    (experiment_dir / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "reference_mse": candidates["stableblend"]["mean_mse"],
        "orthostate_mse": candidates["orthostate"]["mean_mse"],
        "candidate_mse": candidates["orthoblend"]["mean_mse"],
        "stress": stress, "gate": gate, "diagnostics": diagnostics,
        "submission": str(submission_path) if submission_path else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
