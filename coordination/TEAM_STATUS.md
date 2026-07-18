# Datathon 2026 Team Status

Revision: 0034
Active Day: DAY 1
Active Task: TASK 1
Last Global Update: 2026-07-18 13:39:55 +07:00
Competition Clock: RUNNING
Repository Branch: exp/d1-e006-textres
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
| D1-DEC-004 | 2026-07-18 12:32 WIB | Freeze `d1-multifold-v1` at commit `e2136b6` as the official validation harness. | Independent VALIDATION verdict `GO`; exact metric and submission reproduction. | MAIN | A verified implementation defect or official competition clarification invalidates the harness. |
| D1-DEC-005 | 2026-07-18 13:12 WIB | Approve `d1-e002-ridge` for Kaggle submission slot 1. | Kaggle-generated `submission.csv` passes the fail-closed validator with 2,041,200 exact IDs and zero numeric mismatches against the audited ridge reference. | MAIN | Submission Manager finds an upload-preview mismatch or Kaggle rejects the file. |
| D1-DEC-006 | 2026-07-18 13:18 WIB | Treat public MSE `45.980` as diagnostic only and test `d1-e003-lagblend` on frozen local validation before considering slot 2. | Slot 1 ranks 12th on the 30% public split; private 70% remains unseen and official validation is unchanged. | MAIN | A verified implementation defect invalidates the frozen validation or official competition guidance changes. |
| D1-DEC-007 | 2026-07-18 13:24 WIB | Preregister `d1-e004-analog` as a separate-branch nearest-history delta forecaster before scoring. | Lagblend failed because shared weights lost road-specific dynamics; analog forecasting preserves road-level future deltas from similar causal network states. | MAIN | Implementation cannot meet leakage, runtime, or frozen-validation constraints. |
| D1-DEC-008 | 2026-07-18 13:28 WIB | Preregister `d1-e005-ar15` with the same ridge alpha `0.1`, changing only five summary features to all 15 causal lags. | Ridge remains strongest; isolating the full-history feature hypothesis avoids leaderboard tuning and preserves per-road modeling. | MAIN | Implementation fails leakage, stability, or runtime checks. |
| D1-DEC-009 | 2026-07-18 13:34 WIB | Preregister `d1-e006-textres` using fixed global event-type counts to model per-road ridge residuals. | Official texts align one-to-one with timesteps/samples and contain repeated causal event types; no external embedding or road-name translation is required. | MAIN | Text alignment or residual fitting is not leakage-safe or runtime-feasible. |

Only MAIN manages this table; reviewers propose decisions in their role sections.

## 3. Shared Task Board

