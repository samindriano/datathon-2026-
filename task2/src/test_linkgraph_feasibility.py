from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from run_fastlink_feasibility import blue_mask, component_crops
from run_linkgraph_feasibility import TitleMapper, normalize_title, sample_current_ids


class LinkGraphFeasibilityTests(unittest.TestCase):
    def test_normalize_title_is_deterministic(self) -> None:
        self.assertEqual(
            normalize_title("Beyoncé & Jay-Z (duo)"),
            "beyonce and jay z duo",
        )

    def test_sample_current_ids_is_unique_and_order_independent(self) -> None:
        frame = pd.DataFrame({"current_article_id": list(range(150)) + [17, 19]})
        reversed_frame = frame.iloc[::-1].reset_index(drop=True)
        first = sample_current_ids(frame)
        second = sample_current_ids(reversed_frame)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 100)
        self.assertEqual(len(set(first)), 100)

    def test_exact_title_and_unique_parenthetical_alias_mapping(self) -> None:
        articles = pd.DataFrame(
            {
                "article_id": [1, 2, 3],
                "title": ["United Nations", "Mercury (planet)", "Mercury (element)"],
            }
        )
        mapper = TitleMapper(articles)
        self.assertEqual(mapper.map("United Nations", 0.99)["article_id"], 1)
        self.assertIsNone(mapper.map("Mercury", 0.99))

    def test_blue_component_extraction_ignores_black_text(self) -> None:
        image = np.full((40, 120, 3), 255, dtype=np.uint8)
        image[10:18, 10:45] = np.array([11, 0, 238], dtype=np.uint8)
        image[25:33, 60:100] = np.array([0, 0, 0], dtype=np.uint8)
        self.assertEqual(int(blue_mask(image).sum()), 8 * 35)
        crops, blue_pixels = component_crops(image)
        self.assertEqual(blue_pixels, 8 * 35)
        self.assertEqual(len(crops), 1)


if __name__ == "__main__":
    unittest.main()
