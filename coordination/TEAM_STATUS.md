# Datathon 2026 Team Status

Revision: 0015
Active Day: DAY 1
Active Task: TASK 1
Last Global Update: 2026-07-18 12:24:29 +07:00
Competition Clock: RUNNING
Repository Branch: exp/d1-main-model
Current Stable Commit: 53acffe229cad28e934c36d54e97771b37a6cd1a

## 1. Active Competition Brief

- Day: DAY 1
- Task: TASK 1
- Start time: 2026-07-18 12:00 WIB
- End time: 2026-07-18 17:00 WIB
- Notebook deadline: 2026-07-18 18:00 WIB
- Target: traffic speed in km/h for all 1,260 roads at horizons h5, h10, and h15 (+20, +40, +60 minutes).
- Metric: Mean Squared Error averaged across samples, horizons, and roads.
- Train path: `task1/data/competition/dataset-task1/train/` (two continuous blocks with 11,160 and 5,039 timesteps).
- Test path: `task1/data/competition/dataset-task1/test/test_X_hist.npy` with shape `(540, 15, 1260)` and aligned `test_texts.json`.
- Sample submission path: `task1/data/competition/dataset-task1/sample_submission.csv`.
- Number of rows: 16,199 continuous train timesteps across two blocks; 540 test samples; 2,041,200 submission rows.
- Number of features: 15 speed-history steps x 1,260 roads, aligned event text, 1,260 x 1,260 adjacency, and road metadata.
- Output schema: columns `id,speed`; ID format `test_XXXXX_h{5|10|15}_r{0..1259}` in sample order.
- Official constraints: See `AGENTS.md`.
- Information that remains UNKNOWN: hidden-test time ordering, exact relationship between train blocks and test period, and final validated split strategy.

Only MAIN may update this section.

## 2. Global Decisions

| Decision ID | Time | Decision | Evidence | Owner | Reversal Condition |
|---|---|---|---|---|---|
| D1-DEC-001 | 2026-07-18 12:13 WIB | Use direct mean squared error across samples, horizons, and roads as metric implementation. | Official task statement and `task1/src/baseline.py`. | MAIN | Official clarification changes metric aggregation. |
| D1-DEC-002 | 2026-07-18 12:13 WIB | Treat `d1-e001-persist` mean-of-15 forecast as provisional baseline only. | Tail backtest MSE 29.6995; validation review pending. | MAIN | VALIDATION returns NO-GO or a safer baseline is established. |
| D1-DEC-003 | 2026-07-18 12:20 WIB | Accept the audit recommendation: official comparisons require purged multi-fold chronological validation weighted to the observed 372:168 test regimes. | `task1/reports/d1-validation-audit.md`; VALIDATION verdict `INVESTIGATE`. | MAIN | New competition evidence disproves the observed regime mixture. |

Only MAIN manages this table; reviewers propose decisions in their role sections.

## 3. Shared Task Board

| Task ID | Day | Owner | Status | Priority | Dependency | Input | Expected Output | Started | Updated | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| D1-MAIN-001 | PREPARATION | MAIN | DONE | MEDIUM | Official competition rules | Open-weight preparation requirement | Offline-ready candidate pantry tooling | 2026-07-17 22:50 WIB | 2026-07-17 23:06 WIB | Metadata/tooling only; no weights downloaded and no model selected. |
| D1-MAIN-002 | PREPARATION | MAIN | DONE | HIGH | GitHub CLI installed and authenticated | Local project files and target `samindriano/datathon-2026-` | Independent Git repository pushed to GitHub | 2026-07-17 23:14 WIB | 2026-07-17 23:32 WIB | Initial baseline commit `53acffe` pushed to `origin/main`. |
| D1-MAIN-003 | PREPARATION | MAIN | DONE | HIGH | Existing experiment protocol | Request for simple, searchable artifact names | Canonical experiment, branch, artifact, and submission naming rules | 2026-07-18 11:57 WIB | 2026-07-18 11:59 WIB | Use one short experiment ID everywhere; submission includes slot and experiment ID. |
| D1-VAL-001 | DAY 1 | VALIDATION | DONE | HIGH | Official Task 1 dataset available | Competition statement and `datathon-task-1.zip` | Data, leakage, temporal validation, and baseline-risk audit | 2026-07-18 12:07 WIB | 2026-07-18 12:17 WIB | `INVESTIGATE`; audit at `task1/reports/d1-validation-audit.md`; do not submit baseline yet. |
| D1-MAIN-004 | DAY 1 | MAIN | DONE | HIGH | Official Task 1 data | Continuous speeds, text, network, and sample submission | Reproducible chronological baseline and valid submission candidate | 2026-07-18 12:04 WIB | 2026-07-18 12:20 WIB | `d1-e001-persist` is reproducible but remains `INVESTIGATE`; MSE 29.6995 is not an official comparison score. |
| D1-MAIN-005 | DAY 1 | MAIN | NEEDS_REVIEW | HIGH | Completed validation audit | Purged folds, observed regime mixture, and continuous train blocks | Official multi-fold harness and `d1-e002-ridge` candidate | 2026-07-18 12:20 WIB | 2026-07-18 12:24 WIB | Ridge 39.0248 vs mean15 45.5482; `KEEP` for review, submission `INVESTIGATE`. |
| D1-SUB-001 | DAY 1 | SUBMISSION | READY | HIGH | Sample submission | Exact ID order and expected schema | Reusable submission validator and readiness verdict | TODO | 2026-07-18 12:09 WIB | May be handled alongside validation if the same teammate owns both scopes. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: D1-MAIN-005
Status: NEEDS_REVIEW
Last Read Revision: 0014
Last Update: 2026-07-18 12:24:29 +07:00

