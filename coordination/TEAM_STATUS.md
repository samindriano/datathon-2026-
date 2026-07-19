# Datathon 2026 Team Status

Revision: 0016
Active Day: DAY 2
Active Task: TASK 2
Last Global Update: 2026-07-19 12:38:42 +07:00
Competition Clock: RUNNING
Repository Branch: exp/d2-e001-baseline
Current Stable Commit: 53acffe229cad28e934c36d54e97771b37a6cd1a

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
| D2-MAIN-002 | DAY 2 | MAIN | READY | HIGH | `d2-e001-baseline` and frozen validation | Reproduce the audit-only title/category heuristic without tuning | `d2-e002-metarank` with comparable fold/subset diagnostics | TODO | 2026-07-19 12:38 WIB | Frozen formula and gate are recorded in `task2/reports/d2-initial-analysis.md`. |
| D2-VAL-002 | DAY 2 | VALIDATION | READY | HIGH | Stable MAIN baseline commit | Independently reproduce baseline artifacts and audit `d2-e002-metarank` after handoff | GO/NO-GO candidate verdict with gate evidence | TODO | 2026-07-19 12:38 WIB | Do not modify MAIN pipeline or validation folds. |
| D2-SUB-002 | DAY 2 | SUBMISSION | READY | HIGH | Stable MAIN baseline notebook commit | Clean local dual-environment notebook reproduction and exact-reference check | Notebook readiness verdict without Kaggle slot | TODO | 2026-07-19 12:38 WIB | Actual Kaggle Run All is deferred until a competitive candidate exists. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: D2-MAIN-001
Status: DONE
Last Read Revision: 0015
Last Update: 2026-07-19 12:38:42 +07:00

### Current Objective
Freeze a defensible Task 2 validation, complete the cheapest end-to-end baseline, and hand stable artifacts to independent reviewers before starting `d2-e002-metarank`.
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
### Work in Progress
- Preparing one coherent baseline commit and reviewer handoffs.
- `d2-e002-metarank` is queued but has not been implemented or scored.
### Latest Metrics
- `d2-e001-baseline`: mean 0.261333; folds 0.267778, 0.255556, 0.265556, 0.255000, 0.262778; worst 0.255000; std 0.005195.
- Mean current-seen coverage 0.8003; observed-candidate coverage 0.3053; test current-seen rate 0.874167.
- Submission: 6,000 unique state IDs, 544 unique predictions, top-prediction share 0.2715; validator `READY`.
- Tests: 12 submission-validator plus 3 baseline/validation tests pass.
- Clean notebook CSV SHA-256: `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`; exact reference match.
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
### Decisions Needed
- Independent reproduction of `d2-e002-metarank` after MAIN implements the frozen heuristic.
- Whether screenshot link extraction clears its fixed 100-page precision/recall/runtime feasibility gate.
### Tasks Dispatched to Other Agents
- `D2-VAL-002` queued: close the validation report in-repo and independently audit the stable baseline/E002 handoff.
- `D2-SUB-002` queued: reproduce the stable baseline notebook locally and verify exact CSV provenance.
### Blockers
- NONE
### Next Action
- Commit the stable baseline, send its hash to both reviewers, then implement only the frozen `d2-e002-metarank` heuristic on a separate experiment branch.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D1-VAL-001
Status: DONE
Last Read Revision: 0012
Last Update: 2026-07-18 12:17:06 +07:00

