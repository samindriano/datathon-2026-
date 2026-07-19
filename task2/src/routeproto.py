"""Frozen supervised TF-IDF route-prototype ranker for Task 2."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import TfidfVectorizer

from baseline import deterministic_mode


@dataclass
class RouteProtoRanker:
    vectorizer: TfidfVectorizer
    titles: dict[int, str]
    prototypes: dict[int, dict[int, object]]
    candidate_counts: dict[int, Counter]
    global_counts: Counter
    global_mode: int

    @classmethod
    def fit(cls, states: pd.DataFrame, articles: pd.DataFrame) -> "RouteProtoRanker":
        required = {"current_article_id", "target_article_id", "next_article_id"}
        if not required.issubset(states.columns) or states.empty:
            raise ValueError("states must contain non-empty current,target,next columns")
        titles = {int(r.article_id): str(r.title) for r in articles.itertuples(index=False)}
        target_ids = states["target_article_id"].astype(np.int64).to_numpy()
        corpus = [titles.get(int(i), "") for i in target_ids]
        vectorizer = TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), sublinear_tf=True, min_df=1,
            norm="l2", dtype=np.float64,
        )
        matrix = vectorizer.fit_transform(corpus)
        edge_rows: dict[tuple[int, int], list[int]] = defaultdict(list)
        candidate_counts: dict[int, Counter] = {}
        for row_idx, row in enumerate(states.itertuples(index=False)):
            edge_rows[(int(row.current_article_id), int(row.next_article_id))].append(row_idx)
        for current, group in states.groupby("current_article_id", sort=True):
            candidate_counts[int(current)] = Counter(group["next_article_id"].astype(np.int64))
        prototypes: dict[int, dict[int, np.ndarray]] = defaultdict(dict)
        for (current, nxt), idxs in edge_rows.items():
            vec = csr_matrix(matrix[idxs].sum(axis=0))
            nrm = float(np.sqrt(vec.multiply(vec).sum()))
            if nrm:
                vec = vec / nrm
            prototypes[current][nxt] = vec
        global_counts = Counter(states["next_article_id"].astype(np.int64))
        return cls(vectorizer, titles, dict(prototypes), candidate_counts, global_counts,
                   deterministic_mode(states["next_article_id"]))

    def predict(self, states: pd.DataFrame) -> np.ndarray:
        if not {"current_article_id", "target_article_id"}.issubset(states.columns):
            raise ValueError("states must contain current_article_id and target_article_id")
        queries = [self.titles.get(int(i), "") for i in states["target_article_id"]]
        qmat = self.vectorizer.transform(queries)
        cache = {}
        for current, cand in self.candidate_counts.items():
            ids = list(cand)
            cache[current] = (ids, vstack([self.prototypes[current][int(n)] for n in ids]))
        out: list[int] = []
        for i, row in enumerate(states.itertuples(index=False)):
            current = int(row.current_article_id)
            candidates = self.candidate_counts.get(current)
            if not candidates:
                out.append(self.global_mode)
                continue
            ids, proto_mat = cache[current]
            scores = np.asarray(qmat[i].dot(proto_mat.T).toarray()).ravel()
            best = max((float(score), int(candidates[n]), int(self.global_counts[int(n)]), -int(n), int(n))
                       for score, n in zip(scores, ids, strict=True))
            out.append(best[-1])
        return np.asarray(out, dtype=np.int64)

    def seen_current_mask(self, states: pd.DataFrame) -> np.ndarray:
        return states["current_article_id"].astype(np.int64).isin(self.candidate_counts).to_numpy()

    def candidate_coverage(self, states: pd.DataFrame) -> float:
        if "next_article_id" not in states.columns:
            raise ValueError("states must contain next_article_id")
        covered = [int(n) in self.candidate_counts.get(int(c), {})
                   for c, n in zip(states["current_article_id"], states["next_article_id"], strict=True)]
        return float(np.mean(covered))
