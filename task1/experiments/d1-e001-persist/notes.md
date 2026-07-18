# d1-e001-persist

## Hypothesis

A last-value, short rolling-mean, or damped local-trend forecast provides a
fast leakage-safe baseline from the exact 15-step history available at test
time.

## Scope

- Uses speed history only.
- Does not use event text or the road graph yet.
- Does not train a fitted model.
- Uses contiguous tail-origin backtests separately within each train block.
- Must be reviewed by VALIDATION before any Kaggle submission.

## Decision

`INVESTIGATE` until chronological validation and submission schema are audited.
