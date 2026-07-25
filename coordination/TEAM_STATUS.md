# Datathon 2026 Team Status

Revision: 0059
Active Day: CONCEPT
Active Task: NONE
Last Global Update: 2026-07-25 10:42:00 +07:00
Competition Clock: CLOSED
Repository Branch: codex/dcoast-phase0
Current Stable Commit: b3b78204bdc8fb2bc38685c299d16bccbde4fbd8

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
| D2-DEC-004 | 2026-07-19 13:13 WIB | Promote `d2-e002-metarank` to the leading model candidate after independent `GO/KEEP`; do not submit until its notebook reproduces exactly and SUBMISSION returns `READY`. | Audit commit `2e76cab`: 10/10 gates pass, +0.024000 accuracy, 5/5 fold wins, no material leakage, exact CSV reproduction. | MAIN | A later candidate passes its preregistered gate and independent audit with stronger robustness evidence. |
| D2-DEC-005 | 2026-07-19 14:05 WIB | Record E002 as slot 1 and retain it as the provisional leading final candidate; treat public accuracy 0.321 as diagnostic only. | Human Kaggle Run All completed from portability notebook `ef59c31` and submission `sub-s01-d2-e002-metarank.csv` completed successfully. | MAIN | A later candidate passes frozen local gates, immutable audit, and notebook reproduction with stronger private-risk evidence. |
| D2-DEC-006 | 2026-07-19 14:25 WIB | Run only `d2-e010-treerank`; stop `d2-e011-nestedselect` before implementation. | E002+E004 oracle is only 0.292333; E004 net correct by fold is +3/-2/-3/+3/-5, so nested selection lacks distributed headroom. E010 has a frozen nonlinear, fold-local, leave-one-out design and unchanged E002 promotion gate. | MAIN | E010 fails any frozen gate or an immutable audit finds leakage/reproducibility failure. |
| D2-DEC-007 | 2026-07-19 14:56 WIB | Stop Task 2 modeling and select `d2-e002-metarank` as the final candidate; preserve all remaining Kaggle slots. | Independent E010 audit `8f5ee0a` confirms `NO-GO`: mean 0.255556, 0/5 wins, four frozen gates fail, while E002 remains independently `GO/KEEP`, notebook `READY`, and public 0.321 is diagnostic only. | MAIN | Only an official data/rule correction or reproducibility failure in the frozen E002 artifact may reopen selection. |
| D2-DEC-008 | 2026-07-19 15:16 WIB | Reopen only bounded `d2-e012-linkgraph` Stage-0 feasibility while retaining E002 as the fallback final candidate. | Human confirms about two hours remain; leaderboard-gap analysis indicates screenshot hyperlinks are the only structurally credible high-upside path, while E003-E010 ranking variants failed. | MAIN | Any Stage-0 gate failure stops E012 immediately; no slot, notebook, or final-selection change before full validation and audit. |
| D2-DEC-009 | 2026-07-19 15:37 WIB | Reject E012/E013 without rescue, then allow one artifact-first `d2-e014-prelink` attempt while preserving E002. | Both OCR variants exceed their frozen 20-minute projection, but the fixed link-ranker improves a 226-row target-group diagnostic by +0.0708 and wins 5/5 folds; the human explicitly authorizes one more high-upside attempt. | MAIN | E014 must precompute only official-data link candidates within 60 minutes, pass the unchanged full E002 promotion gates, and close notebook/artifact reproducibility before any slot. |
| D2-DEC-010 | 2026-07-19 15:46 WIB | Reject E014 at its precompute gate and refreeze E002 as the final Task 2 candidate; no further model or slot use. | Four-worker benchmark projects 5,383 seconds for the 4,312 relevant pages versus the frozen 3,600-second maximum; full validation, artifact, notebook, and slot were correctly not run. | MAIN | None before the competition close; only a reproducibility failure in E002 would justify emergency action. |
| D2-DEC-011 | 2026-07-19 15:51 WIB | Treat precomputed screenshot-link features as ineligible for the final notebook and retain only end-to-end E002. | Panitia clarification supplied by the human: every preprocessing step before modeling must run end-to-end in the submitted notebook and may not load externally preprocessed data. | MAIN | Only a written official clarification explicitly permitting the exact artifact architecture could reverse this, and runtime would still fail. |
| DCOAST-DEC-001 | 2026-07-25 02:32 WIB | Close Cilegon as `NO_GO_CILEGON_FOR_PHASE1` for the current optical pipeline; retain Teluk Awur only as a conditional technical benchmark and do not start Phase 1. | Credential-enabled Phase 0.6 output: Cilegon has 0 quality-70 dates and fails 3/3 frozen cadence gates; Teluk Awur has 167 quality-70 dates but a 120-day maximum full-period gap and still lacks secured georeferenced validation. | MAIN | A newly preregistered coastal/turbid-water quality method, reviewed AOI/boundary evidence, and secured validation data may justify a fresh gate; do not reverse by lowering the frozen 70% threshold on this evidence. |
| DCOAST-DEC-002 | 2026-07-25 10:42 WIB | Reject both provisional monitoring AOIs at the official-coastline alignment gate; retain the Teluk Awur published extent as reference evidence only and keep Phase 1 blocked. | At the frozen <=1,000 m endpoint gate, Cilegon is 1,569.45/6,665.67 m from the nearest BIG coastline and Teluk Awur is 2,788.00/1,004.50 m away. The open study map is not a station-coordinate table. | MAIN | A separately approved and preregistered AOI redesign passes the same official-coastline screen and domain review, and secured row-level validation data pass the frozen contract. |

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
| D2-MAIN-002 | DAY 2 | MAIN | DONE | HIGH | `d2-baseline-v1` and frozen validation | Reproduce the audit-only title/category heuristic without tuning | `d2-e002-metarank` with comparable fold/subset diagnostics | 2026-07-19 12:48 WIB | 2026-07-19 13:13 WIB | Independent audit `GO/KEEP`; commit `8365193` remains the immutable model snapshot and leading candidate. |
| D2-VAL-002 | DAY 2 | VALIDATION | DONE | HIGH | Stable MAIN baseline commit | Independently reproduce baseline artifacts and audit `d2-e002-metarank` after handoff | GO/NO-GO candidate verdict with gate evidence | 2026-07-19 12:38 WIB | 2026-07-19 13:08 WIB | E002 audit `GO/KEEP`; report at `task2/reports/d2-e002-metarank-validation-audit.md`; submission remains `DO NOT SUBMIT` pending notebook review. |
| D2-SUB-002 | DAY 2 | SUBMISSION | DONE | HIGH | MAIN commit `0f94a1c` with validator ancestor `721c4bf` | Clean local dual-environment notebook reproduction and exact-reference check | Notebook readiness verdict without Kaggle slot | 2026-07-19 12:39 WIB | 2026-07-19 12:49 WIB | `READY`; 12 tests pass, isolated smoke output is byte-identical to reference with SHA-256 `20e629...b70b96`; actual Kaggle Run All remains deferred. |
| D2-MAIN-003 | DAY 2 | MAIN | DONE | HIGH | E002 immutable handoff and frozen validation | Test an instance-based nearest-route hypothesis without changing E002 or its notebook | `d2-e003-routeknn` with directly comparable diagnostics | 2026-07-19 13:02 WIB | 2026-07-19 13:10 WIB | `REJECT`: +0.011222 over baseline misses the frozen +0.015 gate; unseen-current proxy accuracy collapses; do not submit or retune. |
| D2-MAIN-004 | DAY 2 | MAIN | DONE | HIGH | E002 independent `GO/KEEP` | Convert the verified dual-environment notebook to exact E002 inference | Clean E002 notebook and numerically exact local/Kaggle output | 2026-07-19 13:13 WIB | 2026-07-19 14:00 WIB | Portability fix `ef59c31`: numeric prediction hash remains fail-closed; environment-specific CSV bytes are informational; Kaggle rerun required. |
| D2-SUB-003 | DAY 2 | SUBMISSION | DONE | HIGH | Clean-notebook remediation commit `3b28567` with portability ancestor `ef59c31` | Audit clean notebook, exact prediction hash, paths, dependencies, and Run-All contract | `READY`, `NOT READY`, or `INVESTIGATE` without using a slot | 2026-07-19 14:15 WIB | 2026-07-19 14:38 WIB | `READY`: all 14 tests pass, notebook is clean/source-identical, isolated numeric hash and exact-reference validator pass; report commit `691b452`. |
| D2-MAIN-005 | DAY 2 | MAIN | DONE | HIGH | E002 immutable model and frozen validation | Test category-conditioned route posterior without duplicating scout experiments | `d2-e007-catroute` immutable result | 2026-07-19 13:27 WIB | 2026-07-19 14:00 WIB | `REJECT`: mean 0.275111, 0/5 wins vs E002, worst 0.268333; main commit `eaa6915`; no retuning or slot. |
| D2-MAIN-006 | DAY 2 | MAIN | DONE | HIGH | E002 immutable model and frozen validation | Test target-title prototypes per exact-current route | `d2-e008-routeproto` immutable result | 2026-07-19 13:27 WIB | 2026-07-19 14:00 WIB | `REJECT`: mean 0.282111, 0/5 wins vs E002; comparator reporting repaired at main commit `47178af`; no slot. |
| D2-MAIN-007 | DAY 2 | MAIN | DONE | HIGH | E002 immutable model and frozen validation | Test candidate-free global next-label prototypes | `d2-e009-nextproto` immutable result | 2026-07-19 13:27 WIB | 2026-07-19 14:00 WIB | `REJECT`: mean 0.042667, 0/5 wins vs E002; exact comparator repaired at main commit `dcfda11`; no slot. |
| D2-MAIN-008 | DAY 2 | MAIN | DONE | HIGH | Scout E004-E006 working trees and E002 immutable reference | Independently audit scout results and select at most two evidence-backed next hypotheses | Immutable audit verdict and preregistered next-candidate decision | 2026-07-19 14:01 WIB | 2026-07-19 14:25 WIB | E004 `a5933a3`, E005 `e0043b6`, and E006 `a9d195d` are clean direct children of `8365193`; all remain `REJECT / DO NOT SUBMIT`. |
| D2-MAIN-009 | DAY 2 | MAIN | DONE | HIGH | Immutable scout audit and frozen E010 preregistration | Evaluate nonlinear exact-current candidate ranking without feature/parameter rescue | Immutable `d2-e010-treerank` result and independent VALIDATION verdict | 2026-07-19 14:25 WIB | 2026-07-19 14:56 WIB | `REJECT / DO NOT SUBMIT`: commit `13194222`, audit `8f5ee0a`, mean 0.255556, 0/5 wins, no material leakage, no rescue tuning. |
| D2-MAIN-010 | DAY 2 | MAIN | DONE | HIGH | Final E002 selection and notebook readiness | Produce the required maximum-three-page technical writeup consistent with the frozen model and submission | Rendered Task 2 writeup PDF plus reproducible source/build script | 2026-07-19 14:45 WIB | 2026-07-19 15:09 WIB | `READY`: local commit `feca95c`, independent report `877b7b1` integrated as `2343f1e`; 2 pages, exact PDF hash, clean render, consistent content and naming. |
| D2-MAIN-011 | DAY 2 | MAIN | DONE | HIGH | Official screenshot ZIP, E002 fallback, and bounded Stage-0 gate | Test blue-link OCR and closed-vocabulary title mapping before any full graph/model run | Immutable `d2-e012-linkgraph` feasibility verdict; candidate only if every gate passes | 2026-07-19 15:16 WIB | 2026-07-19 15:37 WIB | E012 and detector-free E013 both `REJECT`: recall/precision pass, runtime and Kaggle-packaging gates fail; no full graph, rescue, or slot. |
| D2-MAIN-012 | DAY 2 | MAIN | DONE | HIGH | Strong sampled link-rank signal and rejected online OCR runtime | Precompute official screenshot candidates as a compact reproducible model artifact, then run unchanged frozen validation | `d2-e014-prelink` full-fold verdict, artifact, notebook plan, and slot decision | 2026-07-19 15:37 WIB | 2026-07-19 15:46 WIB | `REJECT`: 200-page benchmark projects 89.72 minutes, failing the frozen 60-minute precompute gate; stopped before full extraction/validation/artifact/notebook/slot. |
| D2-MAIN-013 | DAY 2 | MAIN | DONE | MEDIUM | Human requests a post-competition local E014 rerun | Clean VS Code notebook with resumable official-ZIP extraction, frozen-fold evaluation, CSV creation, and validation | `task2/notebooks/d2-e014-prelink-local.ipynb` plus focused pipeline support | 2026-07-19 16:20 WIB | 2026-07-19 16:33 WIB | Local experiment tooling only; E014 remains unaudited/rejected and E002 remains the official final candidate. |
| DCOAST-PHASE05-001 | CONCEPT | MAIN | DONE | HIGH | Completed Phase 0 feasibility and unresolved OAuth/validation/AOI blockers | Refined water AOIs, per-acquisition quality contract, supplementary evidence, validation classification, and frozen site gates | Phase 0.5 site-lock verdict and reproducible blocker-closure artifacts | 2026-07-24 23:49 WIB | 2026-07-25 00:12 WIB | `CONDITIONAL_GO_CILEGON`; Teluk Awur remains the benchmark; CDSE clear-water and secured georeferenced validation gates remain open; no Phase 1 work authorized. |
| DCOAST-PHASE06-001 | CONCEPT | MAIN | DONE | HIGH | Valid Sentinel Hub OAuth client credentials | Deduplicated site-date clear-water query with retry, provenance, sensitivity, and fail-closed validation | Audited Cilegon/Teluk Awur optical-quality evidence and Phase 0.6 gate verdict | 2026-07-25 01:49 WIB | 2026-07-25 02:32 WIB | `NO_GO_CILEGON_FOR_PHASE1`; Cilegon fails all frozen quality-70 cadence gates, Teluk Awur remains a conditional technical benchmark, and Phase 1 was not started. |
| DCOAST-PHASE07-001 | CONCEPT | MAIN | DONE | HIGH | Phase 0.6 no-go verdict and public BIG coastline service | Query bounded official coastline evidence, audit provisional AOI alignment, and freeze the minimum validation-data contract | AOI review packet and actionable Teluk Awur validation-acquisition package without Phase 1 training/download | 2026-07-25 02:40 WIB | 2026-07-25 10:42 WIB | Both provisional AOIs fail the frozen coastline gate; bounded BIG extracts, study envelope, data contract, and an explicitly unsent request draft are reproducible. Phase 1 remains blocked. |

