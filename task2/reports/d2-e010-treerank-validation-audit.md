# D2 E010 TreeRank Validation Audit

## Verdict

- Candidate commit `13194222f3390c2532f388936eaa35e791496dfc`:
  **NO-GO / REJECT**.
- Submission: **DO NOT SUBMIT**.
- Leakage review: no material outer-fold or leave-one-row-out leakage found.
- The preregistered rejection is sound; do not retune, blend, or rescue E010.

E010 reproduces at mean accuracy `0.255556`, below immutable E002
`0.285333` by `-0.029778`. It loses all five folds, lowers the worst fold,
and fails category-OOD. Four primary promotion gates fail. Passing runtime,
distribution, mutation, and validator checks cannot override those failures.

## Immutable scope

- Audited commit: `13194222f3390c2532f388936eaa35e791496dfc`.
- Exact direct parent: `8365193fd84d754e8b9b45a9b7f9b4af5f201f7a`.
- Comparator: immutable E002 at that parent.
- Validation: unchanged `d2-targetgroup-v1`, seed `20260719`.
- Diff contains exactly six added E010 files:
  `config.json`, `metrics.json`, `notes.md`, `treerank.py`, runner, and test.
- No baseline, E002, official validation, notebook, submission registry, or
  unrelated file is modified by the candidate commit.

## Reproduction evidence

The commit was exported to a temporary snapshot and evaluated against the
official extracted CSVs. No MAIN worktree file was used as candidate code or
modified during reproduction.

| Check | Stored | Reproduced | Result |
|---|---:|---:|---:|
| Mean accuracy | 0.255556 | 0.255556 | exact |
| Fold predictions/metrics | recorded | reproduced | exact |
| CSV SHA-256 | `d91a0807...49518` | `d91a0807...49518` | exact |
| int64 prediction SHA-256 | `a8fa5831...e4ea0b` | `a8fa5831...e4ea0b` | exact |
| Runtime | 68.2639 s | 68.9494 s | pass |
| Related tests | 19 passed | 19 passed | pass |

All stable metrics match after excluding runtime and the temporary archive's
line-ending representation of `config.json`. The actual Git blob is LF and
has SHA-256 `1745267102e56ca21c84236279932537743f98d536748de5e9b1413b387a30bc`,
which exactly matches `config_sha256_frozen_before_scoring`. The ZIP extraction
materialized CRLF (`c6c55b...`); this is an archive EOL effect, not config drift.

## Fold hashes and comparator

All five independently recomputed target hashes match the frozen baseline
manifest and the E010 metrics:

| Fold | Target SHA-256 | E002 | E010 | Delta |
|---:|---|---:|---:|---:|
| 0 | `bc8e8ecf...17d4a` | 0.290556 | 0.265000 | -0.025556 |
| 1 | `0a458097...d488` | 0.282778 | 0.250556 | -0.032222 |
| 2 | `de428921...5bf8` | 0.278333 | 0.253333 | -0.025000 |
| 3 | `64997cac...a09` | 0.280556 | 0.250556 | -0.030000 |
| 4 | `b230f312...5f27` | 0.294444 | 0.258333 | -0.036111 |

The runner refits and reproduces E002 within each outer fold, then requires
exact equality with the immutable stored E002 fold vector. Independent checks
confirmed equality in 5/5 folds. E010 has `0/5` wins and worst fold
`0.250556`, versus E002 worst fold `0.278333`.

## Outer-fold and leave-one-row-out audit

Every label-derived graph, edge count, global next count, candidate set, and
fallback is built from the 7,200-row outer training side only. Validation
targets have zero overlap with outer-training targets. Titles and categories
are official static metadata available at test time.

For each source training row, the implementation copies the exact-current and
global next-label counters, subtracts that row's positive label, removes zero
counts, and only then constructs candidates and features. If the positive
candidate disappears, the row is skipped. If no negative remains, it is also
skipped. Used rows receive total weight 0.5 on the positive and 0.5 across all
negatives.

An independent counter reconstruction, not using `TreeRanker`, matched every
recorded fold diagnostic exactly:

| Fold | Used | Positive absent | No negative | Candidate rows |
|---:|---:|---:|---:|---:|
| 0 | 1,233 | 4,970 | 997 | 3,002 |
| 1 | 1,220 | 4,983 | 997 | 2,948 |
| 2 | 1,234 | 4,976 | 990 | 2,993 |
| 3 | 1,237 | 4,994 | 969 | 2,987 |
| 4 | 1,219 | 5,004 | 977 | 2,957 |

The full-data reconstruction also matches exactly: 2,024/9,000 usable source
rows, 5,802 skipped because the LOO positive disappears, 1,174 skipped for no
negative, and 5,149 expanded candidate rows. The very low usable-row fraction
is a genuine feasibility limitation, not justification for weakening LOO.

## Mutation and leakage checks

- `state_id` is not used by fold assignment, training features, or prediction.
- Mutating validation `state_id` leaves predictions exact in all five folds.
- Mutating validation `next_article_id` leaves predictions exact in all folds.
- Independently mutating held-out labels and IDs in the full frame leaves each
  outer-training input byte-for-byte/dataframe-equal.
- Candidate predictions for seen currents come from outer-training outgoing
  labels; unseen currents use the outer-training global mode.
- No external data, OCR, pretrained model, API, or validation label is used.

The mutation checks are adequate for this architecture. No hidden rescue or
parameter selection is present: features, histogram-tree parameters, seed,
weights, tie-breaks, fallback, and gates are fixed in the committed config.

## Frozen gates

| Gate | Threshold | Result | Verdict |
|---|---:|---:|---:|
| Mean accuracy | >= 0.290333 | 0.255556 | FAIL |
| Fold wins vs E002 | >= 4/5 | 0/5 | FAIL |
| Worst fold | >= 0.273333 | 0.250556 | FAIL |
| Current-unseen | >= 0.118539 | 0.123539 | PASS |
| Category-OOD | >= 0.310200 | 0.278400 | FAIL |
| State-ID mutation | exact | exact | PASS |
| Held-out-label mutation | exact | exact | PASS |
| Test unique predictions | >= 337 | 465 | PASS |
| Test top share | <= 0.3252 | 0.1840 | PASS |
| Runtime | <= 300 s | 68.26/68.95 s | PASS |
| Validator | READY | READY, 6,000 rows | PASS |

## Distribution and diversity

E010 does not collapse: 465 test labels are predicted and the top share is
`0.184`. It disagrees with E002 on `11.4556%` of OOF rows and `17.4167%` of
test rows. However, disagreement is harmful rather than complementary: E010
is uniquely correct on 116 OOF rows while E002 is uniquely correct on 384.

Seen-current accuracy drops from E002 `0.325698` to `0.288491`. Unseen-current
accuracy remains `0.123539` only because both preserve the same fallback.
Entirely-unseen-category accuracy falls from `0.315200` to `0.278400`.

## Final decision

The immutable evidence confirms the scout verdict. E010 is leakage-safe and
reproducible, but decisively inferior to E002 on every fold and key OOD
behavior. Preserve it as negative structural evidence only. **REJECT / DO NOT
SUBMIT**, with no feature, parameter, seed, threshold, fallback, blend, or
ensemble rescue. E011 remains stopped.
