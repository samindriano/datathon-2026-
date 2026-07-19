# Datathon 2026 Team Status

Revision: 0020
Active Day: DAY 2
Active Task: TASK 2
Last Global Update: 2026-07-19 12:58:01 +07:00
Competition Clock: RUNNING
Repository Branch: exp/d2-e002-metarank
Current Stable Commit: 0f94a1cdb8da4929520fce80a64e5203947ed4d9

## 1. Active Competition Brief

- Day: DAY 2
- Task: Wiki Article Next Click Prediction
- Start time: 2026-07-19 12:00 WIB
- End time: 2026-07-19 17:00 WIB
- Notebook deadline: 2026-07-19 18:00 WIB
- Target: exact `next_article_id` clicked from a current Wikipedia article toward a goal article.
- Metric: accuracy (exact match across test states).
- Train path: `task2/data/competition/dataset-task2/states_train.csv` with 9,000 labeled states.
- Test path: `task2/data/competition/dataset-task2/states_test.csv` with 6,000 states.
- Article metadata: 4,604 rows in `articles.csv`; 5,204 category rows across 129 categories.
- Screenshots: 4,604 PNG files in the ZIP, one per article; blue text denotes page links.
- Sample submission path: `task2/data/competition/dataset-task2/sample_submission.csv`.
- Output schema: columns `state_id,predicted_next_article_id`, preserving test/sample state order.
- Official constraints: See `AGENTS.md`.
- Confirmed split signal: train has 360 unique targets, test has 240 unique targets, with zero target-ID overlap; validation must therefore hold out entire target articles.
- Information that remains UNKNOWN: full screenshot-derived outgoing-link coverage, hidden next-click labels, and actual Kaggle notebook runtime for the future competitive candidate.

Only MAIN may update this section.

## 2. Global Decisions

| Decision ID | Time | Decision | Evidence | Owner | Reversal Condition |
|---|---|---|---|---|---|
| D1-DEC-001 | 2026-07-18 12:13 WIB | Use direct mean squared error across samples, horizons, and roads as metric implementation. | Official task statement and `task1/src/baseline.py`. | MAIN | Official clarification changes metric aggregation. |
| D1-DEC-002 | 2026-07-18 12:13 WIB | Treat `d1-e001-persist` mean-of-15 forecast as provisional baseline only. | Tail backtest MSE 29.6995; validation review pending. | MAIN | VALIDATION returns NO-GO or a safer baseline is established. |
| D2-DEC-001 | 2026-07-19 12:15 WIB | Reset Task 2 from `origin/main` on `exp/d2-e001-baseline`; reuse no Task 1 model, metric, validation, feature, or submission assumption. | Official Task 2 is exact-match next-click prediction over Wikipedia states and screenshots, structurally different from Task 1. | MAIN | None; only generic tooling may be reused after compatibility checks. |
| D2-DEC-002 | 2026-07-19 12:15 WIB | Treat target-article-disjoint validation as the leading proposal pending independent audit. | Train and test target sets are disjoint (360 versus 240 unique targets; zero overlap), while 5,245/6,000 test current articles appear in train. | MAIN | VALIDATION demonstrates a more faithful split or finds the observed partition is an artifact. |
| D2-DEC-003 | 2026-07-19 12:38 WIB | Freeze `d2-targetgroup-v1`: five deterministic category-balanced folds grouped by target article, seed 20260719; never use random-row validation. | Independent VALIDATION verdict `GO`; every hidden-test target is unseen, every fold has 72 disjoint targets/1,800 rows, and fold target hashes plus coverage/OOD/state-ID diagnostics are now recorded. | MAIN | Only an official rule/data correction or independently demonstrated structural mismatch can supersede it; model scores do not justify changing folds. |

Only MAIN manages this table; reviewers propose decisions in their role sections.

## 3. Shared Task Board

