"""Fail-closed submission validation and path helpers for Datathon Task 2."""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


EXPECTED_COLUMNS = ("state_id", "predicted_next_article_id")
EXPECTED_ROW_COUNT = 6_000
TASK2_DATA_ENV = "TASK2_DATA_DIR"
TASK2_OUTPUT_ENV = "TASK2_SUBMISSION_PATH"

_TEST_COLUMNS = ("state_id", "current_article_id", "target_article_id")
_ARTICLE_COLUMNS = ("article_id", "title")
_REQUIRED_DATA_FILES = (
    "states_test.csv",
    "sample_submission.csv",
    "articles.csv",
)
_INTEGER_PATTERN = re.compile(r"[+-]?\d+")
_NULL_TOKENS = {"nan", "na", "null", "none"}
_INFINITY_TOKENS = {"inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"}


class SubmissionValidationError(ValueError):
    """Raised when a Task 2 submission or its contract data is invalid."""


@dataclass(frozen=True)
class ValidationResult:
    submission_path: Path
    data_dir: Path
    row_count: int
    unique_prediction_count: int
    reference_checked: bool


@dataclass(frozen=True)
class _Contract:
    data_dir: Path
    state_ids: tuple[str, ...]
    article_ids: frozenset[int]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _require_data_dir(path: Path, source: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise SubmissionValidationError(f"{source} is not a directory: {resolved}")

    missing = [name for name in _REQUIRED_DATA_FILES if not (resolved / name).is_file()]
    if missing:
        raise SubmissionValidationError(
            f"{source} is missing required Task 2 files: {', '.join(missing)}"
        )
    return resolved


def resolve_task2_data_dir(
    explicit: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    repo_root: str | Path | None = None,
    kaggle_input: str | Path = "/kaggle/input",
) -> Path:
    """Resolve Task 2 data locally or on Kaggle, rejecting ambiguous matches."""

    environment = os.environ if environ is None else environ
    if explicit is not None:
        return _require_data_dir(Path(explicit), "explicit data directory")

    configured = environment.get(TASK2_DATA_ENV)
    if configured:
        return _require_data_dir(Path(configured), TASK2_DATA_ENV)

    root = _repo_root() if repo_root is None else Path(repo_root)
    local = root / "task2" / "data" / "competition" / "dataset-task2"
    if local.exists():
        return _require_data_dir(local, "repository-relative data directory")

    kaggle_root = Path(kaggle_input)
    if kaggle_root.is_dir():
        matches = sorted(
            {
                candidate.parent.resolve()
                for candidate in kaggle_root.rglob("sample_submission.csv")
                if all((candidate.parent / name).is_file() for name in _REQUIRED_DATA_FILES)
            },
            key=str,
        )
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            rendered = ", ".join(str(path) for path in matches)
            raise SubmissionValidationError(
                f"multiple Task 2 datasets found under {kaggle_root}: {rendered}; "
                f"set {TASK2_DATA_ENV} explicitly"
            )

    raise SubmissionValidationError(
        f"Task 2 data not found. Set {TASK2_DATA_ENV}, use the repository-relative "
        "task2/data/competition/dataset-task2 path, or attach one matching dataset "
        "under /kaggle/input."
    )


def resolve_submission_output_path(
    *,
    environ: Mapping[str, str] | None = None,
    repo_root: str | Path | None = None,
    kaggle_working: str | Path = "/kaggle/working",
) -> Path:
    """Return the canonical local/Kaggle output path, with an environment override."""

    environment = os.environ if environ is None else environ
    configured = environment.get(TASK2_OUTPUT_ENV)
    if configured:
        return Path(configured).expanduser()

    kaggle_dir = Path(kaggle_working)
    if kaggle_dir.is_dir():
        return kaggle_dir / "submission.csv"

    root = _repo_root() if repo_root is None else Path(repo_root)
    return root / "task2" / "submissions" / "submission.csv"


def _read_csv_rows(
    path: Path,
    expected_columns: Sequence[str],
    label: str,
) -> list[list[str]]:
    if not path.is_file():
        raise SubmissionValidationError(f"{label} does not exist: {path}")

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header != list(expected_columns):
                raise SubmissionValidationError(
                    f"{label} columns must be exactly {list(expected_columns)} in that "
                    f"order; got {header}"
                )
            rows = list(reader)
    except UnicodeDecodeError as exc:
        raise SubmissionValidationError(f"{label} must be UTF-8 CSV: {path}") from exc
    except csv.Error as exc:
        raise SubmissionValidationError(f"{label} is not valid CSV: {exc}") from exc

    for row_number, row in enumerate(rows, start=2):
        if len(row) != len(expected_columns):
            raise SubmissionValidationError(
                f"{label} row {row_number} has {len(row)} fields; "
                f"expected {len(expected_columns)}"
            )
    return rows


def _parse_integers(values: Sequence[str], label: str) -> tuple[int, ...]:
    parsed: list[int] = []
    for offset, raw_value in enumerate(values, start=2):
        value = raw_value.strip()
        lowered = value.lower()
        if not value or lowered in _NULL_TOKENS:
            raise SubmissionValidationError(f"{label} is empty/NaN at CSV row {offset}")
        if lowered in _INFINITY_TOKENS:
            raise SubmissionValidationError(f"{label} is infinite at CSV row {offset}")
        if _INTEGER_PATTERN.fullmatch(value) is None:
            raise SubmissionValidationError(
                f"{label} must contain integer values; got {raw_value!r} at CSV row {offset}"
            )
        parsed.append(int(value))
    return tuple(parsed)


def _ensure_unique(values: Sequence[str] | Sequence[int], label: str) -> None:
    if len(set(values)) != len(values):
        raise SubmissionValidationError(f"{label} contains duplicate values")


def _load_contract(data_dir: Path) -> _Contract:
    test_rows = _read_csv_rows(data_dir / "states_test.csv", _TEST_COLUMNS, "states_test.csv")
    sample_rows = _read_csv_rows(
        data_dir / "sample_submission.csv", EXPECTED_COLUMNS, "sample_submission.csv"
    )
    article_rows = _read_csv_rows(data_dir / "articles.csv", _ARTICLE_COLUMNS, "articles.csv")

    if len(test_rows) != EXPECTED_ROW_COUNT:
        raise SubmissionValidationError(
            f"states_test.csv must contain {EXPECTED_ROW_COUNT} rows; got {len(test_rows)}"
        )
    if len(sample_rows) != EXPECTED_ROW_COUNT:
        raise SubmissionValidationError(
            f"sample_submission.csv must contain {EXPECTED_ROW_COUNT} rows; "
            f"got {len(sample_rows)}"
        )

    test_state_ids = tuple(row[0].strip() for row in test_rows)
    sample_state_ids = tuple(row[0].strip() for row in sample_rows)
    _parse_integers(test_state_ids, "states_test.csv state_id")
    _parse_integers(sample_state_ids, "sample_submission.csv state_id")
    _ensure_unique(test_state_ids, "states_test.csv state_id")
    _ensure_unique(sample_state_ids, "sample_submission.csv state_id")
    if test_state_ids != sample_state_ids:
        raise SubmissionValidationError(
            "source contract mismatch: sample_submission.csv state_id values/order "
            "do not exactly match states_test.csv"
        )

    article_ids = _parse_integers(
        tuple(row[0] for row in article_rows), "articles.csv article_id"
    )
    _ensure_unique(article_ids, "articles.csv article_id")
    article_universe = frozenset(article_ids)
    if not article_universe:
        raise SubmissionValidationError("articles.csv article universe is empty")

    sample_predictions = _parse_integers(
        tuple(row[1] for row in sample_rows),
        "sample_submission.csv predicted_next_article_id",
    )
    sample_outside = sorted(set(sample_predictions) - article_universe)
    if sample_outside:
        raise SubmissionValidationError(
            "sample_submission.csv predicted_next_article_id contains IDs outside "
            f"articles.csv: {sample_outside[:10]}"
        )

    for column_index, column_name in ((1, "current_article_id"), (2, "target_article_id")):
        values = _parse_integers(
            tuple(row[column_index] for row in test_rows),
            f"states_test.csv {column_name}",
        )
        outside = sorted(set(values) - article_universe)
        if outside:
            raise SubmissionValidationError(
                f"states_test.csv {column_name} contains IDs outside articles.csv: "
                f"{outside[:10]}"
            )

    return _Contract(data_dir=data_dir, state_ids=test_state_ids, article_ids=article_universe)


def _validate_candidate(path: Path, contract: _Contract, label: str) -> tuple[int, ...]:
    rows = _read_csv_rows(path, EXPECTED_COLUMNS, label)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise SubmissionValidationError(
            f"{label} must contain exactly {EXPECTED_ROW_COUNT} rows; got {len(rows)}"
        )

    state_ids = tuple(row[0].strip() for row in rows)
    _parse_integers(state_ids, f"{label} state_id")
    _ensure_unique(state_ids, f"{label} state_id")

    expected_set = set(contract.state_ids)
    actual_set = set(state_ids)
    if actual_set != expected_set:
        missing = sorted(expected_set - actual_set)[:10]
        extra = sorted(actual_set - expected_set)[:10]
        raise SubmissionValidationError(
            f"{label} state_id set mismatch; missing={missing}, extra={extra}"
        )
    if state_ids != contract.state_ids:
        raise SubmissionValidationError(
            f"{label} state_id order must exactly match states_test.csv/sample_submission.csv; "
            "do not sort rows"
        )

    predictions = _parse_integers(
        tuple(row[1] for row in rows), f"{label} predicted_next_article_id"
    )
    outside = sorted(set(predictions) - contract.article_ids)
    if outside:
        raise SubmissionValidationError(
            f"{label} predicted_next_article_id contains IDs outside articles.csv: "
            f"{outside[:10]}"
        )
    return predictions


def validate_submission(
    submission_path: str | Path,
    *,
    data_dir: str | Path | None = None,
    reference_path: str | Path | None = None,
) -> ValidationResult:
    """Validate a Task 2 submission and optionally require reference equivalence."""

    resolved_data_dir = resolve_task2_data_dir(data_dir)
    contract = _load_contract(resolved_data_dir)
    candidate_path = Path(submission_path).expanduser().resolve()
    predictions = _validate_candidate(candidate_path, contract, "submission")

    reference_checked = reference_path is not None
    if reference_path is not None:
        reference = Path(reference_path).expanduser().resolve()
        reference_predictions = _validate_candidate(reference, contract, "reference")
        if predictions != reference_predictions:
            mismatch = next(
                index
                for index, (actual, expected) in enumerate(
                    zip(predictions, reference_predictions), start=2
                )
                if actual != expected
            )
            raise SubmissionValidationError(
                f"submission does not match reference at CSV row {mismatch}"
            )

    return ValidationResult(
        submission_path=candidate_path,
        data_dir=resolved_data_dir,
        row_count=len(predictions),
        unique_prediction_count=len(set(predictions)),
        reference_checked=reference_checked,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "submission",
        nargs="?",
        help=(
            "CSV to validate; defaults to TASK2_SUBMISSION_PATH, "
            "task2/submissions/submission.csv, or /kaggle/working/submission.csv"
        ),
    )
    parser.add_argument("--data-dir", help=f"Task 2 data directory (or set {TASK2_DATA_ENV})")
    parser.add_argument("--reference", help="Optional reference CSV that must match predictions")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    submission = args.submission or resolve_submission_output_path()
    try:
        result = validate_submission(
            submission,
            data_dir=args.data_dir,
            reference_path=args.reference,
        )
    except SubmissionValidationError as exc:
        print(f"NOT READY: {exc}")
        return 1

    print(
        "READY: "
        f"{result.row_count} rows, {result.unique_prediction_count} unique predictions, "
        f"reference_checked={result.reference_checked}, file={result.submission_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
