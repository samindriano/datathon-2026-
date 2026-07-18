from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from analog_model import fit_analog, state_features
from multifold import windows_at_origins
from run_analog_experiment import acceptance_gate


class AnalogModelTest(unittest.TestCase):
    def test_features_have_three_groups_for_selected_roads(self):
        history = np.arange(2 * 15 * 5, dtype=np.float32).reshape(2, 15, 5)
        result = state_features(history, np.array([1, 4]))
        self.assertEqual(result.shape, (2, 6))

    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(240, dtype=np.float32)
        block = np.stack(
            (
                20 + 0.05 * time,
                np.zeros_like(time),
                35 + np.sin(time / 7),
                42 + np.cos(time / 11),
            ),
            axis=1,
        )
        model = fit_analog(
            block,
            14,
            170,
            selected_road_count=2,
            neighbor_count=4,
            fit_chunk_size=32,
            query_chunk_size=2,
        )
        self.assertEqual(int(model.candidate_origins.min()), 14)
        self.assertEqual(int(model.candidate_origins.max()), 170)
        histories, _ = windows_at_origins(block, np.array([180, 190]))
        prediction = model.predict(histories)
        self.assertEqual(prediction.shape, (2, 3, 4))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertTrue((prediction[:, :, 1] == 0).all())
        self.assertTrue((prediction >= 0).all())

    def test_acceptance_gate_rejects_single_fold_improvement(self):
        ridge = {
            "mean_mse": 40.0,
            "worst_fold_mse": 45.0,
            "fold_mse": [45.0, 40.0, 35.0],
            "mse_by_horizon": {"5": 35.0, "10": 40.0, "15": 45.0},
        }
        analog = {
            "mean_mse": 39.0,
            "worst_fold_mse": 45.1,
            "fold_mse": [45.1, 40.1, 31.8],
            "mse_by_horizon": {"5": 34.0, "10": 39.0, "15": 44.0},
        }
        self.assertEqual(acceptance_gate(ridge, analog)["status"], "REJECT")


if __name__ == "__main__":
    unittest.main()