| Task ID | Day | Owner | Status | Priority | Dependency | Input | Expected Output | Started | Updated | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| D1-MAIN-001 | PREPARATION | MAIN | DONE | MEDIUM | Official competition rules | Open-weight preparation requirement | Offline-ready candidate pantry tooling | 2026-07-17 22:50 WIB | 2026-07-17 23:06 WIB | Metadata/tooling only; no weights downloaded and no model selected. |
| D1-MAIN-002 | PREPARATION | MAIN | DONE | HIGH | GitHub CLI installed and authenticated | Local project files and target `samindriano/datathon-2026-` | Independent Git repository pushed to GitHub | 2026-07-17 23:14 WIB | 2026-07-17 23:32 WIB | Initial baseline commit `53acffe` pushed to `origin/main`. |
| D1-MAIN-003 | PREPARATION | MAIN | DONE | HIGH | Existing experiment protocol | Request for simple, searchable artifact names | Canonical experiment, branch, artifact, and submission naming rules | 2026-07-18 11:57 WIB | 2026-07-18 11:59 WIB | Use one short experiment ID everywhere; submission includes slot and experiment ID. |
| D1-VAL-001 | DAY 1 | VALIDATION | DONE | HIGH | Official Task 1 dataset available | Competition statement and `datathon-task-1.zip` | Data, leakage, temporal validation, and baseline-risk audit | 2026-07-18 12:07 WIB | 2026-07-18 12:17 WIB | `INVESTIGATE`; audit at `task1/reports/d1-validation-audit.md`; do not submit baseline yet. |
| D1-MAIN-004 | DAY 1 | MAIN | NEEDS_REVIEW | HIGH | Official Task 1 data | Continuous speeds, text, network, and sample submission | Reproducible chronological baseline and valid submission candidate | 2026-07-18 12:04 WIB | 2026-07-18 12:15 WIB | `d1-e001-persist` pushed at `24d7165`; MSE 29.6995; waiting for VALIDATION verdict. |
| D1-SUB-001 | DAY 1 | SUBMISSION | READY | HIGH | Sample submission | Exact ID order and expected schema | Reusable submission validator and readiness verdict | TODO | 2026-07-18 12:09 WIB | May be handled alongside validation if the same teammate owns both scopes. |
| D2-MAIN-001 | DAY 2 | MAIN | DONE | HIGH | Official Task 2 ZIP | Schema audit, target-group validation, cheapest end-to-end baseline, and experiment map | Reproducible `d2-e001-baseline` plus audited handoffs | 2026-07-19 12:08 WIB | 2026-07-19 12:38 WIB | Mean accuracy 0.261333; diagnostic floor only; clean local notebook output exactly matches runner; do not submit. |
| D2-VAL-001 | DAY 2 | VALIDATION | IN_PROGRESS | HIGH | Extracted official CSV metadata | Independent group split, duplicate, leakage, and distribution audit | `GO`, `INVESTIGATE`, or `NO-GO` validation verdict | 2026-07-19 12:15 WIB | 2026-07-19 12:15 WIB | Read-only audit delegated; target-group proposal not yet frozen. |
| D2-SUB-001 | DAY 2 | SUBMISSION | DONE | HIGH | Test, sample submission, and articles CSVs | Fail-closed schema contract and dual local/Kaggle path requirements | Validator, regression tests, and readiness report | 2026-07-19 12:15 WIB | 2026-07-19 12:29 WIB | `READY` for CSV validation at commit `be28757`; no submission authorized or slot used. |
| D2-MAIN-002 | DAY 2 | MAIN | NEEDS_REVIEW | HIGH | `d2-baseline-v1` and frozen validation | Reproduce the audit-only title/category heuristic without tuning | `d2-e002-metarank` with comparable fold/subset diagnostics | 2026-07-19 12:48 WIB | 2026-07-19 12:56 WIB | Exact audit score reproduced; all gates pass; candidate awaits immutable-commit VALIDATION review. |
| D2-VAL-002 | DAY 2 | VALIDATION | IN_PROGRESS | HIGH | Stable MAIN baseline commit | Independently reproduce baseline artifacts and audit `d2-e002-metarank` after handoff | GO/NO-GO candidate verdict with gate evidence | 2026-07-19 12:38 WIB | 2026-07-19 12:50 WIB | Baseline audit complete at `task2/reports/d2-e001-baseline-validation-audit.md`; E002 audit awaits its immutable handoff commit. |
| D2-SUB-002 | DAY 2 | SUBMISSION | DONE | HIGH | MAIN commit `0f94a1c` with validator ancestor `721c4bf` | Clean local dual-environment notebook reproduction and exact-reference check | Notebook readiness verdict without Kaggle slot | 2026-07-19 12:39 WIB | 2026-07-19 12:49 WIB | `READY`; 12 tests pass, isolated smoke output is byte-identical to reference with SHA-256 `20e629...b70b96`; actual Kaggle Run All remains deferred. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: D2-MAIN-002
Status: NEEDS_REVIEW
Last Read Revision: 0018
Last Update: 2026-07-19 12:56:27 +07:00

