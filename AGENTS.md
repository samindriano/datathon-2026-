# Datathon 2026 — Project Instructions

This file is the operating rule for every human and Codex agent working in
this repository.

Read this file and `coordination/TEAM_STATUS.md` before doing any work.

Do not assume that another chat or agent has shared its conversation context.
The repository files are the source of truth.

---

# 1. Project Scope

This repository is used for:

- Day 1 — Kaggle Task 1, 18 July 2026
- Day 2 — Kaggle Task 2, 19 July 2026

Each task runs from 12:00 to 17:00 WIB.

Treat Day 1 and Day 2 as separate tasks.

Do not assume that Day 2 has the same:

- dataset;
- target;
- metric;
- validation strategy;
- features;
- model;
- submission format.

Only reuse shared tooling after confirming that it is compatible.

Recommended repository structure:

```text
datathon-2026/
├── AGENTS.md
├── README.md
├── requirements.txt
├── coordination/
│   └── TEAM_STATUS.md
├── shared/
│   ├── metrics.py
│   ├── experiment_utils.py
│   └── submission_validator.py
├── task1/
│   ├── src/
│   ├── configs/
│   ├── experiments/
│   ├── notebooks/
│   ├── reports/
│   └── submissions/
└── task2/
    ├── src/
    ├── configs/
    ├── experiments/
    ├── notebooks/
    ├── reports/
    └── submissions/
```

Adapt to the actual repository structure when necessary.

Do not invent paths or commands that do not exist.

---

# 2. Official Competition Rules

The following rules are mandatory.

## Schedule

* Task 1: 18 July 2026, 12:00–17:00 WIB.
* Task 2: 19 July 2026, 12:00–17:00 WIB.
* Kaggle links are opened at 12:00 WIB on the relevant day.
* Each task has a maximum of 5 submissions per team.
* The submission quota is shared by the whole team, not per member.

## Leaderboard

* Public leaderboard uses 30% of the test set.
* Private leaderboard uses 70% of the test set.
* The team must select exactly one final submission for each task.
* Public leaderboard score is only a diagnostic signal.
* Do not select a model only because its public score is higher.
* Local validation quality and robustness are the main decision criteria.

## Prohibited Actions

Do not:

* use external data;
* collaborate with another team;
* manually assign predictions;
* modify raw competition data;
* use private or inaccessible model weights;
* use a pretrained model unless its weights are open;
* call OpenAI API or another external model API for:

  * prediction;
  * feature generation;
  * pseudo-label generation;
  * target generation;
  * training;
  * modeling;
  * competition inference.

OpenAI or Codex may be used as a coding and debugging assistant, but the
competition pipeline itself must not depend on an external model API.

## Kaggle Team

* All registered members must join the Kaggle team before submission.
* Team name and team members must match registration data.
* Only the designated Submission Manager should submit files.

## Required Deliverables

Each task requires:

* one inference notebook;
* one technical writeup.

Inference notebook requirements:

* must run using `Run All` in the Kaggle environment;
* must reproduce the selected final submission;
* must not contain local-only paths;
* must not contain credentials or API keys;
* must be submitted by 18:00 WIB on the task day.

Technical writeup requirements:

* maximum 3 pages per task;
* must describe the actual final method;
* must be consistent with the notebook and final submission;
* both writeups are due by 20 July 2026 at 23:59 WIB.

All required model weights must already be available on Kaggle before the
relevant deadline.

Do not modify final artifacts after the official deadline.

---

# 3. Sources of Truth

Use these as the project sources of truth.

| Information         | Source of Truth                                   |
| ------------------- | ------------------------------------------------- |
| Project rules       | `AGENTS.md`                                       |
| Current team status | `coordination/TEAM_STATUS.md`                     |
| Official metric     | Task-specific metric module                       |
| Official validation | Task-specific validation module                   |
| Stable baseline     | Current baseline tag recorded in `TEAM_STATUS.md` |
| Experiment results  | Task-specific `experiments/` directory            |
| Submission history  | `TEAM_STATUS.md`                                  |
| Final notebook      | Task-specific final inference notebook            |
| Final submission    | File recorded as final in `TEAM_STATUS.md`        |

