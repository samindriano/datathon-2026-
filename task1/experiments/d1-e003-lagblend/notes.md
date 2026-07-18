# d1-e003-lagblend

## Hypothesis

One nonnegative weight vector over the 15 causal history steps, learned
separately for each regime and forecast horizon, can improve robustness without
the per-road flexibility that caused the ridge candidate's latest-fold caveat.

## Preregistered comparison

- Use the frozen `d1-multifold-v1` folds without changing their boundaries.
- Compare `mean15`, the frozen ridge reference, and `lagblend` on identical
  validation origins.
- Fit shared weights only on each fold's training origins.
- Constrain every horizon's 15 weights to be nonnegative and sum to one.
- Use fixed regularization `alpha=1.0` toward uniform mean15 weights.
- Exclude all-zero history pairs from fitting and preserve the zero-history
  prediction guard.
- Do not tune weights, alpha, folds, or thresholds after seeing results.

## Acceptance gate

Mark `KEEP` only if all of these hold against ridge:

- weighted mean MSE improves by at least 0.5%;
- at least two of three aggregate folds improve;
- at least two of three horizons improve;
- worst-fold MSE is no more than 1% worse.

Otherwise mark `REJECT` and do not create or submit a Kaggle candidate. Public
leaderboard score `45.980` is not used for fitting or selection.

## Result

- Lagblend mean MSE: `42.8914` versus ridge `39.0248`.
- Lagblend fold scores: `50.6941`, `47.1967`, `30.7834`.
- Lagblend improves only fold 3 and improves `0/3` aggregate horizons.
- Worst-fold MSE worsens from `44.4867` to `50.6941`.
- All four preregistered acceptance checks fail.
- Runtime: `14.75s`; test predictions remain finite, nonnegative, and preserve
  the structural zero guard.

## Recommendation

Model verdict: `REJECT`.

Submission verdict: `DO NOT SUBMIT`. No submission CSV was created, and slot 2
remains unused.