### Current Objective
Reproduce the frozen audit-only title/category heuristic as `d2-e002-metarank` on the unchanged `d2-targetgroup-v1` harness.
### Work Completed
- Created canonical coordination documentation.
- Verified required competition rules, role ownership, synchronization/reporting protocols, Day 1/Day 2 workflows, write-lock instructions, and single canonical status file.
- Cleaned the latest `AGENTS.md` formatting without changing its substantive rules.
- Added an opt-in pretrained candidate pantry with pinned-revision receipts, checksum verification, and selection gates.
- Initialized the independent repository and pushed the collaboration baseline to GitHub `main`.
- Simplified canonical naming for experiments, branches, artifacts, and submissions.
- Built `d1-e001-persist` and generated a schema-valid submission preview.
- Audited the 4.45 GB Task 2 ZIP selectively without modifying or fully extracting raw data.
- Froze `d2-targetgroup-v1` after independent `GO`: five target-disjoint folds, seed 20260719, with persistent target hashes and mandatory coverage/OOD/state-ID reporting.
- Built `d2-e001-baseline`; current-specific mode reaches 0.261333 mean accuracy across five consistent folds.
- Integrated fail-closed submission validator commit `be28757` as `721c4bf`; its 12 regression tests pass.
- Created `EnterYourTeamName_Task2_Notebook.ipynb`; a clean isolated local run produces a 6,000-row CSV exactly matching the runner artifact.
- Preregistered four structurally distinct post-baseline hypotheses and their acceptance gates.
- Published `exp/d2-e001-baseline` and tag `d2-baseline-v1` at commit `0f94a1c` so teammates can branch independently.
- Implemented the exact frozen `d2-e002-metarank` formula with no weight/tokenizer/seed search and reproduced the independent audit mean accuracy exactly.
### Work in Progress
- Preparing the immutable E002 commit and VALIDATION handoff; notebook integration and Kaggle submission remain deferred.
### Latest Metrics
- `d2-e001-baseline`: mean 0.261333; folds 0.267778, 0.255556, 0.265556, 0.255000, 0.262778; worst 0.255000; std 0.005195.
- Mean current-seen coverage 0.8003; observed-candidate coverage 0.3053; test current-seen rate 0.874167.
- Submission: 6,000 unique state IDs, 544 unique predictions, top-prediction share 0.2715; validator `READY`.
- Tests: 12 submission-validator plus 3 baseline/validation tests pass.
- Clean notebook CSV SHA-256: `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`; exact reference match.
- `d2-e002-metarank`: mean 0.285333 versus baseline 0.261333, gain +0.024000; folds 0.290556, 0.282778, 0.278333, 0.280556, 0.294444; 5/5 wins; worst 0.278333.
- E002 current-unseen delta 0.000000; entirely-unseen-target-category accuracy 0.280000 -> 0.315200; test change rate 0.151333; 449 unique predictions; final recorded runtime 12.04s.
- Tests: 7 model/validation plus 12 submission-validator tests pass; E002 submission validator `READY`.
### Files Changed
- `task2/src/`; `task2/tests/`; `task2/experiments/d2-e001-baseline/`; `task2/notebooks/`; `task2/reports/`; `task2/README.md`; `coordination/TEAM_STATUS.md`
### Commands Running
- NONE
### Artifacts Produced
- `coordination/TEAM_STATUS.md`
- `shared/pretrained/candidates.json`
- `shared/pretrained/prepare_candidate.py`
- `shared/pretrained/verify_bundle.py`
- `shared/pretrained/README.md`
- `task1/experiments/d1-e001-persist/metrics.json`
- `task1/experiments/d1-e001-persist/config.json`
- `task1/experiments/d1-e001-persist/submission.csv` (local, ignored)
- `task2/experiments/d2-e001-baseline/{config,metrics,notes,validation_manifest}`
- `task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb`
- `task2/reports/d2-initial-analysis.md`
- `task2/reports/d2-submission-readiness.md`
- `task2/submissions/submission.csv` (local, ignored)
- `task2/experiments/d2-e002-metarank/{config,metrics,notes}`
- `task2/reports/d2-e001-baseline-notebook-audit.md`
- `task2/src/metarank.py`; `task2/src/run_metarank_experiment.py`; `task2/src/test_metarank.py`
### Decisions Needed
- Independent VALIDATION verdict on the immutable `d2-e002-metarank` commit.
- Whether screenshot link extraction clears its fixed 100-page precision/recall/runtime feasibility gate.
### Tasks Dispatched to Other Agents
- `D2-VAL-002` queued: close the validation report in-repo and independently audit the stable baseline/E002 handoff.
- `D2-SUB-002` completed: baseline notebook locally reproducible and byte-identical; actual Kaggle Run All remains deferred.
### Blockers
- NONE
### Next Action
- Commit and push E002, then hand the immutable hash to VALIDATION; do not submit or alter the final notebook until the audit verdict returns.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D2-VAL-002
Status: IN_PROGRESS
Last Read Revision: 0016
Last Update: 2026-07-19 12:50:11 +07:00

