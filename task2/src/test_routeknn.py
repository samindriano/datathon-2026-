import unittest

import pandas as pd

from routeknn import RouteKNN


class RouteKNNTest(unittest.TestCase):
    def setUp(self):
        self.articles = pd.DataFrame(
            {
                "article_id": [1, 2, 10, 20, 30, 40, 90],
                "title": [
                    "Red Current",
                    "Blue Current",
                    "Mars Goal",
                    "Ocean Goal",
                    "Mars Route",
                    "Ocean Route",
                    "Blue Proxy",
                ],
            }
        )
        self.categories = pd.DataFrame(
            {
                "article_id": [1, 2, 10, 20, 30, 40, 90],
                "category": ["red", "blue", "space", "water", "space", "water", "blue"],
            }
        )

    def test_seen_current_retrieves_route_for_similar_target(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1],
                "target_article_id": [10, 20],
                "next_article_id": [30, 40],
            }
        )
        model = RouteKNN.fit(train, self.articles, self.categories)
        query = pd.DataFrame({"current_article_id": [1], "target_article_id": [20]})
        self.assertEqual(model.predict(query).tolist(), [40])

    def test_unseen_current_uses_metadata_proxy(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 2],
                "target_article_id": [10, 20],
                "next_article_id": [30, 40],
            }
        )
        model = RouteKNN.fit(train, self.articles, self.categories)
        query = pd.DataFrame({"current_article_id": [90], "target_article_id": [20]})
        self.assertEqual(model.predict(query).tolist(), [40])

    def test_tie_break_is_frequency_then_smallest_article_id(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 1],
                "target_article_id": [10, 10, 10],
                "next_article_id": [30, 40, 40],
            }
        )
        model = RouteKNN.fit(train, self.articles, self.categories)
        query = pd.DataFrame({"current_article_id": [1], "target_article_id": [10]})
        self.assertEqual(model.predict(query).tolist(), [40])

    def test_state_id_is_ignored(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1],
                "target_article_id": [10],
                "next_article_id": [30],
            }
        )
        model = RouteKNN.fit(train, self.articles, self.categories)
        first = pd.DataFrame(
            {"state_id": [1], "current_article_id": [1], "target_article_id": [10]}
        )
        second = first.assign(state_id=999)
        self.assertEqual(model.predict(first).tolist(), model.predict(second).tolist())


if __name__ == "__main__":
    unittest.main()
