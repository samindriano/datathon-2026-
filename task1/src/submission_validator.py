"""Validate Task 1 submissions without loading all string IDs into memory."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd


HORIZONS = (5, 10, 15)
EXPECTED_COLUMNS = ["id", "speed"]


class SubmissionValidationError(ValueError):
    """Raised when a submission violates the Task 1 contract."""


def expected_ids(start: int, stop: int, road_count: int) -> list[str]:
    rows_per_sample = len(HORIZONS) * road_count
    result = []
    for position in range(start, stop):
        sample, within_sample = divmod(position, rows_per_sample)
        horizon_index, road = divmod(within_sample, road_count)
        result.append(f"test_{sample:05d}_h{HORIZONS[horizon_index]}_r{road}")
    return result


def _chunks(path: Path, chunk_size: int):
    return pd.read_csv(path, chunksize=chunk_size)


def validate_submission(
    template_path: Path,
    submission_path: Path,
    sample_count: int = 540,
    road_count: int = 1260,
    chunk_size: int = 100_000,
    reference_path: Path | None = None,
) -> dict[str, object]:
    """Validate schema, exact IDs, values, and optional numeric reproduction."""
    template_path = Path(template_path)
    submission_path = Path(submission_path)
    reference_path = Path(reference_path) if reference_path is not None else None
    expected_row_count = sample_count * len(HORIZONS) * road_count
    speed_hash = hashlib.sha256()
    row_count = 0
    speed_sum = 0.0
    speed_min = np.inf
    speed_max = -np.inf
    zero_count = 0
    reference_mismatch_count = 0
    reference_max_abs_difference = 0.0

    iterators = [_chunks(template_path, chunk_size), _chunks(submission_path, chunk_size)]
    if reference_path is not None:
        iterators.append(_chunks(reference_path, chunk_size))

    try:
        for parts in itertools.zip_longest(*iterators):
            if any(part is None for part in parts):
                raise SubmissionValidationError(
                    "Template, submission, and reference row counts differ"
                )
            template, submission = parts[0], parts[1]
            reference = parts[2] if reference_path is not None else None
            if template.columns.tolist() != EXPECTED_COLUMNS:
                raise SubmissionValidationError(
                    f"Unexpected template columns: {template.columns.tolist()}"
                )
            if submission.columns.tolist() != EXPECTED_COLUMNS:
                raise SubmissionValidationError(
                    f"Unexpected submission columns: {submission.columns.tolist()}"
                )
            if len(template) != len(submission):
                raise SubmissionValidationError("Template and submission chunk lengths differ")

            stop = row_count + len(submission)
            ids = expected_ids(row_count, stop, road_count)
            if template["id"].tolist() != ids:
                raise SubmissionValidationError(f"Template ID order differs at row {row_count}")
            if submission["id"].tolist() != ids:
                raise SubmissionValidationError(f"Submission ID order differs at row {row_count}")

            speed = pd.to_numeric(submission["speed"], errors="coerce").to_numpy(
                dtype=np.float64
            )
            if not np.isfinite(speed).all():
                raise SubmissionValidationError(f"Non-finite speed found near row {row_count}")
            if (speed < 0).any():
                raise SubmissionValidationError(f"Negative speed found near row {row_count}")
            speed_hash.update(speed.astype("<f8", copy=False).tobytes())
            speed_sum += float(speed.sum(dtype=np.float64))
            speed_min = min(speed_min, float(speed.min()))
            speed_max = max(speed_max, float(speed.max()))
            zero_count += int((speed == 0).sum())

            if reference is not None:
                if reference.columns.tolist() != EXPECTED_COLUMNS:
                    raise SubmissionValidationError(
                        f"Unexpected reference columns: {reference.columns.tolist()}"
                    )
                if reference["id"].tolist() != ids:
                    raise SubmissionValidationError(
                        f"Reference ID order differs at row {row_count}"
                    )
                reference_speed = pd.to_numeric(
                    reference["speed"], errors="coerce"
                ).to_numpy(dtype=np.float64)
                if not np.isfinite(reference_speed).all():
                    raise SubmissionValidationError("Reference contains non-finite speed")
                difference = np.abs(speed - reference_speed)
                reference_mismatch_count += int((difference != 0).sum())
                reference_max_abs_difference = max(
                    reference_max_abs_difference, float(difference.max(initial=0.0))
                )
            row_count = stop
    finally:
        for iterator in iterators:
            iterator.close()

    if row_count != expected_row_count:
        raise SubmissionValidationError(
            f"Submission has {row_count} rows; expected {expected_row_count}"
        )
    report: dict[str, object] = {
        "status": "READY",
        "row_count": row_count,
        "expected_row_count": expected_row_count,
        "columns": EXPECTED_COLUMNS,
        "ids_exact_and_unique": True,
        "finite": True,
        "nonnegative": True,
        "speed_min": speed_min,
        "speed_max": speed_max,
        "speed_mean": speed_sum / row_count,
        "zero_count": zero_count,
        "speed_values_sha256": speed_hash.hexdigest(),
    }
    if reference_path is not None:
        report["reference_mismatch_count"] = reference_mismatch_count
        report["reference_max_abs_difference"] = reference_max_abs_difference
        report["reference_exact_numeric_match"] = reference_mismatch_count == 0
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--sample-count", type=int, default=540)
    parser.add_argument("--road-count", type=int, default=1260)
    parser.add_argument("--chunk-size", type=int, default=100_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_submission(
        template_path=args.template,
        submission_path=args.submission,
        sample_count=args.sample_count,
        road_count=args.road_count,
        chunk_size=args.chunk_size,
        reference_path=args.reference,
    )
    text = json.dumps(report, indent=2) + "\n"
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
