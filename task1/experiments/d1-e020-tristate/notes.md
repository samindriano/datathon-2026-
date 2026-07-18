# d1-e020-tristate

Status before scoring: `RUNNING / PREREGISTERED`.

This is the final Task 1 modeling experiment. E013, E014, and E016 remain
frozen; their failed gates are not revised. E020 tests one new ensemble
hypothesis: global mean, congestion distribution, and latent spatial state have
partially complementary temporal errors, so their equal prediction average may
retain low-rank gain while shrinking rare-state variance.

Frozen design:

- exact `1/3` prediction average of E013, E014, and E016;
- equivalently `75% E010 + 1/12` each global, distribution, and low-rank state;
- rank 4, 360 PCA rows, alpha 0.1, and text z-threshold 3.0;
- no weight, rank, threshold, component, seed, or fold search;
- unchanged `d1-multifold-v1` and 120-origin chunks.

Acceptance requires at least 2% mean improvement over E013, all folds and
horizons, improved worst fold/std, 18/18 cells, at least 35/36 chunks, median
chunk gain >=0.50, worst chunk >=-0.10, nonpositive test-m2 correction versus
ridge, test RMS change versus E013 <=1.0, and finite/nonnegative zero-guarded
predictions. Any failure means `REJECT / DO NOT SUBMIT`, no CSV, and no E021.

Leakage boundary: all component preprocessing and model fits occur separately
inside each training fold. Validation targets are used only for scoring.
