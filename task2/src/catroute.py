"""Fold-local category-conditioned current-to-next transition ranker."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import numpy as np
import pandas as pd
from baseline import deterministic_mode
from validation import broad_category_by_article

@dataclass(frozen=True)
class CatRoute:
    global_next_article_id: int
    edge_counts: dict[int, Counter]
    category_edges: dict[tuple[int, str], Counter]
    global_next_counts: Counter
    broad_by_article: dict[int, str]

    @classmethod
    def fit(cls, states: pd.DataFrame, categories: pd.DataFrame) -> "CatRoute":
        required = {"current_article_id", "next_article_id", "target_article_id"}
        if not required.issubset(states.columns) or states.empty:
            raise ValueError("states missing required non-empty columns")
        broad = broad_category_by_article(categories)
        edges: dict[int, Counter] = {}
        cat_edges: dict[tuple[int, str], Counter] = defaultdict(Counter)
        for current, group in states.groupby("current_article_id", sort=True):
            edges[int(current)] = Counter(group["next_article_id"].astype(np.int64))
            for target, nxt in zip(group["target_article_id"], group["next_article_id"], strict=True):
                category = broad.get(int(target), "__missing__")
                cat_edges[(int(current), category)][int(nxt)] += 1
        global_counts = Counter(states["next_article_id"].astype(np.int64))
        return cls(deterministic_mode(states["next_article_id"]), edges, dict(cat_edges), global_counts, broad)

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        required = {"current_article_id", "target_article_id"}
        if not required.issubset(states.columns):
            raise ValueError("states missing current_article_id/target_article_id")
        out = []
        for current_raw, target_raw in zip(states["current_article_id"], states["target_article_id"], strict=True):
            current, target = int(current_raw), int(target_raw)
            edges = self.edge_counts.get(current)
            if not edges:
                out.append(self.global_next_article_id); continue
            category = self.broad_by_article.get(target, "__missing__")
            cat = self.category_edges.get((current, category), Counter())
            n_current = sum(edges.values()); n_cat = sum(cat.values())
            # score is posterior with fixed prior strength 5; maximize with deterministic ties.
            def key(nxt: int) -> tuple[float, int, int, int]:
                score = (cat.get(nxt, 0) + 5.0 * edges[nxt] / n_current) / (n_cat + 5.0)
                return (score, edges[nxt], self.global_next_counts[nxt], -nxt)
            out.append(max(edges, key=key))
        return np.asarray(out, dtype=np.int64)

    def seen_current_mask(self, states: pd.DataFrame) -> np.ndarray:
        return states["current_article_id"].astype(np.int64).isin(self.edge_counts).to_numpy()

    def candidate_coverage(self, states: pd.DataFrame) -> float:
        return float(np.mean([int(n) in self.edge_counts.get(int(c), Counter()) for c, n in zip(states.current_article_id, states.next_article_id, strict=True)]))
