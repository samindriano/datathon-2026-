import numpy as np
import pandas as pd

from catroute import CatRoute


def test_category_posterior_and_label_invariance():
    states = pd.DataFrame({
        "current_article_id": [1, 1, 1, 1, 2],
        "target_article_id": [10, 10, 11, 11, 10],
        "next_article_id": [20, 20, 21, 21, 22],
        "state_id": [1, 2, 3, 4, 5],
    })
    categories = pd.DataFrame({"article_id": [10, 11], "category": ["subject.news", "subject.sport"]})
    model = CatRoute.fit(states, categories)
    query = states.iloc[[0, 2]].copy()
    pred = model.predict(query)
    query["next_article_id"] = -1
    assert np.array_equal(pred, model.predict(query))
    assert pred.tolist() == [20, 21]


def test_unseen_current_uses_global_mode():
    states = pd.DataFrame({"current_article_id": [1, 1], "target_article_id": [10, 10], "next_article_id": [20, 20]})
    categories = pd.DataFrame({"article_id": [10], "category": ["subject.news"]})
    model = CatRoute.fit(states, categories)
    query = pd.DataFrame({"current_article_id": [999], "target_article_id": [10]})
    assert model.predict(query).tolist() == [20]
