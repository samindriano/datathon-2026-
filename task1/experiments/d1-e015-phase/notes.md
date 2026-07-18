# d1-e015-phase

Status before scoring: `RUNNING / PREREGISTERED`.

Hypothesis: the continuous blocks encode a 360-step daily cycle. A training-only
phase prototype can learn road-specific recurring future deltas that are absent
from E013's local, text, graph-context, and aggregate city-state regressions.

Frozen design before any score:

- infer phase from the complete 15-step trajectory of four training-only road
  speed strata;
- estimate a per-phase, per-horizon, per-road delta from training origins only;
- predict with fixed `75% E013 + 25% seasonal phase`;
- no period, group-count, distance, threshold, or blend-weight search;
- use unchanged `d1-multifold-v1` and 120-origin temporal chunks.

Acceptance requires at least 1% mean improvement over E013, all three folds and
horizons improving, improved worst fold and fold standard deviation, at least
17/18 block-fold-horizon cells and 34/36 chunks improving, median chunk gain at
least 0.30 MSE, no chunk below -0.25 MSE, and finite/nonnegative zero-guarded
test predictions. Failure means `REJECT`; no tuning follow-up and no Kaggle slot.

Leakage boundary: all road strata, phase templates, feature scaling, and future
deltas are fit independently inside each training fold. Validation history is
used only to infer phase; validation targets are never features.
