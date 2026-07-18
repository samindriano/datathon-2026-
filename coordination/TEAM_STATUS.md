# Datathon 2026 Team Status

Revision: 0012
Active Day: DAY 1
Active Task: TASK 1
Last Global Update: 2026-07-18 12:15:05 +07:00
Competition Clock: RUNNING
Repository Branch: main
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

Only MAIN manages this table; reviewers propose decisions in their role sections.

## 3. Shared Task Board

| Task ID | Day | Owner | Status | Priority | Dependency | Input | Expected Output | Started | Updated | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| D1-MAIN-001 | PREPARATION | MAIN | DONE | MEDIUM | Official competition rules | Open-weight preparation requirement | Offline-ready candidate pantry tooling | 2026-07-17 22:50 WIB | 2026-07-17 23:06 WIB | Metadata/tooling only; no weights downloaded and no model selected. |
| D1-MAIN-002 | PREPARATION | MAIN | DONE | HIGH | GitHub CLI installed and authenticated | Local project files and target `samindriano/datathon-2026-` | Independent Git repository pushed to GitHub | 2026-07-17 23:14 WIB | 2026-07-17 23:32 WIB | Initial baseline commit `53acffe` pushed to `origin/main`. |
| D1-MAIN-003 | PREPARATION | MAIN | DONE | HIGH | Existing experiment protocol | Request for simple, searchable artifact names | Canonical experiment, branch, artifact, and submission naming rules | 2026-07-18 11:57 WIB | 2026-07-18 11:59 WIB | Use one short experiment ID everywhere; submission includes slot and experiment ID. |
| D1-VAL-001 | DAY 1 | VALIDATION | IN_PROGRESS | HIGH | Official Task 1 dataset available | Competition statement and `datathon-task-1.zip` | Data, leakage, temporal validation, and baseline-risk audit | 2026-07-18 12:07 WIB | 2026-07-18 12:07 WIB | Read-only audit; no MAIN pipeline changes and no submission-slot use. |
| D1-MAIN-004 | DAY 1 | MAIN | NEEDS_REVIEW | HIGH | Official Task 1 data | Continuous speeds, text, network, and sample submission | Reproducible chronological baseline and valid submission candidate | 2026-07-18 12:04 WIB | 2026-07-18 12:15 WIB | `d1-e001-persist` pushed at `24d7165`; MSE 29.6995; waiting for VALIDATION verdict. |
| D1-SUB-001 | DAY 1 | SUBMISSION | READY | HIGH | Sample submission | Exact ID order and expected schema | Reusable submission validator and readiness verdict | TODO | 2026-07-18 12:09 WIB | May be handled alongside validation if the same teammate owns both scopes. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: NONE
Status: NEEDS_REVIEW
Last Read Revision: 0011
Last Update: 2026-07-18 12:15:05 +07:00

### Current Objective
Read the official Day 1 task, populate the competition brief, and build the first end-to-end baseline.
### Work Completed
- Created canonical coordination documentation.
- Verified required competition rules, role ownership, synchronization/reporting protocols, Day 1/Day 2 workflows, write-lock instructions, and single canonical status file.
- Cleaned the latest `AGENTS.md` formatting without changing its substantive rules.
- Added an opt-in pretrained candidate pantry with pinned-revision receipts, checksum verification, and selection gates.
- Initialized the independent repository and pushed the collaboration baseline to GitHub `main`.
- Simplified canonical naming for experiments, branches, artifacts, and submissions.
- Built `d1-e001-persist` and generated a schema-valid submission preview.
### Work in Progress
- Awaiting VALIDATION review of `d1-e001-persist`; no Kaggle slot used.
### Latest Metrics
- Pretrained tooling tests: 4 passed.
- Data integrity: all NPY arrays finite; all 2,041,200 submission IDs parse completely.
- `d1-e001-persist`: MSE 29.6995; h5 25.9261; h10 29.7722; h15 33.4003.
- Block mean scores: 29.8669 and 29.5322; prediction mean 52.7290 km/h.
### Files Changed
- `.gitignore`; `requirements.txt`; `task1/src/`; `task1/experiments/d1-e001-persist/`; `coordination/TEAM_STATUS.md`
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
### Decisions Needed
- VALIDATION verdict on the chronological tail split and provisional mean15 baseline.
### Tasks Dispatched to Other Agents
- `D1-VAL-001` to VALIDATION: temporal split, leakage, distribution, and metric audit.
- `D1-SUB-001` to SUBMISSION: schema/order/ID/value validator.
### Blockers
- NONE
### Next Action
- Continue with a stronger independent hypothesis while VALIDATION reviews commit `24d7165`; do not submit yet.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D1-VAL-001
Status: IN_PROGRESS
Last Read Revision: 0008
Last Update: 2026-07-18 12:07:25 +07:00

### Scope Being Audited
- Official Task 1 data schema, temporal sampling, leakage risk, validation design, and simple baselines.
### Evidence Reviewed
- Official competition description supplied by the user; ZIP inventory pending detailed inspection.
### Findings
- TODO
### Leakage Risks
- TODO
### Validation Risks
- TODO
### Distribution or Fold Risks
- TODO
### Recommendation
- UNKNOWN

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- TODO
### Blockers
- NONE
### Next Action
- Inspect array/JSON schemas and temporal structure, quantify missingness/distribution, then propose leakage-safe backtesting.
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
| D1-HO-001 | MAIN | VALIDATION | 2026-07-18 12:13 WIB | `task1/src/baseline.py`, `task1/experiments/d1-e001-persist/{config,metrics,notes}.json/md` | Audit origin construction, block aggregation, clipping, and whether MSE 29.6995 is a defensible comparison baseline. | WAITING |

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
