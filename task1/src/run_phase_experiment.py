"""Run the preregistered E013 plus daily seasonal-phase experiment."""

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
from multifold import (
    HORIZONS,
    REGIME_WEIGHTS,
    build_folds,
    mse_by_horizon,
    summarize_fold_scores,
    windows_at_origins,
)
from ridge_model import classify_test_regime
from run_globalstate_only_experiment import TEMPORAL_CHUNK_SIZE
from run_textres_experiment import load_train_text_blocks
from seasonal_phase_model import PERIOD, ROAD_GROUPS, fit_seasonal_phase
from stable_blend import stable_blend_predictions
from text_residual_model import load_aligned_texts
from text_zguard_model import DEFAULT_Z_THRESHOLD, fit_text_zguard


EXPERIMENT_ID = "d1-e015-phase"
ANCHOR_WEIGHT = 0.75
SEASONAL_WEIGHT = 0.25


def phase_blend(anchor: np.ndarray, seasonal: np.ndarray) -> np.ndarray:
    if anchor.shape != seasonal.shape:
        raise ValueError("anchor and seasonal predictions must have identical shapes")
    if not np.isfinite(anchor).all() or not np.isfinite(seasonal).all():
        raise ValueError("blend inputs must be finite")
    result = ANCHOR_WEIGHT * anchor + SEASONAL_WEIGHT * seasonal
    zero_pair = (anchor == 0) & (seasonal == 0)
    return np.where(zero_pair, 0.0, np.maximum(result, 0.0)).astype(np.float32)


def parse_args() -> argparse.Namespace:
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


def acceptance_gate(candidates: dict, stress: dict, diagnostics: dict) -> dict:
    anchor = candidates["stableblend"]
    candidate = candidates["phaseblend"]
    anchor_folds = np.asarray(anchor["fold_mse"], dtype=np.float64)
    candidate_folds = np.asarray(candidate["fold_mse"], dtype=np.float64)
    anchor_horizons = np.asarray(list(anchor["mse_by_horizon"].values()))
    candidate_horizons = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "mean_improves_e013_by_at_least_1_percent": float(candidate["mean_mse"])
        <= 0.99 * float(anchor["mean_mse"]),
        "all_three_folds_improve": int((candidate_folds < anchor_folds).sum()) == 3,
        "all_three_horizons_improve": int((candidate_horizons < anchor_horizons).sum()) == 3,
        "worst_fold_improves": float(candidate["worst_fold_mse"]) < float(anchor["worst_fold_mse"]),
        "fold_standard_deviation_not_worse": float(candidate["std_mse"]) <= float(anchor["std_mse"]),
        "at_least_17_of_18_cells_improve": int(stress["block_fold_horizon_cells_improved"]) >= 17,
        "at_least_34_of_36_chunks_improve": int(stress["temporal_chunks_improved"]) >= 34,
        "median_chunk_gain_at_least_0_30": float(stress["temporal_chunk_gain_median"]) >= 0.30,
        "worst_chunk_not_below_minus_0_25": float(stress["temporal_chunk_gain_min"]) >= -0.25,
        "predictions_are_finite_nonnegative_and_zero_guarded": bool(
            diagnostics["prediction_values_valid"] and diagnostics["all_zero_history_guard_valid"]
        ),
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def _fit_e013_components(block, texts, adjacency, start, end, args):
    graph = fit_graph_ridge(
        block, adjacency, start, end, alpha=args.alpha, chunk_size=args.chunk_size
    )
    globalstate = fit_global_state_ridge(
        block, start, end, alpha=args.alpha, chunk_size=args.chunk_size
    )
    text = fit_text_zguard(
        block,
        texts,
        start,
        end,
        base_alpha=args.alpha,
        residual_alpha=args.text_residual_alpha,
        z_threshold=args.text_z_threshold,
        chunk_size=args.chunk_size,
    )
    return graph, globalstate, text


def _predict_e013(components, histories, texts):
    graph, globalstate, text = components
    e010 = blend_predictions(graph.predict(histories), text.predict(histories, texts))
    return stable_blend_predictions(e010, globalstate.predict(histories))


def evaluate(blocks, text_blocks, adjacency, fold_sets, args):
    methods = ("stableblend", "seasonal", "phaseblend")
    scores = {method: [] for method in methods}
    chunk_gains = []
    origin_win_rates = []
    inferred_phase_counts = np.zeros(PERIOD, dtype=np.int64)

    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores = {method: [] for method in methods}
        for fold in folds:
            origins = np.arange(fold.validation_origin_start, fold.validation_origin_end + 1)
            histories, targets = windows_at_origins(block, origins)
            components = _fit_e013_components(
                block, texts, adjacency, fold.train_origin_start, fold.train_origin_end, args
            )
            phase_model = fit_seasonal_phase(
                block,
                fold.train_origin_start,
                fold.train_origin_end,
                period=PERIOD,
                road_groups=ROAD_GROUPS,
                chunk_size=args.chunk_size,
            )
            validation_texts = [texts[index] for index in origins]
            anchor_prediction = _predict_e013(components, histories, validation_texts)
            seasonal_prediction = phase_model.predict(histories)
            candidate_prediction = phase_blend(anchor_prediction, seasonal_prediction)
            predictions = {
                "stableblend": anchor_prediction,
                "seasonal": seasonal_prediction,
                "phaseblend": candidate_prediction,
            }
            for method in methods:
                block_scores[method].append(mse_by_horizon(targets, predictions[method]))

            inferred_phase_counts += np.bincount(
                phase_model.infer_phase(histories), minlength=PERIOD
            )
            target64 = targets.astype(np.float64)
            anchor_error = np.mean(
                np.square(target64 - anchor_prediction.astype(np.float64)), axis=(1, 2)
            )
            candidate_error = np.mean(
                np.square(target64 - candidate_prediction.astype(np.float64)), axis=(1, 2)
            )
            origin_win_rates.append(float(np.mean(candidate_error < anchor_error)))
            for start in range(0, len(origins), TEMPORAL_CHUNK_SIZE):
                stop = min(start + TEMPORAL_CHUNK_SIZE, len(origins))
                chunk_gains.append(
                    float(anchor_error[start:stop].mean() - candidate_error[start:stop].mean())
                )
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))

    candidates = {method: summarize_fold_scores(scores[method]) for method in methods}
    anchor_cells = np.asarray(candidates["stableblend"]["block_fold_horizon_mse"])
    candidate_cells = np.asarray(candidates["phaseblend"]["block_fold_horizon_mse"])
    chunk_array = np.asarray(chunk_gains, dtype=np.float64)
    stress = {
        "block_fold_horizon_cells_improved": int((candidate_cells < anchor_cells).sum()),
        "block_fold_horizon_cell_count": int(candidate_cells.size),
        "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
        "temporal_chunks_improved": int((chunk_array > 0).sum()),
        "temporal_chunk_count": int(len(chunk_array)),
        "temporal_chunk_gain_min": float(chunk_array.min()),
        "temporal_chunk_gain_median": float(np.median(chunk_array)),
        "temporal_chunk_gain_max": float(chunk_array.max()),
        "temporal_chunk_gains": chunk_array.tolist(),
        "per_block_fold_origin_win_rates": origin_win_rates,
        "inferred_validation_phase_coverage": int((inferred_phase_counts > 0).sum()),
    }
    return candidates, stress