### Scope Being Audited
- MAIN commit `0f94a1c`, experiment `d2-e001-baseline`, and frozen validation `d2-targetgroup-v1`.
### Evidence Reviewed
- Baseline/validation source, committed metrics and manifest, extracted official CSVs, temporary clean reproduction, five independently recomputed target hashes, mutation ablations, and 3 focused tests.
### Findings
- Manifest reproduces byte-for-byte; stable metric fields reproduce exactly after excluding runtime/output path. Mean accuracy is `0.261333` with worst fold `0.255000`.
- All five folds contain 72 disjoint targets and 1,800 rows; all 360 targets occur exactly once; seed is `20260719`; all five recorded SHA-256 values match independent recomputation.
- Aggregate validation current-seen coverage is `0.800333` with accuracy `0.295710`; unseen accuracy is `0.123539`; next-label coverage is `0.942000`; observed outgoing-candidate coverage is `0.305333`.
- Entirely-unseen target categories cover 25 targets/625 rows with accuracy `0.280000`, versus `0.259940` on seen-category rows. Test predictions have 544 unique labels and top share `0.271500`.
### Leakage Risks
- No material baseline leakage found: fold construction ignores `state_id`/next labels, and all current-mode/global-mode/candidate statistics are fit on training-fold rows only.
- Prediction equality holds after mutating validation `state_id` and validation labels in all folds. Future models must repeat this ablation independently.
### Validation Risks
- The gate field `target_groups_are_disjoint` is serialized as literal `True`, although runtime intersection guards and the manifest independently prove the invariant for this snapshot. Future maintenance should compute the reporting flag.
- Validation current-seen coverage (`0.800333`) is lower than test (`0.874167`); retain subset reporting and do not rescale scores from unlabeled test coverage.
### Distribution or Fold Risks
- Entirely-unseen-category support varies from 3 to 10 targets per fold, so both per-fold and pooled subset accuracy must remain visible.
- Only 30.53% of validation truths appear among training outgoing candidates for the same current article; the baseline is a diagnostic floor, not a competitive final model.
### Recommendation
- GO

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Keep `d2-targetgroup-v1` frozen. Treat `d2-e001-baseline` as `DIAGNOSTIC ONLY` and `DO NOT SUBMIT`.
- Hand off the frozen `d2-e002-metarank` commit for independent audit against baseline `0.261333` and the preregistered gates.
### Blockers
- E002 audit is waiting for a commit beyond baseline snapshot `0f94a1c`.
### Next Action
- Audit `d2-e002-metarank` when MAIN publishes its handoff commit; do not alter the model, folds, or Kaggle slots.
<!-- VALIDATION:END -->

