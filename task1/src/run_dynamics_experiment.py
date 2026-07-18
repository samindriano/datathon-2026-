"""Run the preregistered E013 plus asymmetric local-dynamics experiment."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import write_submission
from dynamics_model import FEATURE_NAMES, fit_dynamics_ridge
from global_state_model import fit_global_state_ridge
from graph_model import fit_graph_ridge
from graphtext_blend import blend_predictions
from multifold import HORIZONS, REGIME_WEIGHTS, build_folds, mse_by_horizon, summarize_fold_scores, windows_at_origins
from ridge_model import classify_test_regime
from run_globalstate_only_experiment import TEMPORAL_CHUNK_SIZE
from run_textres_experiment import load_train_text_blocks
from stable_blend import stable_blend_predictions
from text_residual_model import load_aligned_texts
from text_zguard_model import DEFAULT_Z_THRESHOLD, fit_text_zguard


EXPERIMENT_ID = "d1-e017-dynamics"
ANCHOR_WEIGHT = 0.75
DYNAMICS_WEIGHT = 0.25


def dynamics_blend(anchor: np.ndarray, dynamics: np.ndarray) -> np.ndarray:
    if anchor.shape != dynamics.shape:
        raise ValueError("prediction shapes differ")
    if not np.isfinite(anchor).all() or not np.isfinite(dynamics).all():
        raise ValueError("predictions must be finite")
    result = ANCHOR_WEIGHT * anchor + DYNAMICS_WEIGHT * dynamics
    return np.where((anchor == 0) & (dynamics == 0), 0.0, np.maximum(result, 0.0)).astype(np.float32)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=3)
    parser.add_argument("--validation-size", type=int, default=720)
    parser.add_argument("--min-train-origins", type=int, default=1440)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--text-residual-alpha", type=float, default=1.0)
    parser.add_argument("--text-z-threshold", type=float, default=DEFAULT_Z_THRESHOLD)
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def acceptance_gate(candidates, stress, diagnostics):
    anchor = candidates["stableblend"]
    candidate = candidates["dynamicsblend"]
    af = np.asarray(anchor["fold_mse"])
    cf = np.asarray(candidate["fold_mse"])
    ah = np.asarray(list(anchor["mse_by_horizon"].values()))
    ch = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "mean_improves_e013_by_at_least_1_percent": candidate["mean_mse"] <= 0.99 * anchor["mean_mse"],
        "all_three_folds_improve": int((cf < af).sum()) == 3,
        "all_three_horizons_improve": int((ch < ah).sum()) == 3,
        "worst_fold_improves": candidate["worst_fold_mse"] < anchor["worst_fold_mse"],
        "fold_standard_deviation_not_worse": candidate["std_mse"] <= anchor["std_mse"],
        "at_least_17_of_18_cells_improve": stress["block_fold_horizon_cells_improved"] >= 17,
        "at_least_34_of_36_chunks_improve": stress["temporal_chunks_improved"] >= 34,
        "median_chunk_gain_at_least_0_30": stress["temporal_chunk_gain_median"] >= 0.30,
        "worst_chunk_not_below_minus_0_25": stress["temporal_chunk_gain_min"] >= -0.25,
        "predictions_are_finite_nonnegative_and_zero_guarded": diagnostics["prediction_values_valid"] and diagnostics["all_zero_history_guard_valid"],
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def fit_e013(block, texts, adjacency, start, end, args):
    return (
        fit_graph_ridge(block, adjacency, start, end, alpha=args.alpha, chunk_size=args.chunk_size),
        fit_global_state_ridge(block, start, end, alpha=args.alpha, chunk_size=args.chunk_size),
        fit_text_zguard(
            block, texts, start, end, base_alpha=args.alpha,
            residual_alpha=args.text_residual_alpha, z_threshold=args.text_z_threshold,
            chunk_size=args.chunk_size,
        ),
    )


def predict_e013(models, history, texts):
    graph, globalstate, text = models
    e010 = blend_predictions(graph.predict(history), text.predict(history, texts))
    return stable_blend_predictions(e010, globalstate.predict(history))


def evaluate(blocks, text_blocks, adjacency, fold_sets, args):
    methods = ("stableblend", "dynamics", "dynamicsblend")
    scores = {name: [] for name in methods}
    chunk_gains = []
    origin_win_rates = []
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores = {name: [] for name in methods}
        for fold in folds:
            origins = np.arange(fold.validation_origin_start, fold.validation_origin_end + 1)
            history, target = windows_at_origins(block, origins)
            e013_models = fit_e013(block, texts, adjacency, fold.train_origin_start, fold.train_origin_end, args)
            dynamics_model = fit_dynamics_ridge(
                block, fold.train_origin_start, fold.train_origin_end,
                alpha=args.alpha, chunk_size=args.chunk_size,
            )
            e013_prediction = predict_e013(e013_models, history, [texts[index] for index in origins])
            dynamics_prediction = dynamics_model.predict(history)
            candidate_prediction = dynamics_blend(e013_prediction, dynamics_prediction)
            predictions = {
                "stableblend": e013_prediction,
                "dynamics": dynamics_prediction,
                "dynamicsblend": candidate_prediction,
            }
            for name in methods:
                block_scores[name].append(mse_by_horizon(target, predictions[name]))
            target64 = target.astype(np.float64)
            anchor_error = np.mean(np.square(target64 - e013_prediction.astype(np.float64)), axis=(1, 2))
            candidate_error = np.mean(np.square(target64 - candidate_prediction.astype(np.float64)), axis=(1, 2))
            origin_win_rates.append(float(np.mean(candidate_error < anchor_error)))
            for start in range(0, len(origins), TEMPORAL_CHUNK_SIZE):
                stop = min(start + TEMPORAL_CHUNK_SIZE, len(origins))
                chunk_gains.append(float(anchor_error[start:stop].mean() - candidate_error[start:stop].mean()))
        for name in methods:
            scores[name].append(np.asarray(block_scores[name]))
    candidates = {name: summarize_fold_scores(scores[name]) for name in methods}
    anchor_cells = np.asarray(candidates["stableblend"]["block_fold_horizon_mse"])
    candidate_cells = np.asarray(candidates["dynamicsblend"]["block_fold_horizon_mse"])
    chunks = np.asarray(chunk_gains)
    stress = {
        "block_fold_horizon_cells_improved": int((candidate_cells < anchor_cells).sum()),
        "block_fold_horizon_cell_count": int(candidate_cells.size),
        "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
        "temporal_chunks_improved": int((chunks > 0).sum()),
        "temporal_chunk_count": int(len(chunks)),
        "temporal_chunk_gain_min": float(chunks.min()),
        "temporal_chunk_gain_median": float(np.median(chunks)),
        "temporal_chunk_gain_max": float(chunks.max()),
        "temporal_chunk_gains": chunks.tolist(),
        "per_block_fold_origin_win_rates": origin_win_rates,
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
    texts = load_train_text_blocks(data_root, blocks)
    adjacency = np.load(data_root / "static" / "matrix.npy")
    fold_sets = [
        build_folds(len(block), index, args.fold_count, args.validation_size, args.min_train_origins)
        for index, block in enumerate(blocks, start=1)
    ]
    candidates, stress = evaluate(blocks, texts, adjacency, fold_sets, args)

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = np.asarray(load_aligned_texts(data_root / "test" / "test_texts.json", test_keys), dtype=object)
    regimes = classify_test_regime(test_history)
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    anchor_prediction = np.empty(shape, dtype=np.float32)
    dynamics_prediction = np.empty(shape, dtype=np.float32)
    for regime, (block, block_texts) in enumerate(zip(blocks, texts, strict=True)):
        end = len(block) - int(HORIZONS.max()) - 1
        e013_models = fit_e013(block, block_texts, adjacency, 14, end, args)
        dynamics_model = fit_dynamics_ridge(block, 14, end, alpha=args.alpha, chunk_size=args.chunk_size)
        mask = regimes == regime
        history = test_history[mask]
        anchor_prediction[mask] = predict_e013(e013_models, history, test_texts[mask].tolist())
        dynamics_prediction[mask] = dynamics_model.predict(history)
    candidate_prediction = dynamics_blend(anchor_prediction, dynamics_prediction)
    zero_history = np.all(test_history == 0, axis=1)
    zero_values = candidate_prediction[np.broadcast_to(zero_history[:, None, :], candidate_prediction.shape)]
    delta = candidate_prediction.astype(np.float64) - anchor_prediction.astype(np.float64)
    diagnostics = {
        "prediction_values_valid": bool(np.isfinite(candidate_prediction).all() and (candidate_prediction >= 0).all()),
        "all_zero_history_guard_valid": bool(np.all(zero_values == 0)),
        "all_zero_history_pairs": int(zero_history.sum()),
        "candidate_vs_e013_delta_mean": float(delta.mean()),
        "candidate_vs_e013_delta_rms": float(np.sqrt(np.mean(np.square(delta)))),
        "candidate_vs_e013_delta_abs_gt_5_fraction": float(np.mean(np.abs(delta) > 5.0)),
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
            "version": "d1-multifold-v1",
            "fold_count_per_block": args.fold_count,
            "validation_origins_per_fold": args.validation_size,
            "minimum_training_origins": args.min_train_origins,
            "purge_origins": int(HORIZONS.max()),
            "regime_weights": {"m1": float(REGIME_WEIGHTS[0]), "m2": float(REGIME_WEIGHTS[1])},
            "folds": [[fold.to_dict() for fold in folds] for folds in fold_sets],
        },
        "hypothesis": "Asymmetric causal road dynamics add local nonlinear recovery and congestion signals missing from E013.",
        "preregistered_parameters": {
            "feature_names": list(FEATURE_NAMES), "alpha": args.alpha,
            "anchor_weight": ANCHOR_WEIGHT, "dynamics_weight": DYNAMICS_WEIGHT,
            "weight_search": False, "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
            "text_residual_alpha": args.text_residual_alpha,
            "text_z_threshold": args.text_z_threshold, "seed": None,
        },
        "candidates": candidates,
        "stress": stress,
        "test_diagnostics": diagnostics,
        "acceptance_gate": gate,
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
        "anchor_mse": candidates["stableblend"]["mean_mse"],
        "dynamics_mse": candidates["dynamics"]["mean_mse"],
        "candidate_mse": candidates["dynamicsblend"]["mean_mse"],
        "stress": stress, "gate": gate, "diagnostics": diagnostics,
        "submission": str(submission_path) if submission_path else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

