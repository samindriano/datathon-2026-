# Datathon 2026 Team Status

Revision: 0064
Active Day: DAY 1
Active Task: TASK 1
Last Global Update: 2026-07-18 16:11:49 +07:00
Competition Clock: RUNNING
Repository Branch: exp/d1-e016-lowrank
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
| D1-DEC-010 | 2026-07-18 13:42 WIB | Freeze textres at commit `c603cd9` for audit and preregister `d1-e007-graphres` on a separate branch. | Official adjacency is sparse and directed with 5,122 nonzeros; symmetric external-neighbor summaries can test graph signal without a GNN or new dependency. | MAIN | Graph orientation or feature computation cannot be made deterministic and leakage-safe. |
| D1-DEC-011 | 2026-07-18 13:50 WIB | Respond to textres audit with one preregistered OOD guard that neutralizes only the `prohibit left turn` residual feature when it falls outside training range. | VALIDATION found test-m2 `z=-3.434` on this feature and a risky positive correction; leakage safety and aligned text gain otherwise received `GO`/`KEEP`. | MAIN | Guard fails to retain broad local gains or does not remove the risky test correction. |
| D1-DEC-012 | 2026-07-18 13:56 WIB | Treat the failed raw-range guard as frozen and preregister a new standard `|z| > 3` guard for only `prohibit left turn`. | The audit measures shift in standardized units (`z=-3.434`), while `d1-e008-textood` proved raw min/max activates on zero test samples. | MAIN | The z-guard loses broad local gain, fails to reverse risky m2 correction, or requires threshold tuning. |
| D1-DEC-013 | 2026-07-18 14:02 WIB | Preregister an untuned 50:50 prediction blend of audited graphres and frozen textzguard. | Graphres and safe text use distinct official signals; equal averaging is deterministic, avoids residual double-counting, and requires no validation/leaderboard weight search. | MAIN | The blend fails to improve graphres broadly, worsens its worst fold, or reverses the safe m2 correction. |
| D1-DEC-014 | 2026-07-18 14:16 WIB | Accept independent `GO`/`KEEP` for `d1-e010-graphtextblend` and designate it the conditional slot-2 candidate. | Audit reproduced commit `e99d6d6`, fixed 50:50 weights, MSE 37.9040, 15/18 cell gains, safer m2 correction, and no material leakage. | MAIN | Kaggle Run All or SUBMISSION review fails exact reproduction, or a verified implementation defect appears. |
| D1-DEC-015 | 2026-07-18 14:17 WIB | Human Submission Manager retains exclusive control of Chrome/Kaggle upload, Run All, and submission actions. | User explicitly requested that Codex not control Chrome and will upload the notebook manually. | MAIN | User explicitly requests browser assistance again. |
| D1-DEC-016 | 2026-07-18 14:40 WIB | Record slot 2 and prefer `d1-e010-graphtextblend` as the current final-selection candidate; retain ridge only as a reproducible fallback. | Public MSE improved `45.980` to `45.168`; independent audit found positive paired gains on 3/3 folds, 6/6 block-folds, 18/18 block-fold-horizons, and 36/36 temporal chunks. | MAIN | A later preregistered candidate passes frozen validation, independent audit, and reproducibility gates with materially stronger evidence. |
| D1-DEC-017 | 2026-07-18 14:41 WIB | Preregister one final bounded `d1-e011-globalstate` experiment that replaces graph-neighbor summaries with five active-road city-state summaries and uses a fixed 50:50 blend with frozen textzguard. | Graph audit found cross-road/global context gain but no topology-specific advantage; direct city-state features test that mechanism without weight or fold tuning. | MAIN | Implementation cannot preserve causal history-only features, zero guards, frozen folds, or the fixed acceptance gate. |
| D1-DEC-018 | 2026-07-18 14:45 WIB | Freeze e011 as `REJECT` because its blend loses to globalstate alone; treat the unexpectedly strong globalstate-only result as a new post-discovery hypothesis rather than changing the failed gate. | Fixed blend MSE `35.7488` versus globalstate `35.3894`; e011 failed its component-dominance condition even though globalstate beat e010 by `6.63%`. | MAIN | None; e011 remains rejected. Any globalstate-only continuation requires a new experiment ID, stricter preregistration, and independent audit. |
| D1-DEC-019 | 2026-07-18 14:47 WIB | Preregister `d1-e012-globalstate-only` as a disclosed post-discovery candidate whose new evidence comes from temporal-chunk robustness, not aggregate scores already observed in e011. | Globalstate-only improved e010 by 6.63% in e011 diagnostics, but selecting it after seeing that result requires stricter unseen stress gates and independent audit. | MAIN | Any stress gate fails, reproduction differs, or independent audit finds leakage/selection risk too large. |
| D1-DEC-020 | 2026-07-18 14:50 WIB | Reject e012 without relaxing its unseen chunk gates, stop further large model experiments, and retain e010 as the final-selection recommendation. | E012 won only 31/36 chunks and its worst chunk regressed 1.9517 MSE; e010's independent audit won 36/36 chunks versus ridge and already passed Kaggle reproduction. | MAIN | A verified implementation defect invalidates e012 stress results or e010 artifacts; otherwise no further modeling before finalization. |
| D1-DEC-021 | 2026-07-18 14:55 WIB | Use the remaining two-hour window for exactly one conservative `d1-e013-stableblend`: fixed 75% e010 plus 25% globalstate, with no weight search. | User explicitly prefers using the remaining opportunity; e012 exposed a large but volatile signal that can be shrunk toward the already stable e010 anchor. | MAIN | Any preregistered aggregate, chunk, inference-safety, audit, or notebook gate fails; then e010 remains final and modeling stops. |
| D1-DEC-022 | 2026-07-18 15:00 WIB | Mark e013 `KEEP / NEEDS_REVIEW` locally and protect slot 3 until independent audit plus exact Kaggle notebook reproduction. | Fixed 75:25 blend improves e010 by 3.55%, wins 3/3 folds, 3/3 horizons, 18/18 cells, and 36/36 chunks with positive minimum chunk gain 0.1243. | MAIN | Audit is not `GO/KEEP`, notebook differs from frozen CSV, validator is not `READY`, or competition time becomes insufficient. |
| D1-DEC-023 | 2026-07-18 15:15 WIB | Accept independent `GO/KEEP` for e013 and advance it to notebook/submission-readiness review while retaining e010 as final until public evidence exists. | Audit reproduced all metrics and CSV; stricter purge retained 3.543% gain; e013 won 17/17 walk-forward windows and 102/102 diagnostic chunks, with conservative RMS change 0.431 km/h. | MAIN | Kaggle Run All differs from frozen CSV, SUBMISSION is not `READY`, or public/operational evidence invalidates slot-3 use. |
| D1-DEC-024 | 2026-07-18 15:19 WIB | Accept local e013 notebook readiness and require actual Kaggle Run All plus independent output review before slot 3. | Clean five-cell notebook completed in 18 seconds; validator found 0 mismatches, max difference 0.0, exact IDs, and hash `84703083...b6e1d`. | MAIN | Kaggle environment output differs, hidden dependency appears, or SUBMISSION returns other than `READY`. |
| D1-DEC-025 | 2026-07-18 15:25 WIB | Accept actual Kaggle e013 Run All output as an exact frozen-candidate reproduction; keep slot 3 pending only independent SUBMISSION confirmation. | Downloaded `submission.csv` has 2,041,200 exact IDs, zero mismatches, max difference 0.0, and hash `84703083...b6e1d`. | MAIN | SUBMISSION finds a provenance/path/schema issue or the human upload target differs from the validated file. |
| D1-DEC-026 | 2026-07-18 15:52 WIB | Record slot 3 and prefer e013 as the current final-selection candidate over e010. | Public MSE improved `45.168` to `43.511`, closely matching the 3.545% local gain; post-submission audit gives `GO/KEEP` and medium-high private confidence. | MAIN | A final bounded candidate passes stricter frozen validation, audit, Kaggle reproduction, and provides stronger evidence before freeze. |
| D1-DEC-027 | 2026-07-18 16:05 WIB | Preregister parallel `d1-e016-lowrank` on a separate worktree: fixed rank 4, 360 training-only PCA samples, and unchanged 75% e010 plus 25% latent-state blend. | User explicitly requested one parallel candidate while E015 runs; low-rank cross-road factors are orthogonal to seasonal phase and hand-built distribution summaries. | MAIN | Any frozen aggregate, cell, chunk, inference, runtime, or reproducibility gate fails; no rank/sample/weight retuning is allowed. |
| D1-DEC-028 | 2026-07-18 16:11 WIB | Reject `d1-e016-lowrank` without retuning and preserve both remaining Kaggle slots. | Mean MSE improved 2.74% with 18/18 cells and 34/36 chunks, but worst chunk `-0.3186` breached the frozen `-0.25` safety floor. | MAIN | None within E016; any continuation must be a separately preregistered hypothesis, not a relaxed threshold or tuned blend. |

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
| D1-MAIN-014 | DAY 1 | MAIN | DONE | MEDIUM | Frozen textres handoff and official adjacency | Per-road ridge augmented with symmetric neighbor summaries | Last simple official-signal candidate before considering an ensemble | 2026-07-18 13:42 WIB | 2026-07-18 13:53 WIB | `KEEP`: MSE 38.1750; independent audit gives leakage `GO` and prefers graphres after notebook readiness. |
| D1-MAIN-015 | DAY 1 | MAIN | DONE | HIGH | Textres audit `INVESTIGATE` inference | Training-range OOD neutralization for one risky text feature | Robust textres variant before any graph-text combination | 2026-07-18 13:50 WIB | 2026-07-18 13:54 WIB | `REJECT`: raw-range guard never activates on test and leaves risky m2 correction unchanged; no CSV. |
| D1-MAIN-016 | DAY 1 | MAIN | DONE | HIGH | Rejected raw-range guard and audit `z=-3.434` | Fixed `|z| > 3` neutralization for one text feature | Decide whether a safe text path remains viable before graph-plus-text | 2026-07-18 13:56 WIB | 2026-07-18 14:16 WIB | `KEEP`; component identity, fixed guard, correction direction, and leakage safety verified in blend audit. |
| D1-MAIN-017 | DAY 1 | MAIN | DONE | HIGH | Graphres audit `GO`/`KEEP` and locally accepted textzguard | Fixed 50:50 graphres/textzguard prediction blend | Test complementary official graph and text signals without weight tuning | 2026-07-18 14:02 WIB | 2026-07-18 14:16 WIB | Independent audit `GO`/`KEEP`; conditional slot-2 candidate after Kaggle/SUBMISSION readiness. |
| D1-MAIN-018 | DAY 1 | MAIN | DONE | HIGH | Frozen blend commit `e99d6d6` | Self-contained clean-session inference notebook and exact CSV reproduction | Prepare reproducibility gate without spending a Kaggle slot | 2026-07-18 14:06 WIB | 2026-07-18 14:23 WIB | Actual Kaggle output matches frozen CSV exactly; independent SUBMISSION verdict remains. |
| D1-MAIN-019 | DAY 1 | MAIN | DONE | HIGH | Audited e010 and graph topology-null finding | Direct active-road city-state features plus fixed guarded-text blend | Decide whether any candidate materially exceeds e010 without leaderboard tuning | 2026-07-18 14:41 WIB | 2026-07-18 14:45 WIB | `REJECT`: blend loses to globalstate alone; no CSV or slot. Globalstate-only becomes a separate post-discovery hypothesis. |
| D1-MAIN-020 | DAY 1 | MAIN | DONE | HIGH | e011 globalstate-only diagnostic | Frozen globalstate model plus unseen temporal-chunk and correction-distribution stress tests | Determine whether the post-discovery candidate merits independent audit and notebook work | 2026-07-18 14:47 WIB | 2026-07-18 14:50 WIB | `REJECT`: 31/36 chunk wins and worst chunk -1.9517 fail frozen gates; no CSV, audit handoff, notebook, or slot. |
| D1-MAIN-021 | DAY 1 | MAIN | DONE | HIGH | Stable e010 plus volatile e012 signal | Fixed 75:25 e010/globalstate shrinkage blend | Capture meaningful globalstate gain while restoring temporal robustness | 2026-07-18 14:55 WIB | 2026-07-18 15:52 WIB | Slot 3 public 43.511; audit `GO/KEEP`; e013 is current final-selection candidate. |
| D1-MAIN-023 | DAY 1 | MAIN | DONE | HIGH | Confirmed cross-road global-state gain | Training-fold-only rank-4 latent spatial factors under fixed 75:25 e010 anchor blend | Test a cross-road representation orthogonal to E015 seasonal phase | 2026-07-18 16:05 WIB | 2026-07-18 16:11 WIB | `REJECT`: strong aggregate gain, but worst temporal chunk `-0.3186` fails the frozen safety floor; no CSV, audit, notebook, or slot. |
| D1-SUB-001 | DAY 1 | SUBMISSION | DONE | HIGH | Handoff `D1-HO-004` | Notebook, validator, readiness report, audited ridge reference | Independent leakage, schema, reproducibility, and Kaggle readiness verdict | 2026-07-18 12:49 WIB | 2026-07-18 14:27 WIB | Actual Kaggle blend output is `READY`; exact frozen-output match and all schema/reproducibility gates pass. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: D1-MAIN-023
Status: DONE
Last Read Revision: 0063
Last Update: 2026-07-18 16:11:49 +07:00