Owner: `MAIN`, `VALIDATION`, `SUBMISSION`. Status: `BACKLOG`, `READY`, `CLAIMED`, `IN_PROGRESS`, `BLOCKED`, `NEEDS_REVIEW`, `DONE`, `CANCELLED`. IDs: `D1-MAIN-001`, `D1-VAL-001`, `D1-SUB-001`, `D2-MAIN-001`, `D2-VAL-001`, `D2-SUB-001`. MAIN creates/prioritizes/cancels; each role changes only its rows.

## 4. Main Integrator Status

<!-- MAIN:START -->
Role: MAIN
Current Task: NONE
Status: DONE
Last Read Revision: 0058
Last Update: 2026-07-25 10:42:00 +07:00

### Current Objective
Close the official-coastline and validation-acquisition blockers enough to make the next D'Coast site decision without starting Phase 1.
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
- Integrated independent E002 audit commit `2e76cab`: `GO/KEEP`, all 10 gates pass, no material leakage, and exact CSV reproduction.
- Completed E003 without retuning; the failed +0.015 mean-gain gate makes it `REJECT / DO NOT SUBMIT`.
- Closed E010 at immutable candidate commit `13194222` and independent audit `8f5ee0a`: `NO-GO / REJECT / DO NOT SUBMIT`, 0/5 wins, no material leakage, and no rescue tuning.
- Selected E002 as the final candidate and stopped further Task 2 modeling.
- Added a local-only E014 notebook that extracts official screenshot links with resumable shards, evaluates the unchanged target-group folds, writes a separate CSV, and invokes the fail-closed validator.
- Refined Cilegon and Teluk Awur into explicit water-side monitoring AOIs and refreshed the public Sentinel-2 catalogue inventory.
- Inspected the complete Cilegon article and both supplementary files; classified heavy metals as context evidence and declined to invent station coordinates.
- Added fail-closed per-acquisition optical-quality tooling, a transparent 858-row OAuth-blocked work queue, validation inventory, and frozen site-lock gates.
- Issued `CONDITIONAL_GO_CILEGON`; retained Teluk Awur as the technical benchmark and did not start Phase 1.
- Completed the credential-enabled Statistical API workflow: 848 unique site-date rows representing 858 source acquisitions, with provenance, rejection reasons, and bounded retry.
- Aggregated the preregistered 50/70/80 sensitivity and cadence gates; closed Cilegon as no-go for the current optical pipeline and retained Teluk Awur only as a conditional technical benchmark.
- Queried and clipped bounded official BIG coastline extracts with preserved source/type provenance: 5 features for Cilegon and 62 for Teluk Awur.
- Applied the frozen <=1,000 m endpoint screen; both provisional AOIs fail, so neither was silently snapped, redesigned, or promoted.
- Recorded only the approximate published Teluk Awur study envelope, froze the minimum reusable TSS data contract, and prepared an explicitly unsent author-request draft.
### Work in Progress
- NONE
### Latest Metrics
- `d2-e001-baseline`: mean 0.261333; folds 0.267778, 0.255556, 0.265556, 0.255000, 0.262778; worst 0.255000; std 0.005195.
- Mean current-seen coverage 0.8003; observed-candidate coverage 0.3053; test current-seen rate 0.874167.
- Submission: 6,000 unique state IDs, 544 unique predictions, top-prediction share 0.2715; validator `READY`.
- Tests: 12 submission-validator plus 3 baseline/validation tests pass.
- Clean notebook CSV SHA-256: `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`; exact reference match.
- `d2-e002-metarank`: mean 0.285333 versus baseline 0.261333, gain +0.024000; folds 0.290556, 0.282778, 0.278333, 0.280556, 0.294444; 5/5 wins; worst 0.278333.
- E002 current-unseen delta 0.000000; entirely-unseen-target-category accuracy 0.280000 -> 0.315200; test change rate 0.151333; 449 unique predictions; final recorded runtime 12.04s.
- Tests: 7 model/validation plus 12 submission-validator tests pass; E002 submission validator `READY`.
- `d2-e003-routeknn`: mean 0.272556, gain +0.011222 over baseline, 5/5 baseline fold wins, worst 0.266111, but below the frozen +0.015 gate and 0/5 versus E002.
- E003 seen-current accuracy improves 0.295710 -> 0.323199, while unseen-current accuracy falls 0.123539 -> 0.069560; verdict `REJECT / DO NOT SUBMIT` without retuning.
- Clean E002 notebook output: 6,000 rows, 449 unique predictions, prediction SHA-256 `292bb156...d1ba0`, CSV SHA-256 `87b4a480...ad3d81`, byte-identical to the audited artifact.
- Notebook validation: isolated `python -I` smoke pass, fail-closed reference check READY, 7/7 model/validation tests and 12/12 validator tests pass.
- Kaggle exposed environment-dependent CSV byte serialization while the canonical numeric prediction hash remained exact; `ef59c31` keeps numeric/schema checks fail-closed and records CSV byte equality without blocking Run All.
- `d2-e007-catroute`: mean 0.275111, folds 0.278333/0.272222/0.271111/0.268333/0.285556, 0/5 vs E002, verdict `REJECT`.
- `d2-e008-routeproto`: mean 0.282111, folds 0.287222/0.276111/0.277778/0.279444/0.290000, 0/5 vs E002, verdict `REJECT`; E002 comparison uses frozen audited fold references rather than refitting E002.
- `d2-e009-nextproto`: mean 0.042667, worst 0.032778, 0/5 vs exactly reproduced E002, verdict `REJECT`.
- Integrated focused verification: 20 tests plus 8 subtests pass for E007-E009 and notebook/validator contracts.
- Kaggle slot 1: `sub-s01-d2-e002-metarank.csv`, public accuracy 0.321; public 30% remains diagnostic, not a final-selection proof.
- Provisional scout audit: E004 mean 0.284889, 2/5 wins vs E002, with 63 E004-only-correct versus 67 E002-only-correct; E005 mean 0.281778, 0/5 wins, with unfavorable 19 versus 51 complementarity; both are `REJECT / DO NOT SUBMIT`.
- E006 direct ZIP access succeeds for 100/100 deterministic samples from all 4,604 PNGs. RapidOCR exists locally, but weight-license provenance and Kaggle dependency/input reproducibility are unverified; verdict remains `REJECT_FEASIBILITY / DO NOT SUBMIT` at `a9d195d`.
- E011 stopped before implementation: oracle ceiling 0.292333 is only 0.002 above the promotion gate and pairrank's per-fold net corrections are positive in only 2/5 folds.
- E002 notebook delivery: commit `3b28567`, all code-cell outputs/counts cleared, source identical to `ef59c31`, 14 tests pass, exact numeric SHA and reference validator pass; report integrated at `c70f964`.
- `d2-e010-treerank`: mean 0.255556 versus E002 0.285333; folds 0.265000/0.250556/0.253333/0.250556/0.258333; 0/5 wins; worst 0.250556; category-OOD 0.278400. Independent reproduction and 19 tests confirm `REJECT` without leakage.
- `d2-e012-linkgraph`: 100/100 pages, 90.32% unique-edge recall, 99.06% exact mapping share, but projected full OCR 8,189.74s; `REJECT`.
- `d2-e013-fastlink`: 87.63% recall and 98.99% exact mapping share, but projected full OCR 3,794.35s; `REJECT`.
- `d2-e014-prelink`: 200/200 benchmark pages and 99.28% exact mapping share, but projected relevant-page precompute 5,383.06s versus 3,600s gate; `REJECT` before full validation.
- Panitia clarification closes the artifact shortcut: preprocessing must execute end-to-end in the final notebook, so a locally precomputed outgoing-link graph cannot make E014 submission-eligible.
- D'Coast Phase 0.6: Cilegon quality-70 usable dates 0/423, full-year average 0, median 0/month, and no usable-date gap metric; all 3/3 frozen gates fail.
- D'Coast Phase 0.6: Teluk Awur quality-70 usable dates 167/425, full-year average 29, median 2/month, and maximum full-period gap 120 days; cadence passes 2/3 gates.
- D'Coast Phase 0.7: Cilegon endpoint distances 1,569.45 m and 6,665.67 m; Teluk Awur 2,788.00 m and 1,004.50 m; both fail the frozen <=1,000 m official-coastline gate.
- D'Coast Phase 0.7: bounded BIG extracts contain 5 Cilegon and 62 Teluk Awur features; the validation-acquisition package remains `READY_TO_REQUEST_DATA`, not Phase 1 authorization.
### Files Changed
- `concept-paper/dcoast/data/big_coastline/`; `concept-paper/dcoast/data/reference_extents/`; `concept-paper/dcoast/docs/`; `concept-paper/dcoast/reports/`; `concept-paper/dcoast/scripts/site_feasibility/`; `concept-paper/dcoast/tests/test_phase07.py`; `coordination/TEAM_STATUS.md`
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
- `task2/experiments/d2-e003-routeknn/{config,metrics,notes}`
- `task2/src/routeknn.py`; `task2/src/run_routeknn_experiment.py`; `task2/src/test_routeknn.py`
- `task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb` at commit `51d7a9f`
- `task2/reports/d2-e007-e009-preregister.md`
- `task2/experiments/d2-e007-catroute/{config,metrics,notes}` and `task2/src/{catroute,run_catroute_experiment,test_catroute}.py`
- `task2/experiments/d2-e008-routeproto/{config,metrics,notes}` and `task2/src/{routeproto,run_routeproto_experiment,test_routeproto}.py`
- `task2/experiments/d2-e009-nextproto/{config,metrics,notes}` and `task2/src/{nextproto,run_nextproto_experiment,test_nextproto}.py`
- `task2/tests/test_notebook_portability.py`
- `task2/reports/d2-e010-treerank-validation-audit.md`
- `task2/reports/EnterYourTeamName_Task2_Writeup.md`
- `task2/reports/build_task2_writeup.py`
- `output/pdf/EnterYourTeamName_Task2_Writeup.pdf`
- `concept-paper/dcoast/reports/sentinel2_observation_quality.csv`
- `concept-paper/dcoast/reports/sentinel2_monthly_availability.csv`
- `concept-paper/dcoast/reports/phase06_site_quality_summary.csv`
- `concept-paper/dcoast/reports/phase06_monthly_seasonality.csv`
- `concept-paper/dcoast/reports/phase06_clear_water_assessment.md`
- `concept-paper/dcoast/data/big_coastline/{cilegon-industrial-coast,teluk-awur-jepara}.geojson`
- `concept-paper/dcoast/data/reference_extents/teluk_awur_published_study_extent.geojson`
- `concept-paper/dcoast/reports/phase07_aoi_alignment.csv`
- `concept-paper/dcoast/reports/phase07_aoi_review.md`
- `concept-paper/dcoast/reports/phase07_validation_acquisition.md`
- `concept-paper/dcoast/docs/teluk_awur_validation_data_contract.md`
- `concept-paper/dcoast/docs/teluk_awur_data_request_draft.md` (draft only; not sent)
### Decisions Needed
- Human approval is required before any D'Coast Phase 1 work.
### Tasks Dispatched to Other Agents
- `D2-VAL-002` completed: E002 is `GO/KEEP` at immutable model commit `8365193`.
- `D2-SUB-002` completed: baseline notebook locally reproducible and byte-identical; actual Kaggle Run All remains deferred.
- `D2-SUB-003` completed: clean E002 notebook commit `3b28567` is independently `READY`.
- `D2-MAIN-005/006/007` completed; all three failed the shared E002 promotion gate and remain diagnostic only.
- VALIDATION completed E010 audit `8f5ee0a`; Scout and VALIDATION are closed with no additional experiment authorized.
- SUBMISSION completed the immutable writeup audit at `877b7b1` with verdict `READY`; report integrated as `2343f1e`.
- No role task is dispatched during E014 precompute; MAIN works alone to avoid duplicate/fast-mode cost. VALIDATION/SUBMISSION receive a handoff only after a complete immutable candidate passes local gates.
### Blockers
- Both provisional monitoring AOIs fail the frozen official-coastline alignment gate.
- Secured row-level georeferenced optical validation data and expert/domain review remain absent; Cilegon also fails the frozen optical cadence gate.
### Next Action
- Human reviews and explicitly authorizes the Teluk Awur data request. Any new AOI design must be a separate preregistered task using official coastline evidence and domain review; do not start Phase 1 yet.
<!-- MAIN:END -->