### Current Objective
Implement the accepted leakage-safe official validation harness and evaluate one fixed ridge-history hypothesis.
### Work Completed
- Created canonical coordination documentation.
- Verified required competition rules, role ownership, synchronization/reporting protocols, Day 1/Day 2 workflows, write-lock instructions, and single canonical status file.
- Cleaned the latest `AGENTS.md` formatting without changing its substantive rules.
- Added an opt-in pretrained candidate pantry with pinned-revision receipts, checksum verification, and selection gates.
- Initialized the independent repository and pushed the collaboration baseline to GitHub `main`.
- Simplified canonical naming for experiments, branches, artifacts, and submissions.
- Built `d1-e001-persist` and generated a schema-valid submission preview.
### Work in Progress
- Awaiting independent validation review of `d1-e002-ridge`; no Kaggle slot has been used.
### Latest Metrics
- Pretrained tooling tests: 4 passed.
- Data integrity: all NPY arrays finite; all 2,041,200 submission IDs parse completely.
- `d1-e001-persist`: MSE 29.6995; h5 25.9261; h10 29.7722; h15 33.4003.
- Block mean scores: 29.8669 and 29.5322; prediction mean 52.7290 km/h.
- Official-v1 mean15: mean 45.5482; std 10.3820; worst fold 54.8371.
- `d1-e002-ridge`: mean 39.0248; std 5.4669; worst fold 44.4867; 14.32% mean improvement.
- Ridge folds: 44.4867, 41.0327, 31.5551; 7 tests passed; runtime 9.59s.
### Files Changed
- `task1/src/multifold.py`; `task1/src/ridge_model.py`; `task1/src/run_ridge_experiment.py`; `task1/src/test_multifold_ridge.py`; `task1/experiments/d1-e002-ridge/`; `coordination/TEAM_STATUS.md`
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
- `task1/experiments/d1-e002-ridge/{config.json,metrics.json,notes.md}`
- `task1/experiments/d1-e002-ridge/submission.csv` (local, ignored)
### Decisions Needed
- VALIDATION verdict on fold construction and whether a small fold-3 regression is acceptable.
### Tasks Dispatched to Other Agents
- `D1-VAL-001` to VALIDATION: temporal split, leakage, distribution, and metric audit.
- `D1-SUB-001` to SUBMISSION: schema/order/ID/value validator.
### Blockers
- NONE
### Next Action
- Commit the isolated branch and hand `d1-e002-ridge` to VALIDATION; do not submit yet.
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
Current Task: NONE
Status: IDLE
Last Read Revision: 0000
Last Update: TODO

### Submission Schema Status
- TODO
### ID and Row Validation
- TODO
### Missing, Infinity, and Label Validation
- TODO
### Kaggle Path and Dependency Status
- TODO
### Run-All Status
- TODO
### Model Weight Status
- TODO
### Reproducibility Risks
- TODO
### Writeup Status
- TODO
### Recommendation
- UNKNOWN

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- TODO
### Blockers
- NONE
### Next Action
- TODO
<!-- SUBMISSION:END -->

Only SUBMISSION may update this section; it may not change model/validation without MAIN instruction.

## 7. Experiment Registry

| Experiment ID | Day | Owner | Hypothesis | Baseline | Validation | Mean | Fold Scores | Worst Fold | Std | Prediction Distribution | Runtime | Status | Artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1-e001-persist | DAY 1 | MAIN | Mean/last/trend forecasts from the exact 15-step history establish a leakage-safe floor. | NONE | 540 contiguous tail origins per train block | 29.6995 | 29.8669; 29.5322 | 29.8669 | 0.1674 | min 0.0; max 101.9333; mean 52.7290 | 4.83s | INVESTIGATE | `task1/experiments/d1-e001-persist/metrics.json` |
| d1-e002-ridge | DAY 1 | MAIN | Fixed per-road ridge on causal history summaries improves mean15 robustly. | d1-e001-persist | 3 purged 720-origin folds per block; 372:168 weighted | 39.0248 | 44.4867; 41.0327; 31.5551 | 44.4867 | 5.4669 | min 0.0; max 101.5696; mean 52.8826 | 9.59s | KEEP | `task1/experiments/d1-e002-ridge/metrics.json` |

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
| D1-HO-002 | VALIDATION | MAIN | 2026-07-18 12:17 WIB | `task1/reports/d1-validation-audit.md` | Replace the single tail score with purged multi-fold chronological, 372:168 regime-weighted validation before submission. | COMPLETED |
| D1-HO-003 | MAIN | VALIDATION | 2026-07-18 12:24 WIB | `task1/src/{multifold.py,ridge_model.py}` and `task1/experiments/d1-e002-ridge/metrics.json` | Audit purge boundaries, training-only moments, 372:168 aggregation, zero guard, and fold-3 regression. | WAITING |

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
| 2026-07-18 12:20:39 +07:00 | 0014 | MAIN | D1-MAIN-005 | Accepted audit and started isolated model experiment | Created `exp/d1-main-model`; preregistered purged multi-fold comparison of mean15 versus fixed ridge-history model | Implement, test, and report before any submission decision |
| 2026-07-18 12:24:29 +07:00 | 0015 | MAIN | D1-MAIN-005 | Completed first official-v1 model comparison | Ridge improved weighted mean MSE 14.32% and worst fold, but regressed 0.4985 on fold 3; 7 tests and submission preview checks passed | VALIDATION independently reviews branch; verdict remains `INVESTIGATE` |

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
