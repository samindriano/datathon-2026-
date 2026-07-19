"""Rank OCR-derived outgoing links with the frozen E002 metadata signal."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from metarank import MetaRanker


@dataclass(frozen=True)
class PrelinkRanker:
    """Use screenshot links when available and E002 as a deterministic fallback."""

    fallback: MetaRanker
    links_by_current: dict[int, frozenset[int]]
    article_ids: frozenset[int]

    @classmethod
    def fit(
        cls,
        states: pd.DataFrame,
        articles: pd.DataFrame,
        categories: pd.DataFrame,
        links_by_current: dict[int, list[int] | set[int] | frozenset[int]],
    ) -> "PrelinkRanker":
        article_ids = frozenset(articles["article_id"].astype(np.int64))
        normalized = {
            int(current): frozenset(
                int(candidate)
                for candidate in candidates
                if int(candidate) in article_ids
            )
            for current, candidates in links_by_current.items()
        }
        return cls(
            fallback=MetaRanker.fit(states, articles, categories),
            links_by_current=normalized,
            article_ids=article_ids,
        )

    def predict_with_diagnostics(
        self, states: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray]:
        required = {"current_article_id", "target_article_id"}
        if not required.issubset(states.columns):
            raise ValueError(
                "states must contain current_article_id and target_article_id"
            )

        predictions = self.fallback.predict(states)
        used_links = np.zeros(len(states), dtype=bool)
        for index, (current_raw, target_raw) in enumerate(
            zip(
                states["current_article_id"],
                states["target_article_id"],
                strict=True,
            )
        ):
            current = int(current_raw)
            target = int(target_raw)
            candidates = self.links_by_current.get(current, frozenset())
            if not candidates:
                continue
            current_counts = self.fallback.candidate_counts_by_current.get(current, {})
            predictions[index] = max(
                candidates,
                key=lambda candidate: (
                    self.fallback._semantic_score(int(candidate), target),
                    int(current_counts.get(int(candidate), 0)),
                    int(self.fallback.global_next_counts[int(candidate)]),
                    -int(candidate),
                ),
            )
            used_links[index] = True
        return predictions.astype(np.int64, copy=False), used_links

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        predictions, _ = self.predict_with_diagnostics(states)
        return predictions
