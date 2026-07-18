# d1-e017-dynamics

Status before scoring: `RUNNING / PREREGISTERED`.

Hypothesis: asymmetric per-road acceleration and recovery patterns contain
causal signal not represented by the five linear history summaries in E013.

Frozen before scoring:

- ten local features: last, mean3/5/15, separate positive and negative slope,
  three-window curvature, recent-vs-hour gap, hour range, and hour standard
  deviation;
- independent per-road ridge with alpha 0.1;
- fixed `75% E013 + 25% dynamics`; no feature, alpha, or weight search;
- unchanged official validation and 120-origin chunks.

Acceptance requires at least 1% mean gain over E013, all folds and horizons,
improved worst fold/std, 17/18 cells, 34/36 chunks, median chunk gain >=0.30,
worst chunk >=-0.25, and valid zero-guarded test predictions. Otherwise reject
without follow-up tuning or a Kaggle slot.

Leakage boundary: feature standardization and coefficients are fit per training
fold. Every feature uses only the supplied 15-step history.