If a source of truth has not been established, mark it as `TODO`.

Never silently create a competing metric implementation or validation
implementation.

---

# 4. Team Roles

Three Codex roles are used.

## Subagent Use

Subagents may be used when necessary or when independent parallel work can
meaningfully reduce completion time without reducing correctness. Give each
subagent a focused, non-overlapping scope and keep final integration and
verification with the main agent.

Unless explicitly requested otherwise, use the default subagent configuration:
GPT-5.6 Luna with medium reasoning effort.

## MAIN — Main Integrator

Main Integrator:

* works on the main pipeline;
* understands the competition problem;
* defines the official metric and validation;
* creates the stable baseline;
* develops the primary model;
* integrates accepted experiments;
* maintains the main branch;
* manages submission slots;
* prepares the final notebook;
* selects the final submission.

Only MAIN may:

* change the official validation;
* change the stable baseline;
* edit the final notebook;
* approve integration into `main`;
* select the final submission;
* approve a Kaggle submission.

## VALIDATION — Validation and Leakage Reviewer

Validation Reviewer:

* is read-only toward the main modeling pipeline;
* audits validation design;
* audits data leakage;
* checks preprocessing per fold;
* checks temporal or group leakage;
* checks score stability;
* checks class-level performance;
* checks prediction distribution;
* checks whether an improvement comes from only one fold;
* reports `GO`, `NO-GO`, `INVESTIGATE`, or `BLOCKED`.

VALIDATION must not silently fix the main pipeline.

Findings must be reported to `coordination/TEAM_STATUS.md`.

## SUBMISSION — Submission and Reproducibility Reviewer

Submission Reviewer:

* checks sample submission format;
* validates row count and columns;
* checks IDs for completeness and uniqueness;
* checks missing values and infinity;
* checks valid prediction labels or ranges;
* checks Kaggle paths and dependencies;
* checks model weights;
* checks notebook `Run All`;
* checks reproducibility;
* records submission history;
* supports the technical writeup.

SUBMISSION must not change the model or official validation without explicit
approval from MAIN.

---

# 5. Human Git Workflow

The `main` branch must remain stable.

After the baseline is complete, experiments must use separate branches.

Recommended branch names:

```text
exp/d1-main-model
exp/d1-person2-alternative
exp/d1-person3-feature
exp/d2-main-model
exp/d2-person2-alternative
```

Rules:

* do not run unrelated experiments directly on `main`;
* one person owns one experiment branch;
* do not let two people edit the same notebook;
* keep modeling logic in `.py` files where possible;
* use notebooks mainly for exploration and final inference;
* make small, focused commits;
* report the commit hash when handing work to MAIN;
* MAIN should cherry-pick accepted commits instead of merging an entire
  experimental branch blindly.

Before changing files:

```bash
git status
git pull
```

Do not run without explicit approval:

```text
git reset --hard
git clean -fd
force push
mass deletion
```

---

# 6. Baseline Protocol

The first objective after a task opens is an end-to-end baseline.

The baseline must:

* load train and test data;
* identify the target and ID columns;
* implement the official metric;
* implement a defensible validation strategy;
* perform minimal preprocessing;
* train a simple model;
* produce validation scores;
* produce a valid submission;
* pass the submission validator;
* run through one reproducible command.

The baseline does not need to be highly accurate.

The baseline is complete only when the pipeline works end-to-end.

After approval:

1. commit it to `main`;
2. push it to GitHub;
3. create a stable tag.

Recommended tags:

```text
d1-baseline-v1
d2-baseline-v1
```

Every later experiment must state which baseline tag it uses.

---

# 7. Validation and Leakage Rules

Validation must simulate the real test condition as closely as possible.

For every feature, ask:

> Would this information genuinely be available when the prediction is made?

Mandatory rules:

* fit preprocessing only on the training fold;
* do not fit scaler, imputer, encoder, PCA, feature selection, or aggregate
  statistics on the full dataset;