| Task ID | Day | Owner | Status | Priority | Dependency | Input | Expected Output | Started | Updated | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| D1-MAIN-001 | PREPARATION | MAIN | DONE | MEDIUM | Official competition rules | Open-weight preparation requirement | Offline-ready candidate pantry tooling | 2026-07-17 22:50 WIB | 2026-07-17 23:06 WIB | Metadata/tooling only; no weights downloaded and no model selected. |
| D1-MAIN-002 | PREPARATION | MAIN | DONE | HIGH | GitHub CLI installed and authenticated | Local project files and target `samindriano/datathon-2026-` | Independent Git repository pushed to GitHub | 2026-07-17 23:14 WIB | 2026-07-17 23:32 WIB | Initial baseline commit `53acffe` pushed to `origin/main`. |
| D1-MAIN-003 | PREPARATION | MAIN | DONE | HIGH | Existing experiment protocol | Request for simple, searchable artifact names | Canonical experiment, branch, artifact, and submission naming rules | 2026-07-18 11:57 WIB | 2026-07-18 11:59 WIB | Use one short experiment ID everywhere; submission includes slot and experiment ID. |
| D1-VAL-001 | DAY 1 | VALIDATION | DONE | HIGH | Official Task 1 dataset available | Competition statement and model handoffs | Data, leakage, temporal validation, and candidate audits | 2026-07-18 12:07 WIB | 2026-07-18 12:29 WIB | Official-v1 harness `GO`; `d1-e002-ridge` `KEEP`; submission `INVESTIGATE`. |
| D1-MAIN-004 | DAY 1 | MAIN | DONE | HIGH | Official Task 1 data | Continuous speeds, text, network, and sample submission | Reproducible chronological baseline and valid submission candidate | 2026-07-18 12:04 WIB | 2026-07-18 12:20 WIB | `d1-e001-persist` is reproducible but remains `INVESTIGATE`; MSE 29.6995 is not an official comparison score. |
| D1-MAIN-005 | DAY 1 | MAIN | DONE | HIGH | Completed validation audit | Purged folds, observed regime mixture, and continuous train blocks | Official multi-fold harness and `d1-e002-ridge` candidate | 2026-07-18 12:20 WIB | 2026-07-18 12:32 WIB | Harness `GO`; ridge `KEEP`; submission remains `INVESTIGATE`. |
| D1-MAIN-006 | DAY 1 | MAIN | CANCELLED | MEDIUM | Frozen ridge handoff | Same audited folds and 15-step histories | Independent lightweight `d1-e003-lagblend` candidate | 2026-07-18 12:28 WIB | 2026-07-18 12:32 WIB | Cancelled by user before commit; code, metrics, and local preview removed. |
| D1-MAIN-007 | DAY 1 | MAIN | DONE | HIGH | Harness `GO` and ridge `KEEP` | Audited ridge runner, sample submission, and Kaggle constraints | Reusable validator and clean-session inference notebook | 2026-07-18 12:36 WIB | 2026-07-18 12:40 WIB | Clean process reproduced all 2,041,200 predictions exactly; ready for SUBMISSION review. |
| D1-MAIN-008 | DAY 1 | MAIN | DONE | HIGH | User local notebook run | VS Code could not find `/kaggle/input` outside Kaggle | Automatic local/Kaggle data and output path discovery | 2026-07-18 12:43 WIB | 2026-07-18 12:45 WIB | Local Run All completed in 5.67s with zero difference from audited submission. |
| D1-MAIN-009 | DAY 1 | MAIN | DONE | HIGH | SUBMISSION verdict `NOT READY` | Four concrete readiness blockers | Fail-closed validator, clean final notebook, and Kaggle Run All evidence | 2026-07-18 12:56 WIB | 2026-07-18 13:12 WIB | All four blockers closed; Kaggle-generated CSV exactly reproduces audited ridge and slot 1 is approved. |
| D1-MAIN-010 | DAY 1 | MAIN | DONE | HIGH | Frozen `d1-multifold-v1` and slot 1 result | Shared convex lag weights per regime/horizon | Auditable structurally different candidate compared with mean15 and ridge | 2026-07-18 13:18 WIB | 2026-07-18 13:21 WIB | `REJECT`: MSE 42.8914, only fold 3 improves, all acceptance gates fail; no CSV or slot used. |
| D1-MAIN-011 | DAY 1 | MAIN | DONE | HIGH | Rejected lagblend and frozen ridge reference | Nearest historical network states using training-only selected roads and future deltas | Structurally different candidate with fixed runtime-safe parameters | 2026-07-18 13:24 WIB | 2026-07-18 13:27 WIB | `REJECT`: MSE 55.4014, 0/3 folds and horizons improve; no CSV or slot used. |
| D1-MAIN-012 | DAY 1 | MAIN | DONE | HIGH | Frozen ridge remains strongest | Per-road direct ridge using all 15 causal lag values | Comparable feature-expansion candidate on frozen folds | 2026-07-18 13:28 WIB | 2026-07-18 13:31 WIB | `REJECT`: MSE 39.0830, only fold 3 improves and 0/3 horizons improve; no CSV or slot used. |
| D1-MAIN-013 | DAY 1 | MAIN | NEEDS_REVIEW | HIGH | Text schema audit and frozen ridge | Fixed event-count features predicting per-road ridge residuals | First causal use of official event text with no external model | 2026-07-18 13:34 WIB | 2026-07-18 13:39 WIB | `KEEP`: MSE 38.3456, all folds/horizons improve; independent leakage audit required before slot 2. |
| D1-SUB-001 | DAY 1 | SUBMISSION | BLOCKED | HIGH | Handoff `D1-HO-004` | Notebook, validator, readiness report, audited ridge reference | Independent leakage, schema, reproducibility, and Kaggle readiness verdict | 2026-07-18 12:49 WIB | 2026-07-18 12:53 WIB | Leakage `GO`, local reproduction passes; not ready pending fail-closed validator, final filename, clean notebook, and actual Kaggle Run All. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: D1-MAIN-013
Status: NEEDS_REVIEW
Last Read Revision: 0033
Last Update: 2026-07-18 13:39:55 +07:00