Only MAIN may update this section.

## 5. Validation and Leakage Reviewer Status

<!-- VALIDATION:START -->
Role: VALIDATION
Current Task: D2-MAIN-009 (audit)
Status: DONE
Last Read Revision: 0032
Last Update: 2026-07-19 14:53:25 +07:00

### Scope Being Audited
- Immutable E010 commit `13194222`, direct parent/E002 anchor `8365193`, frozen `d2-targetgroup-v1`, outer-fold isolation, LOO construction, comparator, mutations, distribution, runtime, and validator.
### Evidence Reviewed
- Exact Git parent/diff, six added candidate files, temporary commit snapshot, official CSVs, full five-fold reproduction, 19 tests, independent LOO counter reconstruction, Git-blob config hash, prediction hashes, and validator output.
### Findings
- Direct parent is exactly `8365193`; diff is exactly six added E010 files and does not touch validation, E002, notebook, or submission registry.
- Reproduced E010 mean `0.255556`, folds `0.265000/0.250556/0.253333/0.250556/0.258333`, `0/5` wins, worst `0.250556`, and gain `-0.029778` versus exact E002.
- CSV and int64 prediction hashes reproduce exactly; runtime is `68.26s` stored and `68.95s` reproduced; 19 tests pass.
- Current-unseen is `0.123539`, category-OOD `0.278400`, 465 test predictions, top share `0.1840`; four primary gates fail.
### Leakage Risks
- No material leakage found. Label-derived candidates/counts are outer-fold-only and each source training row is removed before candidate/count feature construction.
- Independent LOO reconstruction matches every fold and full-data diagnostic exactly; state-ID/held-out-label mutations are exact and outer-training inputs are invariant to held-out mutations.
### Validation Risks
- Only 2,024/9,000 full-training source rows remain usable under strict LOO. This is a structural data limitation and must not be repaired by relaxing the leakage guard.
- The archive snapshot materialized CRLF, but the actual Git config blob SHA-256 exactly matches the frozen hash; predictive artifacts remain exact.
### Distribution or Fold Risks
- E010 loses every fold and OOD accuracy falls `0.315200 -> 0.278400`; diversity is harmful (116 E010-only correct versus 384 E002-only correct).
- Prediction distribution itself is non-collapsed, but passing diversity/runtime gates cannot override accuracy and OOD failures.
### Recommendation
- NO-GO

