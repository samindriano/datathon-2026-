from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from multifold import windows_at_origins
from run_textres_experiment import acceptance_gate
from text_residual_model import fit_text_residual, load_aligned_texts, text_features


class TextResidualModelTest(unittest.TestCase):
    def test_fixed_event_counts(self):
        text = (
            "a general traffic accident and road closure on alpha. "
            "construction and road traffic control on beta. prohibit left turn."
        )
        features = text_features([text])
        np.testing.assert_array_equal(features[0], [1, 1, 1, 1, 0, 1, 3])

    def test_alignment_loader_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "texts.json"
            path.write_text(json.dumps({"x_2": "event"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_aligned_texts(path, ["x_1"])

    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(220, dtype=np.float32)
        block = np.stack(
            (20 + 0.05 * time, np.zeros_like(time), 35 + np.sin(time / 7)), axis=1
        )
        texts = [
            "road closure. construction." if index % 2 else "an announcement."
            for index in range(len(block))
        ]
        model = fit_text_residual(block, texts, 14, 160, chunk_size=32)
        origins = np.array([170, 180])
        histories, _ = windows_at_origins(block, origins)
        prediction = model.predict(histories, [texts[index] for index in origins])
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
        textres = {
            "mean_mse": 39.0,
            "worst_fold_mse": 44.0,
            "fold_mse": [44.0, 39.0, 34.0],
            "mse_by_horizon": {"5": 34.0, "10": 39.0, "15": 44.0},
        }
        self.assertEqual(acceptance_gate(ridge, textres)["status"], "KEEP")


if __name__ == "__main__":
    unittest.main()
