from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


MODULE_PATH = Path(__file__).with_name("baseline.py")
SPEC = importlib.util.spec_from_file_location("task1_baseline", MODULE_PATH)
baseline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(baseline)


class BaselineTest(unittest.TestCase):
    def test_persistence_shape_and_values(self):
        history = np.arange(2 * 15 * 3, dtype=np.float32).reshape(2, 15, 3)
        result = baseline.predict(history, "persist")
        self.assertEqual(result.shape, (2, 3, 3))
        np.testing.assert_allclose(result[:, 0], history[:, -1])
        np.testing.assert_allclose(result[:, 2], history[:, -1])

    def test_validation_windows_do_not_cross_future(self):
        block = np.arange(100, dtype=np.float32)[:, None]
        histories, targets = baseline.validation_windows(block, count=2)
        self.assertEqual(histories.shape, (2, 15, 1))
        self.assertEqual(targets.shape, (2, 3, 1))
        np.testing.assert_array_equal(targets[-1, :, 0], [89, 94, 99])
        self.assertEqual(histories[-1, -1, 0], 84)

    def test_submission_order_is_enforced(self):
        predictions = np.ones((2, 3, 2), dtype=np.float32)
        ids = [
            f"test_{sample:05d}_h{horizon}_r{road}"
            for sample in range(2)
            for horizon in baseline.HORIZONS
            for road in range(2)
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template = root / "sample.csv"
            output = root / "submission.csv"
            pd.DataFrame({"id": ids, "speed": 0.0}).to_csv(template, index=False)
            baseline.write_submission(template, predictions, output)
            result = pd.read_csv(output)
        self.assertEqual(result["id"].tolist(), ids)
        self.assertTrue((result["speed"] == 1.0).all())


if __name__ == "__main__":
    unittest.main()