Allowed: `GO`, `NO-GO`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Preserve E010 as `REJECT / DO NOT SUBMIT`; no rescue tuning, blend, ensemble, or additional slot.
- Retain audited E002 as the leading anchor. E011 remains stopped.
### Blockers
- NONE
### Next Action
- Close E010 audit after handing the immutable report commit to MAIN/SCOUT.
<!-- VALIDATION:END -->

Only VALIDATION may update this section; it is read-only against the main pipeline.

## 6. Submission and Reproducibility Reviewer Status

<!-- SUBMISSION:START -->
Role: SUBMISSION
Current Task: D2-SUB-004
Status: READY
Last Read Revision: 0034
Last Update: 2026-07-19 15:06:49 +07:00

### Submission Schema Status
- `states_test.csv` has 6,000 rows and columns `state_id,current_article_id,target_article_id`; sample has 6,000 rows and exact columns `state_id,predicted_next_article_id`.
- Sample state IDs match test state IDs exactly in order; IDs are non-contiguous, so preserve test/sample row order.
### ID and Row Validation
- No nulls or duplicate state IDs. All article references observed in train/test/sample are within `articles.csv` IDs 0..4603.
- ZIP central listing contains 4,604 screenshot PNGs; current extracted working tree contains only 8 screenshots.
### Missing, Infinity, and Label Validation
- E002 isolated output passes exact column/order, 6,000-row, exact state-ID order, uniqueness, finite integer, article-universe, and exact-reference checks; validator returned `READY`.
- Candidate-link membership should be added once the screenshot/link representation is available; article-universe membership alone is not enough to prove a valid click.
### Kaggle Path and Dependency Status
- Source uses only official Task 2 CSVs through `TASK2_DATA_DIR`, repository-relative discovery, or `/kaggle/input`; output contract remains `TASK2_SUBMISSION_PATH`, local `task2/submissions/submission.csv`, or `/kaggle/working/submission.csv`. No network/API/external weight is used.
### Run-All Status
- Human Kaggle Run All is recorded as successful for slot 1/public 0.321. Commit `3b28567` is now a clean delivery artifact: every code-cell execution count is null, outputs are empty, sources exactly match `ef59c31`, and isolated local smoke passes.
### Model Weight Status
- No external/private model weights or APIs permitted; any weights must be open and packaged/available in Kaggle.
### Reproducibility Risks
- Numeric hash is fail-closed at `292bb1567ac81cd70b87b1f4730468830640388919b72126aef69f198e9d1ba0`. Local/Kaggle CSV byte hashes differ only by serialization and both preserve the numeric hash; a one-value mutation changes the numeric hash and is rejected by reference validation.
- Commit `3b28567` contains no retained output or local path. Its clean-delivery regression test fails if execution counts, outputs, or `C:\Users\...` paths return.
- Reference `submission.csv` is ignored and not stored in commit `0f94a1c`, but the clean notebook output reproduced it byte-for-byte and matched tracked expected SHA-256 `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`.
- Test target IDs have 0% overlap with train target IDs; test current IDs overlap train at 87.42% and current→mode baseline has 62.46% train accuracy (87.42% test coverage, global-mode fallback). Avoid target memorization.
### Writeup Status
- Commit `feca95c` PDF is technically valid: 2 A4 pages, readable render with no clipping/overlap, exact SHA-256 `fcfcc27858b4cca7659ef85327f2eaf9a85e01f92e6002c50e68984023631db3`, and Git binary handling. Claims match immutable E002/E010 audits, notebook `3b28567`, slot-1 public `0.321`, and the actual final method. Isolated local rebuild produces the same two-page text and pixel-identical render without network or external data.
- Direct human confirmation establishes that the registered team name is exactly `Enter Your Team Name` and authorizes compact filename token `EnterYourTeamName`; filename, visible title/footer, metadata, source, and notebook naming are therefore intentional and compliant.
### Recommendation
- READY: technical PDF, content consistency, filename/team/task identity, Git binary contract, and reproducible local build all pass. The earlier provisional naming blocker is closed by authoritative human confirmation.