def main() -> int:
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
        build_folds(
            len(block),
            block_index=index,
            fold_count=args.fold_count,
            validation_size=args.validation_size,
            min_train_origins=args.min_train_origins,
        )
        for index, block in enumerate(blocks, start=1)
    ]
    candidates, stress = evaluate(blocks, text_blocks, adjacency, fold_sets, args)

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = np.asarray(
        load_aligned_texts(data_root / "test" / "test_texts.json", test_keys), dtype=object
    )
    regimes = classify_test_regime(test_history)
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    anchor_prediction = np.empty(shape, dtype=np.float32)
    seasonal_prediction = np.empty(shape, dtype=np.float32)
    inferred_test_phases = np.empty(len(test_history), dtype=np.int64)
    full_models = []
    for block, texts in zip(blocks, text_blocks, strict=True):
        end = len(block) - int(HORIZONS.max()) - 1
        full_models.append(
            (
                _fit_e013_components(block, texts, adjacency, 14, end, args),
                fit_seasonal_phase(
                    block, 14, end, period=PERIOD, road_groups=ROAD_GROUPS, chunk_size=args.chunk_size
                ),
            )
        )
    for regime_index, (components, phase_model) in enumerate(full_models):
        mask = regimes == regime_index
        histories = test_history[mask]
        anchor_prediction[mask] = _predict_e013(
            components, histories, test_texts[mask].tolist()
        )
        seasonal_prediction[mask] = phase_model.predict(histories)
        inferred_test_phases[mask] = phase_model.infer_phase(histories)
    candidate_prediction = phase_blend(anchor_prediction, seasonal_prediction)

    zero_history = np.all(test_history == 0, axis=1)
    zero_values = candidate_prediction[
        np.broadcast_to(zero_history[:, None, :], candidate_prediction.shape)
    ]
    delta = candidate_prediction.astype(np.float64) - anchor_prediction.astype(np.float64)
    diagnostics = {
        "prediction_values_valid": bool(
            np.isfinite(candidate_prediction).all() and (candidate_prediction >= 0).all()
        ),
        "all_zero_history_guard_valid": bool(np.all(zero_values == 0)),
        "all_zero_history_pairs": int(zero_history.sum()),
        "candidate_vs_e013_delta_mean": float(delta.mean()),
        "candidate_vs_e013_delta_rms": float(np.sqrt(np.mean(np.square(delta)))),
        "candidate_vs_e013_delta_abs_gt_5_fraction": float(np.mean(np.abs(delta) > 5.0)),
        "inferred_test_phase_coverage": int(len(np.unique(inferred_test_phases))),
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
        "hypothesis": "A training-only 360-step phase prototype adds recurring road-specific daily deltas missing from E013.",
        "preregistered_parameters": {
            "period": PERIOD,
            "road_groups": ROAD_GROUPS,
            "anchor_weight": ANCHOR_WEIGHT,
            "seasonal_weight": SEASONAL_WEIGHT,
            "weight_search": False,
            "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
            "alpha": args.alpha,
            "text_residual_alpha": args.text_residual_alpha,
            "text_z_threshold": args.text_z_threshold,
            "seed": None,
        },
        "candidates": candidates,
        "stress": stress,
        "test_diagnostics": diagnostics,
        "acceptance_gate": gate,
        "test_regime_counts": {"m1": int((regimes == 0).sum()), "m2": int((regimes == 1).sum())},
        "prediction": {
            "shape": list(candidate_prediction.shape),
            "min": float(candidate_prediction.min()),
            "max": float(candidate_prediction.max()),
            "mean": float(candidate_prediction.mean()),
            "submission_rows": int(candidate_prediction.size),
        },
        "submission": str(submission_path) if submission_path is not None else None,
        "runtime_seconds": float(time.perf_counter() - started),
    }
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "anchor_mse": candidates["stableblend"]["mean_mse"],
        "seasonal_mse": candidates["seasonal"]["mean_mse"],
        "candidate_mse": candidates["phaseblend"]["mean_mse"],
        "stress": stress,
        "gate": gate,
        "diagnostics": diagnostics,
        "submission": str(submission_path) if submission_path else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