Only VALIDATION may update this section; it is read-only against the main pipeline.

## 6. Submission and Reproducibility Reviewer Status

<!-- SUBMISSION:START -->
Role: SUBMISSION
Current Task: D2-SUB-002
Status: READY
Last Read Revision: 0016
Last Update: 2026-07-19 12:49:19 +07:00

### Submission Schema Status
- `states_test.csv` has 6,000 rows and columns `state_id,current_article_id,target_article_id`; sample has 6,000 rows and exact columns `state_id,predicted_next_article_id`.
- Sample state IDs match test state IDs exactly in order; IDs are non-contiguous, so preserve test/sample row order.
### ID and Row Validation
- No nulls or duplicate state IDs. All article references observed in train/test/sample are within `articles.csv` IDs 0..4603.
- ZIP central listing contains 4,604 screenshot PNGs; current extracted working tree contains only 8 screenshots.
### Missing, Infinity, and Label Validation
- Implemented fail-closed checks for exact column order, 6,000 rows, state ID equality to test/sample, uniqueness, integer finite predictions, article-ID membership, and optional reference equality.
- Candidate-link membership should be added once the screenshot/link representation is available; article-universe membership alone is not enough to prove a valid click.
### Kaggle Path and Dependency Status
- `TASK2_DATA_DIR` and `TASK2_SUBMISSION_PATH` passed against official local data. Repository-relative resolution and isolated `/kaggle/input` discovery passed; local output is `task2/submissions/submission.csv` and Kaggle output contract is `/kaggle/working/submission.csv`.
### Run-All Status
- LOCAL CLEAN-SMOKE VERIFIED with `python -I task2/src/run_notebook_smoke.py`; actual Kaggle `Restart Session -> Run All` remains deliberately deferred until a competitive candidate exists.
### Model Weight Status
- No external/private model weights or APIs permitted; any weights must be open and packaged/available in Kaggle.
### Reproducibility Risks
- Reference `submission.csv` is ignored and not stored in commit `0f94a1c`, but the clean notebook output reproduced it byte-for-byte and matched tracked expected SHA-256 `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`.
- Test target IDs have 0% overlap with train target IDs; test current IDs overlap train at 87.42% and current→mode baseline has 62.46% train accuracy (87.42% test coverage, global-mode fallback). Avoid target memorization.
### Writeup Status
- TODO
### Recommendation
- READY: notebook at `0f94a1c` is clean and locally reproducible; 12 validator tests pass, fail-closed reference validation passes, and the audit is recorded in `task2/reports/d2-e001-baseline-notebook-audit.md`. This diagnostic baseline remains `DO NOT SUBMIT`.

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Reuse the verified dual-environment/output contract for a competitive candidate, then perform actual Kaggle `Restart Session -> Run All` and validate `/kaggle/working/submission.csv` before any submission decision.
### Blockers
- None for local baseline notebook reproducibility. Actual Kaggle Run All is intentionally deferred by instruction.
### Next Action
- MAIN reviews the D2-SUB-002 report and continues competitive modeling without spending a slot on `d2-e001-baseline`.
<!-- SUBMISSION:END -->

