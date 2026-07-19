import unittest
import pandas as pd
from routeproto import RouteProtoRanker


class RouteProtoRankerTest(unittest.TestCase):
    def setUp(self):
        self.articles = pd.DataFrame({"article_id": [10, 20, 30], "title": ["Red Planet", "Blue Ocean", "Ocean Goal"]})

    def test_semantic_route_choice(self):
        train = pd.DataFrame({"current_article_id": [1, 1, 1], "target_article_id": [30, 30, 10], "next_article_id": [10, 10, 20]})
        model = RouteProtoRanker.fit(train, self.articles)
        self.assertEqual(model.predict(pd.DataFrame({"current_article_id": [1], "target_article_id": [30]})).tolist(), [10])

    def test_unseen_current_global_mode(self):
        train = pd.DataFrame({"current_article_id": [1, 1, 2], "target_article_id": [30, 30, 10], "next_article_id": [10, 10, 20]})
        model = RouteProtoRanker.fit(train, self.articles)
        self.assertEqual(model.predict(pd.DataFrame({"current_article_id": [999], "target_article_id": [30]})).tolist(), [10])

    def test_state_and_label_columns_do_not_change_predictions(self):
        train = pd.DataFrame({"current_article_id": [1, 1], "target_article_id": [30, 10], "next_article_id": [10, 20], "state_id": [1, 2]})
        model = RouteProtoRanker.fit(train, self.articles)
        states = pd.DataFrame({"current_article_id": [1], "target_article_id": [30], "state_id": [7], "next_article_id": [20]})
        changed = states.assign(state_id=-1, next_article_id=-999)
        self.assertEqual(model.predict(states).tolist(), model.predict(changed).tolist())


if __name__ == "__main__":
    unittest.main()
