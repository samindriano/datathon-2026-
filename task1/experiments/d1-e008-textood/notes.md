# d1-e008-textood

## Hypothesis

Neutralizing only the `prohibit left turn` residual feature when its raw count
falls outside the training-origin range preserves aligned text gains while
removing the risky positive correction observed on test m2.

## Preregistered comparison

- Keep frozen `d1-multifold-v1`, ridge, text features, coefficients, alphas,
  and zero guard unchanged from `d1-e006-textres`.
- Record the training-origin minimum and maximum for `prohibit left turn`.
- At validation/test inference only, if that raw count is outside the fitted
  range, set only its standardized value to zero (the training mean).
- Do not clip, remove, or retune any other feature.
- Do not use labels or leaderboard feedback to trigger the guard.

## Acceptance gate

- Improve ridge mean by at least 0.5%, at least two folds, and at least two
  horizons; keep worst fold within 1% of ridge.
- Stay within 0.1% MSE of exact textres locally.
- Make guarded test-m2 mean correction versus ridge nonpositive and lower than
  exact textres.

Otherwise mark `REJECT` and do not create or submit a candidate. Slot 2 remains
protected pending independent audit.

## Result

`REJECT`.

- Mean MSE: `38.283964` versus ridge `39.024844` and exact textres
  `38.345626`.
- Fold MSE: `44.007651`, `40.586363`, `30.257876`.
- Worst fold: `44.007651`; standard deviation: `5.844648`.
- The guard activated for 390 validation samples in m2 fold 3, but activated
  for zero test samples in both regimes.
- Test-m2 mean correction versus ridge remained unchanged at `+0.347038`
  km/h, so the two inference-risk gates failed.
- No submission CSV was created and no Kaggle slot should be used.

The raw min/max definition did not capture the standardized distribution shift
reported by VALIDATION. Any z-score guard must be treated as a separate,
preregistered experiment rather than a post-hoc change to this result.
