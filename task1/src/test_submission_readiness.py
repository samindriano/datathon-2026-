from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from clean_notebook_runner import execute_notebook
from submission_validator import SubmissionValidationError, validate_submission


class SubmissionValidatorTest(unittest.TestCase):
    def _frames(self):
        ids = [
            f"test_{sample:05d}_h{horizon}_r{road}"
            for sample in range(2)
            for horizon in (5, 10, 15)
            for road in range(2)
        ]
        template = pd.DataFrame({"id": ids, "speed": 0.0})
        submission = pd.DataFrame({"id": ids, "speed": range(len(ids))})
        return template, submission

    def test_valid_submission_and_reference_match(self):
        template, submission = self._frames()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template_path = root / "sample.csv"
            submission_path = root / "submission.csv"
            template.to_csv(template_path, index=False)
            submission.to_csv(submission_path, index=False)
            report = validate_submission(
                template_path,
                submission_path,
                sample_count=2,
                road_count=2,
                chunk_size=5,
                reference_path=submission_path,
            )
        self.assertEqual(report["status"], "READY")
        self.assertTrue(report["reference_exact_numeric_match"])

    def test_reordered_id_is_rejected(self):
        template, submission = self._frames()
        submission.loc[[0, 1], "id"] = submission.loc[[1, 0], "id"].to_numpy()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template_path = root / "sample.csv"
            submission_path = root / "submission.csv"
            template.to_csv(template_path, index=False)
            submission.to_csv(submission_path, index=False)
            with self.assertRaises(SubmissionValidationError):
                validate_submission(
                    template_path,
                    submission_path,
                    sample_count=2,
                    road_count=2,
                    chunk_size=5,
                )

    def test_reference_mismatch_is_rejected(self):
        template, submission = self._frames()
        different = submission.copy()
        different["speed"] = different["speed"] + 1
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template_path = root / "sample.csv"
            submission_path = root / "submission.csv"
            reference_path = root / "reference.csv"
            template.to_csv(template_path, index=False)
            submission.to_csv(submission_path, index=False)
            different.to_csv(reference_path, index=False)
            with self.assertRaisesRegex(
                SubmissionValidationError, "differs from the requested reference"
            ):
                validate_submission(
                    template_path,
                    submission_path,
                    sample_count=2,
                    road_count=2,
                    chunk_size=5,
                    reference_path=reference_path,
                )
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("submission_validator.py")),
                    "--template",
                    str(template_path),
                    "--submission",
                    str(submission_path),
                    "--reference",
                    str(reference_path),
                    "--sample-count",
                    "2",
                    "--road-count",
                    "2",
                    "--chunk-size",
                    "5",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("differs from the requested reference", result.stderr)


class CleanNotebookRunnerTest(unittest.TestCase):
    def test_executes_code_cells_in_order(self):
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {"cell_type": "code", "metadata": {}, "source": ["value = 40\n"]},
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": ["Path(output).write_text(str(value + 2))\n"],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "test.ipynb"
            output = root / "result.txt"
            notebook["cells"][0]["source"].insert(0, "from pathlib import Path\n")
            notebook["cells"][0]["source"].append(f"output = {str(output)!r}\n")
            path.write_text(json.dumps(notebook), encoding="utf-8")
            execute_notebook(path)
            self.assertEqual(output.read_text(), "42")


if __name__ == "__main__":
    unittest.main()
