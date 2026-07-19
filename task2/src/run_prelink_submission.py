"""Build and validate a Task 2 submission from an E014 link extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from metarank import MetaRanker
from prelink import PrelinkRanker
from submission_validator import (
    resolve_submission_output_path,
    resolve_task2_data_dir,
    validate_submission,
)
from validation import accuracy, make_target_group_folds


E002_REFERENCE_MEAN = 0.2853333333333333


def load_link_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("experiment_id") != "d2-e014-prelink":
        raise ValueError(f"unexpected extraction experiment: {payload.get('experiment_id')}")
    if not isinstance(payload.get("links"), dict):
        raise ValueError("link extraction must contain a links object")
    extracted = {int(value) for value in payload.get("article_ids", [])}
    link_keys = {int(value) for value in payload["links"]}
    if link_keys != extracted:
        raise ValueError("link extraction keys do not exactly match extracted article IDs")
    return payload


def evaluate_prelink(
    data_root: Path, link_json: Path
) -> dict[str, object]:
    """Evaluate E014 and E002 on the unchanged target-disjoint folds."""

    train = pd.read_csv(data_root / "states_train.csv")
    articles = pd.read_csv(data_root / "articles.csv")
    categories = pd.read_csv(data_root / "categories.csv")
    payload = load_link_payload(link_json)
    links = {
        int(current): [int(candidate) for candidate in candidates]
        for current, candidates in payload["links"].items()
    }
    required_currents = set(train["current_article_id"].astype(np.int64))
    missing = sorted(required_currents - {int(value) for value in payload["article_ids"]})
    if missing:
        raise ValueError(
            f"validation extraction is incomplete ({len(missing)} missing currents)"
        )

    folds = make_target_group_folds(train, categories)
    e002_scores: list[float] = []
    e014_scores: list[float] = []
    fold_rows: list[dict[str, object]] = []
    for fold in range(5):
        training = train.loc[folds != fold]
        validation = train.loc[folds == fold]
        truth = validation["next_article_id"].to_numpy(dtype=np.int64)
        e002 = MetaRanker.fit(training, articles, categories)
        e014 = PrelinkRanker.fit(training, articles, categories, links)
        e002_prediction = e002.predict(validation)
        e014_prediction, used_links = e014.predict_with_diagnostics(validation)
        e002_score = accuracy(truth, e002_prediction)
        e014_score = accuracy(truth, e014_prediction)
        e002_scores.append(e002_score)
        e014_scores.append(e014_score)
        fold_rows.append(
            {
                "fold": fold,
                "rows": int(len(validation)),
                "e002_accuracy": e002_score,
                "e014_accuracy": e014_score,
                "gain": e014_score - e002_score,
                "rows_using_screenshot_links": int(used_links.sum()),
            }
        )

    mean_e002 = float(np.mean(e002_scores))
    mean_e014 = float(np.mean(e014_scores))
    if mean_e002 != E002_REFERENCE_MEAN:
        raise RuntimeError(
            f"E002 reference did not reproduce: {mean_e002} != {E002_REFERENCE_MEAN}"
        )
    gates = {
        "mean_accuracy_at_least_0_290333": mean_e014 >= 0.29033333333333333,
        "fold_wins_at_least_4_of_5": sum(
            candidate > anchor
            for candidate, anchor in zip(e014_scores, e002_scores, strict=True)
        )
        >= 4,
        "worst_fold_at_least_0_273333": min(e014_scores) >= 0.2733333333333333,
    }
    return {
        "validation": "d2-targetgroup-v1",
        "folds": fold_rows,
        "e002_mean_accuracy": mean_e002,
        "e014_mean_accuracy": mean_e014,
        "mean_gain": mean_e014 - mean_e002,
        "fold_wins": int(
            sum(
                candidate > anchor
                for candidate, anchor in zip(e014_scores, e002_scores, strict=True)
            )
        ),
        "e014_worst_fold": float(min(e014_scores)),
        "partial_acceptance_gates": gates,
        "partial_gate_status": "PASS" if all(gates.values()) else "REJECT",
    }


def build_submission(
    data_root: Path,
    link_json: Path,
    output_path: Path,
) -> dict[str, object]:
    started = time.perf_counter()
    train = pd.read_csv(data_root / "states_train.csv")
    test = pd.read_csv(data_root / "states_test.csv")
    articles = pd.read_csv(data_root / "articles.csv")
    categories = pd.read_csv(data_root / "categories.csv")
    sample = pd.read_csv(data_root / "sample_submission.csv")
    payload = load_link_payload(link_json)

    required_currents = set(train["current_article_id"].astype(np.int64)) | set(
        test["current_article_id"].astype(np.int64)
    )
    extracted_currents = {int(value) for value in payload.get("article_ids", [])}
    missing = sorted(required_currents - extracted_currents)
    if missing:
        raise ValueError(
            "extraction is incomplete; missing current article IDs "
            f"({len(missing)} total): {missing[:10]}"
        )

    links = {
        int(current): [int(candidate) for candidate in candidates]
        for current, candidates in payload["links"].items()
    }
    ranker = PrelinkRanker.fit(train, articles, categories, links)
    prediction, used_links = ranker.predict_with_diagnostics(test)
    fallback_prediction = MetaRanker.fit(train, articles, categories).predict(test)

    if sample.columns.tolist() != ["state_id", "predicted_next_article_id"]:
        raise ValueError(f"unexpected sample columns: {sample.columns.tolist()}")
    if len(sample) != len(prediction):
        raise ValueError("sample row count does not match predictions")
    submission = sample.copy()
    submission["predicted_next_article_id"] = prediction
    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    validated = validate_submission(output_path, data_dir=data_root)

    counts = submission["predicted_next_article_id"].value_counts(normalize=True)
    return {
        "experiment_id": "d2-e014-prelink",
        "status": "READY",
        "rows": int(validated.row_count),
        "unique_predictions": int(validated.unique_prediction_count),
        "top_prediction_share": float(counts.iloc[0]),
        "rows_using_screenshot_links": int(used_links.sum()),
        "screenshot_link_usage_rate": float(used_links.mean()),
        "prediction_change_rate_vs_e002": float(
            np.mean(prediction != fallback_prediction)
        ),
        "prediction_sha256": hashlib.sha256(
            prediction.astype("<i8", copy=False).tobytes()
        ).hexdigest(),
        "csv_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "runtime_seconds": float(time.perf_counter() - started),
        "link_json": str(link_json.resolve()),
        "output": str(output_path.resolve()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--link-json", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data_root = resolve_task2_data_dir(args.data_root)
    output = args.output or resolve_submission_output_path()
    print(
        json.dumps(
            build_submission(data_root, args.link_json.resolve(), output), indent=2
        )
    )


if __name__ == "__main__":
    main()