Allowed: `READY`, `NOT READY`, `INVESTIGATE`, `BLOCKED`.

### Required Action from Main
- Cherry-pick the immutable SUBMISSION report commit and retain `feca95c` PDF/source/build artifacts unchanged for delivery.
### Blockers
- None for Task 2 writeup delivery.
### Next Action
- MAIN hands the reviewed PDF to the human Submission Manager for upload before the writeup deadline; no additional model, validation, notebook, Kaggle, or slot action is required by this audit.
<!-- SUBMISSION:END -->

Only SUBMISSION may update this section; it may not change model/validation without MAIN instruction.

## 7. Experiment Registry

| Experiment ID | Day | Owner | Hypothesis | Baseline | Validation | Mean | Fold Scores | Worst Fold | Std | Prediction Distribution | Runtime | Status | Artifact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1-e001-persist | DAY 1 | MAIN | Mean/last/trend forecasts from the exact 15-step history establish a leakage-safe floor. | NONE | 540 contiguous tail origins per train block | 29.6995 | 29.8669; 29.5322 | 29.8669 | 0.1674 | min 0.0; max 101.9333; mean 52.7290 | 4.83s | INVESTIGATE | `task1/experiments/d1-e001-persist/metrics.json` |
| d2-e001-baseline | DAY 2 | MAIN | Current-specific next-click mode is the cheapest transferable floor when test targets are unseen. | NONE | `d2-targetgroup-v1` | 0.261333 | 0.267778; 0.255556; 0.265556; 0.255000; 0.262778 | 0.255000 | 0.005195 | 544 unique test predictions; top share 0.2715 | 4.96s | KEEP | `task2/experiments/d2-e001-baseline/metrics.json` |
| d2-e002-metarank | DAY 2 | MAIN | Frozen target-aware category/title similarity improves candidate selection without changing candidate coverage. | `d2-baseline-v1` | `d2-targetgroup-v1` | 0.285333 | 0.290556; 0.282778; 0.278333; 0.280556; 0.294444 | 0.278333 | 0.006142 | 449 unique test predictions; top share 0.2752; change rate 0.1513 | 12.04s | KEEP | `task2/experiments/d2-e002-metarank/metrics.json` |
| d2-e003-routeknn | DAY 2 | MAIN | One nearest fold-local route transfers across unseen targets using exact current and static metadata. | `d2-baseline-v1` | `d2-targetgroup-v1` | 0.272556 | 0.277222; 0.266111; 0.271667; 0.271667; 0.276111 | 0.266111 | 0.003938 | 464 unique test predictions; top share 0.1692; 13.40% disagreement vs E002 | 25.08s | REJECT | `task2/experiments/d2-e003-routeknn/metrics.json` |
| d2-e007-catroute | DAY 2 | MAIN | Broad target category conditions the route posterior within an exact current. | `d2-e002-metarank` | `d2-targetgroup-v1` | 0.275111 | 0.278333; 0.272222; 0.271111; 0.268333; 0.285556 | 0.268333 | 0.006160 | 503 unique test predictions; top share 0.2660 | 41.85s | REJECT | `task2/experiments/d2-e007-catroute/metrics.json` |
| d2-e008-routeproto | DAY 2 | MAIN | Historical target-title prototypes represent each exact-current outgoing route. | `d2-e002-metarank` | `d2-targetgroup-v1` | 0.282111 | 0.287222; 0.276111; 0.277778; 0.279444; 0.290000 | 0.276111 | 0.005482 | 432 unique test predictions; top share 0.2753 | 151.42s | REJECT | `task2/experiments/d2-e008-routeproto/metrics.json` |
| d2-e009-nextproto | DAY 2 | MAIN | Global next-label prototypes can break the exact-current candidate ceiling. | `d2-e002-metarank` | `d2-targetgroup-v1` | 0.042667 | 0.045000; 0.032778; 0.042222; 0.044444; 0.048889 | 0.032778 | 0.005391 | 881 unique test predictions; top share 0.0205 | 180.97s | REJECT | `task2/experiments/d2-e009-nextproto/metrics.json` |

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
| 1 | `sub-s01-d2-e002-metarank.csv` | `d2-e002-metarank` | 0.285333 | 0.321 | 2026-07-19 ~14:05 WIB | Samuel Indriano | YES (model frozen; Kaggle selection pending) | Independent model audit `GO/KEEP`; notebook `READY`; later challengers failed frozen gates; public score remains diagnostic only. |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 4 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 5 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

Public score is never the sole final-selection reason.

## 9. Shared Blockers

