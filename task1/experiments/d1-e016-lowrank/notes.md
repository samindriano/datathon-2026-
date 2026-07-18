# d1-e016-lowrank

Status before scoring: `RUNNING`.

## Hypothesis

Four training-fold-only latent spatial factors capture coordinated road modes
that city averages, hand-built distribution summaries, graph neighbors, and
seasonal phase may miss. PCA uses exactly 360 evenly spaced causal training
history rows with per-road standardization. Each factor receives the same five
temporal summaries as ridge. The candidate remains 75% e010 plus 25% low-rank
state.

No rank, PCA sample count, alpha, or blend-weight search is allowed.

## Preregistered gate versus e013

All conditions must pass:

1. at least 1% mean MSE improvement;
2. all 3 folds and all 3 horizons improve;
3. worst fold improves and fold standard deviation does not worsen;
4. at least 17/18 block-fold-horizon cells improve;
5. at least 34/36 temporal chunks improve;
6. median chunk gain is at least 0.25 MSE;
7. worst chunk gain is at least -0.25 MSE;
8. test-m2 correction versus ridge is nonpositive;
9. test RMS change versus e013 is at most 1.0 km/h;
10. predictions are finite, nonnegative, and zero-history guarded.

Failure means immediate `REJECT`, no retuning, no audit, no notebook, and no
Kaggle slot. E013 remains selected throughout.

## Result

Status: `REJECT`.

The candidate improved mean MSE from `36.560253` to `35.557597` (`2.7436%`),
all three folds, all three horizons, worst-fold MSE (`41.751514` to
`40.567433`), fold standard deviation (`5.160868` to `4.829910`), and all
`18/18` block-fold-horizon cells. It improved `34/36` temporal chunks with a
median gain of `0.749104` MSE.

One frozen safety condition failed: the worst temporal-chunk gain was
`-0.318567` MSE, below the preregistered `-0.25` floor. Therefore no
submission CSV, audit request, notebook, or Kaggle slot is produced. The gate
is not retuned after observing the score, and E013 remains the final candidate.
