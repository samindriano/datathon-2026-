import json
import unittest
from pathlib import Path

import pandas as pd

from prelink import PrelinkRanker


class PrelinkRankerTest(unittest.TestCase):
    def setUp(self):
        self.articles = pd.DataFrame(
            {
                "article_id": [10, 20, 30, 40],
                "title": ["Common", "Ocean", "Ocean goal", "Fallback"],
            }
        )
        self.categories = pd.DataFrame(
            {
                "article_id": [10, 20, 30, 40],
                "category": ["other", "water", "water", "other"],
            }
        )
        self.train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 2, 2, 2],
                "next_article_id": [10, 10, 40, 40, 40],
            }
        )

    def test_screenshot_candidates_override_e002_candidate_set(self):
        model = PrelinkRanker.fit(
            self.train, self.articles, self.categories, {1: [10, 20]}
        )
        states = pd.DataFrame(
            {"current_article_id": [1], "target_article_id": [30]}
        )
        prediction, used = model.predict_with_diagnostics(states)
        self.assertEqual(prediction.tolist(), [20])
        self.assertEqual(used.tolist(), [True])

    def test_empty_or_missing_links_use_e002_fallback(self):
        model = PrelinkRanker.fit(
            self.train, self.articles, self.categories, {1: [], 999: [9999]}
        )
        states = pd.DataFrame(
            {
                "current_article_id": [1, 999],
                "target_article_id": [30, 30],
            }
        )
        prediction, used = model.predict_with_diagnostics(states)
        self.assertEqual(prediction.tolist(), [10, 40])
        self.assertEqual(used.tolist(), [False, False])


class PrelinkNotebookTest(unittest.TestCase):
    def test_local_notebook_is_clean_and_has_no_user_path(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "notebooks"
            / "d2-e014-prelink-local.ipynb"
        )
        raw = path.read_text(encoding="utf-8")
        notebook = json.loads(raw)
        self.assertNotIn("C:\\Users\\", raw)
        for cell in notebook["cells"]:
            if cell.get("cell_type") != "code":
                continue
            self.assertIsNone(cell.get("execution_count"))
            self.assertEqual(cell.get("outputs", []), [])


if __name__ == "__main__":
    unittest.main()