| Blocker ID | Reported By | Time | Description | Blocking Task | Owner | Status | Resolution |
|---|---|---|---|---|---|---|---|
| DCOAST-BLK-001 | MAIN | 2026-07-24 22:00 WIB | CDSE public catalogue was accessible, but AOI-level Statistical API clear-water fractions required OAuth credentials that were initially absent | Final 50/70/80 clear-water sensitivity and Phase 1 approval | Human / MAIN | CLOSED | Human supplied credentials privately; 848 site-date rows were generated and validated without storing credentials. The result closes Cilegon as no-go rather than authorizing Phase 1. |
| DCOAST-BLK-002 | MAIN | 2026-07-25 10:42 WIB | Both provisional AOIs fail the official BIG coastline endpoint gate, and the Teluk Awur studies do not publish a reusable row-level georeferenced table | Monitoring-AOI lock, technical benchmark reproduction, and Phase 1 approval | Human / MAIN | OPEN | Review the unsent data request; authorize contact if appropriate; redesign any AOI only in a separate preregistered task with domain review. |

## 10. Handoff Queue

| Handoff ID | From | To | Time | Artifact or Evidence | Required Action | Status |
|---|---|---|---|---|---|---|
| D1-HO-001 | MAIN | VALIDATION | 2026-07-18 12:13 WIB | `task1/src/baseline.py`, `task1/experiments/d1-e001-persist/{config,metrics,notes}.json/md` | Audit origin construction, block aggregation, clipping, and whether MSE 29.6995 is a defensible comparison baseline. | COMPLETED |
| D1-HO-002 | VALIDATION | MAIN | 2026-07-18 12:17 WIB | `task1/reports/d1-validation-audit.md` | Replace the single tail score with purged multi-fold chronological, 372:168 regime-weighted validation before submission. | WAITING |
| D2-HO-001 | VALIDATION | MAIN | 2026-07-19 12:35 WIB | User-supplied independent Task 2 schema, leakage, validation, and baseline audit | Freeze target-group folds; add fold hashes, coverage, category-OOD, and state-ID diagnostics; do not submit baseline. | ACKNOWLEDGED |
| D2-HO-002 | SUBMISSION | MAIN | 2026-07-19 12:29 WIB | Commit `be28757`, 12 tests, and `task2/reports/d2-submission-readiness.md` | Reconcile MAIN validator, integrate the fail-closed implementation, and validate notebook output by exact reference. | COMPLETED |
| D2-HO-003 | SUBMISSION | MAIN | 2026-07-19 12:49 WIB | Audit commit `6d337a8` and `task2/reports/d2-e001-baseline-notebook-audit.md` | Preserve the verified dual-environment contract; defer actual Kaggle Run All until a competitive candidate exists. | ACKNOWLEDGED |
| D2-HO-004 | VALIDATION | MAIN | 2026-07-19 12:50 WIB | Audit commit `6e7d41a` and `task2/reports/d2-e001-baseline-validation-audit.md` | Keep the harness frozen, baseline diagnostic only, and provide an immutable E002 commit for the next audit. | ACKNOWLEDGED |
| D2-HO-005 | MAIN | VALIDATION | 2026-07-19 13:01 WIB | E002 commit `8365193`, branch `exp/d2-e002-metarank`, and `task2/experiments/d2-e002-metarank/metrics.json` | Independently reproduce E002, apply frozen gates, and return GO/NO-GO/INVESTIGATE without changing model/folds/notebook or using a slot. | COMPLETED |
| D2-HO-006 | VALIDATION | MAIN | 2026-07-19 13:08 WIB | Audit commit `2e76cab` and `task2/reports/d2-e002-metarank-validation-audit.md` | Retain E002 as `KEEP`; build its notebook and obtain independent SUBMISSION `READY` before any slot. | ACKNOWLEDGED |
| D2-HO-007 | MAIN | SUBMISSION | 2026-07-19 13:19 WIB | Notebook commit `51d7a9f`, expected CSV SHA-256 `87b4a480...ad3d81`, and prediction SHA-256 `292bb156...d1ba0` | Independently run and audit E002 notebook locally; return readiness verdict without changing model/notebook or using a slot. | REJECTED |
| D2-HO-008 | MAIN | SUBMISSION | 2026-07-19 14:00 WIB | Portability commit `ef59c31`; canonical prediction SHA-256 `292bb156...d1ba0`; local CSV SHA `87b4a480...ad3d81`; Kaggle CSV SHA `e5fa5af1...dff68` | Audit numeric/schema fail-closed behavior across environments; CSV byte hash is informational; no slot until clean Run All. | REJECTED |
| D2-HO-009 | MAIN | SUBMISSION | 2026-07-19 14:31 WIB | Clean notebook commit `3b28567` and regression test | Re-audit source equality, clean JSON, numeric hash, alternate serialization, and exact-reference validator without using a slot. | COMPLETED |

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
| 2026-07-19 13:01:28 +07:00 | 0021 | MAIN | D2-MAIN-002 | Published the immutable E002 challenger | Commit `8365193` pushed; exact audit score and all frozen gates pass; submission remains `INVESTIGATE` pending independent review | VALIDATION audits `8365193`; MAIN starts a structurally independent candidate from `d2-baseline-v1` |
| 2026-07-19 13:02:41 +07:00 | 0022 | MAIN | D2-MAIN-003 | Started the structurally independent route-neighbor challenger | Branch `exp/d2-e003-routeknn` preserves E002 commit `8365193` and the frozen validation; no notebook or slot changed | Preregister the exact neighbor rule, implement once, and apply the fixed gate |
| 2026-07-19 13:10:41 +07:00 | 0023 | MAIN | D2-MAIN-003 | Completed the preregistered one-nearest-route challenger | `REJECT`: mean gain +0.011222 misses +0.015 gate; unseen-current proxy accuracy falls to 0.069560; validator remains READY | Preserve the diagnostic without retuning or submission; E002 remains the candidate awaiting audit |
| 2026-07-19 13:08:06 +07:00 | 0024 | VALIDATION | D2-VAL-002 | Independently reproduced and audited E002 commit `8365193` | `GO/KEEP`; mean gain `+0.024000`, 5/5 folds, improved worst fold/OOD, exact state-ID ablation, all frozen gates pass; submission remains `DO NOT SUBMIT` | MAIN retains E002 and prepares an immutable notebook for SUBMISSION review |
| 2026-07-19 13:19:20 +07:00 | 0025 | MAIN | D2-MAIN-004 | Reproduced the audited E002 candidate in the final dual-environment notebook | Commit `51d7a9f`; local clean CSV is byte-identical, validator READY, 7/7 plus 12/12 tests pass; no slot used | SUBMISSION audits the immutable notebook, then the human runs it cleanly on Kaggle |
| 2026-07-19 13:27:12 +07:00 | 0026 | MAIN | D2-MAIN-005/006/007 | Preregistered three challengers orthogonal to the scout's E004-E006 work | Frozen category-route, route-prototype, and candidate-free next-prototype rules plus shared E002 gate; no scoring, notebook change, or slot use | Execute in isolated high-reasoning workers and accept `REJECT` without retuning if any gate fails |
| 2026-07-19 14:00:14 +07:00 | 0027 | MAIN | D2-MAIN-004/005/006/007 | Fixed Kaggle CSV portability and integrated three parallel challenger results | E002 numeric hash remains exact; 13 notebook/validator tests and 20 integrated experiment tests pass; E007-E009 all `REJECT`; no slot recorded | Human reruns fixed notebook on Kaggle; SUBMISSION audits `ef59c31`; retain E002 as leading candidate |
| 2026-07-19 14:05:59 +07:00 | 0028 | MAIN | D2-MAIN-008 | Recorded successful E002 slot 1 and independently audited scout E004-E006 working artifacts | Public accuracy 0.321; E004/E005 remain below E002 and E006 remains feasibility-rejected; scout verdicts are provisional until immutable commits exist | Preserve E002, obtain scout commit hashes, and preregister no more than two genuinely distinct follow-up hypotheses |
| 2026-07-19 14:14:02 +07:00 | 0029 | MAIN | D2-MAIN-008 | Corrected submission-registry placement | E002 slot 1 moved from the Day 1 table to Day 2; experiment, score, and submission evidence are unchanged | Continue immutable scout audit and keep E002 as the provisional anchor |
| 2026-07-19 14:29:03 +07:00 | 0031 | SUBMISSION | D2-SUB-003 | Audited E002 portability commit `ef59c31` in a separate worktree | `NOT READY`: 13 tests, isolated numeric hash, alternate CSV serialization, and validator pass; committed notebook retains execution counts, outputs, and local paths; report `e4695f1` | MAIN creates a source-identical clean-output notebook commit and requests quick re-audit; no additional slot needed |
| 2026-07-19 14:25:59 +07:00 | 0030 | MAIN | D2-MAIN-008/009 | Closed immutable E004-E006 audit and admitted only frozen E010 TreeRank | Three reject commits verified; E006 ZIP access corrected but OCR provenance remains blocked; E011 stopped before implementation; VALIDATION and SUBMISSION handoffs sent at `gpt-5.6-sol` medium | Await E010 immutable result and parallel notebook readiness audit |
| 2026-07-19 14:38:00 +07:00 | 0032 | SUBMISSION | D2-SUB-003 | Re-audited clean-notebook remediation commit `3b28567` in an isolated worktree | `READY`: clean JSON and source equality pass; 14 tests pass; isolated numeric hash `292bb156...d1ba0`, alternate serialization, and exact-reference validator pass; report `691b452` | MAIN cherry-picks the immutable report and retains `3b28567` as the clean E002 delivery notebook; no additional slot required |
| 2026-07-19 14:53:25 +07:00 | 0033 | VALIDATION | D2-MAIN-009 (audit) | Independently reproduced and audited immutable E010 commit `13194222` | `NO-GO / REJECT`; four gates fail, 0/5 wins versus exact E002, LOO/outer-fold leakage checks pass, prediction hashes and validator reproduce | Preserve negative evidence, do not retune or submit; E002 remains anchor and E011 stays stopped |
| 2026-07-19 14:56:43 +07:00 | 0034 | MAIN | D2-MAIN-009/010 | Froze E002 as the final model candidate, stopped further modeling, and produced a two-page technical writeup | E010 audit `8f5ee0a` confirms rejection; E002 notebook remains `READY`; writeup PDF passes local page-count/text/render checks | Request one independent writeup consistency review, then hand notebook/writeup paths to the human Submission Manager |
| 2026-07-19 15:06:03 +07:00 | 0035 | SUBMISSION | D2-SUB-004 | Independently audited Task 2 writeup commit `feca95c` in an isolated worktree | `NOT READY`: two-page render, exact PDF SHA/Git binary contract, all method/metric claims, and isolated local rebuild pass; filename/title/footer/metadata still use an unverified team-name placeholder | MAIN obtains the registered team name, applies naming-only remediation, rebuilds the PDF, and requests quick re-audit; no Kaggle or slot action needed |
| 2026-07-19 15:06:49 +07:00 | 0036 | SUBMISSION | D2-SUB-004 | Resolved the provisional writeup naming blocker using authoritative human registration context | `READY`: registered team name is exactly `Enter Your Team Name`; compact token `EnterYourTeamName` is authorized, and every remaining technical/content/build check passes | Preserve `feca95c` artifacts unchanged, cherry-pick the immutable audit report, and hand the reviewed PDF to the human Submission Manager |
| 2026-07-19 15:09:50 +07:00 | 0037 | MAIN | D2-MAIN-010 | Integrated the immutable final-writeup audit and closed all repository-side Task 2 work | Audit report `877b7b1` integrated as `2343f1e`; notebook and writeup are `READY`; E002 remains the frozen final candidate | Human selects slot 1 and uploads the clean notebook/writeup by their official deadlines; no further model or slot use |
| 2026-07-19 15:16:13 +07:00 | 0038 | MAIN | D2-MAIN-011 | Reopened one bounded screenshot-link feasibility path while preserving E002 as the READY fallback | Only `d2-e012-linkgraph` may proceed; all Stage-0 OCR provenance, mapping quality, recall, and runtime gates are frozen before scoring | Run deterministic Stage-0; stop without a slot on any failed gate, otherwise validate the full graph against E002 |
| 2026-07-19 15:37:38 +07:00 | 0039 | MAIN | D2-MAIN-011/012 | Rejected two online OCR implementations, then admitted one final artifact-first attempt | E012/E013 recall and precision pass but runtime/Kaggle packaging fail; sampled link-ranking gains +0.0708 across 5/5 diagnostic folds; E002 remains READY fallback | Precompute with fixed rules for at most 60 minutes, then require full frozen-fold promotion and reproducibility before any slot |
| 2026-07-19 15:46:09 +07:00 | 0040 | MAIN | D2-MAIN-012 | Stopped E014 at the frozen precompute gate and refroze E002 | 200-page four-worker benchmark projects 5,383 seconds for the relevant union, exceeding 3,600 seconds; no full extraction, validation, notebook, or slot | Commit/push negative evidence; human selects E002 slot 1 and uploads the READY notebook before 18:00 WIB |
| 2026-07-19 15:51:11 +07:00 | 0041 | MAIN | D2-MAIN-012 | Applied the human-supplied panitia clarification to final eligibility | Screenshot preprocessing must run end-to-end inside the submitted notebook; E014's precomputed-artifact architecture is ineligible in addition to failing runtime | Preserve E002 as the only eligible READY final and use no more slots |
| 2026-07-19 16:33:11 +07:00 | 0042 | MAIN | D2-MAIN-013 | Prepared a resumable local E014 experiment notebook at the human's request | Clean 12-cell notebook, focused ranker tests, syntax checks, two-page OCR smoke extraction, and checkpoint reuse pass; full 4,312-page extraction intentionally not run | Human may run `d2-e014-prelink-local.ipynb` in VS Code; treat its CSV as diagnostic until frozen-fold results and independent audit pass |
| 2026-07-19 17:35:42 +07:00 | 0043 | MAIN | D2-MAIN-014 | Reconfigured the E014 local notebook for a responsive checkpoint-resume run | Balanced CPU mode uses 2 workers with 1 thread each; notebook cleanliness tests and a one-page OCR smoke run pass | Start VS Code `Run All`; leave the long local run unattended and do not treat its output as an official submission without audit |
| 2026-07-19 18:43:17 +07:00 | 0044 | MAIN | D2-MAIN-014 | Closed and documented the post-competition E014 research run | Full local validation reached 0.369556 versus E002 0.285333 with 5/5 fold wins; Kaggle late diagnostic displayed 0.375 versus official E002 0.321 | Preserve E002 as official; publish reproducible E014 code and documentation without raw data, checkpoints, or generated CSV |
| 2026-07-19 18:47:38 +07:00 | 0045 | MAIN | ARCHIVE | Archived remaining independent Task 1 audit reports and local-tooling exclusions | E006, E007, and public-leaderboard-gap reports are now tracked; local worktrees and temporary files remain excluded without deletion | Keep experiment history on remote branch `exp/d2-e014-prelink` for future research |
| 2026-07-24 17:45:24 +07:00 | 0046 | MAIN | CONCEPT-001 | Reviewed the supplied D'Coast concept papers and prepared a minimal product foundation | Added `concept-paper/dcoast/FOUNDATION.md`; no data acquisition, modeling, web implementation, or performance claim was started | Select one candidate pilot area and run a narrow data-feasibility check before implementation |
| 2026-07-24 21:15:31 +07:00 | 0047 | MAIN | DCOAST-PHASE0-001 | Started the D'Coast pilot-site feasibility study | Froze four candidates: Morowali and Cilegon as operational candidates, Teluk Awur as the primary technical benchmark, and Nusa Lembongan as an additional optical benchmark; no model training or bulk imagery download authorized | Query metadata, document AOI-level clear-water access blockers, score evidence, and recommend one operational pilot plus benchmark |
| 2026-07-24 22:00:19 +07:00 | 0048 | MAIN | DCOAST-PHASE0-001 | Completed the D'Coast pilot-site feasibility study and stopped at the Phase 0 gate | Conditional recommendation: Cilegon operational pilot and Teluk Awur technical benchmark; 4 valid provisional AOIs, 1,704 unique acquisitions, 268 monthly rows, source inventory, scores, and fail-closed scripts validated at 424,071 bytes; AOI clear-water sensitivity remains blocked by absent CDSE OAuth | Human reviews the recommendation and supplies OAuth plus validation/boundary access before approving any Phase 1 download, preprocessing, or model work |
| 2026-07-24 23:49:40 +07:00 | 0049 | MAIN | DCOAST-PHASE05-001 | Started the bounded D'Coast Phase 0.5 blocker-closure and site-lock review | CDSE OAuth remains absent; supplementary Cilegon map and calculation workbook were inspected without adopting unverifiable coordinates; no imagery download, training, or Phase 1 work started | Refine water-only AOIs, prepare fail-closed observation-quality tooling, classify validation evidence, test artifacts, and issue one site-lock verdict |
| 2026-07-25 00:12:04 +07:00 | 0050 | MAIN | DCOAST-PHASE05-001 | Completed Phase 0.5 and stopped at the site-lock gate | `CONDITIONAL_GO_CILEGON`; Teluk Awur remains benchmark; 4 AOIs, 1,704 acquisitions, 858 blocked quality rows, 268 monthly rows, 5 tests, syntax checks, and fail-closed artifact validation pass; no station coordinates, imagery download, model, or Phase 1 artifact was created | Human configures CDSE OAuth and secures a georeferenced validation/expert-review path before requesting any Phase 1 work |
| 2026-07-25 01:49:53 +07:00 | 0051 | MAIN | DCOAST-PHASE06-001 | Started the credential-enabled clear-water blocker closure | Human confirmed credentials are ready in a private PowerShell; runner preparation is migrating 858 acquisition rows to 848 unique site-date mosaics with bounded retry, explicit quality status, rejection reason, and provenance | Complete local regression checks, then hand one secret-safe command to the human for execution in the credential-bearing PowerShell |
| 2026-07-25 02:05:00 +07:00 | 0052 | MAIN | DCOAST-PHASE06-001 | Diagnosed the first credential-bearing runner failure | Token endpoint returned HTTP 401 before any Statistical API call; non-empty environment variables were present but the pair was not accepted as a Sentinel Hub OAuth client | Human creates or recopies a dedicated client under CDSE Dashboard User Settings > OAuth clients, resets the two environment variables, and reruns the same one-command workflow |
| 2026-07-25 02:12:00 +07:00 | 0053 | MAIN | DCOAST-PHASE06-001 | Diagnosed the second runner failure after valid authentication | Token exchange succeeded; the first statistics request returned HTTP 400 because the runner used an obsolete `/api/v1/statistics` path instead of the current documented `/statistics/v1` endpoint | Rerun the corrected one-command workflow; any further non-transient API rejection will now expose a bounded server validation message without credential values |
| 2026-07-25 02:20:00 +07:00 | 0054 | MAIN | DCOAST-PHASE06-001 | Diagnosed the current endpoint's precise resolution rejection | API reported an effective 21,132.99 m pixel because numeric `60` was interpreted in WGS84 coordinate units; payload now declares EPSG:4326 and uses 0.00054-degree resolution, approximately 60 m near the pilot latitudes | Rerun the corrected workflow in the same credential-bearing PowerShell |
| 2026-07-25 02:27:00 +07:00 | 0055 | MAIN | DCOAST-PHASE06-001 | Removed remaining Statistical API resolution ambiguity | The API repeated the same effective one-pixel rejection despite decimal WGS84 resolution; runner now calculates and sends explicit width/height from AOI extent at the frozen approximate 60 m target, with a 2500-pixel fail-closed guard | Rerun the corrected workflow in the same credential-bearing PowerShell |
| 2026-07-25 02:31:00 +07:00 | 0056 | MAIN | DCOAST-PHASE06-001 | Detected and validated the completed Statistical API artifact despite stale pasted traceback | `sentinel2_observation_quality.csv` now has 848 unique site-date rows representing 858 acquisitions; validator passes; Cilegon quality-70 count is 0 versus Teluk Awur 167 | Freeze the proven request configuration, aggregate frozen gates, explain the Cilegon SCL-screening failure without relabeling it as pollution, and issue the Phase 0.6 verdict |
| 2026-07-25 02:32:00 +07:00 | 0057 | MAIN | DCOAST-PHASE06-001 | Completed Phase 0.6 and stopped before Phase 1 | Cilegon has 0 quality-70 dates and fails 3/3 frozen cadence gates; Teluk Awur has 167 quality-70 dates and passes volume but fails the 120-day gap gate; all 848 rows, summaries, seasonality, report, and fail-closed checks are reproducible | Keep `NO_GO_CILEGON_FOR_PHASE1`; require new AOI/expert evidence and secured georeferenced validation before any new human-approved phase |
| 2026-07-25 02:40:00 +07:00 | 0058 | MAIN | DCOAST-PHASE07-001 | Started the bounded AOI and validation-acquisition closure | Official BIG exposes a queryable 1:25,000 coastline feature service, and the Teluk Awur study states that supporting data are available from the corresponding author upon reasonable request | Extract only small site-bounded coastline vectors, quantify provisional AOI alignment, and prepare a minimum reusable TSS data contract without contacting anyone or starting Phase 1 |
| 2026-07-25 10:42:00 +07:00 | 0059 | MAIN | DCOAST-PHASE07-001 | Completed the bounded official-coastline and validation-acquisition review | Cilegon and Teluk Awur both fail the frozen <=1,000 m endpoint gate; 5/62 BIG features, approximate study extent, data contract, and unsent author-request draft are reproducible | Human reviews the request and separately authorizes any contact or AOI redesign; Phase 1 remains blocked |

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

- Final submission: `sub-s01-d2-e002-metarank.csv`, public accuracy 0.321; model decision frozen, Kaggle final-selection checkbox remains a human action.
- Final experiment: `d2-e002-metarank` at immutable model commit `8365193`; local mean accuracy 0.285333 with 5/5 fold wins over baseline.
- Notebook status: `READY` at clean delivery commit `3b28567`, independently re-audited in report commit `691b452`; final Kaggle notebook upload remains a human action.
- Optional post-competition experiment: `task2/notebooks/d2-e014-prelink-local.ipynb` can run E014 end-to-end locally with resumable checkpoints; it is not the selected final notebook and has not completed full validation.
- Writeup status: `READY`; two-page `output/pdf/EnterYourTeamName_Task2_Writeup.pdf` is independently audited in `task2/reports/d2-final-writeup-audit.md`.
- Unresolved reproducibility risk: no known model/notebook blocker; only the human Kaggle final-selection and deliverable uploads remain outside the repository.
- Final deliverable checklist: submission exists; select slot 1 as final; upload/run the clean notebook before 18:00 WIB; deliver the reviewed writeup by 20 July 23:59 WIB.
