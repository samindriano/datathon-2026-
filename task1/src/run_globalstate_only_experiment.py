"""Stress-test the disclosed post-discovery Task 1 globalstate-only candidate."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import write_submission
from global_state_model import FEATURE_NAMES, fit_global_state_ridge
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
from ridge_model import classify_test_regime, fit_road_ridge
from run_textres_experiment import load_train_text_blocks
from text_zguard_model import DEFAULT_Z_THRESHOLD, fit_text_zguard


EXPERIMENT_ID = "d1-e012-globalstate-only"
TEMPORAL_CHUNK_SIZE = 120


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--fold-count", type=int, default=3)
    parser.add_argument("--validation-size", type=int, default=720)
    parser.add_argument("--min-train-origins", type=int, default=1440)
    parser.add_argument("--global-alpha", type=float, default=0.1)
    parser.add_argument("--graph-alpha", type=float, default=0.1)
    parser.add_argument("--text-base-alpha", type=float, default=0.1)
    parser.add_argument("--text-residual-alpha", type=float, default=1.0)
    parser.add_argument("--text-z-threshold", type=float, default=DEFAULT_Z_THRESHOLD)
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def acceptance_gate(candidates: dict, stress: dict, diagnostics: dict) -> dict:
    reference = candidates["graphtextblend"]
    candidate = candidates["globalstate"]
    reference_folds = np.asarray(reference["fold_mse"], dtype=np.float64)
    candidate_folds = np.asarray(candidate["fold_mse"], dtype=np.float64)
    reference_horizons = np.asarray(list(reference["mse_by_horizon"].values()))
    candidate_horizons = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "aggregate_mean_improves_e010_by_at_least_3_percent": float(
            candidate["mean_mse"]
        )
        <= 0.97 * float(reference["mean_mse"]),
        "all_three_folds_improve": int((candidate_folds < reference_folds).sum())
        == 3,
        "all_three_horizons_improve": int(
            (candidate_horizons < reference_horizons).sum()
        )
        == 3,
        "worst_fold_improves": float(candidate["worst_fold_mse"])
        < float(reference["worst_fold_mse"]),
        "fold_standard_deviation_not_worse": float(candidate["std_mse"])
        <= float(reference["std_mse"]),
        "at_least_15_of_18_block_fold_horizon_cells_improve": int(
            stress["block_fold_horizon_cells_improved"]
        )
        >= 15,
        "at_least_34_of_36_temporal_chunks_improve": int(
            stress["temporal_chunks_improved"]
        )
        >= 34,
        "median_temporal_chunk_gain_at_least_1_mse": float(
            stress["temporal_chunk_gain_median"]
        )
        >= 1.0,
        "worst_temporal_chunk_gain_not_below_minus_0_25": float(
            stress["temporal_chunk_gain_min"]
        )
        >= -0.25,
        "test_m2_mean_correction_is_nonpositive": float(
            diagnostics["global_m2_mean_correction_vs_ridge"]
        )
        <= 0.0,
        "predictions_are_finite_nonnegative_and_zero_guarded": bool(
            diagnostics["prediction_values_valid"]
            and diagnostics["all_zero_history_guard_valid"]
        ),
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def evaluate_stress(blocks, text_blocks, adjacency, fold_sets, args):
    methods = ("graphtextblend", "globalstate")
    scores = {method: [] for method in methods}
    chunk_gains = []
    origin_win_rates = []
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores = {method: [] for method in methods}
        for fold in folds:
            origins = np.arange(
                fold.validation_origin_start, fold.validation_origin_end + 1
            )
            histories, targets = windows_at_origins(block, origins)
            graph_model = fit_graph_ridge(
                block,
                adjacency,
                fold.train_origin_start,
                fold.train_origin_end,
                alpha=args.graph_alpha,
                chunk_size=args.chunk_size,
            )
            global_model = fit_global_state_ridge(
                block,
                fold.train_origin_start,
                fold.train_origin_end,
                alpha=args.global_alpha,
                chunk_size=args.chunk_size,
            )
            text_model = fit_text_zguard(
                block,
                texts,
                fold.train_origin_start,
                fold.train_origin_end,
                base_alpha=args.text_base_alpha,
                residual_alpha=args.text_residual_alpha,
                z_threshold=args.text_z_threshold,
                chunk_size=args.chunk_size,
            )
            validation_texts = [texts[index] for index in origins]
            reference_prediction = blend_predictions(
                graph_model.predict(histories),
                text_model.predict(histories, validation_texts),
            )
            candidate_prediction = global_model.predict(histories)
            predictions = {
                "graphtextblend": reference_prediction,
                "globalstate": candidate_prediction,
            }
            for method in methods:
                block_scores[method].append(
                    mse_by_horizon(targets, predictions[method])
                )

            target64 = targets.astype(np.float64)
            reference_error = np.mean(
                np.square(target64 - reference_prediction.astype(np.float64)),
                axis=(1, 2),
            )
            candidate_error = np.mean(
                np.square(target64 - candidate_prediction.astype(np.float64)),
                axis=(1, 2),
            )
            origin_win_rates.append(float(np.mean(candidate_error < reference_error)))
            for start in range(0, len(origins), TEMPORAL_CHUNK_SIZE):
                stop = min(start + TEMPORAL_CHUNK_SIZE, len(origins))
                chunk_gains.append(
                    float(reference_error[start:stop].mean() - candidate_error[start:stop].mean())
                )
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))

    candidates = {
        method: summarize_fold_scores(scores[method]) for method in methods
    }
    reference_cells = np.asarray(
        candidates["graphtextblend"]["block_fold_horizon_mse"]
    )
    candidate_cells = np.asarray(candidates["globalstate"]["block_fold_horizon_mse"])
    chunk_array = np.asarray(chunk_gains, dtype=np.float64)
    stress = {
        "block_fold_horizon_cells_improved": int(
            (candidate_cells < reference_cells).sum()
        ),
        "block_fold_horizon_cell_count": int(candidate_cells.size),
        "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
        "temporal_chunks_improved": int((chunk_array > 0).sum()),
        "temporal_chunk_count": int(len(chunk_array)),
        "temporal_chunk_gain_min": float(chunk_array.min()),
        "temporal_chunk_gain_median": float(np.median(chunk_array)),
        "temporal_chunk_gain_max": float(chunk_array.max()),
        "temporal_chunk_gains": chunk_array.tolist(),
        "per_block_fold_origin_win_rates": origin_win_rates,
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
    candidates, stress = evaluate_stress(
        blocks, text_blocks, adjacency, fold_sets, args
    )

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    regimes = classify_test_regime(test_history)
    global_models = [
        fit_global_state_ridge(
            block,
            origin_start=14,
            origin_end=len(block) - int(HORIZONS.max()) - 1,
            alpha=args.global_alpha,
            chunk_size=args.chunk_size,
        )
        for block in blocks
    ]
    ridge_models = [
        fit_road_ridge(
            block,
            origin_start=14,
            origin_end=len(block) - int(HORIZONS.max()) - 1,
            alpha=args.global_alpha,
            chunk_size=args.chunk_size,
        )
        for block in blocks
    ]
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    ridge_prediction = np.empty(shape, dtype=np.float32)
    global_prediction = np.empty(shape, dtype=np.float32)
    for regime_index, (global_model, ridge_model) in enumerate(
        zip(global_models, ridge_models, strict=True)
    ):
        mask = regimes == regime_index
        ridge_prediction[mask] = ridge_model.predict(test_history[mask])
        global_prediction[mask] = global_model.predict(test_history[mask])

    zero_history = np.all(test_history == 0, axis=1)
    zero_prediction_values = global_prediction[
        np.broadcast_to(zero_history[:, None, :], global_prediction.shape)
    ]
    diagnostics = {
        "global_m1_mean_correction_vs_ridge": float(
            (global_prediction[regimes == 0] - ridge_prediction[regimes == 0]).mean()
        ),
        "global_m2_mean_correction_vs_ridge": float(
            (global_prediction[regimes == 1] - ridge_prediction[regimes == 1]).mean()
        ),
        "global_correction_min": float((global_prediction - ridge_prediction).min()),
        "global_correction_max": float((global_prediction - ridge_prediction).max()),
        "global_correction_mean": float((global_prediction - ridge_prediction).mean()),
        "prediction_values_valid": bool(
            np.isfinite(global_prediction).all() and (global_prediction >= 0).all()
        ),
        "all_zero_history_guard_valid": bool(
            np.all(zero_prediction_values == 0)
        ),
        "all_zero_history_pairs": int(zero_history.sum()),
    }
    gate = acceptance_gate(candidates, stress, diagnostics)

    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(
            data_root / "sample_submission.csv", global_prediction, submission_path
        )

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "selection_disclosure": "Globalstate aggregate score was observed as a diagnostic in rejected e011; e012 acceptance adds preregistered unseen temporal-chunk stress.",
        "metric": "mse",
        "validation": {
            "version": "d1-multifold-v1",
            "fold_count_per_block": args.fold_count,
            "validation_origins_per_fold": args.validation_size,
            "minimum_training_origins": args.min_train_origins,
            "purge_origins": int(HORIZONS.max()),
            "regime_weights": {
                "m1": float(REGIME_WEIGHTS[0]),
                "m2": float(REGIME_WEIGHTS[1]),
            },
            "folds": [[fold.to_dict() for fold in folds] for folds in fold_sets],
        },
        "hypothesis": "The discovered globalstate-only gain is broad enough to survive strict unseen temporal-chunk stress and justify independent audit.",
        "preregistered_parameters": {
            "features": list(FEATURE_NAMES),
            "active_road_rule": "any nonzero value in the causal 15-step history",
            "alpha": args.global_alpha,
            "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
            "zero_history_guard": True,
            "seed": None,
        },
        "candidates": candidates,
        "stress": stress,
        "test_diagnostics": diagnostics,
        "acceptance_gate": gate,
        "test_regime_counts": {
            "m1": int((regimes == 0).sum()),
            "m2": int((regimes == 1).sum()),
        },
        "prediction": {
            "shape": list(global_prediction.shape),
            "min": float(global_prediction.min()),
            "max": float(global_prediction.max()),
            "mean": float(global_prediction.mean()),
            "submission_rows": int(global_prediction.size),
        },
        "submission": str(submission_path) if submission_path is not None else None,
        "runtime_seconds": float(time.perf_counter() - started),
    }
    (experiment_dir / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print(f"submission={submission_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
