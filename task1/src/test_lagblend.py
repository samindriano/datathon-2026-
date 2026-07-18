from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from lagblend_model import fit_lagblend, project_simplex
from multifold import windows_at_origins
from run_lagblend_experiment import acceptance_gate


class LagBlendModelTest(unittest.TestCase):
    def test_simplex_projection_is_nonnegative_and_sums_to_one(self):
        result = project_simplex(np.array([-2.0, 0.2, 0.8, 3.0]))
        self.assertTrue((result >= 0).all())
        self.assertAlmostEqual(float(result.sum()), 1.0)

    def test_model_is_convex_finite_and_preserves_zero_history(self):
        time = np.arange(220, dtype=np.float32)
        block = np.stack(
            (20 + 0.05 * time, np.zeros_like(time), 35 + np.sin(time / 7)), axis=1
        )
        model = fit_lagblend(block, 14, 160, chunk_size=32)
        np.testing.assert_allclose(model.weights.sum(axis=1), 1.0, atol=1e-9)
        self.assertTrue((model.weights >= 0).all())
        histories, _ = windows_at_origins(block, np.array([170, 180]))
        prediction = model.predict(histories)
        self.assertEqual(prediction.shape, (2, 3, 3))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertTrue((prediction[:, :, 1] == 0).all())
        lower = histories.min(axis=1)[:, None, :]
        upper = histories.max(axis=1)[:, None, :]
        self.assertTrue((prediction >= lower - 1e-5).all())
        self.assertTrue((prediction <= upper + 1e-5).all())

    def test_acceptance_gate_requires_mean_fold_horizon_and_worst_fold(self):
        ridge = {
            "mean_mse": 40.0,
            "worst_fold_mse": 45.0,
            "fold_mse": [45.0, 40.0, 35.0],
            "mse_by_horizon": {"5": 35.0, "10": 40.0, "15": 45.0},
        }
        accepted = {
            "mean_mse": 39.0,
            "worst_fold_mse": 44.0,
            "fold_mse": [44.0, 39.0, 34.0],
            "mse_by_horizon": {"5": 34.0, "10": 39.0, "15": 44.0},
        }
        rejected = {**accepted, "fold_mse": [44.0, 41.0, 36.0]}
        self.assertEqual(acceptance_gate(ridge, accepted)["status"], "KEEP")
        self.assertEqual(acceptance_gate(ridge, rejected)["status"], "REJECT")


if __name__ == "__main__":
    unittest.main()