Only SUBMISSION may update this section; it may not change model/validation without MAIN instruction.

## 7. Experiment Registry

| Experiment ID | Day | Owner | Hypothesis | Baseline | Validation | Mean | Fold Scores | Worst Fold | Std | Prediction Distribution | Runtime | Status | Artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1-e001-persist | DAY 1 | MAIN | Mean/last/trend forecasts from the exact 15-step history establish a leakage-safe floor. | NONE | 540 contiguous tail origins per train block | 29.6995 | 29.8669; 29.5322 | 29.8669 | 0.1674 | min 0.0; max 101.9333; mean 52.7290 | 4.83s | INVESTIGATE | `task1/experiments/d1-e001-persist/metrics.json` |
| d2-e001-baseline | DAY 2 | MAIN | Current-specific next-click mode is the cheapest transferable floor when test targets are unseen. | NONE | `d2-targetgroup-v1` | 0.261333 | 0.267778; 0.255556; 0.265556; 0.255000; 0.262778 | 0.255000 | 0.005195 | 544 unique test predictions; top share 0.2715 | 4.96s | KEEP | `task2/experiments/d2-e001-baseline/metrics.json` |
| d2-e002-metarank | DAY 2 | MAIN | Frozen target-aware category/title similarity improves candidate selection without changing candidate coverage. | `d2-baseline-v1` | `d2-targetgroup-v1` | 0.285333 | 0.290556; 0.282778; 0.278333; 0.280556; 0.294444 | 0.278333 | 0.006142 | 449 unique test predictions; top share 0.2752; change rate 0.1513 | 12.04s | KEEP | `task2/experiments/d2-e002-metarank/metrics.json` |

Status: `PLANNED`, `RUNNING`, `KEEP`, `REJECT`, `INVESTIGATE`, `FINAL_CANDIDATE`. Record validation, seed, fold scores, worst fold, std, runtime, artifact, and decision. Never invent scores.

## 8. Submission Registry

### Day 1 - Task 1

| Slot | File | Experiment ID | Local Score | Public Score | Time | Submitted By | Final Candidate | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 4 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 5 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

### Day 2 - Task 2

| Slot | File | Experiment ID | Local Score | Public Score | Time | Submitted By | Final Candidate | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 4 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 5 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

Public score is never the sole final-selection reason.

## 9. Shared Blockers

| Blocker ID | Reported By | Time | Description | Blocking Task | Owner | Status | Resolution |
|---|---|---|---|---|---|---|---|

## 10. Handoff Queue

| Handoff ID | From | To | Time | Artifact or Evidence | Required Action | Status |
|---|---|---|---|---|---|---|
| D1-HO-001 | MAIN | VALIDATION | 2026-07-18 12:13 WIB | `task1/src/baseline.py`, `task1/experiments/d1-e001-persist/{config,metrics,notes}.json/md` | Audit origin construction, block aggregation, clipping, and whether MSE 29.6995 is a defensible comparison baseline. | COMPLETED |
| D1-HO-002 | VALIDATION | MAIN | 2026-07-18 12:17 WIB | `task1/reports/d1-validation-audit.md` | Replace the single tail score with purged multi-fold chronological, 372:168 regime-weighted validation before submission. | WAITING |
| D2-HO-001 | VALIDATION | MAIN | 2026-07-19 12:35 WIB | User-supplied independent Task 2 schema, leakage, validation, and baseline audit | Freeze target-group folds; add fold hashes, coverage, category-OOD, and state-ID diagnostics; do not submit baseline. | ACKNOWLEDGED |
| D2-HO-002 | SUBMISSION | MAIN | 2026-07-19 12:29 WIB | Commit `be28757`, 12 tests, and `task2/reports/d2-submission-readiness.md` | Reconcile MAIN validator, integrate the fail-closed implementation, and validate notebook output by exact reference. | COMPLETED |
| D2-HO-003 | SUBMISSION | MAIN | 2026-07-19 12:49 WIB | Audit commit `6d337a8` and `task2/reports/d2-e001-baseline-notebook-audit.md` | Preserve the verified dual-environment contract; defer actual Kaggle Run All until a competitive candidate exists. | ACKNOWLEDGED |
| D2-HO-004 | VALIDATION | MAIN | 2026-07-19 12:50 WIB | Audit commit `6e7d41a` and `task2/reports/d2-e001-baseline-validation-audit.md` | Keep the harness frozen, baseline diagnostic only, and provide an immutable E002 commit for the next audit. | ACKNOWLEDGED |

