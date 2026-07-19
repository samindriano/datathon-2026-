import unittest

import pandas as pd

from metarank import MetaRanker, jaccard, title_tokens


class MetaRankerTest(unittest.TestCase):
    def setUp(self):
        self.articles = pd.DataFrame(
            {
                "article_id": [10, 20, 30, 40],
                "title": ["Red Planet", "Blue Ocean", "Ocean Goal", "Other"],
            }
        )
        self.categories = pd.DataFrame(
            {
                "article_id": [10, 20, 30, 40],
                "category": ["space", "water", "water", "other"],
            }
        )

    def test_title_tokens_and_jaccard_are_deterministic(self):
        self.assertEqual(title_tokens("Blue-Ocean (2026)"), {"blue", "ocean", "2026"})
        self.assertEqual(jaccard(frozenset({"a", "b"}), frozenset({"b", "c"})), 1 / 3)
        self.assertEqual(jaccard(frozenset(), frozenset()), 0.0)

    def test_target_metadata_changes_candidate_choice(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 1],
                "next_article_id": [10, 10, 20],
            }
        )
        model = MetaRanker.fit(train, self.articles, self.categories)
        states = pd.DataFrame(
            {"current_article_id": [1], "target_article_id": [30]}
        )
        self.assertEqual(model.predict(states).tolist(), [20])

    def test_unseen_current_uses_deterministic_global_mode(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 2],
                "next_article_id": [10, 10, 20],
            }
        )
        model = MetaRanker.fit(train, self.articles, self.categories)
        states = pd.DataFrame(
            {"current_article_id": [999], "target_article_id": [30]}
        )
        self.assertEqual(model.predict(states).tolist(), [10])

    def test_exact_tie_prefers_current_frequency_then_smallest_id(self):
        articles = pd.DataFrame(
            {"article_id": [10, 20, 30], "title": ["A", "B", "Goal"]}
        )
        categories = pd.DataFrame(
            {"article_id": [10, 20, 30], "category": ["x", "x", "y"]}
        )
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 1, 2],
                "next_article_id": [10, 20, 20, 10],
            }
        )
        model = MetaRanker.fit(train, articles, categories)
        states = pd.DataFrame(
            {"current_article_id": [1], "target_article_id": [30]}
        )
        self.assertEqual(model.predict(states).tolist(), [20])


if __name__ == "__main__":
    unittest.main()
