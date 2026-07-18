# d1-e018-lowrankguard

Status before scoring: `RUNNING`.

## Selection-risk disclosure

E018 was designed only after E016 showed strong aggregate gains but failed two
temporal chunks. It is a new robustness hypothesis, not a retune of E016. The
E016 gate remains failed and unchanged.

## Frozen hypothesis

E016 is trusted only when its rank-4 latent temporal summaries and spatial
reconstruction error are within three training-fold standard deviations. The
21 novelty statistics are fitted on training origins only. An untrusted origin
reverts completely to E013; trusted origins retain the exact frozen E016
prediction. The rank, PCA sample count, ridge alpha, and 75:25 base blend are
unchanged. There is no threshold, weight, or guard-action search.

## Preregistered gate versus E013

All conditions must pass:

1. at least 2% mean MSE improvement;
2. all 3 folds and all 3 horizons improve;
3. worst fold improves and fold standard deviation does not worsen;
4. all 18 block-fold-horizon cells improve;
5. at least 35/36 temporal chunks improve;
6. median chunk gain is at least 0.50 MSE;
7. worst chunk gain is at least -0.10 MSE;
8. test-m2 correction versus ridge is nonpositive;
9. test RMS change versus E013 is at most 1.0 km/h;
10. no more than 20% of test origins are reverted;
11. predictions are finite, nonnegative, and zero-history guarded.

Failure means immediate `REJECT`, without threshold or weight changes. Passing
means `KEEP / NEEDS_REVIEW`, not automatic authorization for a Kaggle slot.

## Result

Status: `REJECT`.

The guard retained a `2.0301%` mean improvement over E013 (`36.560253` to
`35.818046`), improved all folds, horizons, and `18/18` cells, and reduced
E016's worst chunk regression from `-0.318567` to `-0.106403`. It nevertheless
failed three frozen conditions:

- `33/36` chunks improved, below the required `35/36`;
- worst chunk `-0.106403` remained below the `-0.10` floor;
- `30.37%` of test origins were reverted, above the `20%` cap.

No submission CSV, audit request, notebook, or Kaggle slot is produced. The
three-sigma threshold and full-reversion action are not changed after scoring.
