# d1-e004-analog

## Hypothesis

Road-level future speed changes following historical network states similar to
the current state capture repeated traffic dynamics that fixed per-road ridge
summaries miss.

## Preregistered comparison

- Use frozen `d1-multifold-v1` folds and the unchanged ridge reference.
- Select 64 roads with the highest last-speed variance using training origins
  only for each fold and regime.
- Represent each state by last speed, mean5, and slope5 on selected roads.
- Standardize using the training candidate library only.
- Use the 8 nearest states with uniform weight.
- Predict each road from its current last speed plus 50% of the neighbors'
  average road-level future delta, separately for h5, h10, and h15.
- Preserve all-zero history predictions as zero.
- Do not tune road count, neighbors, shrinkage, features, or folds after scores.

## Acceptance gate

Mark `KEEP` only if all of these hold against ridge:

- weighted mean MSE improves by at least 0.5%;
- at least two of three aggregate folds improve;
- at least two of three horizons improve;
- worst-fold MSE is no more than 1% worse.

Otherwise mark `REJECT` and do not create or submit a Kaggle candidate. Public
leaderboard score `45.980` is diagnostic only and is not used by this model.

## Result

- Analog mean MSE: `55.4014` versus ridge `39.0248`.
- Analog fold scores: `62.6974`, `57.1239`, `46.3828`.
- Analog improves `0/3` folds and `0/3` horizons.
- Worst-fold MSE worsens from `44.4867` to `62.6974`.
- All four acceptance checks fail.
- Runtime: `6.98s`; test predictions are finite and nonnegative, but the local
  accuracy is not competitive.

## Recommendation

Model verdict: `REJECT`.

Submission verdict: `DO NOT SUBMIT`. No submission CSV was created, and slot 2
remains unused.
