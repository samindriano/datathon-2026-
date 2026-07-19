import unittest

import pandas as pd

from baseline import CurrentModeBaseline


class BaselineTest(unittest.TestCase):
    def test_current_mode_and_global_fallback_are_deterministic(self):
        train = pd.DataFrame(
            {
                "current_article_id": [1, 1, 1, 2, 2],
                "next_article_id": [7, 8, 7, 9, 8],
            }
        )
        model = CurrentModeBaseline.fit(train)
        states = pd.DataFrame({"current_article_id": [1, 2, 999]})
        self.assertEqual(model.predict(states).tolist(), [7, 8, 7])


if __name__ == "__main__":
    unittest.main()