### Current Objective
Preserve e013 as the final candidate after E016 failed one frozen temporal safety gate.
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
- `d1-e006-textres` is frozen for audit at commit `c603cd9`; graph work occurs only on `exp/d1-e007-graphres`.
- Adjacency audit: shape 1,260 x 1,260, 5,122 binary nonzeros, directed, diagonal present, external degree small.
- `d1-e007-graphres` passes all preregistered gates; independent audit gives leakage `GO`, evidence `KEEP`, and prefers it over exact textres after notebook readiness.
- VALIDATION gave textres leakage `GO` and evidence `KEEP`, but exact inference remains `INVESTIGATE` because test-m2 `prohibit left turn` is OOD and pushes correction upward.
- `d1-e008-textood` is `REJECT`: its raw-range guard activates on zero test samples and leaves test-m2 correction unchanged at `+0.3470` km/h.
- `d1-e009-textzguard` is isolated on `exp/d1-e009-textzguard` with a fixed `|z| > 3` rule before scoring.
- `d1-e009-textzguard` passes all preregistered gates; its test-m2 correction is `-0.0899` km/h and requires independent review before reuse.
- `d1-e010-graphtextblend` passes all preregistered gates at MSE `37.9040`; fold 2 regresses slightly versus graphres and remains visible for audit.
- The blend notebook reproduces the frozen CSV exactly in an isolated `python -I` run; all code-cell outputs remain clean.
- VALIDATION independently gives blend leakage `GO` and candidate `KEEP`; it is the conditional slot-2 candidate after Kaggle/SUBMISSION readiness.
- The fail-closed reference gate and clean local notebook are complete.
- The final competition-named notebook is `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`.
- Kaggle generated `submission.csv`; the downloaded file exactly matches the audited ridge predictions and is approved for slot 1.
- Slot 2 used `d1-e010-graphtextblend`; public MSE is 45.168 and the independent post-submission audit prefers it over ridge for final selection.
- `d1-e011-globalstate` is `REJECT` because its 50:50 blend does not beat globalstate alone; no submission was generated.
- `d1-e012-globalstate-only` is `REJECT`: it fails two new temporal-chunk robustness gates; no submission was generated.
- `d1-e013-stableblend` is local `KEEP`: fixed 75:25 weights pass every aggregate, temporal, inference-safety, and schema gate.
- Independent e013 audit returns model/leakage `GO` and candidate `KEEP`; selection bias remains disclosed and e010 stays final pending public evidence.
- The competition-named e013 notebook reproduces the frozen CSV locally with zero mismatches and clean outputs.
- Actual Kaggle Run All produced `C:\Users\Sam\Downloads\submission.csv`; it matches the frozen e013 CSV exactly.
- Slot 3 public MSE is 43.511; independent public/private risk audit recommends e013 over e010.
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
- `d1-e007-graphres`: mean 38.1750; folds 43.7473, 39.9422, 30.8355; worst 43.7473; 2.18% improvement over ridge; all folds/horizons improve; runtime 26.94s.
- `d1-e008-textood`: mean 38.2840; folds 44.0077, 40.5864, 30.2579; worst 44.0077; raw-range guard does not activate on test; `REJECT`; no submission generated.
- `d1-e009-textzguard`: mean 38.2840; folds 44.0077, 40.5864, 30.2579; worst 44.0077; test-m2 guard 144/168; correction -0.0899; `KEEP`; runtime 21.65s.
- `d1-e010-graphtextblend`: mean 37.9040; folds 43.4387, 39.9813, 30.2920; worst 43.4387; all horizons improve graphres; correction -0.1674; `KEEP`; runtime 37.25s.
- Blend notebook: 16.18s; 2,041,200 exact values; zero reference mismatches; validator `READY`; 34 tests pass.
- Blend audit: 15/18 block-fold-horizon cells improve graphres; fold 2 regresses +0.0391; correction m2 remains -0.1674 km/h.
- Kaggle-generated `C:\Users\Sam\Downloads\submission.csv` is an exact numeric match to frozen `d1-e010-graphtextblend`: 2,041,200 rows, zero mismatches, max difference 0.0.
- Public-to-private audit: e010 retains 72.45% of its local gain on public and improves ridge on all 36/36 consecutive temporal chunks; current final-selection recommendation is e010.
- e011 diagnostic globalstate-only: mean 35.3894; folds 40.0654, 36.4597, 29.6431; worst 40.0654; std 4.3217; all folds/horizons beat e010; test-m2 correction -0.4117 km/h.
- E012 unseen stress: 17/18 block-fold-horizon wins but only 31/36 temporal-chunk wins; median chunk gain 1.9871, minimum -1.9517, weakest origin win rate 49.44%; `REJECT`.
- E013: mean 36.5603; folds 41.7515, 38.4076, 29.5217; worst 41.7515; std 5.1609; 18/18 cell and 36/36 chunk wins versus e010; minimum chunk gain 0.1243; `KEEP / NEEDS_REVIEW`.
- E013 audit stress: stricter purge gain 3.543%; 17/17 walk-forward windows and 102/102 chunks improve; worst gains +0.5940 window and +0.0967 chunk; RMS test change 0.431 km/h.
- E013 notebook: isolated 18-second run; exact 2,041,200 IDs; zero numeric mismatches; max difference 0.0; validator `READY`; 44 tests pass.
- Actual Kaggle e013 output: 2,041,200 exact IDs; min 0.0; max 101.6040; mean 52.863277; zero mismatches; max difference 0.0; hash `84703083...b6e1d`.
- E013 public confirmation: gain 1.657 MSE (3.669%) versus e010, closely aligned with local gain 1.3438 (3.545%); public retains 123.3% of local gain.
- E016 low-rank blend: mean MSE 35.5576 versus e013 36.5603; all folds/horizons and 18/18 cells improve, but worst chunk -0.3186 fails the frozen -0.25 floor, so status is REJECT without retuning.
### Files Changed
- `coordination/TEAM_STATUS.md`; `task1/src/lowrank_state_model.py`; `task1/src/run_lowrank_experiment.py`; tests; `task1/experiments/d1-e016-lowrank/` artifacts.
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
- `task1/reports/d1-e010-kaggle-output-validation.json`
- `task1/experiments/d1-e016-lowrank/metrics.json`
### Decisions Needed
- Await the independent E015 result; E016 is closed and may not consume a Kaggle slot.
### Tasks Dispatched to Other Agents
- `D1-VAL-001` to VALIDATION: temporal split, leakage, distribution, and metric audit.
- `D1-SUB-001` to SUBMISSION: schema/order/ID/value validator.
### Blockers
- NONE
### Next Action
- Keep E013 selected; do not retune E016 or relax its failed gate.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D1-VAL-003
Status: DONE
Last Read Revision: 0050
Last Update: 2026-07-18 14:35:23 +07:00

