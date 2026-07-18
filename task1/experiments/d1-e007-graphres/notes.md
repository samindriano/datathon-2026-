# d1-e007-graphres

## Hypothesis

Mean speed-history summaries from directly connected road segments provide
local network context that independent per-road ridge summaries miss.

## Preregistered comparison

- Use frozen `d1-multifold-v1` folds and unchanged ridge reference.
- Convert official directed adjacency to a symmetric union, remove diagonal
  self-links, and row-normalize external neighbors to a mean.
- Keep the five local ridge features and append their five neighbor means.
- Keep fixed ridge alpha `0.1` to isolate the graph-feature hypothesis.
- Preserve the all-zero history guard and nonnegative output floor.
- Use NumPy sparse edge aggregation; no GNN, pretrained weight, or new runtime
  dependency.
- Do not tune adjacency direction, alpha, features, folds, or gates after
  scores.

## Acceptance gate

Mark `KEEP` only if all of these hold against ridge:

- weighted mean MSE improves by at least 0.5%;
- at least two of three aggregate folds improve;
- at least two of three horizons improve;
- worst-fold MSE is no more than 1% worse.

Otherwise mark `REJECT` and do not create or submit a Kaggle candidate. Public
leaderboard score `45.980` is diagnostic only and is not used for selection.

## Result

- Graphres mean MSE: `38.1750` versus ridge `39.0248`.
- Improvement: `0.8498` MSE or `2.18%`.
- Graphres fold scores: `43.7473`, `39.9422`, `30.8355`.
- All `3/3` folds and `3/3` aggregate horizons improve.
- Worst fold improves from `44.4867` to `43.7473`.
- All four preregistered acceptance checks pass.
- Runtime: `26.94s`; external symmetric edge count is `3,892`.
- Submission validator reports `READY`: 2,041,200 exact unique IDs, finite,
  nonnegative, and all 40,250 structural zero sample-road pairs remain zero.

## Recommendation

Model verdict: `KEEP`, pending independent graph-feature and leakage audit.

Submission verdict: `INVESTIGATE`. Do not use a Kaggle slot before VALIDATION
confirms adjacency handling, training-only fitting, and score reproduction.