* create target encoding out-of-fold;
* do not use validation targets in validation features;
* do not use future data in temporal features;
* do not use actual future values during recursive inference;
* avoid random splits when the test structure is temporal;
* avoid placing the same entity in train and validation when that creates
  group leakage;
* detect exact and near-duplicate records;
* keep validation unchanged when comparing experiments;
* do not tune repeatedly against the public leaderboard.

Any suspected leakage must be reported before the experiment is accepted.

---

# 8. Experiment Standard

One experiment must test one clear hypothesis.

Experiment ID format:

```text
EXP-D1-001-short-description
EXP-D2-001-short-description
```

Each experiment must have its own directory:

```text
task1/experiments/EXP-D1-001-baseline/
├── config.yaml
├── metrics.json
└── notes.md
```

Optional artifacts may include:

```text
oof_predictions.csv
feature_importance.csv
confusion_matrix.csv
test_predictions.csv
```

Do not commit very large artifacts unless they are required for
reproducibility.

## Required Experiment Information

Every experiment must record:

* experiment ID;
* owner;
* branch;
* commit hash;
* baseline tag;
* hypothesis;
* changes from baseline;
* dataset version;
* feature version;
* official validation version;
* model and parameters;
* random seed;
* mean validation score;
* score for every fold;
* worst fold;
* standard deviation;
* per-class score when applicable;
* prediction distribution;
* runtime;
* artifact paths;
* leakage check;
* recommendation.

Allowed experiment status:

```text
PLANNED
RUNNING
KEEP
REJECT
INVESTIGATE
FINAL_CANDIDATE
```

## Acceptance Criteria

An experiment may be marked `KEEP` only when:

* validation is directly comparable with the baseline;
* mean score improves meaningfully;
* improvement is not caused by only one fold;
* worst-fold performance does not materially deteriorate;
* prediction distribution remains credible;
* no new leakage is introduced;
* results can be reproduced;
* runtime remains realistic for the competition deadline.

Reject experiments that improve only the public leaderboard or use an
incompatible validation scheme.

---

# 9. Coordination Protocol

The shared coordination file is:

```text
coordination/TEAM_STATUS.md
```

Every Codex agent must read it:

* before starting work;
* before claiming a task;
* after a long-running command finishes;
* before making a recommendation;
* before handing work to another role;
* before finishing its response.

Every agent must update it when:

* starting a task;
* completing a milestone;
* producing a new metric;
* finding leakage;
* finding a blocker;
* producing an artifact;
* completing a task;
* requesting action from another role.

Each agent may only edit:

* its own role section;
* its own task status;
* append-only activity entries.

MAIN owns:

* global decisions;
* active task information;
* official validation;
* baseline information;
* final candidate;
* submission registry.

Before editing `TEAM_STATUS.md`:

1. read the latest version from disk;
2. make a minimal patch;
3. do not overwrite another role's section;
4. preserve previous activity log entries;
5. reread the file after saving.

If another agent has changed the file, reread it before applying a new patch.

Do not rely on another chat's conversation history.

---

# 10. Submission Policy

There are only five submission slots per task.

Recommended use:

1. baseline and format verification;
2. strongest locally validated model;
3. structurally different alternative model;
4. validated ensemble or major improvement;
5. emergency or final candidate.

Do not spend submission slots on tiny parameter changes without strong local
evidence.

Before using a submission slot, the responsible agent must give an explicit
final-chat verdict: `SUBMIT`, `DO NOT SUBMIT`, or `INVESTIGATE`. If the candidate
does not show sufficient validation evidence, meaningful diversity, or a clear
expected benefit over the current best candidate, the verdict must be `DO NOT
SUBMIT` and the agent must say why. Do not submit every generated candidate;
preserve the five-slot budget for candidates that are genuinely justified.

Every submission must record:

* slot number;
* filename;
* experiment ID;
* local validation score;
* public score;
* submit time;
* submitted by;
* reason for submission;
* whether it is a final candidate.

Only the Submission Manager may submit to Kaggle.

The final submission must not be selected solely from public score.