### Scope Being Audited
- Post-submission public-to-private risk and paired temporal stability of `d1-e010-graphtextblend` versus slot-1 ridge.
### Evidence Reviewed
- Public scores ridge `45.980` and blend `45.168`; frozen local metrics; exact refits across six official block-fold windows; per-origin, horizon, and consecutive-time-chunk paired errors.
### Findings
- Public gain is `0.812` MSE (`1.766%`), retaining `72.45%` of the local paired gain `1.1208` (`2.872%`).
- Versus ridge, blend gains are positive on all `3/3` weighted folds, `6/6` block-folds, `18/18` block-fold-horizon cells, and `36/36` consecutive 120-origin chunks.
- Fold gains are `1.0480`, `1.0514`, and `1.2630`; a 10,000-repeat 30-origin moving-block bootstrap gives diagnostic gain interval `[0.9204, 1.3355]`.
### Leakage Risks
- No new leakage or implementation issue found; the fixed blend was preregistered before its local and public scores.
- The bootstrap is a stress diagnostic on frozen folds, not a replacement validation or private probability estimate.
### Validation Risks
- Absolute calibration remains optimistic: public-minus-local gap is `6.9552` for ridge and `7.2640` for blend.
- Private chronology, composition, and leaderboard masking unit are unknown; no precise private score or probability is defensible.
- Text guard local activation remains concentrated in m2 fold 3, and graph benefit is generic cross-road context rather than proven topology.
### Distribution or Fold Risks
- Raw fold-score standard deviation is slightly worse (`5.5645` blend versus `5.4669` ridge), so only paired-gain consistency—not lower absolute variance—is supported.
- The smallest 120-origin chunk gain is positive but narrow at `0.0762`; hidden extreme regimes could still reverse it.
### Recommendation
- `GO`/`KEEP`. Prefer `d1-e010-graphtextblend` over ridge as the final-selection candidate; current evidence makes a private improvement more likely than a private regression, without guaranteeing it.

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Record the slot-2 public score and use this paired audit in final selection. Do not spend another slot merely to chase the public delta.
### Blockers
- NONE
### Next Action
- MAIN decides the final selected submission; retain ridge as a reproducible fallback.
<!-- VALIDATION:END -->

