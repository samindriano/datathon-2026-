"""Global TF-IDF state-document prototype ranker for Task 2."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

_TOK = re.compile(r"[a-z0-9]+")

def _tokens(value: object) -> list[str]:
    return _TOK.findall(str(value).casefold())

def _metadata(articles: pd.DataFrame, categories: pd.DataFrame):
    titles = {int(r.article_id): str(r.title) for r in articles.itertuples(index=False)}
    cats: dict[int, list[str]] = defaultdict(list)
    for r in categories.itertuples(index=False):
        cats[int(r.article_id)].append(str(r.category))
    return titles, cats

def state_document(current: int, target: int, titles: dict[int, str], cats: dict[int, list[str]]) -> str:
    parts: list[str] = []
    for prefix, aid in (("current_title", current), ("current_category", current), ("target_title", target), ("target_category", target)):
        vals = _tokens(titles.get(aid, "")) if prefix.endswith("title") else [x for c in cats.get(aid, []) for x in _tokens(c)]
        parts.extend(f"{prefix}_{token}" for token in vals)
    return " ".join(parts)

@dataclass
class NextProto:
    vectorizer: TfidfVectorizer
    labels: np.ndarray
    prototypes: object
    global_counts: Counter

    @classmethod
    def fit(cls, states: pd.DataFrame, articles: pd.DataFrame, categories: pd.DataFrame) -> "NextProto":
        req = {"current_article_id", "target_article_id", "next_article_id"}
        if not req.issubset(states.columns) or states.empty:
            raise ValueError("states missing required columns or empty")
        titles, cats = _metadata(articles, categories)
        docs = [state_document(int(c), int(t), titles, cats) for c, t in zip(states.current_article_id, states.target_article_id, strict=True)]
        vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True, min_df=1, norm="l2")
        X = vec.fit_transform(docs)
        labels = np.sort(states.next_article_id.astype(np.int64).unique())
        rows = []
        global_counts = Counter(states.next_article_id.astype(np.int64))
        for label in labels:
            ix = np.flatnonzero(states.next_article_id.to_numpy(dtype=np.int64) == label)
            rows.append(X[ix].mean(axis=0))
        P = normalize(np.vstack([np.asarray(r).ravel() for r in rows]), norm="l2")
        return cls(vec, labels, P, global_counts)

    def predict(self, states: pd.DataFrame, articles: pd.DataFrame, categories: pd.DataFrame) -> np.ndarray:
        titles, cats = _metadata(articles, categories)
        docs = [state_document(int(c), int(t), titles, cats) for c, t in zip(states.current_article_id, states.target_article_id, strict=True)]
        X = self.vectorizer.transform(docs)
        scores = X @ self.prototypes.T
        out = []
        for row in scores:
            vals = np.asarray(row.toarray() if hasattr(row, "toarray") else row).ravel()
            best = max(range(len(self.labels)), key=lambda i: (float(vals[i]), self.global_counts[int(self.labels[i])], -int(self.labels[i])))
            out.append(int(self.labels[best]))
        return np.asarray(out, dtype=np.int64)
