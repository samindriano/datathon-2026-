from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from ar15_model import fit_road_ar15, history_features
from multifold import windows_at_origins
from run_ar15_experiment import acceptance_gate


class AR15ModelTest(unittest.TestCase):
    def test_features_preserve_all_lags_per_road(self):
        history = np.arange(2 * 15 * 3, dtype=np.float32).reshape(2, 15, 3)
        features = history_features(history)
        self.assertEqual(features.shape, (2, 3, 15))
        np.testing.assert_array_equal(features[0, 2], history[0, :, 2])

    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(220, dtype=np.float32)
        block = np.stack(
            (20 + 0.05 * time, np.zeros_like(time), 35 + np.sin(time / 7)), axis=1
        )
        model = fit_road_ar15(block, 14, 160, alpha=0.1, chunk_size=32)
        histories, _ = windows_at_origins(block, np.array([170, 180]))
        prediction = model.predict(histories)
        self.assertEqual(prediction.shape, (2, 3, 3))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertTrue((prediction[:, :, 1] == 0).all())
        self.assertTrue((prediction >= 0).all())

    def test_acceptance_gate_requires_broad_improvement(self):
        ridge = {
            "mean_mse": 40.0,
            "worst_fold_mse": 45.0,
            "fold_mse": [45.0, 40.0, 35.0],
            "mse_by_horizon": {"5": 35.0, "10": 40.0, "15": 45.0},
        }
        ar15 = {
            "mean_mse": 39.0,
            "worst_fold_mse": 44.0,
            "fold_mse": [44.0, 39.0, 34.0],
            "mse_by_horizon": {"5": 34.0, "10": 39.0, "15": 44.0},
        }
        self.assertEqual(acceptance_gate(ridge, ar15)["status"], "KEEP")


if __name__ == "__main__":
    unittest.main()
