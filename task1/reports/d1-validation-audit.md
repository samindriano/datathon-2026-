# D1 Validation and Leakage Audit

Time: 2026-07-18 12:07-12:17 WIB  
Role: VALIDATION  
Task: `D1-VAL-001`  
Data source: official `datathon-task-1.zip` archive (read-only, not committed)

## Verdict

`INVESTIGATE`

The baseline implementation is a valid leakage-free no-training forecast, and
its history/target indexing, MSE aggregation, and submission order are correct.
However, the reported MSE of `29.6995` comes from one 540-origin tail slice per
block, gives the two blocks equal weight, and selects the method on the same
slice used for reporting. It is not yet a defensible official comparison score.

Submission verdict for `d1-e001-persist`: **DO NOT SUBMIT yet**. Preserve the
five-slot budget until the score is reproduced under multi-fold chronological,
regime-weighted validation.

## Verified data contract

| Item | Evidence |
| --- | --- |
| Train speeds | m1 `(11160, 1260)` and m2 `(5039, 1260)`, both `float32`, finite, nonnegative |
| Test histories | `(540, 15, 1260)`, `float32`, finite |
| Targets | h5, h10, h15 = +20, +40, +60 minutes |
| Metric | unweighted MSE over every sample, horizon, and road |
| Submission | 2,041,200 unique IDs in exact sample-horizon-road order |
| Graph | `(1260, 1260)` binary adjacency, 1,260 self-loops, 3,862 off-diagonal directed edges |
| Metadata | 1,260 lists containing 7,122 underlying road-link dictionaries; output index is the outer list index |
| Spatial mask | length 1,296 = 36 x 36, with 1,260 active cells |

The metadata structure is important: do not flatten the 7,122 link records and
align them directly to the 1,260 outputs. Aggregate link metadata within each
outer road/grid group.

## Main findings

### 1. There are two identifiable coverage regimes

- m1 has 13 roads that are zero for the entire block.
- m2 has 210 roads that are zero for the entire block.
- Test contains 372 m1-like samples and 168 m2-like samples.
- The test proportions are 68.8889% / 31.1111%, nearly identical to the train
  timestep proportions 68.8931% / 31.1069%.
- Test samples have 13-16 or 210-211 roads that are zero throughout their
  15-step history, so regime identity is available without using hidden data.

This is structural sensor/coverage behavior, not ordinary congestion. A road
whose complete 15-step history is zero remains zero at the targets more than
99.9% of the time in both train blocks. Preserve an explicit all-zero-history
guard, or at minimum verify that every model naturally retains zero predictions
for these roads.

### 2. No direct test shortcut was found

- Zero test last rows exactly match a train row.
- Zero complete test windows exactly match a train window.
- Zero test windows overlap another test window by a one-step temporal shift.
- Test has no duplicated complete speed-history windows.
- Only 2 of 540 test texts exactly occur in train; each of those text values is
  repeated six times in train.

The test order appears shuffled and independent. Do not infer targets from
neighboring test samples or use exact text lookup.

### 3. Random row/window splitting would leak heavily

Training texts are persistent: adjacent text is identical 42.5% of the time in
m1 and 54.0% in m2, with maximum unchanged runs of 116 and 104 timesteps.
Speed windows also overlap by 14 of 15 rows when consecutive origins are used.
A random split would put nearly identical histories and repeated event text on
both sides of the split.

Use chronological blocks. For any fitted model, the last training origin must
have all of its targets before the first validation origin; with maximum horizon
15, purge training origins whose target reaches the validation period. Fit
scalers, imputers, text vectorizers, dimensionality reduction, feature
selection, and graph normalizers on the training fold only.

### 4. The current tail score is optimistic and fold-sensitive

Independent diagnostic baselines over every valid origin gave:

| No-fit method | h5 | h10 | h15 | Mean MSE |
| --- | ---: | ---: | ---: | ---: |
| Last value | 48.475 | 59.293 | 66.829 | 58.199 |
| Mean of last 5 | 38.608 | 47.863 | 55.113 | 47.194 |
| Mean of last 15 | 39.762 | 47.608 | 54.502 | 47.291 |

These are broad diagnostics, not a replacement for chronological folds. Their
difference from the reported tail MSE `29.6995` shows strong temporal
difficulty variation. For the horizon-aware mean baseline, daily MSE ranges
from 31.659 to 73.964 in m1 and 25.436 to 40.260 in m2. The final m1 days used by
the current tail slice are among the easiest days in the block.

The current evaluator also uses 540 origins from each block, which weights m1
and m2 50/50. Official comparison should weight block-level scores using the
observed test mixture 372/540 and 168/540, or construct validation samples in
that ratio. The present mean15 block scores happen to be close, but this will
not generally remain true for learned models.

### 5. Text and graph signals need guarded experiments

- Train text is long (median about 178-184 words and 27-28 clauses), highly
  repeated locally, but almost never an exact test match. Start with causal,
  low-dimensional event counts or train-fold-only text features; memorization
  is not credible.
- Event text uses English/transliterated road names while static metadata uses
  Chinese names. A direct string join is not currently available and must not
  be fabricated.
- The adjacency is almost symmetric but contains 64 weak components. Raw speed
  smoothness is not guaranteed: m1 adjacent-road speed differences were not
  smaller than deterministic random road pairs in the audit sample. If using a
  graph model, retain strong self/history paths and validate graph effects on
  residuals rather than blindly averaging neighbor speeds.

## Review of `d1-e001-persist`

Confirmed:

- `validation_windows` uses history `t-14..t` and targets `t+5,t+10,t+15`.
- Windows do not cross train-block boundaries.
- No future target is used by the no-training predictors.
- MSE implementation matches the official elementwise mean.
- Submission reshape/order matches the 2,041,200-row template.
- Targeted tests pass: `3 passed`.

Required before treating its score as official:

1. Replace the single tail estimate with at least three multi-day,
   chronological folds per independent block.
2. Report every fold, horizon, block/regime, mean, standard deviation, and worst
   fold; aggregate regimes at 372:168.
3. Separate method selection from final reporting, or preregister mean15 before
   scoring the reporting folds.
4. Preserve/verify the all-zero-history road guard.
5. Record owner, branch/commit, dataset and validation versions, leakage check,
   artifact paths, and recommendation in the experiment metadata.
6. Treat upper clipping at 160 km/h as a model choice requiring validation;
   only the nonnegative lower bound is physically certain. Clipping is inert
   for the current mean prediction, whose maximum is about 101.93 km/h.

## Recommended official validation shape

- Keep m1 and m2 as separate chronological series.
- Use expanding-origin folds with contiguous multi-day validation blocks.
- Purge 15 origins at each train/validation boundary so no training label
  reaches the validation period.
- Score each block separately, then combine at 372/540 for m1 and 168/540 for
  m2.
- Report h5, h10, and h15 separately as well as the exact combined MSE.
- Use fold-level variability and worst fold for model decisions; do not select
  from the mean alone.
- Keep a broad no-fit reference (mean5/mean15) to detect suspiciously large
  gains from leakage or fold selection.
