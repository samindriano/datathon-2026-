# D2 E002 MetaRank Validation Audit

## Verdict

- Candidate `d2-e002-metarank` at commit `8365193`: **GO / KEEP**.
- Frozen gate result: **10/10 PASS**.
- Leakage review: **GO; no material validation leakage found**.
- Submission: **INVESTIGATE / DO NOT SUBMIT** until a candidate notebook is
  independently reproduced and reviewed. This audit did not use a Kaggle slot.

E002 is a real and consistently distributed improvement over
`d2-baseline-v1`, not a one-fold gain. Its exact-match accuracy increases from
`0.261333` to `0.285333` (`+0.024000` absolute), all five folds improve, and
both the worst fold and the entirely-unseen-target-category subset improve.

## Scope and immutable inputs

- MAIN handoff commit: `8365193fd84d754e8b9b45a9b7f9b4af5f201f7a`.
- Baseline tag/commit: `d2-baseline-v1` / `0f94a1c`.
- Experiment: `d2-e002-metarank`.
- Validation: unchanged `d2-targetgroup-v1`, five target-disjoint folds, seed
  `20260719`.
- Independent audit branch/worktree: `codex/audit-d2-e002-metarank`.
- The model, folds, notebook, raw data, and submission registry were not
  modified. Reproduction output was written only to a temporary directory.

## Frozen method verification

The implementation matches the preregistered rule:

```text
2 * Jaccard(candidate categories, target categories)
+ 1 * Jaccard(candidate title tokens, target title tokens)
```

Candidate sets and frequency tie-break statistics are derived only from the
training portion of each fold. Ties are resolved by current-specific frequency,
then global next-label frequency, then smaller article ID. Unseen currents use
the fold-training global mode. The code and config use fixed weights `2.0:1.0`,
the lowercase ASCII-alphanumeric set tokenizer, five folds, and seed
`20260719`; no weight, tokenizer, threshold, fold, or seed search is present.

Article titles and categories are official static competition metadata. Using
the target article's metadata mirrors test-time availability and is not target
label leakage.

## Independent reproduction

The committed runner was executed against the official extracted CSVs with the
tracked baseline artifacts. After normalizing only the environment-dependent
output path and runtime, the reproduced `metrics.json` matches the committed
object exactly.

| Reproduction check | Result |
|---|---:|
| Stable `metrics.json` fields | Exact |
| Stored runtime | 12.038961 s |
| Reproduced runtime | 6.485703 s |
| Stored/reproduced CSV SHA-256 | `87b4a480008eabe06921a36edc14ea12abf4a006b86850f5260d959c54ad3d81` |
| Baseline/validation/metarank tests | 7/7 passed |
| Submission-validator tests | 12/12 passed |

The submission CSV itself is intentionally not tracked, but the independently
generated file exactly matches its recorded SHA-256.

## Frozen gate evaluation

| Gate | Requirement | Evidence | Result |
|---|---|---|---:|
| Reference reproduction | accuracy `0.285333` | `0.2853333333333333` exact | PASS |
| Mean improvement | at least `+0.010` | `+0.024000` | PASS |
| Fold wins | at least 4/5 | 5/5 | PASS |
| Worst fold | not below `0.255000` | `0.278333` | PASS |
| Current-unseen delta | at least `-0.005` | `0.000000` | PASS |
| Entirely-unseen-category delta | at least `-0.005` | `+0.035200` | PASS |
| Target disjointness | seen rate zero | `0.0` in 5/5 folds | PASS |
| State-ID ablation | exact | exact in 5/5 folds | PASS |
| Runtime | below 180 s | 12.04 s stored; 6.49 s reproduced | PASS |
| Submission validation | valid 6,000 rows | validator `READY` | PASS |

The fold standard deviation rises slightly from `0.005195` to `0.006142`, but
this is not a frozen rejection gate and is not evidence of fragility: every
fold improves and the worst absolute fold improves by `+0.023333`.

## Fold stability

| Fold | Baseline | E002 | Gain | Prediction change rate |
|---:|---:|---:|---:|---:|
| 0 | 0.267778 | 0.290556 | +0.022778 | 0.131111 |
| 1 | 0.255556 | 0.282778 | +0.027222 | 0.126111 |
| 2 | 0.265556 | 0.278333 | +0.012778 | 0.125000 |
| 3 | 0.255000 | 0.280556 | +0.025556 | 0.121111 |
| 4 | 0.262778 | 0.294444 | +0.031667 | 0.140556 |

The smallest fold improvement is still `+0.012778`. Across the 1,159
validation rows whose prediction changes, baseline accuracy is approximately
`0.0759` and E002 accuracy approximately `0.2623`; the total 216 additional
correct predictions account exactly for the `+0.024000` aggregate gain.

## Coverage and OOD behavior

- Current-unseen rows: 1,797. Both models score `0.123539`; delta is exactly
  zero because both use the same fold-training global fallback.
- Entirely-unseen target-category rows: 625. Accuracy improves from `0.280000`
  to `0.315200`.
- Entirely-unseen-category accuracy does not regress in any fold: it is equal
  in fold 0 and higher in folds 1-4.
- Current-seen accuracy by fold is `0.331237`, `0.323034`, `0.322469`,
  `0.314440`, and `0.337781`; all improvement is therefore attributable to
  causal reranking where training-fold candidates exist.
- Next-label and observed-candidate coverage are unchanged from the baseline;
  the model reranks existing candidates rather than manufacturing label
  coverage.

## Candidate provenance and leakage audit

Independent mutation and provenance tests found:

1. Every current-seen prediction in every fold belongs to that current's
   training-fold candidate set (rate `1.0` in all folds).
2. Every current-unseen prediction equals the training-fold global mode.
3. Replacing every validation `state_id` and `next_article_id` leaves all
   predictions identical in all five folds.
4. Refitting after changing only held-out labels also leaves all predictions
   identical in all five folds.
5. Each fold hash is checked against the frozen baseline manifest before model
   fitting, and `target_seen_rate` remains exactly zero.
6. `state_id` is not read by the model. No external data, pretrained embedding,
   OCR, or API is used.

The full official `articles.csv` and `categories.csv` are loaded for static
metadata lookup. This is permitted because the same metadata is available for
test target and candidate articles; no validation next-click label is used to
construct semantic features.

## Prediction distribution and private-risk interpretation

Test predictions change on `0.151333` of rows relative to the baseline. Unique
predictions decrease from 544 to 449, while the top-prediction share changes
only from `0.271500` to `0.275167`. This is a moderate consolidation, not a
single-class collapse, and is consistent with deterministic semantic reranking.

Local evidence is strong enough for `KEEP`: 5/5 fold gains, improved worst
fold, unchanged current-unseen behavior, improved category-OOD behavior, and
exact reproduction. It does not yet establish submission readiness because the
final inference notebook has not been updated and independently reproduced for
E002. Public/private leaderboard performance also remains unknown.

## Handoff recommendation

MAIN may retain E002 as an accepted candidate and compare later structural
experiments against it on the frozen harness. If E002 remains competitive, the
next authorized step is a separate candidate-notebook reproduction and
SUBMISSION review. Until that succeeds, the explicit submission verdict is
**DO NOT SUBMIT**.
