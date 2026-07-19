# D1 E007 Graphres Independent Validation Audit

- Time: 2026-07-18 13:48-13:53 WIB
- Role: VALIDATION
- Reviewed commit: `81bb9f1`

## Verdict

- Graph construction and leakage: `GO`
- Local candidate: `KEEP`
- Claim that the gain is topology-specific: `NO-GO`
- Kaggle slot 2 now: `INVESTIGATE` — **DO NOT SUBMIT** until a clean inference
  notebook reproduces this candidate and SUBMISSION validates it.

Graphres is currently the strongest defensible slot-2 candidate after that
reproducibility gate. It improves ridge by `0.849830` MSE (`2.18%`), improves
all 18 block-fold-horizon cells, improves the latest tail, and moves the shifted
m2 test predictions in the direction that reduces ridge's known overprediction.

The city adjacency itself is not responsible for most of the gain. Three graph
nulls made by relabeling the same topology score essentially the same as or
slightly better than the real topology. Graphres should therefore be described
as a sparse cross-road/city-state model, not evidence that adjacent-road causal
propagation was learned.

## Construction and leakage checks

- Official adjacency is the only static graph input.
- Directed edges are converted to a deterministic symmetric union.
- All 1,260 diagonal self-links are removed.
- The resulting external edge list has 3,892 directed entries (1,946 undirected
  pairs), 13 isolated roads, and external degrees from 0 to 10.
- Non-isolated row weights sum to one; an independent dense implementation
  matches sparse neighbor features to maximum absolute difference `1.31e-05`.
- All local and neighbor feature moments, scales, target means, covariances, and
  coefficients are fitted on training origins only.
- Validation/test histories are used only for prediction.
- The all-zero history guard and nonnegative floor are retained.
- No test target, event text, external data, API, pretrained weight, or new
  dependency is used.

No leakage defect was found. The symmetric-union choice is a preregistered
model choice; it is not inferred from validation labels.

## Independent reproduction

- 28 tests pass.
- Ridge: `39.024844`.
- Graphres: `38.175014`.
- Folds: `43.747325`, `39.942200`, `30.835516`.
- Horizons: `32.281328`, `38.809405`, `43.434307`.
- In each of the six block/fold cells, between 710 and 989 of 1,260 roads
  improve over ridge.
- Prediction range remains finite and credible, and structural zeros stay zero.

## Topology null result

The real graph and three deterministic node-relabel nulls were each fitted from
scratch on the frozen folds:

| Graph | Mean MSE | Difference from real |
| --- | ---: | ---: |
| Real city graph | 38.175014 | 0.000000 |
| Relabel null A | 38.214062 | +0.039048 |
| Relabel null B | 38.169004 | -0.006010 |
| Relabel null C | 38.165236 | -0.009778 |

Two of three wrong graphs slightly beat the real graph. The `0.85` gain over
per-road ridge is therefore mostly produced by generic cross-road summaries
that proxy network-wide traffic state. Selecting the best random graph/seed
after these diagnostics would be validation hacking and must not be done. Keep
the deterministic official graph if this model proceeds.

## Shift and stress behavior

Graph feature shift is much less severe than textres:

- m1: 1.32% of graph feature values exceed `|z| > 3`;
- m2: 3.40% exceed `|z| > 3`, including 3.85% of neighbor features;
- mean graph-minus-ridge correction is `+0.046` km/h in m1 and `-0.245` in m2;
- m2 corrections are negative at all horizons (`-0.228`, `-0.251`, `-0.257`),
  the helpful direction for ridge's positive low-speed bias.

Where low-speed validation samples exist, graphres also improves them. In the
latest m2 fold below the train 10th-percentile speed, MSE falls from `28.5563`
to `27.5079` and signed bias from `+2.202` to `+1.659` km/h.

Corrections are usually small (RMS `1.05` m1 and `1.15` m2). Absolute changes
above 10 km/h affect only `0.058%` of m1 and `0.088%` of m2 predictions, though
the largest individual corrections reach `35.6` and `26.3` km/h. Submission
review should retain range/distribution checks.

## Recommendation to MAIN

1. Keep graphres as the leading next candidate, while documenting that the
   benefit is generic cross-road context rather than validated road topology.
2. Do not create or select random-graph variants from the null seeds.
3. Build a clean Kaggle inference notebook for the exact official-graph commit,
   reproduce its CSV, and obtain SUBMISSION `READY` before using slot 2.
4. Prefer graphres over the current exact textres for slot 2 because graphres
   has the larger broad local gain and safer m2 correction direction.
5. If MAIN tests a graph-plus-safe-text ensemble, preregister it as a new
   hypothesis and compare on the same frozen folds; do not tune its blend from
   public leaderboard feedback.

No model, official validation, notebook, or submission artifact was changed by
this audit.
