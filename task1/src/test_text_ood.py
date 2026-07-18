from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from multifold import windows_at_origins
from text_ood_model import fit_text_ood, guarded_standardized_features


class TextOODModelTest(unittest.TestCase):
    def test_only_out_of_range_guarded_feature_is_neutralized(self):
        raw = np.array([[1.0, -1.0], [2.0, 3.0], [4.0, 1.0]])
        standardized, mask = guarded_standardized_features(
            raw,
            feature_mean=np.array([2.0, 1.0]),
            feature_scale=np.array([1.0, 2.0]),
            guard_index=0,
            training_minimum=1.0,
            training_maximum=3.0,
        )
        np.testing.assert_array_equal(mask, [False, False, True])
        self.assertEqual(float(standardized[2, 0]), 0.0)
        self.assertEqual(float(standardized[2, 1]), 0.0)
        self.assertEqual(float(standardized[0, 0]), -1.0)

    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(220, dtype=np.float32)
        block = np.stack(
            (20 + 0.05 * time, np.zeros_like(time), 35 + np.sin(time / 7)), axis=1
        )
        texts = [
            "prohibit left turn. road closure." if index % 4 else "construction."
            for index in range(len(block))
        ]
        model = fit_text_ood(block, texts, 14, 160, chunk_size=32)
        origins = np.array([170, 180])
        histories, _ = windows_at_origins(block, origins)
        prediction = model.predict(histories, [texts[index] for index in origins])
        self.assertEqual(prediction.shape, (2, 3, 3))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertTrue((prediction[:, :, 1] == 0).all())
        self.assertTrue((prediction >= 0).all())


if __name__ == "__main__":
    unittest.main()