Status: `WAITING`, `ACKNOWLEDGED`, `COMPLETED`, `REJECTED`.

## 11. Append-Only Activity Log

| Time | Revision | Agent | Task ID | Event | Result | Next |
|---|---|---|---|---|---|---|
| TODO | 0001 | MAIN | NONE | Initialized coordination tooling | Canonical status and protocols created; no competition artifact changed | Populate only from official evidence |
| 2026-07-17 21:31:53 +07:00 | 0002 | MAIN | NONE | Completed documentation validation | Required structures present; only documentation/coordination files changed | Await user approval; do not commit |
| 2026-07-17 21:45:15 +07:00 | 0003 | MAIN | NONE | Cleaned AGENTS.md formatting | Removed copied conversation wrapper, repaired code fences, and verified headings | Await further project instructions |
| 2026-07-17 23:06:32 +07:00 | 0004 | MAIN | D1-MAIN-001 | Prepared open-weight candidate pantry | 4 tests passed; no weights downloaded, training run, or model selected | Inspect Day 1 task and activate only justified candidates |
| 2026-07-17 23:14:37 +07:00 | 0005 | MAIN | D1-MAIN-002 | Attempted GitHub repository setup | BLOCKED: GitHub CLI is not installed; local repo was not initialized or pushed | Install `gh`, authenticate, then resume setup |
| 2026-07-17 23:31:03 +07:00 | 0006 | MAIN | D1-MAIN-002 | Resumed GitHub repository setup | Authentication verified; independent repo initialized on `main`; remote is empty and connected; 4 tests passed | Review, commit, and push initial baseline |
| 2026-07-17 23:32:32 +07:00 | 0007 | MAIN | D1-MAIN-002 | Published initial collaboration baseline | Commit `53acffe` pushed to `origin/main`; task directories and pretrained tooling are available to teammates | Clone repository and wait for the official task |
| 2026-07-18 11:59:11 +07:00 | 0008 | MAIN | D1-MAIN-003 | Simplified project naming rules | One sortable experiment ID now links branch, directory, artifacts, status, and submission filename | Read Task 1 and populate the active brief |
| 2026-07-18 12:07:25 +07:00 | 0009 | VALIDATION | D1-VAL-001 | Started Task 1 validation and leakage audit | Claimed read-only data/schema/temporal audit; MAIN pipeline and submission slots remain untouched | Inspect ZIP data and propose defensible backtesting |
| 2026-07-18 12:09:37 +07:00 | 0010 | MAIN | D1-MAIN-004 | Inspected official Task 1 dataset | Verified shapes, finite values, text alignment, adjacency, and 2,041,200-row output schema | Build chronological baseline and await validation audit |
| 2026-07-18 12:13:41 +07:00 | 0011 | MAIN | D1-MAIN-004 | Completed provisional baseline | Mean15 MSE 29.6995; 3 tests passed; 2,041,200-row preview is unique and finite | Publish artifacts and await VALIDATION verdict; do not submit yet |
| 2026-07-18 12:15:05 +07:00 | 0012 | MAIN | D1-MAIN-004 | Published provisional baseline artifacts | Commit `24d7165` is on `origin/main`; raw data and submission preview remain ignored | VALIDATION reviews commit; MAIN explores next hypothesis |
| 2026-07-18 12:17:06 +07:00 | 0013 | VALIDATION | D1-VAL-001 | Completed data, leakage, and baseline audit | `INVESTIGATE`: baseline code is leakage-safe, but MSE 29.6995 is a selected single-tail estimate with wrong regime weighting | MAIN implements purged multi-fold 372:168 validation; do not submit yet |
| 2026-07-19 12:15:21 +07:00 | 0014 | MAIN | D2-MAIN-001 | Started Task 2 from zero on a separate branch | Selective ZIP audit found 4,604 screenshots, 9,000 train states, 6,000 test states, and zero train/test target overlap | Audit target-group validation and submission contract before implementing the cheapest baseline |
| 2026-07-19 12:29:04 +07:00 | 0015 | SUBMISSION | D2-SUB-001 | Completed Task 2 CSV validator in a separate worktree | Commit `be28757`; 12 regression tests passed; official sample passed reference validation; no notebook/raw data/model/slot changed | MAIN reconciles untracked validator files, then cherry-picks `be28757` and validates the final artifact |
| 2026-07-19 12:38:42 +07:00 | 0016 | MAIN | D2-MAIN-001 | Completed and reproduced the Task 2 diagnostic baseline | Validation frozen with independent GO; mean accuracy 0.261333; validator integrated; clean local notebook exactly matches the runner CSV; no slot used | Commit stable artifacts, hand hash to reviewers, then start frozen `d2-e002-metarank` |
| 2026-07-19 12:48:31 +07:00 | 0017 | MAIN | D2-MAIN-002 | Published the stable Task 2 baseline and started the first challenger | Branch `exp/d2-e001-baseline` and tag `d2-baseline-v1` point to `0f94a1c`; new branch `exp/d2-e002-metarank` isolates the frozen heuristic | Implement without tuning, run the official folds, and hand the candidate to VALIDATION |
| 2026-07-19 12:49:19 +07:00 | 0018 | SUBMISSION | D2-SUB-002 | Independently audited MAIN commit `0f94a1c` notebook in a separate worktree | `READY`; 12 tests pass; isolated smoke output is byte-identical to reference and matches SHA-256 `20e629...b70b96`; no Kaggle slot used | MAIN preserves the notebook contract and defers actual Kaggle Run All until a competitive candidate exists |
| 2026-07-19 12:56:27 +07:00 | 0019 | MAIN | D2-MAIN-002 | Completed the frozen metadata-rank challenger | Exact audit mean 0.285333 reproduced; +0.024000 over baseline; 5/5 folds and all preregistered gates pass; no notebook or Kaggle slot changed | Commit and push the immutable candidate, then request independent VALIDATION review |
| 2026-07-19 12:50:11 +07:00 | 0020 | VALIDATION | D2-VAL-002 | Independently reproduced and audited `d2-e001-baseline` at `0f94a1c` | Harness `GO`; baseline `DIAGNOSTIC ONLY`; submission `DO NOT SUBMIT`; manifest and stable metrics reproduced with no material leakage | Await the frozen `d2-e002-metarank` handoff commit and apply preregistered gates |

Append only. Correct errors with a new entry; do not erase history.

## 12. Day 1 Closing Summary

- Final submission: TODO
- Final experiment: TODO
- Private-risk assessment: TODO
- Notebook status: TODO
- Writeup TODO: TODO
- Reusable tooling: TODO
- Lessons for Day 2: TODO
- Assumptions not carried into Day 2: target, metric, validation, dataset, features, model.

## 13. Day 2 Closing Summary

- Final submission: TODO
- Final experiment: TODO
- Notebook status: TODO
- Writeup status: TODO
- Unresolved reproducibility risk: TODO
- Final deliverable checklist: TODO
