# d1-e009-textzguard

## Hypothesis

A fixed three-sigma guard on only `prohibit left turn` captures the standardized
test-m2 shift reported by VALIDATION, while preserving the causal aligned-text
gain of `d1-e006-textres`.

## Preregistered comparison

- Keep `d1-multifold-v1`, ridge, text features, coefficients, alphas, routing,
  and zero guard unchanged.
- Compute z-scores only from each fitted training fold/model.
- At inference, set only the guarded standardized value to zero when
  `abs(z) > 3.0`; do not clip or alter any other feature.
- The threshold is fixed before scoring and will not be tuned.
- Do not use validation/test labels or leaderboard feedback.

## Acceptance gate

- Improve ridge mean by at least 0.5%, at least two folds, and at least two
  horizons; keep worst fold within 1% of ridge.
- Stay within 0.1% MSE of exact textres locally.
- Activate on at least one test-m2 sample, make the guarded test-m2 mean
  correction versus ridge nonpositive, and lower it versus exact textres.

Otherwise mark `REJECT`, stop the text-guard path, and generate no candidate.
Even if `KEEP`, do not use a Kaggle slot before independent review.

## Result

`KEEP`, pending independent audit.

- Mean MSE: `38.283964` versus ridge `39.024844` and exact textres
  `38.345626`.
- Fold MSE: `44.007651`, `40.586363`, `30.257876`; all three improve over
  ridge. Worst fold: `44.007651`; standard deviation: `5.844648`.
- All three aggregate horizons improve over ridge.
- The guard activates on `144/168` test-m2 samples and zero test-m1 samples.
- Test-m2 mean correction versus ridge changes from exact textres `+0.347038`
  to guarded `-0.089853` km/h.
- Submission validator reports `READY`; 2,041,200 IDs are exact and unique,
  values are finite/nonnegative, and all 40,250 zero-history sample-road pairs
  remain zero across three horizons.
- Full Task 1 suite: `32 passed`.

Do not submit this candidate directly. Graphres remains locally stronger and
already has an independent `GO`/`KEEP`; use this result only after audit and as
the safe text component of a separately preregistered comparison.
