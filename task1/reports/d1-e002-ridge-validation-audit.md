# D1 E002 Ridge Independent Validation Audit

- Time: 2026-07-18 12:24-12:29 WIB
- Role: VALIDATION
- Reviewed commit: `e2136b6269db4dc9618a3003df4d44fc63dc63d4`

## Verdicts

- Validation harness: `GO`
- Model candidate `d1-e002-ridge`: `KEEP`
- Kaggle submission: `INVESTIGATE`

The official-v1 fold construction, purge boundary, training-only fitting,
regime weighting, scoring, zero-history guard, and generated submission were
independently reproduced. Ridge improves the weighted mean, every aggregate
horizon, and the worst fold. It is a valid candidate for continued comparison.

Submission is not yet authorized because the latest chronological fold is
slightly worse than mean15 and the separate submission/notebook reproducibility
review has not been completed.

## Independently verified

### Fold construction and purge

Each block has three non-overlapping 720-origin validation windows. Training is
expanding from origin 14. For every fold:

- `train_origin_end = validation_origin_start - 16`;
- the final training target at h15 is
  `validation_origin_start - 1`;
- 15 possible training origins are purged;
- validation targets remain inside their own train block.

The validation history legitimately contains observations immediately before
its forecast origin. Those observations are available at prediction time; no
validation target at or after the origin is used to fit the model.

### Training-only model fitting

For each block and fold, feature moments, target means, covariance,
cross-covariance, and ridge coefficients are accumulated only from the fold's
training-origin range. No validation history, target, text, graph, test label,
API, or pretrained weight enters fitting.

The five fixed causal features are `last`, `mean3`, `mean5`, `mean15`, and
`slope5`; alpha is fixed at 0.1. The final test model is retrained independently
on every valid origin in its corresponding full train block.

### Regime aggregation and routing

- Fold scores are computed separately for m1 and m2.
- Scores are combined with 372/540 and 168/540 weights.
- Test routing independently reproduces 372 m1-like and 168 m2-like samples.
- The threshold is separated from observed zero-road counts (13-16 versus
  210-211), so routing is unambiguous on this test set.

### Reproduced metrics

| Metric | Mean15 | Ridge-history | Ridge delta |
| --- | ---: | ---: | ---: |
| Mean MSE | 45.548238 | 39.024844 | -6.523394 (-14.32%) |
| Worst fold | 54.837085 | 44.486736 | -10.350349 |
| h5 | 38.506758 | 32.800178 | -5.706579 |
| h10 | 45.837496 | 39.741927 | -6.095570 |
| h15 | 52.300461 | 44.532427 | -7.768034 |

Fold comparison:

| Fold | Mean15 | Ridge | Ridge minus mean15 |
| --- | ---: | ---: | ---: |
| 1 | 54.837085 | 44.486736 | -10.350349 |
| 2 | 50.751010 | 41.032714 | -9.718297 |
| 3 (latest tail) | 31.056619 | 31.555082 | +0.498462 |

The gain is not caused by one fold: folds 1 and 2 both improve materially, all
three aggregate horizons improve, and worst-fold behavior improves. The fold-3
regression is small relative to the total gain but is relevant because it is
the latest validation period in both blocks.

Fold-3 detail shows the regression is concentrated in later horizons:

- m1: h5 improves by about 0.314 MSE; h10 worsens by about 0.662; h15 worsens
  by about 1.488;
- m2: h5 is effectively tied (+0.002); h10 worsens by about 0.391; h15 worsens
  by about 0.349.

This does not invalidate `KEEP`, but it prevents treating ridge as an automatic
final candidate when hidden-test chronology is unknown.

### Submission and reproducibility

- Targeted tests independently pass: `7 passed`.
- Recomputed metrics match `metrics.json` exactly.
- Recomputed test predictions match every stored submission speed exactly.
- Submission has 2,041,200 rows and 2,041,200 unique IDs.
- All predictions are finite and nonnegative, range `[0.0, 101.569557]`.
- All 40,250 sample-road all-zero histories produce exact zero at all horizons.
- Runtime is about 10 seconds and no model artifact is required because fitting
  is deterministic and inexpensive.

## Remaining risks and required actions

1. Freeze `d1-multifold-v1`; do not move fold boundaries after seeing model
   results. All later candidates must use the same folds.
2. Preserve the fold-3 regression in experiment comparisons and writeup.
3. Record commit `e2136b6` with the experiment handoff/metadata.
4. Complete `D1-SUB-001`, including a clean-session inference/Run-All check,
   before authorizing any Kaggle slot.
5. Treat any ridge/mean15 blend or lag-weight model as a new preregistered
   hypothesis; do not tune it retrospectively to repair fold 3.

No code change to the modeling pipeline is requested by this audit.