### Current Objective
Test fixed event-type counts as training-only per-road residual corrections to the strongest ridge candidate.
### Work Completed
- Created canonical coordination documentation.
- Verified required competition rules, role ownership, synchronization/reporting protocols, Day 1/Day 2 workflows, write-lock instructions, and single canonical status file.
- Cleaned the latest `AGENTS.md` formatting without changing its substantive rules.
- Added an opt-in pretrained candidate pantry with pinned-revision receipts, checksum verification, and selection gates.
- Initialized the independent repository and pushed the collaboration baseline to GitHub `main`.
- Simplified canonical naming for experiments, branches, artifacts, and submissions.
- Built `d1-e001-persist` and generated a schema-valid submission preview.
- Received independent `GO` for `d1-multifold-v1` and `KEEP` for `d1-e002-ridge` at commit `e2136b6`.
### Work in Progress
- Slot 1 used `d1-e002-ridge`; public MSE is 45.980 and remains diagnostic only.
- `d1-e002-ridge` remains frozen at commit `e2136b6`.
- `d1-e003-lagblend` is frozen as `REJECT` at commit `b341d6e`.
- `d1-e004-analog` is isolated on `exp/d1-e004-analog` and rejected without producing a submission.
- `d1-e005-ar15` is isolated on `exp/d1-e005-ar15` and rejected without producing a submission.
- Event-text audit found 11,160 and 5,039 aligned train strings plus 540 test strings; event vocabulary includes accident, closure, construction, traffic control, announcement, and turn restriction.
- `d1-e006-textres` passes every preregistered gate and awaits independent validation/leakage review.
- The fail-closed reference gate and clean local notebook are complete.
- The final competition-named notebook is `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`.
- Kaggle generated `submission.csv`; the downloaded file exactly matches the audited ridge predictions and is approved for slot 1.
### Latest Metrics
- Pretrained tooling tests: 4 passed.
- Data integrity: all NPY arrays finite; all 2,041,200 submission IDs parse completely.
- `d1-e001-persist`: MSE 29.6995; h5 25.9261; h10 29.7722; h15 33.4003.
- Block mean scores: 29.8669 and 29.5322; prediction mean 52.7290 km/h.
- Official-v1 mean15: mean 45.5482; std 10.3820; worst fold 54.8371.
- `d1-e002-ridge`: mean 39.0248; std 5.4669; worst fold 44.4867; 14.32% mean improvement.
- Ridge folds: 44.4867, 41.0327, 31.5551; 7 tests passed; runtime 9.59s.
- Clean notebook: 4.95s; 2,041,200 rows; exact numeric match with audited ridge CSV; 10 tests passed.
- Direct local Run All: 5.67s; automatic repository data discovery; exact numeric match retained.
- Kaggle output validation: 2,041,200 exact unique IDs; finite and nonnegative; 0 reference mismatches; mean 52.8826; min 0.0; max 101.5696.
- `d1-e003-lagblend`: mean 42.8914; folds 50.6941, 47.1967, 30.7834; worst 50.6941; `REJECT`; no submission generated.
- `d1-e004-analog`: mean 55.4014; folds 62.6974, 57.1239, 46.3828; worst 62.6974; `REJECT`; no submission generated.
- `d1-e005-ar15`: mean 39.0830; folds 44.8119, 41.1142, 31.3228; worst 44.8119; `REJECT`; no submission generated.
- `d1-e006-textres`: mean 38.3456; folds 44.0077, 40.5864, 30.4429; worst 44.0077; 1.74% improvement over ridge; all folds/horizons improve; runtime 22.76s.
### Files Changed
- `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`; `coordination/TEAM_STATUS.md`
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
- `task1/notebooks/d1-ridge-inference.ipynb`
- `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`
- `task1/reports/d1-submission-readiness.{md,json}`
### Decisions Needed
- Independent VALIDATION verdict for text alignment, training-only residual fitting, and whether the 1.74% gain is audit-safe.
### Tasks Dispatched to Other Agents
- `D1-VAL-001` to VALIDATION: temporal split, leakage, distribution, and metric audit.
- `D1-SUB-001` to SUBMISSION: schema/order/ID/value validator.
### Blockers
- NONE
### Next Action
- Hand commit and artifacts to VALIDATION; do not use slot 2 before `GO`.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D1-VAL-002
Status: IN_PROGRESS
Last Read Revision: 0032
Last Update: 2026-07-18 13:34:00 +07:00

