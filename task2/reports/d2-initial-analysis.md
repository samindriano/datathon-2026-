# Task 2 Initial Analysis

Status: baseline complete; complex experiments not started. Independent
VALIDATION verdict: `GO` for `d2-targetgroup-v1`. Baseline verdict:
`DIAGNOSTIC ONLY / DO NOT SUBMIT`.

## Problem contract

- Unit of observation: one navigation state `(current_article_id,
  target_article_id)`.
- Target: the exact `next_article_id` clicked from the current page.
- Metric: exact-match accuracy; higher is better.
- Train: 9,000 states with 360 unique targets.
- Test: 6,000 states with 240 unique targets.
- Crucial split fact: train and test target IDs have zero overlap.
- Test current coverage: 5,245/6,000 rows (87.42%) use a current article seen
  in train.
- Static inputs: 4,604 articles, 129 categories, and one screenshot for every
  article. Blue screenshot text represents outgoing links.
- Submission: exact columns `state_id,predicted_next_article_id`, 6,000 rows,
  preserving sample/test state order. State IDs are not assumed contiguous.

The 4.45 GB ZIP was inspected selectively. Only the five CSV files and eight
representative screenshots were extracted locally; raw data remains ignored by
Git and was not modified.

## Leakage and validation

Random row splitting is rejected. It would let the same target article appear
on both sides even though every hidden-test target is unseen during training.

Official validation uses five deterministic folds grouped by
`target_article_id`. Each fold holds out 72 complete target groups and 1,800
rows. Broad target categories are balanced between folds. All learned
transition counts, encoders, scalers, vocabularies, and model parameters must be
fit only on the training side of each fold.

Required reporting:

- mean, all five fold accuracies, worst fold, and fold standard deviation;
- accuracy for seen-current and unseen-current subsets;
- candidate-link or observed-candidate coverage;
- prediction distribution and runtime;
- explicit leakage verdict.

Primary leakage risks are target memorization, fitting metadata transforms on
all states, using validation labels to construct outgoing candidates, and
tuning repeatedly against the public leaderboard. Article titles, categories,
and screenshots are official static inputs, but label-derived features remain
fold-local.

## Stable baseline: d2-e001-baseline

The model predicts the training-fold mode of `next_article_id` for each current
article. An unseen current uses the global training-fold next-click mode.

| Candidate | Mean accuracy | Worst fold | Fold std |
| --- | ---: | ---: | ---: |
| sample current article | 0.000000 | 0.000000 | 0.000000 |
| global next-click mode | 0.116444 | 0.111111 | 0.004298 |
| current-specific mode | 0.261333 | 0.255000 | 0.005195 |

Current-mode fold scores are `0.267778`, `0.255556`, `0.265556`, `0.255000`,
and `0.262778`. Validation current-seen rate is 79.11%-82.33%, slightly more
pessimistic than test. Observed next-candidate coverage is only
29.83%-31.00%, so frequency retuning alone has little headroom.

Verdict: `KEEP` only as the stable diagnostic floor. Submission verdict:
`DO NOT SUBMIT`.

## Preregistered experiment queue

No experiment below has been scored. Gates are frozen before implementation.

### 1. d2-e002-metarank

- Hypothesis: target-aware title/category similarity can choose the correct
  next click among transition candidates better than current-mode frequency.
- Method: reproduce the audit-only deterministic heuristic exactly. Candidates
  are fold-local observed next labels for the current article; rank by
  `2 * Jaccard(candidate_categories, target_categories) +
  Jaccard(candidate_title_tokens, target_title_tokens)`, then break ties by
  current-specific frequency, global frequency, and smallest article ID.
  Current-unseen rows use the fold-training global mode.
- Runtime risk: low; expected under 3 minutes for five folds.
- Leakage risk: medium if candidate counts or encoders are built on validation
  labels; every learned component must be fold-local.
- Expected benefit: the independent audit-only implementation reported 0.285333
  mean accuracy, +0.024000 over current-mode, but MAIN must reproduce it before
  the number becomes an official experiment result.