Only VALIDATION may update this section; it is read-only against the main pipeline.

## 6. Submission and Reproducibility Reviewer Status

<!-- SUBMISSION:START -->
Role: SUBMISSION
Current Task: D1-SUB-001
Status: DONE
Last Read Revision: 0049
Last Update: 2026-07-18 14:27:46 +07:00

### Submission Schema Status
- PASS: actual Kaggle CSV has 2,041,200 canonical ordered unique IDs and exact `id,speed` columns.
### ID and Row Validation
- PASS: exact template order, row count, and uniqueness; zero numeric differences from frozen blend commit `e99d6d6`.
### Missing, Infinity, and Label Validation
- PASS: all predictions finite and nonnegative in `[0.0, 101.63601]`; 120,750 structural zero predictions.
### Kaggle Path and Dependency Status
- PASS: notebook uses only Python, NumPy, pandas, and official competition inputs; actual Kaggle `Run All` completed.
### Run-All Status
- PASS: user completed Kaggle Restart Session / Run All and downloaded `/kaggle/working/submission.csv`.
### Model Weight Status
- PASS: deterministic retraining from official train speeds, event text, and adjacency; no stored/private/pretrained weight or external API.
### Reproducibility Risks
- No blocking risk found. Independent validator reports zero reference mismatches, maximum absolute difference `0.0`, and value fingerprint `a1e1f9f9296022fea70682333145f3a798dc33a4472e93f7f822e51c87d4644e`.
### Writeup Status
- Submission-readiness report exists; final technical writeup remains TODO under MAIN.
### Recommendation
- READY — `SUBMIT` `d1-e010-graphtextblend` as slot 2 using the exact validated Kaggle output.

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Authorize the designated Submission Manager to upload a byte-identical copy named `sub-s02-d1-e010-graphtextblend.csv`, then record slot 2 and its public score.
### Blockers
- None for slot-2 submission readiness.
### Next Action
- MAIN issues slot-2 approval; designated Submission Manager submits without editing prediction content.
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
| d1-e007-graphres | DAY 1 | MAIN | Neighbor history summaries add local road-network context missing from independent per-road ridge. | d1-e002-ridge | Frozen `d1-multifold-v1` | 38.1750 | 43.7473; 39.9422; 30.8355 | 43.7473 | 5.4173 | min 0.0; max 101.5309; mean 52.8380 | 26.94s | KEEP | `task1/experiments/d1-e007-graphres/metrics.json` |
| d1-e008-textood | DAY 1 | MAIN | Neutralizing the single OOD turn-restriction path preserves text gain while avoiding risky test-m2 extrapolation. | d1-e006-textres | Frozen `d1-multifold-v1` | 38.2840 | 44.0077; 40.5864; 30.2579 | 44.0077 | 5.8446 | min 0.0; max 101.7411; mean 52.9878 | 18.54s | REJECT | `task1/experiments/d1-e008-textood/metrics.json` |
| d1-e009-textzguard | DAY 1 | MAIN | A standard three-sigma guard neutralizes the audited text OOD path while preserving causal aligned-text gain. | d1-e006-textres | Frozen `d1-multifold-v1` | 38.2840 | 44.0077; 40.5864; 30.2579 | 44.0077 | 5.8446 | min 0.0; max 101.7411; mean 52.8519 | 21.65s | KEEP | `task1/experiments/d1-e009-textzguard/metrics.json` |
| d1-e010-graphtextblend | DAY 1 | MAIN | Equal averaging of complementary graph and guarded-text predictions improves robustness without tuning blend weights. | d1-e007-graphres; d1-e009-textzguard | Frozen `d1-multifold-v1` | 37.9040 | 43.4387; 39.9813; 30.2920 | 43.4387 | 5.5645 | min 0.0; max 101.6360; mean 52.8449 | 37.25s | KEEP | `task1/experiments/d1-e010-graphtextblend/metrics.json` |
| d1-e011-globalstate | DAY 1 | MAIN | Direct citywide active-road summaries capture the generic cross-road context found by graph audit; a fixed 50:50 blend with frozen textzguard can materially improve e010 without tuning. | d1-e010-graphtextblend | Frozen `d1-multifold-v1` | 35.7488 | 40.7378; 37.4727; 29.0358 | 40.7378 | 4.9304 | min 0.0; max 101.6245; mean 52.8851 | 36.81s | REJECT | `task1/experiments/d1-e011-globalstate/metrics.json` |
| d1-e012-globalstate-only | DAY 1 | MAIN | The post-discovery globalstate-only signal is broad enough to survive strict unseen temporal-chunk stress and justify audit despite selection after e011 diagnostics. | d1-e010-graphtextblend | Frozen `d1-multifold-v1` plus preregistered 120-origin chunks | 35.3894 | 40.0654; 36.4597; 29.6431 | 40.0654 | 4.3217 | min 0.0; max 101.5080; mean 52.9184 | 36.67s | REJECT | `task1/experiments/d1-e012-globalstate-only/metrics.json` |
| d1-e013-stableblend | DAY 1 | MAIN | Fixed 75% e010 plus 25% globalstate captures part of the large global signal while shrinking the five unstable e012 chunks toward the audited anchor. | d1-e010-graphtextblend; d1-e012-globalstate-only | Frozen `d1-multifold-v1` plus fixed 120-origin chunks | 36.5603 | 41.7515; 38.4076; 29.5217 | 41.7515 | 5.1609 | min 0.0; max 101.6040; mean 52.8633 | 61.14s | KEEP | `task1/experiments/d1-e013-stableblend/metrics.json` |
| d1-e016-lowrank | DAY 1 | MAIN | Four training-fold-only latent road factors capture coordinated spatial modes that global averages, graph neighbors, and seasonal phase miss. | d1-e013-stableblend | Frozen `d1-multifold-v1` plus fixed 120-origin chunks | 35.5576 | 40.5674; 37.0736; 29.0317 | 40.5674 | 4.8299 | min 0.0; max 100.3403; mean 52.8626 | 80.75s | REJECT | `task1/experiments/d1-e016-lowrank/metrics.json` |

