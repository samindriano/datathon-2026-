from __future__ import annotations

import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from submission_validator import (  # noqa: E402
    EXPECTED_ROW_COUNT,
    SubmissionValidationError,
    resolve_submission_output_path,
    resolve_task2_data_dir,
    validate_submission,
)


class SubmissionValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "dataset-task2"
        self.data_dir.mkdir()

        self.state_ids = [str(index * 2) for index in range(EXPECTED_ROW_COUNT)]
        self.predictions = [str(index % 17) for index in range(EXPECTED_ROW_COUNT)]
        self._write_csv(
            self.data_dir / "states_test.csv",
            ["state_id", "current_article_id", "target_article_id"],
            [[state_id, str(index % 17), str((index + 1) % 17)]
             for index, state_id in enumerate(self.state_ids)],
        )
        self._write_csv(
            self.data_dir / "sample_submission.csv",
            ["state_id", "predicted_next_article_id"],
            zip(self.state_ids, self.predictions),
        )
        self._write_csv(
            self.data_dir / "articles.csv",
            ["article_id", "title"],
            [[str(index), f"Article {index}"] for index in range(17)],
        )
        self.valid_path = self.root / "submission.csv"
        self._write_submission(self.valid_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _write_csv(path: Path, header: list[str], rows) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows(rows)

    def _write_submission(
        self,
        path: Path,
        *,
        header: list[str] | None = None,
        state_ids: list[str] | None = None,
        predictions: list[str] | None = None,
    ) -> None:
        self._write_csv(
            path,
            header or ["state_id", "predicted_next_article_id"],
            zip(state_ids or self.state_ids, predictions or self.predictions),
        )

    def assert_rejected(self, path: Path) -> None:
        with self.assertRaises(SubmissionValidationError):
            validate_submission(path, data_dir=self.data_dir)

    def test_accepts_valid_submission_with_exact_contract(self) -> None:
        result = validate_submission(self.valid_path, data_dir=self.data_dir)
        self.assertEqual(result.row_count, EXPECTED_ROW_COUNT)
        self.assertFalse(result.reference_checked)

    def test_rejects_wrong_column_name_or_order(self) -> None:
        cases = (
            ["state_id", "prediction"],
            ["predicted_next_article_id", "state_id"],
        )
        for index, header in enumerate(cases):
            with self.subTest(header=header):
                path = self.root / f"bad-columns-{index}.csv"
                self._write_submission(path, header=header)
                self.assert_rejected(path)

    def test_rejects_row_count_other_than_6000(self) -> None:
        for suffix, state_ids, predictions in (
            ("missing", self.state_ids[:-1], self.predictions[:-1]),
            ("extra", self.state_ids + ["20000"], self.predictions + ["1"]),
        ):
            with self.subTest(case=suffix):
                path = self.root / f"bad-row-count-{suffix}.csv"
                self._write_submission(path, state_ids=state_ids, predictions=predictions)
                self.assert_rejected(path)

    def test_rejects_missing_or_extra_state_id_with_same_row_count(self) -> None:
        changed = self.state_ids.copy()
        changed[-1] = "20001"
        path = self.root / "state-set-mismatch.csv"
        self._write_submission(path, state_ids=changed)
        self.assert_rejected(path)

    def test_rejects_duplicate_state_id(self) -> None:
        changed = self.state_ids.copy()
        changed[-1] = changed[0]
        path = self.root / "duplicate-state.csv"
        self._write_submission(path, state_ids=changed)
        self.assert_rejected(path)

    def test_rejects_changed_state_order(self) -> None:
        changed = self.state_ids.copy()
        changed[0], changed[1] = changed[1], changed[0]
        path = self.root / "reordered-state.csv"
        self._write_submission(path, state_ids=changed)
        self.assert_rejected(path)

    def test_rejects_empty_nan_or_infinite_prediction(self) -> None:
        for index, invalid in enumerate(("", "NaN", "inf", "-Infinity")):
            with self.subTest(value=invalid):
                changed = self.predictions.copy()
                changed[37] = invalid
                path = self.root / f"invalid-prediction-{index}.csv"
                self._write_submission(path, predictions=changed)
                self.assert_rejected(path)

    def test_rejects_non_integer_prediction(self) -> None:
        changed = self.predictions.copy()
        changed[19] = "1.5"
        path = self.root / "non-integer.csv"
        self._write_submission(path, predictions=changed)
        self.assert_rejected(path)

    def test_rejects_prediction_outside_article_universe(self) -> None:
        changed = self.predictions.copy()
        changed[23] = "17"
        path = self.root / "unknown-article.csv"
        self._write_submission(path, predictions=changed)
        self.assert_rejected(path)

    def test_reference_must_match_when_provided(self) -> None:
        matching = self.root / "matching-reference.csv"
        self._write_submission(matching)
        result = validate_submission(
            self.valid_path,
            data_dir=self.data_dir,
            reference_path=matching,
        )
        self.assertTrue(result.reference_checked)

        changed = self.predictions.copy()
        changed[11] = "16" if changed[11] != "16" else "15"
        mismatching = self.root / "mismatching-reference.csv"
        self._write_submission(mismatching, predictions=changed)
        with self.assertRaises(SubmissionValidationError):
            validate_submission(
                self.valid_path,
                data_dir=self.data_dir,
                reference_path=mismatching,
            )

    def test_resolves_explicit_environment_and_repository_data_paths(self) -> None:
        self.assertEqual(resolve_task2_data_dir(self.data_dir), self.data_dir.resolve())
        self.assertEqual(
            resolve_task2_data_dir(environ={"TASK2_DATA_DIR": str(self.data_dir)}),
            self.data_dir.resolve(),
        )

        repo = self.root / "repo"
        local_data = repo / "task2" / "data" / "competition" / "dataset-task2"
        shutil.copytree(self.data_dir, local_data)
        self.assertEqual(
            resolve_task2_data_dir(environ={}, repo_root=repo, kaggle_input=self.root / "absent"),
            local_data.resolve(),
        )

    def test_resolves_kaggle_data_and_output_contracts(self) -> None:
        kaggle_input = self.root / "kaggle" / "input"
        kaggle_dataset = kaggle_input / "task2-data"
        shutil.copytree(self.data_dir, kaggle_dataset)
        self.assertEqual(
            resolve_task2_data_dir(
                environ={}, repo_root=self.root / "no-repo", kaggle_input=kaggle_input
            ),
            kaggle_dataset.resolve(),
        )

        override = self.root / "custom.csv"
        self.assertEqual(
            resolve_submission_output_path(environ={"TASK2_SUBMISSION_PATH": str(override)}),
            override,
        )
        kaggle_working = self.root / "kaggle" / "working"
        kaggle_working.mkdir()
        self.assertEqual(
            resolve_submission_output_path(
                environ={}, repo_root=self.root / "repo", kaggle_working=kaggle_working
            ),
            kaggle_working / "submission.csv",
        )
        self.assertEqual(
            resolve_submission_output_path(
                environ={}, repo_root=self.root / "repo", kaggle_working=self.root / "absent"
            ),
            self.root / "repo" / "task2" / "submissions" / "submission.csv",
        )


if __name__ == "__main__":
    unittest.main()