---

# 11. Reproducibility Requirements

All final candidates must:

* use fixed random seeds;
* record all dependencies;
* avoid local-only absolute paths;
* avoid API calls;
* avoid credentials and secrets;
* load only permitted Kaggle inputs;
* have all required weights available;
* generate a valid submission from a clean session;
* run within the available time and memory;
* reproduce the selected final submission.

Before final submission:

* restart the Kaggle session;
* run the notebook using `Run All`;
* validate the generated submission;
* verify that output rows and IDs match the sample submission;
* verify that no hidden local files are required.

---

# 12. File and Secret Safety

Never commit:

```text
API keys
Kaggle credentials
.env files
local credential files
raw competition datasets
temporary caches
large model artifacts unless explicitly required
```

Never:

* modify raw competition files;
* overwrite previous submissions;
* place secrets inside notebooks;
* print secrets into logs;
* delete old artifacts without checking whether they are still needed.

Submission files must use explicit versioned names.

Example:

```text
submission_EXP-D1-004_lgbm-ensemble.csv
```

---

# 13. Day 1 and Day 2 Workflow

## Before 12:00

* confirm Kaggle access;
* confirm all members are in the Kaggle team;
* confirm Git pull and push work;
* confirm dependencies are installed;
* confirm no secret is tracked;
* read this file and `TEAM_STATUS.md`.

## 12:00–12:15

MAIN:

* reads the problem statement;
* inspects train, test, and sample submission;
* identifies target, metric, and schema;
* updates `TEAM_STATUS.md`;
* creates tasks for VALIDATION and SUBMISSION.

VALIDATION:

* audits split strategy and leakage risks.

SUBMISSION:

* audits sample submission and prepares validation checks.

## 12:15–13:00

MAIN:

* builds the end-to-end baseline;
* establishes the initial official validation;
* generates a baseline submission.

VALIDATION:

* reviews validation and preprocessing.

SUBMISSION:

* validates baseline output.

The baseline should be pushed before large experiments begin.

## 13:00–15:30

* all human experiments branch from the stable baseline;
* MAIN develops the primary approach;
* other members test independent hypotheses;
* VALIDATION reviews stable experiment artifacts;
* SUBMISSION maintains validation and reproducibility checks.

## 15:30–16:30

* compare candidates using the same validation;
* inspect mean, folds, worst fold, class scores, distribution, and runtime;
* select robust candidates;
* avoid chasing small public leaderboard changes.

## 16:30–17:00

* stop large experiments;
* freeze model candidates;
* validate final submissions;
* select the final candidate;
* record the final commit and artifact.

## 17:00–18:00

* prepare or finalize the inference notebook;
* run it from a clean Kaggle session;
* validate the reproduced submission;
* submit the notebook before the deadline.

## Day 2 Reset

Before Task 2:

* preserve the Day 1 experiment and submission records;
* update `TEAM_STATUS.md` to Day 2;
* create new `D2-*` task and experiment IDs;
* inspect Task 2 from zero;
* do not reuse Day 1 assumptions without verification.

---

# 14. Definition of Done

A final candidate is ready only when:

* the official metric is correct;
* the validation design is defensible;
* no known leakage remains;
* results are stable across folds;
* submission format is valid;
* all IDs are present and unique;
* no predictions are missing or invalid;
* dependencies and weights are available;
* the notebook runs using `Run All`;
* the output can be reproduced;
* no external data or external model API is used;
* the final experiment and commit are documented;
* the final submission is recorded;
* the technical writeup matches the implementation.

---

# 15. Current Project State

This section must be updated only from evidence in the repository.

```text
Active Day: PREPARATION
Active Task: NONE

Official Metric: TODO
Official Validation: TODO
Stable Baseline Tag: TODO
Stable Baseline Commit: TODO
Current Best Experiment: TODO
Current Final Candidate: NONE

Known Risks:
- TODO

Known Leakage Concerns:
- TODO

Current Blockers:
- TODO

Next Highest-Value Action:
- Wait for the active Kaggle task to open.
```
