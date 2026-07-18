# d1-e005-ar15

## Hypothesis

Direct per-road ridge coefficients over all 15 causal history values retain
useful dynamics that are lost when history is compressed into last, mean, and
slope summaries.

## Preregistered comparison

- Use frozen `d1-multifold-v1` folds and unchanged ridge reference.
- Change only the feature representation: five summaries become all 15 lags.
- Keep the same standardized per-road direct multi-horizon regression.
- Keep fixed ridge `alpha=0.1` to isolate the feature hypothesis.
- Preserve the all-zero history guard and nonnegative output floor.
- Do not tune alpha, lag count, folds, or acceptance thresholds after scores.

## Acceptance gate

Mark `KEEP` only if all of these hold against ridge:

- weighted mean MSE improves by at least 0.5%;
- at least two of three aggregate folds improve;
- at least two of three horizons improve;
- worst-fold MSE is no more than 1% worse.

Otherwise mark `REJECT` and do not create or submit a Kaggle candidate. Public
leaderboard score `45.980` is diagnostic only and is not used for selection.

## Result

- AR15 mean MSE: `39.0830` versus ridge `39.0248`.
- AR15 fold scores: `44.8119`, `41.1142`, `31.3228`.
- AR15 improves only fold 3 and improves `0/3` aggregate horizons.
- Worst fold remains within the 1% tolerance, but the other three acceptance
  checks fail.
- Runtime: `11.99s`; test prediction distribution remains credible.

## Recommendation

Model verdict: `REJECT`.

Submission verdict: `DO NOT SUBMIT`. No submission CSV was created, and slot 2
remains unused.
