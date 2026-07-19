"""Deterministic title/category ranker for Task 2 next-click prediction."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd

from baseline import deterministic_mode


TITLE_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def title_tokens(title: str) -> frozenset[str]:
    """Return deterministic lowercase ASCII-alphanumeric title tokens."""
    return frozenset(TITLE_TOKEN_PATTERN.findall(str(title).casefold()))


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    """Jaccard similarity, defined as zero when both sets are empty."""
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


@dataclass(frozen=True)
class MetaRanker:
    """Rank fold-local outgoing candidates using official static metadata."""

    global_next_article_id: int
    candidate_counts_by_current: dict[int, Counter[int]]
    global_next_counts: Counter[int]
    title_tokens_by_article: dict[int, frozenset[str]]
    categories_by_article: dict[int, frozenset[str]]

    @classmethod
    def fit(
        cls,
        states: pd.DataFrame,
        articles: pd.DataFrame,
        categories: pd.DataFrame,
    ) -> "MetaRanker":
        required_states = {"current_article_id", "next_article_id"}
        if not required_states.issubset(states.columns) or states.empty:
            raise ValueError("states must contain non-empty current and next columns")
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
        candidate_counts = {
            int(current): Counter(group["next_article_id"].astype(np.int64))
            for current, group in states.groupby("current_article_id", sort=True)
        }
        global_counts = Counter(states["next_article_id"].astype(np.int64))
        return cls(
            global_next_article_id=deterministic_mode(states["next_article_id"]),
            candidate_counts_by_current=candidate_counts,
            global_next_counts=global_counts,
            title_tokens_by_article=article_tokens,
            categories_by_article=category_sets,
        )

    def _semantic_score(self, candidate: int, target: int) -> float:
        candidate_categories = self.categories_by_article.get(candidate, frozenset())
        target_categories = self.categories_by_article.get(target, frozenset())
        candidate_title = self.title_tokens_by_article.get(candidate, frozenset())
        target_title = self.title_tokens_by_article.get(target, frozenset())
        return 2.0 * jaccard(candidate_categories, target_categories) + jaccard(
            candidate_title, target_title
        )

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        required = {"current_article_id", "target_article_id"}
        if not required.issubset(states.columns):
            raise ValueError("states must contain current_article_id and target_article_id")
        predictions: list[int] = []
        for current_raw, target_raw in zip(
            states["current_article_id"],
            states["target_article_id"],
            strict=True,
        ):
            current = int(current_raw)
            target = int(target_raw)
            counts = self.candidate_counts_by_current.get(current)
            if not counts:
                predictions.append(self.global_next_article_id)
                continue
            prediction = max(
                counts,
                key=lambda candidate: (
                    self._semantic_score(int(candidate), target),
                    counts[int(candidate)],
                    self.global_next_counts[int(candidate)],
                    -int(candidate),
                ),
            )
            predictions.append(int(prediction))
        return np.asarray(predictions, dtype=np.int64)

    def seen_current_mask(self, states: pd.DataFrame) -> np.ndarray:
        return states["current_article_id"].astype(np.int64).isin(
            self.candidate_counts_by_current
        ).to_numpy()

    def candidate_coverage(self, states: pd.DataFrame) -> float:
        if "next_article_id" not in states.columns:
            raise ValueError("states must contain next_article_id")
        covered = [
            int(next_article)
            in self.candidate_counts_by_current.get(int(current), Counter())
            for current, next_article in zip(
                states["current_article_id"], states["next_article_id"], strict=True
            )
        ]
        return float(np.mean(covered))