### Scope Being Audited
- Official Task 1 data schema, temporal sampling, leakage risk, validation design, and simple baselines.
### Evidence Reviewed
- Official description; all 10 ZIP files; train/test arrays, text, graph, road metadata, sample submission; `d1-e001-persist` code, metrics, config, notes, commit `24d7165`; targeted tests.
### Findings
- Train blocks are `(11160,1260)` and `(5039,1260)`; test is `(540,15,1260)`; all arrays are finite and submission order is correct.
- Test has 372 m1-like and 168 m2-like samples, matching train proportions; no train-window copy, duplicate test window, or shifted test-window overlap was found.
- Baseline origin/target indexing, elementwise MSE, and submission reshape are correct; 3 targeted tests passed.
### Leakage Risks
- Random window splits leak 14/15 overlapping history rows and persistent event text; adjacent train text is identical 42.5% in m1 and 54.0% in m2.
- Fit every learned preprocessing/text component on the training fold only and purge 15 origins at validation boundaries.
### Validation Risks
- Current MSE 29.6995 uses one tail slice and selects methods on that same slice; it is not a defensible official comparison score.
- Equal 540-window block aggregation weights regimes 50/50 instead of the observed test mixture 372:168.
### Distribution or Fold Risks
- Structural all-zero roads differ sharply: 13 in m1 versus 210 in m2; an all-zero 15-step history stays zero at targets more than 99.9% of the time.
- Daily no-fit MSE varies widely (m1 31.659-73.964; m2 25.436-40.260); the current m1 tail is unusually easy.
### Recommendation
- INVESTIGATE

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Establish at least three multi-day chronological folds per block, purge 15 origins, aggregate at 372:168, report horizon/block/fold/worst/std, separate selection from reporting, and preserve an all-zero-history guard.
### Blockers
- NONE
### Next Action
- Review a revised official-validation artifact; keep `d1-e001-persist` provisional and do not spend a Kaggle slot yet.
<!-- VALIDATION:END -->

Only VALIDATION may update this section; it is read-only against the main pipeline.

## 6. Submission and Reproducibility Reviewer Status

<!-- SUBMISSION:START -->
Role: SUBMISSION
Current Task: D2-SUB-001
Status: READY
Last Read Revision: 0014
Last Update: 2026-07-19 12:29:04 +07:00

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
- Validator resolves explicit paths, `TASK2_DATA_DIR`, repository-relative data, or one unambiguous dataset under `/kaggle/input`; output helper uses local/Kaggle canonical paths with `TASK2_SUBMISSION_PATH` override.
### Run-All Status
- NOT YET VERIFIED. Notebook must resolve relative/Kaggle input paths, write `submission.csv`, and run cleanly in VS Code and Kaggle `Run All`.
### Model Weight Status
- No external/private model weights or APIs permitted; any weights must be open and packaged/available in Kaggle.
### Reproducibility Risks
- Test target IDs have 0% overlap with train target IDs; test current IDs overlap train at 87.42% and current→mode baseline has 62.46% train accuracy (87.42% test coverage, global-mode fallback). Avoid target memorization.
### Writeup Status
- TODO
### Recommendation
- READY: CSV validator, path helpers, and all 12 regression tests are ready at commit `be28757`; this does not approve the model, final notebook, or a Kaggle submission.

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Reconcile the untracked MAIN-worktree validator files, then cherry-pick `be28757` and invoke the fail-closed validator on the final generated artifact.
### Blockers
- None for the CSV validator. Candidate-link validity and final-notebook Run All remain separate pre-submission checks for MAIN.
### Next Action
- MAIN cherry-picks `be28757`, runs the documented test command, and validates the final notebook output; no Kaggle slot was used.
<!-- SUBMISSION:END -->

Only SUBMISSION may update this section; it may not change model/validation without MAIN instruction.

## 7. Experiment Registry

| Experiment ID | Day | Owner | Hypothesis | Baseline | Validation | Mean | Fold Scores | Worst Fold | Std | Prediction Distribution | Runtime | Status | Artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1-e001-persist | DAY 1 | MAIN | Mean/last/trend forecasts from the exact 15-step history establish a leakage-safe floor. | NONE | 540 contiguous tail origins per train block | 29.6995 | 29.8669; 29.5322 | 29.8669 | 0.1674 | min 0.0; max 101.9333; mean 52.7290 | 4.83s | INVESTIGATE | `task1/experiments/d1-e001-persist/metrics.json` |
| d2-e001-baseline | DAY 2 | MAIN | Current-specific next-click mode is the cheapest transferable floor when test targets are unseen. | NONE | `d2-targetgroup-v1` | 0.261333 | 0.267778; 0.255556; 0.265556; 0.255000; 0.262778 | 0.255000 | 0.005195 | 544 unique test predictions; top share 0.2715 | 4.96s | KEEP | `task2/experiments/d2-e001-baseline/metrics.json` |

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
