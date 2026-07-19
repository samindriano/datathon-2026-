# D2 E001 Baseline Validation Audit

## Verdict

- Validation harness `d2-targetgroup-v1`: **GO** for model comparison.
- Baseline `d2-e001-baseline`: **DIAGNOSTIC ONLY**.
- Submission: **DO NOT SUBMIT**.

The five target-group folds at MAIN commit `0f94a1c` are deterministic,
target-disjoint, balanced at 72 targets and 1,800 rows each, and reproducible
from the official extracted CSV data. No material train/validation leakage was
found in the baseline. The baseline is useful as a fixed comparison floor, but
its limited transition coverage and global fallback do not justify spending a
Kaggle slot.

## Scope and boundaries

- Audited snapshot: MAIN commit `0f94a1c` (`d2-e001-baseline`).
- Validation version: `d2-targetgroup-v1`.
- Independent branch: `codex/audit-d2-e001-validation` in a separate worktree.
- Data were read from `task2/data/competition/dataset-task2/` in the MAIN
  workspace because raw competition data are intentionally ignored by Git.
- Reproduction output was written only to a temporary directory. No model,
  fold, notebook, raw-data, or submission-slot mutation was made.

## Reproduction

The committed runner was executed with its frozen defaults: five folds and
seed `20260719`. The focused baseline and validation tests also passed (3/3).

| Check | Result |
|---|---:|
| Manifest byte-for-byte reproduction | PASS |
| Source/reproduced manifest SHA-256 | `9aa3570b354702d3cd5a357a7014a4a85796f4ae52bf4ea120b5256a95c1b6ac` |
| Stable `metrics.json` fields exact | PASS |
| Recorded runtime | 4.962540 s |
| Reproduced runtime | 4.129760 s |

The only expected `metrics.json` differences were the temporary submission
path and wall-clock runtime. After normalizing those two environment-dependent
fields, the JSON objects matched exactly.

## Fold and manifest integrity

All 360 train targets occur exactly once in the manifest. There are no missing
or duplicated target assignments, and the manifest target universe exactly
matches the 360 unique `target_article_id` values in `states_train.csv`.

| Fold | Targets | Rows | Independently recomputed target SHA-256 |
|---:|---:|---:|---|
| 0 | 72 | 1,800 | `bc8e8ecf5a66be6affdf2fae7f2decb2fd377add53d5e1f5ffdfe43aa7517d4a` |
| 1 | 72 | 1,800 | `0a458097d42ba7fde0db28d4887f1d655badd2ededf7daccfd0460932329d488` |
| 2 | 72 | 1,800 | `de428921a9020152dd166b49f05d9365355c77c8d318b7bdae762b8c92ef5bf8` |
| 3 | 72 | 1,800 | `64997cacbbb16182f47506dc371179a46769d7abe5880358a0cb5378d679ba09` |
| 4 | 72 | 1,800 | `b230f3126a424cbde2ab1cc09a7602cdf3f05885ad004e7572ed8a0934895f27` |

For every fold, training contains 7,200 rows and 288 targets, validation
contains 1,800 rows and 72 targets, and the target intersection is empty.
Consequently, `target_seen_rate` is exactly `0.0` in all five folds.

## Baseline score and coverage diagnostics

The exact-match current-mode baseline reproduces mean accuracy `0.261333`,
fold scores `0.267778`, `0.255556`, `0.265556`, `0.255000`, and `0.262778`,
worst fold `0.255000`, and standard deviation `0.005195`. The global-mode
diagnostic is `0.116444`; predicting the current article is `0.000000`.

| Fold | Accuracy | Current seen | Seen acc. | Unseen acc. | Next-label seen | Observed candidate |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.267778 | 0.795000 | 0.302586 | 0.132791 | 0.943333 | 0.307778 |
| 1 | 0.255556 | 0.791111 | 0.288624 | 0.130319 | 0.941111 | 0.298333 |
| 2 | 0.265556 | 0.801111 | 0.306519 | 0.100559 | 0.936111 | 0.307222 |
| 3 | 0.255000 | 0.823333 | 0.283401 | 0.122642 | 0.950000 | 0.303333 |
| 4 | 0.262778 | 0.791111 | 0.297753 | 0.130319 | 0.939444 | 0.310000 |

