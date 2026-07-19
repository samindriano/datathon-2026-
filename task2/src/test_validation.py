import unittest

import pandas as pd

from validation import accuracy, make_target_group_folds


class ValidationTest(unittest.TestCase):
    def test_target_groups_never_cross_folds(self):
        states = pd.DataFrame(
            {"target_article_id": [10, 10, 20, 20, 30, 30, 40, 40]}
        )
        categories = pd.DataFrame(
            {
                "article_id": [10, 20, 30, 40],
                "category": [
                    "subject.A.a",
                    "subject.A.b",
                    "subject.B.a",
                    "subject.B.b",
                ],
            }
        )
        folds = make_target_group_folds(states, categories, fold_count=2, seed=1)
        for target in states["target_article_id"].unique():
            self.assertEqual(
                len(set(folds[states["target_article_id"] == target])), 1
            )

    def test_accuracy_is_exact_match(self):
        self.assertEqual(accuracy([1, 2, 3], [1, 0, 3]), 2 / 3)


if __name__ == "__main__":
    unittest.main()
