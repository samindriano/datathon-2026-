# D1 Public-Leaderboard Gap Audit

- Time: 2026-07-18 13:34-13:44 WIB
- Role: VALIDATION
- Candidate: `d1-e002-ridge`
- Local official-v1 MSE: `39.024844`
- Kaggle public MSE: `45.980`

## Verdict

- Data/model leakage: `GO` (none found)
- Frozen validation as a relative model-comparison harness: `GO`
- Frozen validation as an absolute estimate of hidden-test MSE: `INVESTIGATE`
- Another ridge-like submission based only on the public score: **DO NOT SUBMIT**

The public score is `6.9552` MSE (`17.82%`) worse than local validation and
`1.4933` worse than the local worst fold. The submitted artifact, horizon/road
order, regime routing, and deterministic predictions were already reproduced
exactly, so this is not an output-format or notebook-identity failure.

The dominant risk is train-to-test difficulty/concept shift, with visible
covariate shift in the low-speed m2 regime. However, reweighting historical
errors to the observed test history-speed distribution estimates ridge MSE at
only `39.4152`; the visible covariate shift alone does not explain `45.980`.
The remaining gap can therefore come from unseen future dynamics/events and/or
the composition of the 30% public partition. One public score is not sufficient
evidence to retune the pipeline.

## Leakage review

No use of test targets, future validation values, full-data preprocessing,
external data, APIs, pretrained weights, text, or graph information was found
in `d1-e002-ridge`.

The original 15-origin purge makes the last training target occur one timestep
before the validation origin. Consequently, 14 target timestamps from the end
of training also appear as past values inside the first validation history.
This is legitimate under online forecasting semantics, but stricter batch-test
isolation requires 14 additional purged origins so that no raw timestamp occurs
on both sides.

This stricter isolation has no material effect:

| Additional purge | Mean MSE | Worst fold |
| ---: | ---: | ---: |
| 0 | 39.024844 | 44.486736 |
| 14 (no shared raw timestamp) | 39.024965 | 44.476657 |
| 30 | 39.024817 | 44.464567 |

The exact no-overlap sensitivity changes mean MSE by only `+0.000121`.
Larger one- and two-day embargoes on folds 2-3 raise ridge MSE from `36.2939`
to `36.4826` and `36.7746`; temporal adjacency helps mildly but does not create
the reported six-point gain or explain the public gap.

## Temporal stability

An exhaustive expanding walk-forward diagnostic used every non-overlapping
720-origin window available after the minimum training period:

| Regime | Windows | Ridge wins | Mean15 MSE | Ridge MSE |
| --- | ---: | ---: | ---: | ---: |
| m1 | 13 | 13 | 54.6861 | 45.2492 |
| m2 | 4 | 4 | 33.8213 | 29.2618 |
| 372:168 weighted | 17 | 17 | 48.1948 | 40.2754 |

Thus the relative ridge improvement is not an artifact of the three chosen
fold locations. The weakness is test calibration: historical walk-forward MSE
is still roughly `5.70` below the public score.

At road level, ridge is net better on 1,165 roads and net worse on 91. It wins
all three official folds on 523 roads and two folds on 706 roads. Yet in the
latest fold only 531 roads improve while 725 worsen. The global mean therefore
hides broad late-period regression even though early/middle gains are real.
The top 100 roads account for 36.1% of positive gain, so the improvement is not
only a handful of roads, but it is still uneven.

## Distribution shift

The test histories confirm a low-speed shift, especially for m2:

- m2 median global history speed is `46.64` km/h versus `49.30` in train;
- 67/168 (`39.9%`) m2 test samples fall below the train-history 10th percentile;
- zero m2 test samples lie above the train 75th percentile;
- standardized m2 test features have means from `-0.38` to `-0.54` for the four
  speed-level summaries and 2.94% of feature values exceed `|z| > 3`, versus
  1.48% in m1;
- the final m2 ridge forecast is on average `+0.75` km/h above mean15, rising
  from `+0.56` at h5 to `+0.93` at h15;
- in the latest m2 fold the signed ridge bias is already positive and increases
  by horizon: `+1.28`, `+1.59`, and `+1.86` km/h.

This is a credible failure mode: ridge shrinks low-speed histories upward just
where test m2 is concentrated. Still, test-distribution reweighting over six
history-speed bins yields estimated MSE `39.4152`, not `45.980`. Treat the shift
as a stress-test axis, not as proof of the hidden labels.

The structural-zero guard remains safe. All-zero histories almost always stay
zero at the targets, regime separation remains unambiguous, and no test window
or complete last row exactly matches train.

## Required follow-up

1. Keep `d1-e002-ridge` as the reproducible anchor; do not reinterpret the
   public score as evidence of code leakage.
2. Add a diagnostic low-speed/m2 stress table and the latest-tail result to the
   review gate for new candidates. Do not replace or move frozen official folds.
3. Require a new candidate to improve more than the overall mean: inspect all
   folds/horizons, low-speed m2 bins, signed bias, worst fold, and prediction
   shift relative to ridge.
4. Do not tune coefficients or blends to one 30% public score. Preserve the
   remaining four slots for preregistered, locally robust hypotheses.
5. Prioritize genuinely new causal information (for example official event
   text) over another near-identical lag/ridge parameterization.

No main-pipeline change was made by this audit.