### Scope Being Audited
- Public-LB gap for `d1-e002-ridge`: artifact identity, temporal representativeness, purge/embargo sensitivity, regime shift, road-level stability, and residual leakage risk.
### Evidence Reviewed
- Official data audit and baseline; commit `e2136b6`; `multifold.py`, `ridge_model.py`, runner, tests, config, notes, metrics, and full submission; independent metric and prediction reproduction.
### Findings
- Official-v1 uses three non-overlapping 720-origin folds per block, exact 15-origin purge, training-only fitting, and 372:168 aggregation; validation harness verdict is `GO`.
- Ridge reproduces exactly at MSE 39.0248 versus mean15 45.5482, improves every aggregate horizon and worst fold, and passes 7 tests; model verdict is `KEEP`.
- Submission predictions reproduce exactly: 2,041,200 unique ordered finite nonnegative values; all zero-history roads remain zero.
### Leakage Risks
- No target, preprocessing, text, graph, test label, API, or pretrained-weight leakage found in ridge fitting.
- Freeze fold boundaries now; changing official-v1 after seeing results would create validation-selection leakage.
### Validation Risks
- Ridge is worse than mean15 by 0.4985 MSE on fold 3, the latest tail in both blocks, despite large gains on folds 1 and 2.
- Hidden-test chronology remains unknown, so `KEEP` does not yet imply final-candidate or submission approval.
### Distribution or Fold Risks
- Fold-3 regression is concentrated at h10/h15; preserve it in comparisons and the writeup.
- Test routing has a wide observed margin (13-16 versus 210-211 all-zero roads) and exactly reproduces the 372:168 mixture.
### Recommendation
- GO for official-v1 validation; KEEP `d1-e002-ridge`; INVESTIGATE submission.

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Freeze official-v1, retain the tail caveat, record commit `e2136b6`, and complete `D1-SUB-001` plus clean-session notebook reproduction before requesting a Kaggle slot.
### Blockers
- NONE
### Next Action
- Diagnose the `39.0248` local versus `45.980` public gap without changing the frozen harness/model or using another submission slot.
<!-- VALIDATION:END -->

Only VALIDATION may update this section; it is read-only against the main pipeline.

## 6. Submission and Reproducibility Reviewer Status

<!-- SUBMISSION:START -->
Role: SUBMISSION
Current Task: D1-SUB-001
Status: BLOCKED
Last Read Revision: 0022
Last Update: 2026-07-18 12:53:02 +07:00

