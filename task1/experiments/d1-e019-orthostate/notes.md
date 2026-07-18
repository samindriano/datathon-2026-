# d1-e019-orthostate

Status before scoring: `RUNNING / PREREGISTERED`.

E016 is frozen `REJECT`; its rank, PCA sample count, alpha, weight, and failed
threshold are not changed. E019 tests a new representation hypothesis: E016's
latent factors may duplicate city-level congestion and become unstable in rare
late regimes. Explicit city summaries are retained while PCA is fit only to
cross-sectionally residualized road states.

Frozen design:

- rank 4 and 360 evenly spaced training-only PCA rows;
- subtract the active-road cross-sectional standardized mean before PCA;
- concatenate five local, five explicit city, and twenty residual-factor
  temporal summaries in one per-road ridge with alpha 0.1;
- fixed `75% E010 + 25% orthostate`; no rank/sample/alpha/weight search;
- unchanged official folds and 120-origin chunks.

Because this is an adaptive follow-up, acceptance is stricter than E016: mean
must improve E013 by at least 1%, all folds/horizons, worst fold/std, all 18/18
cells, and all 36/36 chunks must improve; median chunk gain >=0.25; worst chunk
must be positive; inference correction must remain conservative and valid.
Failure means `REJECT` with no retuning, notebook, CSV, or Kaggle slot.

Leakage boundary: road standardization, active mask, cross-sectional removal,
PCA basis, feature scaling, and ridge coefficients are independently fit inside
each training fold. Validation targets never enter features or preprocessing.
