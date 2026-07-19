"""Deterministic one-nearest-route model for Task 2."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd

from baseline import deterministic_mode
from metarank import jaccard, title_tokens


@dataclass(frozen=True)
class RouteKNN:
    """Retrieve one fold-local route using official article metadata."""

    global_next_article_id: int
    routes_by_current: dict[int, tuple[tuple[int, int], ...]]
    current_counts: Counter[int]
    next_counts_by_current: dict[int, Counter[int]]
    global_next_counts: Counter[int]
    title_tokens_by_article: dict[int, frozenset[str]]
    categories_by_article: dict[int, frozenset[str]]

    @classmethod
    def fit(
        cls,
        states: pd.DataFrame,
        articles: pd.DataFrame,
        categories: pd.DataFrame,
    ) -> "RouteKNN":
        required = {"current_article_id", "target_article_id", "next_article_id"}
        if not required.issubset(states.columns) or states.empty:
            raise ValueError("states must contain non-empty current, target, and next columns")
        if articles.columns.tolist() != ["article_id", "title"]:
            raise ValueError("articles must have exact columns article_id,title")
        if categories.columns.tolist() != ["article_id", "category"]:
            raise ValueError("categories must have exact columns article_id,category")

        article_tokens = {
            int(row.article_id): title_tokens(row.title)
            for row in articles.itertuples(index=False)
        }
        category_sets = {
            int(article_id): frozenset(group["category"].astype(str))
            for article_id, group in categories.groupby("article_id", sort=True)
        }
        routes = {
            int(current): tuple(
                (int(target), int(next_article))
                for target, next_article in zip(
                    group["target_article_id"], group["next_article_id"], strict=True
                )
            )
            for current, group in states.groupby("current_article_id", sort=True)
        }
        next_counts = {
            int(current): Counter(group["next_article_id"].astype(np.int64))
            for current, group in states.groupby("current_article_id", sort=True)
        }
        return cls(
            global_next_article_id=deterministic_mode(states["next_article_id"]),
            routes_by_current=routes,
            current_counts=Counter(states["current_article_id"].astype(np.int64)),
            next_counts_by_current=next_counts,
            global_next_counts=Counter(states["next_article_id"].astype(np.int64)),
            title_tokens_by_article=article_tokens,
            categories_by_article=category_sets,
        )

    def _metadata_score(self, left: int, right: int) -> float:
        return 2.0 * jaccard(
            self.categories_by_article.get(left, frozenset()),
            self.categories_by_article.get(right, frozenset()),
        ) + jaccard(
            self.title_tokens_by_article.get(left, frozenset()),
            self.title_tokens_by_article.get(right, frozenset()),
        )

    def _proxy_current(self, current: int) -> int | None:
        if current in self.routes_by_current:
            return current
        if not self.routes_by_current:
            return None
        return max(
            self.routes_by_current,
            key=lambda candidate: (
                self._metadata_score(int(candidate), current),
                self.current_counts[int(candidate)],
                -int(candidate),
            ),
        )

    def _predict_one(self, current: int, target: int) -> int:
        proxy_current = self._proxy_current(current)
        if proxy_current is None:
            return self.global_next_article_id
        routes = self.routes_by_current[proxy_current]
        next_counts = self.next_counts_by_current[proxy_current]
        _, prediction = max(
            routes,
            key=lambda route: (
                self._metadata_score(route[0], target),
                next_counts[route[1]],
                self.global_next_counts[route[1]],
                -route[1],
            ),
        )
        return int(prediction)

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        required = {"current_article_id", "target_article_id"}
        if not required.issubset(states.columns):
            raise ValueError("states must contain current_article_id and target_article_id")
        return np.fromiter(
            (
                self._predict_one(int(current), int(target))
                for current, target in zip(
                    states["current_article_id"],
                    states["target_article_id"],
                    strict=True,
                )
            ),
            dtype=np.int64,
            count=len(states),
        )

    def seen_current_mask(self, states: pd.DataFrame) -> np.ndarray:
        return states["current_article_id"].astype(np.int64).isin(
            self.routes_by_current
        ).to_numpy()
