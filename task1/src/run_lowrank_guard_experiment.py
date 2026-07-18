"""Run the fixed Task 1 low-rank novelty-guard experiment."""

from __future__ import annotations

import json
import time

import numpy as np

from baseline import write_submission
from global_state_model import fit_global_state_ridge
from graph_model import fit_graph_ridge
from graphtext_blend import blend_predictions
from lowrank_novelty_guard import (
    DEFAULT_Z_THRESHOLD,
    apply_lowrank_novelty_guard,
    fit_lowrank_novelty_guard,
)
from lowrank_state_model import DEFAULT_PCA_SAMPLES, DEFAULT_RANK, fit_lowrank_state_ridge
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
from run_lowrank_experiment import parse_args
from run_textres_experiment import load_train_text_blocks
from stable_blend import ANCHOR_WEIGHT, GLOBALSTATE_WEIGHT, stable_blend_predictions
from text_residual_model import load_aligned_texts
from text_zguard_model import DEFAULT_Z_THRESHOLD as TEXT_Z_THRESHOLD
from text_zguard_model import fit_text_zguard


EXPERIMENT_ID = "d1-e018-lowrankguard"


def acceptance_gate(candidates: dict, stress: dict, diagnostics: dict) -> dict:
    reference = candidates["stableblend"]
    candidate = candidates["lowrankguard"]
    reference_folds = np.asarray(reference["fold_mse"], dtype=np.float64)
    candidate_folds = np.asarray(candidate["fold_mse"], dtype=np.float64)
    reference_horizons = np.asarray(list(reference["mse_by_horizon"].values()))
    candidate_horizons = np.asarray(list(candidate["mse_by_horizon"].values()))
    checks = {
        "mean_improves_e013_by_at_least_2_percent": float(candidate["mean_mse"])
        <= 0.98 * float(reference["mean_mse"]),
        "all_three_folds_improve": bool(np.all(candidate_folds < reference_folds)),
        "all_three_horizons_improve": bool(
            np.all(candidate_horizons < reference_horizons)
        ),
        "worst_fold_improves": float(candidate["worst_fold_mse"])
        < float(reference["worst_fold_mse"]),
        "fold_standard_deviation_not_worse": float(candidate["std_mse"])
        <= float(reference["std_mse"]),
        "all_18_cells_improve": int(stress["block_fold_horizon_cells_improved"])
        == 18,
        "at_least_35_of_36_chunks_improve": int(stress["temporal_chunks_improved"])
        >= 35,
        "median_chunk_gain_at_least_0_50_mse": float(
            stress["temporal_chunk_gain_median"]
        )
        >= 0.50,
        "worst_chunk_gain_not_below_minus_0_10": float(
            stress["temporal_chunk_gain_min"]
        )
        >= -0.10,
        "test_m2_correction_is_nonpositive": float(
            diagnostics["lowrankguard_m2_mean_correction_vs_ridge"]
        )
        <= 0.0,
        "test_change_vs_e013_is_conservative": float(
            diagnostics["lowrankguard_vs_e013_rms"]
        )
        <= 1.0,
        "test_reversion_rate_at_most_20_percent": float(
            diagnostics["test_reversion_rate"]
        )
        <= 0.20,
        "predictions_are_valid_and_zero_guarded": bool(
            diagnostics["prediction_values_valid"]
            and diagnostics["all_zero_history_guard_valid"]
        ),
    }
    return {"checks": checks, "status": "KEEP" if all(checks.values()) else "REJECT"}