Status: `PLANNED`, `RUNNING`, `KEEP`, `REJECT`, `INVESTIGATE`, `FINAL_CANDIDATE`. Record validation, seed, fold scores, worst fold, std, runtime, artifact, and decision. Never invent scores.

## 8. Submission Registry

### Day 1 - Task 1

| Slot | File | Experiment ID | Local Score | Public Score | Time | Submitted By | Final Candidate | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `submission.csv` | d1-e002-ridge | 39.0248 | 45.980 | 2026-07-18 13:14 WIB | Samuel Indriano | NO | First validated ridge entry; public 30% score is diagnostic only. |
| 2 | `sub-s02-d1-e010-graphtextblend.csv` | d1-e010-graphtextblend | 37.9040 | 45.168 | 2026-07-18 14:34 WIB | Samuel Indriano | YES | Exact Kaggle Run All output; independently `READY`; preferred over ridge by paired temporal audit. |
| 3 | `sub-s03-d1-e013-stableblend.csv` | d1-e013-stableblend | 36.5603 | 43.511 | 2026-07-18 15:51 WIB | Samuel Indriano | YES | Exact Kaggle Run All output; audit `GO/KEEP`; local and public gains align closely. |
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
| D1-HO-005 | MAIN | VALIDATION | 2026-07-18 13:39 WIB | Commit for `task1/src/text_residual_model.py`, `run_textres_experiment.py`, tests, config, metrics, notes, and ignored submission preview | Audit text-key alignment, origin-only features, training-only scaling/residual fitting, exact ridge reference, fold/horizon gains, and zero guard; return `GO`, `NO-GO`, or `INVESTIGATE`. | COMPLETED |
| D1-HO-006 | MAIN | VALIDATION | 2026-07-18 13:47 WIB | `task1/src/graph_model.py`, `run_graphres_experiment.py`, tests, config, metrics, notes, and ignored submission preview | Audit symmetric adjacency construction, diagonal removal, row normalization, training-only fitting, score reproduction, and zero guard; return `GO`, `NO-GO`, or `INVESTIGATE`. | COMPLETED |
| D1-HO-007 | MAIN | VALIDATION | 2026-07-18 14:00 WIB | `d1-e009-textzguard` code, tests, config, metrics, notes, and ignored submission preview | Audit training-only z-score, fixed threshold, guard activation, exact score reproduction, correction direction, and zero guard. | COMPLETED |
| D1-HO-008 | MAIN | VALIDATION | 2026-07-18 14:05 WIB | `d1-e010-graphtextblend` code, tests, config, metrics, notes, and ignored submission preview | Audit fixed weights, component identity, exact score reproduction, fold-2 regression, correction direction, and zero guard. | COMPLETED |
| D1-HO-009 | MAIN | SUBMISSION | 2026-07-18 14:11 WIB | `EnterYourTeamName_Task1_Notebook.ipynb`, `d1-e010-notebook-readiness.{md,json}`, and downloaded Kaggle `submission.csv` | Inspect self-contained paths/dependencies, run clean Kaggle session, and compare output exactly with frozen blend CSV. | COMPLETED |
| D1-HO-010 | MAIN | VALIDATION | 2026-07-18 15:00 WIB | Commit `27baf8f` containing `d1-e013-stableblend` code, tests, config, metrics, notes, and ignored CSV | Reproduce fixed 75:25 weights, 3/3 folds, 18/18 cells, 36/36 chunks, correction direction, zero guard, and selection-history disclosure; return `GO`, `NO-GO`, or `INVESTIGATE`. | COMPLETED |
| D1-HO-011 | MAIN | SUBMISSION | 2026-07-18 15:19 WIB | `EnterYourTeamName_Task1_Notebook.ipynb`, frozen e013 CSV, `d1-e013-notebook-readiness.{md,json}`, and actual Kaggle output validation | Inspect clean-session provenance, paths/dependencies, and exact output comparison; return `READY`, `NOT READY`, or `INVESTIGATE`. | WAITING |

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
| 2026-07-18 13:42:49 +07:00 | 0035 | MAIN | D1-MAIN-014 | Started separate-branch graph residual experiment | Textres frozen at `c603cd9`; sparse symmetric external-neighbor summaries will augment ridge without changing validation | Implement, test, and compare while slot 2 remains protected |
| 2026-07-18 13:47:23 +07:00 | 0036 | MAIN | D1-MAIN-014 | Completed graphres candidate and requested independent audit | `KEEP`: mean 38.1750, 2.18% better than ridge, all folds/horizons and worst fold improve; 28 tests and submission validator pass | Freeze commit, audit graph handling, and test graph plus text residuals separately |
| 2026-07-18 13:48:30 +07:00 | 0037 | VALIDATION | D1-VAL-002 | Completed public-gap and textres independent audits | No material leakage; textres gain is aligned but one m2 feature extrapolates in the risky bias direction | Keep evidence, do not submit exact textres, and begin graphres review |
| 2026-07-18 13:50:02 +07:00 | 0038 | MAIN | D1-MAIN-015 | Started separate-branch text OOD robustness experiment | Preregistered one guard: neutralize only out-of-training-range `prohibit left turn` values; graphres remains frozen for audit | Verify local gains and test-m2 correction direction before any slot decision |
| 2026-07-18 13:53:11 +07:00 | 0039 | VALIDATION | D1-VAL-003 | Completed graphres independent audit | Leakage `GO`, candidate `KEEP`; three topology nulls show the gain is generic cross-road context rather than the true road topology | Prefer graphres over exact textres after notebook readiness; never select random-graph seeds |
| 2026-07-18 13:54:55 +07:00 | 0040 | MAIN | D1-MAIN-015 | Completed raw-range text OOD experiment | `REJECT`: guard activates on zero test samples, m2 correction remains `+0.3470` km/h, and no submission is generated | Freeze the branch and treat any z-score guard as a new preregistered experiment |
| 2026-07-18 13:56:59 +07:00 | 0041 | MAIN | D1-MAIN-016 | Started separate-branch standardized text OOD experiment | Fixed one rule before scoring: neutralize only `prohibit left turn` when its training-standardized value exceeds three sigma | Compare on frozen folds and stop the text path if inference-risk gates fail |
| 2026-07-18 14:00:40 +07:00 | 0042 | MAIN | D1-MAIN-016 | Completed standardized text OOD experiment and requested audit | `KEEP`: MSE 38.2840; guard activates on 144/168 test-m2 samples and changes correction from +0.3470 to -0.0899 km/h; validator READY; 32 tests pass | Freeze commit; VALIDATION audits before any graph-plus-safe-text reuse or slot 2 decision |
| 2026-07-18 14:02:22 +07:00 | 0043 | MAIN | D1-MAIN-017 | Started separate-branch graph and guarded-text blend | Fixed 50:50 prediction average before scoring; no weight search, validation change, or leaderboard feedback | Compare against graphres on frozen folds and preserve slot 2 pending audit/readiness |
| 2026-07-18 14:05:25 +07:00 | 0044 | MAIN | D1-MAIN-017 | Completed fixed graph and guarded-text blend and requested audit | `KEEP`: MSE 37.9040; folds 1/3, worst fold, and all horizons improve graphres; fold 2 regresses 0.0391; validator READY; 34 tests pass | Freeze commit; audit both components/blend before notebook or slot 2 |
| 2026-07-18 14:06:58 +07:00 | 0045 | MAIN | D1-MAIN-018 | Started separate-branch blend notebook preparation | Frozen blend commit `e99d6d6`; notebook may be prepared locally but no Kaggle slot is authorized | Reproduce frozen CSV exactly from a clean process and await audit |
| 2026-07-18 14:11:00 +07:00 | 0046 | MAIN | D1-MAIN-018 | Completed local clean-session blend notebook reproduction | `python -I` finished in 16.18s; validator READY with zero reference mismatches; 34 tests pass; notebook outputs are clean | VALIDATION/SUBMISSION review and actual Kaggle Run All remain; do not submit |
| 2026-07-18 14:16:52 +07:00 | 0047 | MAIN | D1-MAIN-018 | Accepted independent blend audit and prepared Kaggle handoff | Leakage `GO`, candidate `KEEP`, conditional slot-2 recommendation; browser is at Import Notebook but upload requires user confirmation | Upload exact notebook, Run All, validate output, and obtain SUBMISSION `READY`; do not submit yet |
| 2026-07-18 14:17:59 +07:00 | 0048 | MAIN | D1-MAIN-018 | Returned all Chrome/Kaggle control to the user | No upload, Run All, version save, or submission was performed; user will complete browser steps manually | Validate the user-downloaded Kaggle CSV against frozen blend predictions |
| 2026-07-18 14:23:35 +07:00 | 0049 | MAIN | D1-MAIN-018 | Validated actual Kaggle-generated blend CSV | `READY`: 2,041,200 exact IDs; finite/nonnegative; zero reference mismatches and max absolute difference 0.0 versus frozen commit `e99d6d6` | Obtain independent SUBMISSION verdict, then decide slot 2 |
| 2026-07-18 14:27:46 +07:00 | 0050 | SUBMISSION | D1-SUB-001 | Completed final independent review of actual Kaggle blend output | `READY`; exact template IDs, finite/nonnegative values, zero mismatches and max difference 0.0 versus frozen `e99d6d6`; verdict `SUBMIT` for slot 2 | MAIN authorizes designated Submission Manager; upload the byte-identical canonical-named copy and record result |
| 2026-07-18 14:35:23 +07:00 | 0051 | VALIDATION | D1-VAL-003 | Completed post-submission public-to-private risk audit | Public gain retains 72.45% of local gain; blend beats ridge on 18/18 block-fold-horizon cells and 36/36 temporal chunks; `GO`/`KEEP`, prefer blend for final selection | MAIN records slot 2 and avoids spending another slot solely on public-score chasing |
| 2026-07-18 14:40:30 +07:00 | 0052 | MAIN | D1-MAIN-018 | Recorded slot 2 and accepted the post-submission audit | Public MSE 45.168; e010 is the current final-selection candidate and ridge remains fallback; three Kaggle slots remain protected | Freeze e010 artifacts and run at most one bounded local hypothesis on a separate branch |
| 2026-07-18 14:41:30 +07:00 | 0053 | MAIN | D1-MAIN-019 | Preregistered the final bounded city-state hypothesis on a separate branch | Five causal global summaries, fixed 50:50 guarded-text blend, frozen folds, and no leaderboard tuning; no slot authorized | Implement once and retain only if it materially beats e010 across folds, horizons, and worst fold |
| 2026-07-18 14:45:28 +07:00 | 0054 | MAIN | D1-MAIN-019 | Completed and froze the preregistered city-state blend experiment | `REJECT`: blend 35.7488 loses to globalstate 35.3894; no CSV or slot. Globalstate alone improves e010 by 6.63% and becomes a disclosed post-discovery hypothesis | Commit e011 unchanged, then preregister stricter globalstate-only stress tests on a new branch |
| 2026-07-18 14:47:06 +07:00 | 0055 | MAIN | D1-MAIN-020 | Preregistered disclosed post-discovery globalstate-only stress testing | New evidence must include at least 34/36 winning temporal chunks, 15/18 winning block-fold-horizons, median chunk gain at least 1.0 MSE, no chunk worse than -0.25, safer m2 correction, and exact output validity | Run once on frozen folds; reject on any failed gate and keep slot 3 protected |
| 2026-07-18 14:50:18 +07:00 | 0056 | MAIN | D1-MAIN-020 | Completed strict globalstate-only stress testing and stopped further modeling | `REJECT`: 31/36 chunks improve and worst chunk is -1.9517; no CSV or slot. E010 remains the final-selection recommendation | Human selects e010 as the one final Kaggle entry, preserves the validated notebook, and prepares writeup |
| 2026-07-18 14:55:26 +07:00 | 0057 | MAIN | D1-MAIN-021 | Reopened one bounded opportunity at the user's request | Preregistered exactly one fixed 75:25 e010/globalstate shrinkage blend; no weight grid and no slot authorization | Run once and continue only if aggregate, 34/36 chunks, worst chunk, inference safety, audit, and notebook gates pass |
| 2026-07-18 15:00:01 +07:00 | 0058 | MAIN | D1-MAIN-021 | Completed fixed conservative stable-blend experiment | `KEEP / NEEDS_REVIEW`: MSE 36.5603, 18/18 cells and 36/36 chunks improve e010, minimum chunk gain 0.1243, validator `READY`, 44 tests pass | Freeze commit for independent audit; prepare notebook without spending slot 3 |
| 2026-07-18 15:15:23 +07:00 | 0059 | MAIN | D1-MAIN-021 | Accepted independent e013 audit and started notebook readiness | `GO/KEEP`; exact reproduction, stricter purge, 17/17 windows, and 102/102 diagnostic chunks pass; selection bias and m2 global-feature shift remain disclosed | Build clean e013 notebook and require exact Kaggle Run All plus SUBMISSION `READY` before slot 3 |
| 2026-07-18 15:19:03 +07:00 | 0060 | MAIN | D1-MAIN-021 | Completed local e013 notebook readiness | Clean notebook reproduced all 2,041,200 values exactly in 18 seconds; validator `READY`, zero mismatches, max difference 0.0, and 44 tests pass | Human performs Kaggle Restart Session / Run All and returns downloaded CSV for independent SUBMISSION review |
| 2026-07-18 15:25:22 +07:00 | 0061 | MAIN | D1-MAIN-021 | Validated actual Kaggle e013 output | `READY`: 2,041,200 exact IDs, finite/nonnegative, zero reference mismatches, max difference 0.0, and frozen hash match | Obtain independent SUBMISSION confirmation, then decide slot 3 |
| 2026-07-18 15:52:09 +07:00 | 0062 | MAIN | D1-MAIN-021 | Recorded slot 3 and accepted post-submission risk audit | Public MSE 43.511; gain magnitude aligns with local validation; e013 becomes current final-selection recommendation over e010 | Keep e013 selected and permit only one final distinct feature hypothesis, not weight retuning |
| 2026-07-18 16:05:02 +07:00 | 0063 | MAIN | D1-MAIN-023 | Preregistered parallel low-rank spatial-factor experiment | Fixed rank 4, 360 evenly spaced training-only PCA rows, per-road standardization, alpha 0.1, and unchanged 75:25 anchor weight | Implement once in isolated worktree and reject without retuning on any failed gate |
| 2026-07-18 16:11:49 +07:00 | 0064 | MAIN | D1-MAIN-023 | Completed and closed E016 low-rank experiment | `REJECT`: mean improves 2.74%, 18/18 cells and 34/36 chunks improve, but worst chunk `-0.3186` fails frozen `-0.25` floor; no submission generated | Preserve both remaining slots, keep E013 selected, and await the independent E015 verdict |

Append only. Correct errors with a new entry; do not erase history.

| 2026-07-18 16:15:34 +07:00 | E019-001 | EXPERIMENT | D1-E019 | Preregistered orthogonal hybrid-state candidate in isolated worktree | Preserve E016 rank/sample/alpha/weight; combine explicit global summaries with PCA of cross-sectionally residualized road state; require 36/36 chunks | Run focused tests, freeze commit, then score once |

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
