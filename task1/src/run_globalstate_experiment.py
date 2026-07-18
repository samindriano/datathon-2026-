"""Run the preregistered global-city-state replacement for Task 1 e010."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from baseline import write_submission
from global_state_model import FEATURE_NAMES, fit_global_state_ridge
from graph_model import fit_graph_ridge
from graphtext_blend import GRAPH_WEIGHT, TEXT_WEIGHT, blend_predictions
from multifold import (
    HORIZONS,
    REGIME_WEIGHTS,
    build_folds,
    mse_by_horizon,
    summarize_fold_scores,
    windows_at_origins,
)
from ridge_model import classify_test_regime
from run_textres_experiment import load_train_text_blocks
from text_residual_model import load_aligned_texts
from text_zguard_model import DEFAULT_Z_THRESHOLD, fit_text_zguard


EXPERIMENT_ID = "d1-e011-globalstate"


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


def acceptance_gate(candidates: dict, diagnostics: dict) -> dict:
    graph = candidates["graphres"]
    globalstate = candidates["globalstate"]
    text = candidates["textzguard"]
    reference = candidates["graphtextblend"]
    candidate = candidates["globaltextblend"]
    reference_folds = np.asarray(reference["fold_mse"], dtype=np.float64)
    candidate_folds = np.asarray(candidate["fold_mse"], dtype=np.float64)
    reference_horizons = np.asarray(list(reference["mse_by_horizon"].values()))
    candidate_horizons = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "globalstate_mean_beats_graphres": float(globalstate["mean_mse"])
        < float(graph["mean_mse"]),
        "blend_mean_improves_e010_by_at_least_0_5_percent": float(
            candidate["mean_mse"]
        )
        <= 0.995 * float(reference["mean_mse"]),
        "blend_improves_at_least_two_folds_vs_e010": int(
            (candidate_folds < reference_folds).sum()
        )
        >= 2,
        "blend_improves_at_least_two_horizons_vs_e010": int(
            (candidate_horizons < reference_horizons).sum()
        )
        >= 2,
        "blend_worst_fold_not_worse_than_e010": float(candidate["worst_fold_mse"])
        <= float(reference["worst_fold_mse"]),
        "blend_mean_beats_globalstate": float(candidate["mean_mse"])
        < float(globalstate["mean_mse"]),
        "blend_mean_beats_textzguard": float(candidate["mean_mse"])
        < float(text["mean_mse"]),
        "test_m2_mean_correction_is_nonpositive": float(
            diagnostics["blend_m2_mean_correction_vs_ridge"]
        )
        <= 0.0,
    }
    return {
        "checks": checks,
        "folds_improved_vs_e010": int((candidate_folds < reference_folds).sum()),
        "horizons_improved_vs_e010": int(
            (candidate_horizons < reference_horizons).sum()
        ),
        "status": "KEEP" if all(checks.values()) else "REJECT",
    }


def evaluate_candidates(blocks, text_blocks, adjacency, fold_sets, args):
    methods = (
        "ridge-history",
        "graphres",
        "globalstate",
        "textzguard",
        "graphtextblend",
        "globaltextblend",
    )
    scores = {method: [] for method in methods}
    text_guard_counts = []
    for block, texts, folds in zip(blocks, text_blocks, fold_sets, strict=True):
        block_scores = {method: [] for method in methods}
        block_guard_counts = []
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
            ridge_prediction = text_model.base.base_model.predict(histories)
            graph_prediction = graph_model.predict(histories)
            global_prediction = global_model.predict(histories)
            text_prediction = text_model.predict(histories, validation_texts)
            predictions = {
                "ridge-history": ridge_prediction,
                "graphres": graph_prediction,
                "globalstate": global_prediction,
                "textzguard": text_prediction,
                "graphtextblend": blend_predictions(
                    graph_prediction, text_prediction
                ),
                "globaltextblend": blend_predictions(
                    global_prediction, text_prediction
                ),
            }
            block_guard_counts.append(int(text_model.guard_mask(validation_texts).sum()))
            for method in methods:
                block_scores[method].append(
                    mse_by_horizon(targets, predictions[method])
                )
        text_guard_counts.append(block_guard_counts)
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))
    return (
        {method: summarize_fold_scores(scores[method]) for method in methods},
        text_guard_counts,
    )


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
    candidates, validation_guard_counts = evaluate_candidates(
        blocks, text_blocks, adjacency, fold_sets, args
    )

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = load_aligned_texts(data_root / "test" / "test_texts.json", test_keys)
    test_text_array = np.asarray(test_texts, dtype=object)
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
    text_models = [
        fit_text_zguard(
            block,
            texts,
            origin_start=14,
            origin_end=len(block) - int(HORIZONS.max()) - 1,
            base_alpha=args.text_base_alpha,
            residual_alpha=args.text_residual_alpha,
            z_threshold=args.text_z_threshold,
            chunk_size=args.chunk_size,
        )
        for block, texts in zip(blocks, text_blocks, strict=True)
    ]
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    ridge_prediction = np.empty(shape, dtype=np.float32)
    global_prediction = np.empty(shape, dtype=np.float32)
    text_prediction = np.empty(shape, dtype=np.float32)
    guard_counts = {}
    for regime_index, (global_model, text_model) in enumerate(
        zip(global_models, text_models, strict=True)
    ):
        mask = regimes == regime_index
        subset_texts = test_text_array[mask].tolist()
        ridge_prediction[mask] = text_model.base.base_model.predict(test_history[mask])
        global_prediction[mask] = global_model.predict(test_history[mask])
        text_prediction[mask] = text_model.predict(test_history[mask], subset_texts)
        guard_counts[f"m{regime_index + 1}"] = int(
            text_model.guard_mask(subset_texts).sum()
        )
    blend_prediction = blend_predictions(global_prediction, text_prediction)

    m2 = regimes == 1
    diagnostics = {
        "global_m2_mean_correction_vs_ridge": float(
            (global_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "textzguard_m2_mean_correction_vs_ridge": float(
            (text_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "blend_m2_mean_correction_vs_ridge": float(
            (blend_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "test_m1_guarded_samples": guard_counts["m1"],
        "test_m2_guarded_samples": guard_counts["m2"],
    }
    gate = acceptance_gate(candidates, diagnostics)

    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(
            data_root / "sample_submission.csv", blend_prediction, submission_path
        )

    summary = {
        "experiment_id": EXPERIMENT_ID,
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
            "text_guarded_validation_samples": validation_guard_counts,
        },
        "hypothesis": "Direct active-road city summaries replace graph topology proxy; a fixed equal guarded-text blend materially improves e010.",
        "preregistered_parameters": {
            "features": list(FEATURE_NAMES),
            "active_road_rule": "any nonzero value in the causal 15-step history",
            "global_weight": GRAPH_WEIGHT,
            "textzguard_weight": TEXT_WEIGHT,
            "global_alpha": args.global_alpha,
            "graph_reference_alpha": args.graph_alpha,
            "text_base_alpha": args.text_base_alpha,
            "text_residual_alpha": args.text_residual_alpha,
            "text_z_threshold": args.text_z_threshold,
            "zero_history_guard": True,
            "seed": None,
        },
        "candidates": candidates,
        "test_diagnostics": diagnostics,
        "acceptance_gate": gate,
        "test_regime_counts": {
            "m1": int((regimes == 0).sum()),
            "m2": int((regimes == 1).sum()),
        },
        "prediction": {
            "shape": list(blend_prediction.shape),
            "min": float(blend_prediction.min()),
            "max": float(blend_prediction.max()),
            "mean": float(blend_prediction.mean()),
            "submission_rows": int(blend_prediction.size),
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