def evaluate_candidates(blocks, text_blocks, adjacency, fold_sets, args):
    methods = ("stableblend", "lowrankblend", "lowrankguard")
    scores = {method: [] for method in methods}
    chunk_gains = []
    origin_win_rates = []
    validation_reversion_rates = []
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
                alpha=args.alpha,
                chunk_size=args.chunk_size,
            )
            global_model = fit_global_state_ridge(
                block,
                fold.train_origin_start,
                fold.train_origin_end,
                alpha=args.alpha,
                chunk_size=args.chunk_size,
            )
            lowrank_model = fit_lowrank_state_ridge(
                block,
                fold.train_origin_start,
                fold.train_origin_end,
                alpha=args.alpha,
                rank=args.rank,
                pca_sample_count=args.pca_samples,
                chunk_size=args.chunk_size,
            )
            novelty_guard = fit_lowrank_novelty_guard(
                block,
                lowrank_model,
                fold.train_origin_start,
                fold.train_origin_end,
                z_threshold=DEFAULT_Z_THRESHOLD,
                chunk_size=args.chunk_size,
            )
            text_model = fit_text_zguard(
                block,
                texts,
                fold.train_origin_start,
                fold.train_origin_end,
                base_alpha=args.alpha,
                residual_alpha=args.text_residual_alpha,
                z_threshold=args.text_z_threshold,
                chunk_size=args.chunk_size,
            )
            validation_texts = [texts[index] for index in origins]
            anchor_prediction = blend_predictions(
                graph_model.predict(histories),
                text_model.predict(histories, validation_texts),
            )
            e013_prediction = stable_blend_predictions(
                anchor_prediction, global_model.predict(histories)
            )
            e016_prediction = stable_blend_predictions(
                anchor_prediction, lowrank_model.predict(histories)
            )
            trusted = novelty_guard.trusted(histories, lowrank_model)
            guarded_prediction = apply_lowrank_novelty_guard(
                e013_prediction, e016_prediction, trusted
            )
            predictions = {
                "stableblend": e013_prediction,
                "lowrankblend": e016_prediction,
                "lowrankguard": guarded_prediction,
            }
            validation_reversion_rates.append(float(np.mean(~trusted)))
            for method in methods:
                block_scores[method].append(mse_by_horizon(targets, predictions[method]))
            target64 = targets.astype(np.float64)
            reference_error = np.mean(
                np.square(target64 - e013_prediction.astype(np.float64)), axis=(1, 2)
            )
            candidate_error = np.mean(
                np.square(target64 - guarded_prediction.astype(np.float64)), axis=(1, 2)
            )
            origin_win_rates.append(float(np.mean(candidate_error < reference_error)))
            for start in range(0, len(origins), TEMPORAL_CHUNK_SIZE):
                stop = min(start + TEMPORAL_CHUNK_SIZE, len(origins))
                chunk_gains.append(
                    float(
                        reference_error[start:stop].mean()
                        - candidate_error[start:stop].mean()
                    )
                )
        for method in methods:
            scores[method].append(np.asarray(block_scores[method]))
    candidates = {method: summarize_fold_scores(scores[method]) for method in methods}
    reference_cells = np.asarray(candidates["stableblend"]["block_fold_horizon_mse"])
    candidate_cells = np.asarray(candidates["lowrankguard"]["block_fold_horizon_mse"])
    chunk_array = np.asarray(chunk_gains, dtype=np.float64)
    stress = {
        "block_fold_horizon_cells_improved": int((candidate_cells < reference_cells).sum()),
        "block_fold_horizon_cell_count": int(candidate_cells.size),
        "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
        "temporal_chunks_improved": int((chunk_array > 0).sum()),
        "temporal_chunk_count": int(len(chunk_array)),
        "temporal_chunk_gain_min": float(chunk_array.min()),
        "temporal_chunk_gain_median": float(np.median(chunk_array)),
        "temporal_chunk_gain_max": float(chunk_array.max()),
        "temporal_chunk_gains": chunk_array.tolist(),
        "per_block_fold_origin_win_rates": origin_win_rates,
        "validation_reversion_rates": validation_reversion_rates,
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
    candidates, stress = evaluate_candidates(
        blocks, text_blocks, adjacency, fold_sets, args
    )

    test_history = np.load(data_root / "test" / "test_X_hist.npy", mmap_mode="r")
    test_keys = [f"test_{index:05d}" for index in range(len(test_history))]
    test_texts = np.asarray(
        load_aligned_texts(data_root / "test" / "test_texts.json", test_keys),
        dtype=object,
    )
    regimes = classify_test_regime(test_history)
    train_end = [len(block) - int(HORIZONS.max()) - 1 for block in blocks]
    graph_models = [
        fit_graph_ridge(
            block, adjacency, 14, end, alpha=args.alpha, chunk_size=args.chunk_size
        )
        for block, end in zip(blocks, train_end, strict=True)
    ]
    global_models = [
        fit_global_state_ridge(
            block, 14, end, alpha=args.alpha, chunk_size=args.chunk_size
        )
        for block, end in zip(blocks, train_end, strict=True)
    ]
    lowrank_models = [
        fit_lowrank_state_ridge(
            block,
            14,
            end,
            alpha=args.alpha,
            rank=args.rank,
            pca_sample_count=args.pca_samples,
            chunk_size=args.chunk_size,
        )
        for block, end in zip(blocks, train_end, strict=True)
    ]
    novelty_guards = [
        fit_lowrank_novelty_guard(
            block,
            model,
            14,
            end,
            z_threshold=DEFAULT_Z_THRESHOLD,
            chunk_size=args.chunk_size,
        )
        for block, model, end in zip(blocks, lowrank_models, train_end, strict=True)
    ]
    text_models = [
        fit_text_zguard(
            block,
            texts,
            14,
            end,
            base_alpha=args.alpha,
            residual_alpha=args.text_residual_alpha,
            z_threshold=args.text_z_threshold,
            chunk_size=args.chunk_size,
        )
        for block, texts, end in zip(blocks, text_blocks, train_end, strict=True)
    ]
    shape = (len(test_history), len(HORIZONS), test_history.shape[2])
    ridge_prediction = np.empty(shape, dtype=np.float32)
    e013_prediction = np.empty(shape, dtype=np.float32)
    e016_prediction = np.empty(shape, dtype=np.float32)
    trusted_test = np.empty(len(test_history), dtype=bool)
    for index, (
        graph_model,
        global_model,
        lowrank_model,
        novelty_guard,
        text_model,
    ) in enumerate(
        zip(
            graph_models,
            global_models,
            lowrank_models,
            novelty_guards,
            text_models,
            strict=True,
        )
    ):
        mask = regimes == index
        histories = test_history[mask]
        texts = test_texts[mask].tolist()
        ridge_prediction[mask] = text_model.base.base_model.predict(histories)
        anchor = blend_predictions(
            graph_model.predict(histories), text_model.predict(histories, texts)
        )
        e013_prediction[mask] = stable_blend_predictions(
            anchor, global_model.predict(histories)
        )
        e016_prediction[mask] = stable_blend_predictions(
            anchor, lowrank_model.predict(histories)
        )
        trusted_test[mask] = novelty_guard.trusted(histories, lowrank_model)
    candidate_prediction = apply_lowrank_novelty_guard(
        e013_prediction, e016_prediction, trusted_test
    )
    zero_history = np.all(test_history == 0, axis=1)
    zero_values = candidate_prediction[
        np.broadcast_to(zero_history[:, None, :], candidate_prediction.shape)
    ]
    m2 = regimes == 1
    delta = candidate_prediction.astype(np.float64) - e013_prediction.astype(np.float64)
    diagnostics = {
        "lowrankguard_m2_mean_correction_vs_ridge": float(
            (candidate_prediction[m2] - ridge_prediction[m2]).mean()
        ),
        "lowrankguard_vs_e013_rms": float(np.sqrt(np.mean(np.square(delta)))),
        "lowrankguard_vs_e013_mean": float(delta.mean()),
        "test_reverted_origins": int((~trusted_test).sum()),
        "test_reversion_rate": float(np.mean(~trusted_test)),
        "test_reversion_rate_m1": float(np.mean(~trusted_test[regimes == 0])),
        "test_reversion_rate_m2": float(np.mean(~trusted_test[regimes == 1])),
        "prediction_values_valid": bool(
            np.isfinite(candidate_prediction).all() and (candidate_prediction >= 0).all()
        ),
        "all_zero_history_guard_valid": bool(np.all(zero_values == 0)),
        "all_zero_history_pairs": int(zero_history.sum()),
    }
    gate = acceptance_gate(candidates, stress, diagnostics)
    submission_path = None
    if gate["status"] == "KEEP":
        submission_path = experiment_dir / "submission.csv"
        write_submission(
            data_root / "sample_submission.csv", candidate_prediction, submission_path
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
        },
        "selection_risk": "Designed after observing E016 temporal failures; no threshold, weight, rank, alpha, or action search.",
        "hypothesis": "A training-only three-sigma latent/reconstruction novelty guard preserves broad E016 gains while reverting rare OOD origins exactly to E013.",
        "preregistered_parameters": {
            "rank": DEFAULT_RANK,
            "pca_sample_count": DEFAULT_PCA_SAMPLES,
            "alpha": args.alpha,
            "anchor_weight": ANCHOR_WEIGHT,
            "lowrank_weight": GLOBALSTATE_WEIGHT,
            "novelty_features": "20 latent temporal summaries plus reconstruction RMS",
            "novelty_z_threshold": DEFAULT_Z_THRESHOLD,
            "novelty_action": "full reversion to e013",
            "text_z_threshold": TEXT_Z_THRESHOLD,
            "temporal_chunk_size_origins": TEMPORAL_CHUNK_SIZE,
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
    print(json.dumps(summary, indent=2))
    print(f"submission={submission_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
