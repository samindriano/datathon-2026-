# d1-e019-orthostate

Final status: `REJECT / DO NOT SUBMIT`.

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

Frozen-run result:

- E013 reference MSE: `36.560253`;
- orthostate component MSE: `33.311566`;
- fixed orthoblend MSE: `35.468004` (`2.9875%` better than E013);
- all folds, horizons, worst fold, and fold standard deviation improve;
- only `17/18` block-fold-horizon cells and `33/36` chunks improve;
- median chunk gain: `0.802959`, but worst chunk: `-1.415704`;
- inference diagnostics remain conservative and valid;
- no submission CSV was produced.

Interpretation: separating city level strengthens the aggregate latent signal
but materially worsens rare-regime tail risk. This fails the explicit purpose
and frozen safety gates of E019. Do not adjust residualization, rank, PCA rows,
alpha, or blend weight from this result.
