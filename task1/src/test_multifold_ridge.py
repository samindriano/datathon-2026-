from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from multifold import HORIZONS, build_folds, summarize_fold_scores, windows_at_origins
from ridge_model import classify_test_regime, fit_road_ridge


class MultifoldTest(unittest.TestCase):
    def test_folds_are_purged_and_end_within_block(self):
        folds = build_folds(5039, block_index=2)
        self.assertEqual(len(folds), 3)
        for fold in folds:
            self.assertLess(fold.train_origin_end + int(HORIZONS.max()), fold.validation_origin_start)
            self.assertLessEqual(fold.validation_origin_end + int(HORIZONS.max()), 5038)

    def test_regime_weighting(self):
        m1 = np.full((3, 3), 10.0)
        m2 = np.full((3, 3), 20.0)
        result = summarize_fold_scores([m1, m2])
        expected = (372 * 10.0 + 168 * 20.0) / 540
        self.assertAlmostEqual(result["mean_mse"], expected)


class RidgeModelTest(unittest.TestCase):
    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(180, dtype=np.float32)
        block = np.stack((20 + 0.1 * time, np.zeros_like(time), 30 + np.sin(time / 8)), axis=1)
        model = fit_road_ridge(block, 14, 120, alpha=0.1, chunk_size=32)
        histories, _ = windows_at_origins(block, np.array([121, 130]))
        prediction = model.predict(histories)
        self.assertEqual(prediction.shape, (2, 3, 3))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertTrue((prediction[:, :, 1] == 0).all())

    def test_regime_routing_uses_structural_zero_count(self):
        history = np.ones((2, 15, 1260), dtype=np.float32)
        history[0, :, :13] = 0
        history[1, :, :210] = 0
        np.testing.assert_array_equal(classify_test_regime(history), [0, 1])


if __name__ == "__main__":
    unittest.main()