### Submission Schema Status
- PASS: independently reproduced 2,041,200 canonical ordered unique IDs and exact `id,speed` columns.
### ID and Row Validation
- PASS: exact template order, row count, and uniqueness; zero difference from frozen ridge reference.
### Missing, Infinity, and Label Validation
- PASS: all predictions finite and nonnegative in `[0.0, 101.569557]`; 120,750 structural zero predictions.
### Kaggle Path and Dependency Status
- SOURCE PASS: committed notebook uses only NumPy/pandas and discovers `/kaggle/input`; actual Kaggle environment remains unverified.
### Run-All Status
- LOCAL PASS: independent `python -I` run in 5.88s; KAGGLE NOT RUN.
### Model Weight Status
- PASS: deterministic retraining from official competition train speeds; no stored/private/pretrained weight.
### Reproducibility Risks
- No data leakage found. Blocking risks: reference mismatch is fail-open; current working notebook contains local-path outputs; final competition filename and actual Kaggle Run All are missing.
### Writeup Status
- Submission-readiness report exists; final technical writeup remains TODO under MAIN.
### Recommendation
- NOT READY

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Make reference mismatch fail closed with a test; clear notebook outputs; create `TeamName_TaskName_Notebook.ipynb`; obtain actual clean Kaggle Run All evidence.
### Blockers
- Actual Kaggle clean-session Run All has not been performed.
- Registered team name is needed for the required final notebook filename.
### Next Action
- MAIN fixes local readiness findings; designated Submission Manager runs Kaggle Run All and returns output evidence for final review.
<!-- SUBMISSION:END -->

Only SUBMISSION may update this section; it may not change model/validation without MAIN instruction.

## 7. Experiment Registry

| Experiment ID | Day | Owner | Hypothesis | Baseline | Validation | Mean | Fold Scores | Worst Fold | Std | Prediction Distribution | Runtime | Status | Artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1-e001-persist | DAY 1 | MAIN | Mean/last/trend forecasts from the exact 15-step history establish a leakage-safe floor. | NONE | 540 contiguous tail origins per train block | 29.6995 | 29.8669; 29.5322 | 29.8669 | 0.1674 | min 0.0; max 101.9333; mean 52.7290 | 4.83s | INVESTIGATE | `task1/experiments/d1-e001-persist/metrics.json` |
| d1-e002-ridge | DAY 1 | MAIN | Fixed per-road ridge on causal history summaries improves mean15 robustly. | d1-e001-persist | 3 purged 720-origin folds per block; 372:168 weighted | 39.0248 | 44.4867; 41.0327; 31.5551 | 44.4867 | 5.4669 | min 0.0; max 101.5696; mean 52.8826 | 9.59s | KEEP | `task1/experiments/d1-e002-ridge/metrics.json` |
| d1-e003-lagblend | DAY 1 | MAIN | Shared convex weights over the 15 causal lags can improve robustness without per-road overfit. | d1-e002-ridge | Frozen `d1-multifold-v1` | 42.8914 | 50.6941; 47.1967; 30.7834 | 50.6941 | 8.6799 | min 0.0; max 103.4315; mean 52.7449 | 14.75s | REJECT | `task1/experiments/d1-e003-lagblend/metrics.json` |
| d1-e004-analog | DAY 1 | MAIN | Road-level future deltas from nearest causal network states capture repeated traffic dynamics missed by ridge. | d1-e002-ridge | Frozen `d1-multifold-v1` | 55.4014 | 62.6974; 57.1239; 46.3828 | 62.6974 | 6.7709 | min 0.0; max 126.5625; mean 52.8064 | 6.98s | REJECT | `task1/experiments/d1-e004-analog/metrics.json` |
| d1-e005-ar15 | DAY 1 | MAIN | All 15 road-specific causal lags retain useful dynamics lost by five handcrafted summaries. | d1-e002-ridge | Frozen `d1-multifold-v1` | 39.0830 | 44.8119; 41.1142; 31.3228 | 44.8119 | 5.6911 | min 0.0; max 100.9657; mean 52.8687 | 11.99s | REJECT | `task1/experiments/d1-e005-ar15/metrics.json` |
| d1-e006-textres | DAY 1 | MAIN | Global event-type counts explain systematic per-road residuals beyond speed history. | d1-e002-ridge | Frozen `d1-multifold-v1` | 38.3456 | 44.0077; 40.5864; 30.4429 | 44.0077 | 5.7600 | min 0.0; max 101.7411; mean 52.9878 | 22.76s | KEEP | `task1/experiments/d1-e006-textres/metrics.json` |