Aggregate coverage across all 9,000 out-of-fold rows:

- current seen: 7,203/9,000 (`0.800333`), accuracy `0.295710`;
- current unseen: 1,797/9,000 (`0.199667`), accuracy `0.123539`;
- next label observed in the training fold: 8,478/9,000 (`0.942000`);
- exact next label observed among the training outgoing candidates for the same
  current article: 2,748/9,000 (`0.305333`).

The test current-seen rate is higher at `0.874167`, so the group validation is
somewhat harsher on current-article coverage than the observed test inputs.
That does not reveal hidden test labels and is not a reason to rescale or tune
the validation score.

## Target-category OOD reporting

Every one of the 360 train target articles has category metadata. The
entirely-unseen-category counts by fold are 3, 3, 10, 5, and 4 targets. Because
each target contributes 25 states, this is 625 rows from 25 targets in total.

| Fold | Entirely unseen targets | Seen-category acc. | Entirely-unseen-category acc. |
|---:|---:|---:|---:|
| 0 | 3 | 0.266667 | 0.293333 |
| 1 | 3 | 0.253913 | 0.293333 |
| 2 | 10 | 0.261290 | 0.292000 |
| 3 | 5 | 0.254925 | 0.256000 |
| 4 | 4 | 0.262941 | 0.260000 |

Aggregated accuracy is `0.259940` on 8,375 seen-category rows and `0.280000`
on 625 entirely-unseen-category rows. This baseline does not collapse on that
subset, although the subset is too small and structurally uneven to support a
claim that category generalization is solved.

## State ID and prediction-distribution audit

- `state_id` is never read by `CurrentModeBaseline.fit` or `predict`.
- Replacing every validation `state_id` with unrelated values produces exact
  prediction equality in all five folds.
- Replacing every validation `next_article_id` before prediction, and refitting
  after changing only held-out labels, also produces exact prediction equality
  in every fold.
- Fold construction remains identical when both `state_id` and
  `next_article_id` are changed, confirming that grouping depends only on
  target identity and static category metadata.
- Fold unique prediction counts are 322, 308, 330, 334, and 321; top-prediction
  shares are `0.320000`, `0.332222`, `0.323889`, `0.309444`, and `0.322222`.
- Full-test predictions contain 544 unique article IDs with a top-prediction
  share of `0.271500`; they are not a single-label collapse.

The state-ID ablation result applies only to this baseline. Every future model,
including `d2-e002-metarank`, must repeat the ablation independently.

## Leakage review

No label-derived model feature is built from a validation fold:

1. Fold assignment uses `target_article_id` and static category metadata, not
   `next_article_id` or `state_id`.
2. For each fold, `CurrentModeBaseline.fit(training)` constructs the global
   next mode, per-current next mode, and outgoing candidate sets from the 7,200
   training rows only.
3. Next-label coverage and training-target-category unions are also computed
   from the training fold only.
4. Validation `next_article_id` is consumed after prediction for accuracy and
   diagnostic coverage, not as a model input.

One reporting weakness is noted: the serialized gate field
`target_groups_are_disjoint` is assigned literal `True` rather than computed
from the manifest. This does not invalidate this frozen result because the
runner separately raises on each train/validation target intersection and the
independent manifest audit proves the invariant. Future harness maintenance
should compute the gate explicitly so a reporting flag cannot become stale.

## Decision and handoff criteria

`d2-targetgroup-v1` is approved as the fixed official comparison harness. The
baseline is reproducible and leakage-safe, but remains diagnostic because only
30.53% of validation truths are observed outgoing candidates for their current
article, unseen-current accuracy is only 12.35%, and the method does not use
the richer article metadata. Therefore the submission verdict is **DO NOT
SUBMIT**.

When MAIN hands off `d2-e002-metarank`, review it against baseline `0.261333`
without changing folds or gates. It must improve by at least `+0.010`, win at
least 4/5 folds, not worsen the `0.255000` worst fold, lose no more than `0.005`
on current-unseen accuracy, avoid collapse on entirely-unseen target category,
and remain independent of `state_id`.
