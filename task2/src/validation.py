"""Official Task 2 target-group validation helpers."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd


DEFAULT_FOLD_COUNT = 5
DEFAULT_SEED = 20260719


def broad_category_by_article(categories: pd.DataFrame) -> dict[int, str]:
    """Map each categorized article to a deterministic broad category."""
    required = {"article_id", "category"}
    if not required.issubset(categories.columns):
        raise ValueError(f"categories must contain {sorted(required)}")
    result: dict[int, str] = {}
    grouped = categories.groupby("article_id", sort=True)["category"]
    for article_id, values in grouped:
        category = min(str(value) for value in values)
        parts = category.split(".")
        broad = parts[1] if len(parts) > 1 and parts[0] == "subject" else parts[0]
        result[int(article_id)] = broad
    return result


def make_target_group_folds(
    states: pd.DataFrame,
    categories: pd.DataFrame,
    fold_count: int = DEFAULT_FOLD_COUNT,
    seed: int = DEFAULT_SEED,
) -> np.ndarray:
    """Create deterministic category-balanced folds with whole targets held out."""
    if "target_article_id" not in states.columns:
        raise ValueError("states must contain target_article_id")
    if fold_count < 2:
        raise ValueError("fold_count must be at least 2")
    targets = np.sort(states["target_article_id"].astype(np.int64).unique())
    if len(targets) < fold_count:
        raise ValueError("not enough targets for requested folds")
    category_map = broad_category_by_article(categories)
    targets_by_category: dict[str, list[int]] = defaultdict(list)
    for target in targets:
        targets_by_category[category_map.get(int(target), "__missing__")].append(
            int(target)
        )

    rng = np.random.default_rng(seed)
    fold_targets: list[list[int]] = [[] for _ in range(fold_count)]
    fold_category_counts: list[dict[str, int]] = [
        defaultdict(int) for _ in range(fold_count)
    ]
    for category, category_targets in sorted(
        targets_by_category.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        shuffled = np.asarray(sorted(category_targets), dtype=np.int64)
        rng.shuffle(shuffled)
        for target in shuffled:
            fold = min(
                range(fold_count),
                key=lambda index: (
                    fold_category_counts[index][category],
                    len(fold_targets[index]),
                    index,
                ),
            )
            fold_targets[fold].append(int(target))
            fold_category_counts[fold][category] += 1

    target_to_fold = {
        target: fold
        for fold, assigned_targets in enumerate(fold_targets)
        for target in assigned_targets
    }
    folds = states["target_article_id"].astype(np.int64).map(target_to_fold)
    if folds.isna().any():
        raise RuntimeError("failed to assign every target to a fold")
    return folds.to_numpy(dtype=np.int64)


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Exact-match accuracy with strict shape validation."""
    truth = np.asarray(y_true)
    prediction = np.asarray(y_pred)
    if truth.shape != prediction.shape or truth.size == 0:
        raise ValueError("truth and prediction must have the same non-empty shape")
    return float(np.mean(truth == prediction))