- Acceptance gate: reproduce the frozen formula without tuning; at least +0.010
  mean accuracy over baseline, improve at least 4/5 folds, worst fold not worse,
  current-unseen accuracy no more than 0.005 lower, no collapse on entirely
  unseen target-category rows, no state-ID dependence, credible prediction
  distribution, and runtime under 3 minutes.

### 2. d2-e003-routeknn

- Hypothesis: navigation states with similar current/target titles and
  categories share route choices even when target IDs differ.
- Method: instance-based nearest-state retrieval with exact-current bonus and
  fold-local voting over `next_article_id`.
- Runtime risk: medium; sparse/batched similarity is required.
- Leakage risk: medium; vocabulary/IDF and neighbor search index must exclude
  the validation fold.
- Expected benefit: moderate, especially on seen-current rows where the target
  changes which outgoing route is appropriate.
- Acceptance gate: at least +0.015 mean accuracy, improve at least 4/5 folds,
  improve seen-current accuracy by at least 0.010, worst fold no more than 0.005
  below baseline, and full five-fold runtime under 10 minutes.

### 3. d2-e004-linkocr

- Hypothesis: recovering the true outgoing-link set from blue screenshot text
  removes the observed-candidate ceiling and provides valid candidates for
  unseen currents.
- Method: blue-pixel segmentation, offline/open-weight OCR, fuzzy mapping to
  official article titles, then deterministic target-semantic ranking.
- Runtime risk: high because 4,604 screenshots total 4.45 GB and many pages are
  very tall.
- Leakage risk: low for static extraction, medium if mapping thresholds are
  tuned using held-out answers. No API or external data is allowed.
- Expected benefit: high if link recovery is precise; zero if OCR coverage or
  runtime fails.
- Acceptance gate before full extraction: on a fixed 100-page development
  sample, mapped-link precision at least 0.95, labeled true-next candidate recall
  at least 0.70, projected full runtime under 35 minutes, and no external API.
  Model gate after extraction: at least +0.020 mean accuracy, improve at least
  4/5 folds, and no material worst-fold regression.

### 4. d2-e005-semembed

- Hypothesis: an open-weight sentence encoder better captures semantic direction
  from candidate titles toward unseen targets than token/category overlap.
- Method: offline embeddings of official titles only, used to rank candidates
  supplied by observed transitions or a validated screenshot link graph.
- Runtime risk: medium; weights must already be open, available in Kaggle, and
  inference must fit the notebook deadline.
- Leakage risk: low if embeddings are fixed; model selection and any learned
  calibration remain fold-local.
- Expected benefit: moderate and complementary to frequency/retrieval models.
- Acceptance gate: all weights have recorded license/checksum and Kaggle path;
  at least +0.010 mean accuracy over the strongest available non-embedding
  candidate, improve at least 4/5 folds, worst fold no more than 0.003 worse,
  and clean offline inference under 10 minutes.

Expected value per time: `d2-e002-metarank`, `d2-e003-routeknn`, staged
`d2-e004-linkocr`, then `d2-e005-semembed`. Link OCR feasibility may run in
parallel, but it must stop at its preregistered sample gate before costly full
extraction.

## Role split

- MAIN: owns `d2-targetgroup-v1`, stable baseline, experiment integration,
  final model choice, and final notebook.
- VALIDATION: independently audits target-group separation, fold-local fitting,
  duplicate/leakage risks, all preregistered gates, and fold/subset stability;
  it does not edit MAIN model code.
- SUBMISSION: owns fail-closed output checks, local clean-run reproduction,
  Kaggle `Restart Session -> Run All`, dependency/weight/path checks, artifact
  hashes, and readiness verdict; it does not change the model.

The baseline notebook runs unchanged locally and in Kaggle, but it is not yet a
recommended Kaggle slot. The next highest-value modeling action after audit is
`d2-e002-metarank` while link-OCR feasibility is evaluated independently.
