# d2-e002-metarank

Status after MAIN scoring: `KEEP`, pending independent VALIDATION review.
Submission verdict: `INVESTIGATE`; do not use a Kaggle slot yet.

## Frozen hypothesis

For a current article with multiple next-click candidates observed in the
fold-training labels, target-aware category and title similarity can select the
appropriate route better than current-specific frequency alone.

The formula is fixed before MAIN scoring:

```text
2 * Jaccard(candidate categories, target categories)
+ 1 * Jaccard(candidate title tokens, target title tokens)
```

Ties use current-specific frequency, global next frequency, then the smallest
article ID. Unseen currents use the same fold-training global mode as the
baseline. There is no weight, tokenizer, threshold, or seed search.

## Acceptance gate

- reproduce the independent audit reference mean accuracy `0.2853333333333333`;
- improve mean accuracy by at least `0.010` over `d2-e001-baseline`;
- improve at least `4/5` folds;
- worst fold must not be worse than the baseline worst fold;
- current-unseen accuracy may not fall by more than `0.005`;
- entirely-unseen-target-category accuracy may not fall by more than `0.005`;
- state-ID ablation must be exact;
- runtime must remain under 180 seconds;
- submission must pass the fail-closed validator.

Passing this gate permits `KEEP` and independent VALIDATION review. It does not
authorize a Kaggle slot.

## Result

- audit reference reproduced exactly: `0.2853333333333333`;
- baseline mean accuracy: `0.2613333333333333`;
- metarank mean accuracy: `0.2853333333333333`;
- gain: `+0.0240000000000000` absolute accuracy;
- folds: `0.290556`, `0.282778`, `0.278333`, `0.280556`, `0.294444`;
- wins: `5/5` folds;
- worst fold: `0.278333` versus baseline `0.255000`;
- fold standard deviation: `0.006142`;
- current-unseen accuracy: unchanged at `0.123539`;
- entirely-unseen-target-category accuracy: `0.280000 -> 0.315200`;
- test prediction change rate from baseline: `0.151333`;
- test predictions: 449 unique, top share `0.275167`;
- final recorded runtime: about 12.0 seconds;
- submission validator: `READY`.
- submission CSV SHA-256:
  `87b4a480008eabe06921a36edc14ea12abf4a006b86850f5260d959c54ad3d81`.

All preregistered checks passed. The result remains a candidate rather than a
submission recommendation until the immutable commit is independently audited.
