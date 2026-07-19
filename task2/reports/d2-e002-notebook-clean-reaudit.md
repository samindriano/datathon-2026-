# D2-E002 Clean Notebook Re-audit

## Verdict

`READY` for final notebook delivery at immutable commit `3b28567`.

The sole blocker recorded in the prior SUBMISSION audit (`e4695f1`) is
remediated: all five code cells are clean, their sources are exactly unchanged
from `ef59c31`, isolated reproduction preserves the canonical numeric
prediction hash, and fail-closed validation passes against the exact E002
reference. This audit did not modify MAIN's notebook, model, or validation and
did not access Kaggle or consume a submission slot.

## Scope and provenance

- Remediation commit: `3b28567` (`fix(task2): clear final notebook outputs`).
- Parent: `ac74850`.
- Prior portability source commit: `ef59c31`.
- Prior SUBMISSION report commit: `e4695f1` (`NOT READY`).
- Audit branch/worktree: `codex/audit-d2-e002-clean`, checked out directly from
  `3b28567`.
- `ef59c31` is an ancestor of `3b28567`.

The exact `ac74850..3b28567` diff contains only:

- `task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb`;
- `task2/tests/test_notebook_portability.py`.

## Notebook integrity and safety

Independent JSON inspection found:

- five code cells, all with `execution_count: null`;
- all code-cell `outputs` equal to `[]`;
- code-cell sources exactly equal, cell for cell, to `ef59c31`;
- no `C:\Users`, `OneDrive`, `Documents`, or other Windows absolute path;
- no URL, network call, API client, credential, external data, or external
  weight reference.

The added regression test fails if execution counts, outputs, or a
`C:\Users\...` path return. The existing portability test continues to require
the numeric prediction-hash guard while treating CSV byte hash as diagnostic.

## Regression tests

Command:

```powershell
python -m unittest `
  task2.tests.test_submission_validator `
  task2.tests.test_notebook_portability -v
```

Result: all 14 tests passed in 1.701 seconds:

- 12 fail-closed submission-validator regression tests;
- one numeric-hash/CSV-portability policy test;
- one clean-delivery notebook regression test.

## Clean isolated reproduction

The notebook was executed from a new Python isolated-mode process using the
official local Task 2 dataset, an explicit `TASK2_DATA_DIR`, and an explicit
audit-worktree `TASK2_SUBMISSION_PATH`:

```powershell
python -I task2/src/run_notebook_smoke.py `
  task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb
```

Observed output:

- 6,000 rows and 6,000 unique state IDs;
- 449 unique predictions;
- all predictions in the 4,604-article universe;
- canonical numeric SHA-256:
  `292bb1567ac81cd70b87b1f4730468830640388919b72126aef69f198e9d1ba0`;
- local CSV SHA-256:
  `87b4a480008eabe06921a36edc14ea12abf4a006b86850f5260d959c54ad3d81`;
- `csv_matches_local_reference: true`;
- notebook status: `READY`.

The fail-closed validator returned `READY` with the exact
`task2/experiments/d2-e002-metarank/submission.csv` reference, confirming exact
columns/order/state IDs, finite integer article IDs in the official universe,
and exact parsed reference predictions.

## Numeric hash cannot be masked by CSV bytes

An alternate LF serialization changed CSV SHA-256 from
`87b4a480...ad3d81` to `e5fa5af1...dff68`, while preserving numeric SHA-256
`292bb156...d1ba0`; the reference validator accepted it. Changing one parsed
prediction changed numeric SHA-256 to `0246d1e5...144a0`, and reference
validation rejected it at CSV row 2.

The notebook computes and enforces the numeric hash before writing the CSV.
Consequently, serialization differences remain informational, but prediction
content differences fail closed and cannot be hidden by a CSV byte mismatch.

## Delivery readiness

The notebook is a clean, portable, self-contained final-delivery artifact. It
retains the repository-relative and `/kaggle/input` data resolver, the local
and `/kaggle/working/submission.csv` output contract, and environment-variable
overrides. Per team status, the human Kaggle Run All evidence and slot-1 public
score are diagnostic only; this re-audit did not interact with Kaggle and no
additional slot is required for the hygiene remediation.
