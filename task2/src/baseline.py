"""Cheapest leakage-safe Task 2 next-click baseline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def deterministic_mode(values: pd.Series) -> int:
    """Return the most frequent integer value, breaking ties by article ID."""
    numeric = values.astype(np.int64)
    counts = numeric.value_counts(sort=False)
    if counts.empty:
        raise ValueError("cannot compute mode of empty values")
    maximum = int(counts.max())
    return int(min(int(value) for value in counts[counts == maximum].index))


@dataclass(frozen=True)
class CurrentModeBaseline:
    global_next_article_id: int
    next_by_current: dict[int, int]
    candidates_by_current: dict[int, frozenset[int]]

    @classmethod
    def fit(cls, states: pd.DataFrame) -> "CurrentModeBaseline":
        required = {"current_article_id", "next_article_id"}
        if not required.issubset(states.columns) or len(states) == 0:
            raise ValueError("states must contain non-empty current and next columns")
        next_by_current: dict[int, int] = {}
        candidates: dict[int, frozenset[int]] = {}
        for current, group in states.groupby("current_article_id", sort=True):
            next_by_current[int(current)] = deterministic_mode(group["next_article_id"])
            candidates[int(current)] = frozenset(
                group["next_article_id"].astype(np.int64).tolist()
            )
        return cls(
            global_next_article_id=deterministic_mode(states["next_article_id"]),
            next_by_current=next_by_current,
            candidates_by_current=candidates,
        )

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        if "current_article_id" not in states.columns:
            raise ValueError("states must contain current_article_id")
        return np.fromiter(
            (
                self.next_by_current.get(int(current), self.global_next_article_id)
                for current in states["current_article_id"]
            ),
            dtype=np.int64,
            count=len(states),
        )

    def seen_current_mask(self, states: pd.DataFrame) -> np.ndarray:
        return states["current_article_id"].astype(np.int64).isin(
            self.next_by_current
        ).to_numpy()

    def candidate_coverage(self, states: pd.DataFrame) -> float:
        if "next_article_id" not in states.columns:
            raise ValueError("states must contain next_article_id")
        covered = [
            int(next_article) in self.candidates_by_current.get(int(current), ())
            for current, next_article in zip(
                states["current_article_id"], states["next_article_id"], strict=True
            )
        ]
        return float(np.mean(covered))