Status: `PLANNED`, `RUNNING`, `KEEP`, `REJECT`, `INVESTIGATE`, `FINAL_CANDIDATE`. Record validation, seed, fold scores, worst fold, std, runtime, artifact, and decision. Never invent scores.

## 8. Submission Registry

### Day 1 - Task 1

| Slot | File | Experiment ID | Local Score | Public Score | Time | Submitted By | Final Candidate | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `submission.csv` | d1-e002-ridge | 39.0248 | 45.980 | 2026-07-18 13:14 WIB | Samuel Indriano | NO | First validated ridge entry; public 30% score is diagnostic only. |
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
| D1-HO-003 | MAIN | VALIDATION | 2026-07-18 12:24 WIB | `task1/src/{multifold.py,ridge_model.py}` and `task1/experiments/d1-e002-ridge/metrics.json` | Audit purge boundaries, training-only moments, 372:168 aggregation, zero guard, and fold-3 regression. | COMPLETED |
| D1-HO-004 | MAIN | SUBMISSION | 2026-07-18 12:40 WIB | `task1/notebooks/d1-ridge-inference.ipynb`, `task1/src/submission_validator.py`, and `task1/reports/d1-submission-readiness.{md,json}` | Independently inspect Kaggle paths/dependencies and perform actual clean-session `Run All`; return readiness verdict. | ACKNOWLEDGED |
| D1-HO-005 | MAIN | VALIDATION | 2026-07-18 13:39 WIB | Commit for `task1/src/text_residual_model.py`, `run_textres_experiment.py`, tests, config, metrics, notes, and ignored submission preview | Audit text-key alignment, origin-only features, training-only scaling/residual fitting, exact ridge reference, fold/horizon gains, and zero guard; return `GO`, `NO-GO`, or `INVESTIGATE`. | WAITING |

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
| 2026-07-18 12:28:10 +07:00 | 0016 | MAIN | D1-MAIN-006 | Started lightweight parallel candidate | Created `exp/d1-lagblend` from frozen ridge commit; preregistered shared 15-lag weights per horizon and regime | Run on unchanged folds; do not interpret as official before audit `GO` |
| 2026-07-18 12:29:17 +07:00 | 0017 | VALIDATION | D1-VAL-001 | Independently audited official-v1 and `d1-e002-ridge` | Harness `GO`; ridge `KEEP`; metrics and submission reproduced exactly; latest-tail regression remains visible | Freeze folds and complete submission/notebook review; submission stays `INVESTIGATE` |
| 2026-07-18 12:32:20 +07:00 | 0018 | MAIN | D1-MAIN-006 | Cancelled lightweight lagblend experiment | Removed all uncommitted lagblend code, metrics, and preview; preserved audit report and validation verdict | Return to frozen ridge branch and complete submission/notebook review |
| 2026-07-18 12:36:27 +07:00 | 0019 | MAIN | D1-MAIN-007 | Started submission-readiness implementation | Pushed audit commit `41a30bb`; claimed validator and clean-session notebook work without changing the frozen model | Reproduce output exactly and request independent SUBMISSION verdict |
| 2026-07-18 12:40:03 +07:00 | 0020 | MAIN | D1-MAIN-007 | Completed local submission-readiness implementation | Self-contained notebook reproduced the audited 2,041,200 predictions exactly in 4.95s; validator and 10 tests passed | SUBMISSION performs independent Kaggle `Run All`; verdict remains `INVESTIGATE` |
| 2026-07-18 12:45:49 +07:00 | 0021 | MAIN | D1-MAIN-008 | Fixed direct local notebook execution | Added relative repository data discovery and ignored local output path; local Run All and exact CSV comparison passed | User may restart kernel and Run All locally; Kaggle behavior is unchanged |
| 2026-07-18 12:49:20 +07:00 | 0022 | SUBMISSION | D1-SUB-001 | Started independent submission and leakage audit | Claimed committed notebook, validator, clean-run, path/dependency, and exact-output review; no Kaggle slot used | Reproduce locally, then determine whether actual Kaggle Run All is the only remaining gate |
| 2026-07-18 12:53:02 +07:00 | 0023 | SUBMISSION | D1-SUB-001 | Completed local submission and leakage audit | Leakage `GO`; exact clean reproduction and schema pass; `NOT READY` due fail-open reference check, non-final filename, dirty local outputs, and missing actual Kaggle Run All | Fix local blockers, then perform Kaggle Run All before any submission slot |
| 2026-07-18 12:56:12 +07:00 | 0024 | MAIN | D1-MAIN-009 | Started submission blocker repair | Accepted all four audit findings; frozen model and Kaggle slot remain untouched | Make reference mismatch fail closed, clean/name notebook, and run it in Kaggle |
| 2026-07-18 13:05:37 +07:00 | 0025 | MAIN | D1-MAIN-009 | Prepared final competition-named notebook | PDF page 14 confirms `TeamName_TaskName_Notebook.ipynb`; clean byte-identical copy created as `EnterYourTeamName_Task1_Notebook.ipynb` | Upload to Kaggle and perform Restart Session plus Run All; do not use a submission slot yet |
| 2026-07-18 13:12:33 +07:00 | 0026 | MAIN | D1-MAIN-009 | Validated Kaggle-generated submission and closed readiness repair | `submission.csv` is READY with 2,041,200 exact IDs and zero numeric mismatches against audited ridge; slot 1 approved | Submission Manager uploads the validated file and reports public score |
| 2026-07-18 13:18:28 +07:00 | 0027 | MAIN | D1-MAIN-010 | Recorded slot 1 and preregistered next model experiment | Ridge public MSE 45.980, rank 12 at observation; `d1-e003-lagblend` will use frozen folds and no leaderboard tuning | Implement shared convex lag weights and protect slot 2 until validation and audit |
| 2026-07-18 13:21:30 +07:00 | 0028 | MAIN | D1-MAIN-010 | Completed preregistered lagblend experiment | `REJECT`: mean 42.8914 versus ridge 39.0248; only fold 3 improves and all four gates fail; no submission generated | Preserve slot 2 and test a structurally different analog model |
| 2026-07-18 13:24:04 +07:00 | 0029 | MAIN | D1-MAIN-011 | Started separate-branch analog experiment | `exp/d1-e004-analog` uses fixed training-only state features and nearest-neighbor future deltas; no score or slot used yet | Implement, test, and compare on frozen folds |
| 2026-07-18 13:27:22 +07:00 | 0030 | MAIN | D1-MAIN-011 | Completed preregistered analog experiment | `REJECT`: mean 55.4014 versus ridge 39.0248; no fold or horizon improves; no submission generated | Preserve slot 2 and test per-road full-history AR15 ridge on a new branch |
| 2026-07-18 13:28:49 +07:00 | 0031 | MAIN | D1-MAIN-012 | Started separate-branch AR15 experiment | Same per-road ridge and alpha 0.1, replacing five summaries with all 15 causal lags; no score or slot used yet | Implement, test, and compare on frozen folds |
| 2026-07-18 13:31:38 +07:00 | 0032 | MAIN | D1-MAIN-012 | Completed preregistered AR15 experiment | `REJECT`: mean 39.0830 versus ridge 39.0248; only fold 3 improves and no aggregate horizon improves; no submission generated | Preserve slot 2 and inspect causal event-text features before another model |
| 2026-07-18 13:34:47 +07:00 | 0033 | MAIN | D1-MAIN-013 | Started separate-branch text residual experiment | Official texts align to every train timestep/test sample; six fixed event counts plus total events will correct ridge residuals without APIs or embeddings | Implement, test, and compare on frozen folds |
| 2026-07-18 13:39:55 +07:00 | 0034 | MAIN | D1-MAIN-013 | Completed text residual candidate and requested independent audit | `KEEP`: mean 38.3456, 1.74% better than ridge, all folds/horizons and worst fold improve; 24 tests and submission validator pass | VALIDATION audits leakage and alignment before any slot 2 decision |

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
