from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).parent))

from graph_model import build_neighbor_edges, fit_graph_ridge, graph_history_features
from multifold import windows_at_origins
from run_graphres_experiment import acceptance_gate


class GraphModelTest(unittest.TestCase):
    def test_edges_are_symmetric_external_and_row_normalized(self):
        adjacency = np.eye(3, dtype=np.int8)
        adjacency[0, 1] = 1
        adjacency[1, 2] = 1
        rows, columns, weights = build_neighbor_edges(adjacency)
        self.assertEqual(set(zip(rows.tolist(), columns.tolist())), {(0, 1), (1, 0), (1, 2), (2, 1)})
        for road in range(3):
            self.assertAlmostEqual(float(weights[rows == road].sum()), 1.0)

    def test_neighbor_features_use_connected_road_mean(self):
        history = np.zeros((1, 15, 3), dtype=np.float32)
        history[:, :, 0] = 10
        history[:, :, 1] = 20
        history[:, :, 2] = 40
        adjacency = np.eye(3, dtype=np.int8)
        adjacency[0, 1] = 1
        adjacency[1, 2] = 1
        rows, columns, weights = build_neighbor_edges(adjacency)
        features = graph_history_features(history, rows, columns, weights)
        self.assertEqual(features.shape, (1, 3, 10))
        self.assertAlmostEqual(float(features[0, 0, 5]), 20.0)
        self.assertAlmostEqual(float(features[0, 1, 5]), 25.0)

    def test_model_is_finite_and_preserves_zero_history(self):
        time = np.arange(220, dtype=np.float32)
        block = np.stack(
            (20 + 0.05 * time, np.zeros_like(time), 35 + np.sin(time / 7)), axis=1
        )
        adjacency = np.eye(3, dtype=np.int8)
        adjacency[0, 1] = adjacency[1, 2] = 1
        model = fit_graph_ridge(block, adjacency, 14, 160, chunk_size=32)
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
        graphres = {
            "mean_mse": 39.0,
            "worst_fold_mse": 44.0,
            "fold_mse": [44.0, 39.0, 34.0],
            "mse_by_horizon": {"5": 34.0, "10": 39.0, "15": 44.0},
        }
        self.assertEqual(acceptance_gate(ridge, graphres)["status"], "KEEP")


if __name__ == "__main__":
    unittest.main()
