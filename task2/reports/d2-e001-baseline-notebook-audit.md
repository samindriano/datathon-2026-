# D2-E001 Baseline Notebook Audit

## Verdict

`READY` for local clean-session reproducibility and CSV-contract handoff.

This verdict applies to the diagnostic `d2-e001-baseline` notebook at MAIN
commit `0f94a1c`. It does not make the baseline competitive, authorize a Kaggle
submission, or replace the deferred Kaggle `Restart Session -> Run All` check.
No Kaggle slot was used.

## Audit scope and provenance

- MAIN commit: `0f94a1c` (`feat(task2): add target-group baseline`).
- Validator ancestor: `721c4bf` (`feat(task2): add fail-closed submission
  validator`). `git merge-base --is-ancestor 721c4bf 0f94a1c` succeeded.
- Notebook:
  `task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb`.
- Reference artifact:
  `task2/experiments/d2-e001-baseline/submission.csv` in the MAIN worktree.
- Audit branch/worktree: `audit/d2-e001-notebook`, created directly from
  `0f94a1c`.

The reference CSV is intentionally ignored by `.gitignore` and is not a blob
inside commit `0f94a1c`. It was available locally for this audit. The notebook
reproduced it byte-for-byte, and the expected SHA-256 is recorded in tracked
experiment notes, so the reference result is independently reproducible from
the audited commit and official local data.

## Regression tests

Command:

```powershell
python -m unittest task2.tests.test_submission_validator -v
```

Result: all 12 tests passed in 1.115 seconds. The suite covers exact column
names/order, exactly 6,000 rows, missing/extra/duplicate/reordered state IDs,
empty/NaN/infinite/non-integer predictions, article-universe membership,
reference mismatch, and local/Kaggle path helpers.

## Notebook cleanliness

The notebook JSON contains 6 cells, including 5 code cells.

- every code-cell `execution_count` is `null`;
- every code-cell `outputs` list is empty;
- the worktree notebook blob exactly matches the notebook blob in `0f94a1c`
  (`12a7ac53671beea1010ea76502595cd09b0630ed`);
- no `C:\Users\Sam` path or other hard-coded local user path was found;
- no URL, network module/command, API client, credential, secret, or package
  installation was found;
- no external data or external/pretrained weight is loaded;
- code imports are limited to standard-library modules, NumPy, and pandas.

The words `pretrained` and `weight` occur only in explanatory markdown that
states they are not used; there are no such code hits.

## Clean-session smoke run

The notebook was executed sequentially by the requested runner in a fresh,
isolated Python process:

```powershell
$env:TASK2_DATA_DIR = "C:\path\to\official\dataset-task2"
$env:TASK2_SUBMISSION_PATH = "task2\submissions\submission.csv"
python -I task2/src/run_notebook_smoke.py `
  task2/notebooks/EnterYourTeamName_Task2_Notebook.ipynb
```

Observed result:

- train rows: 9,000;
- test/output rows: 6,000;
- article universe: 4,604 IDs;
- unique state IDs: 6,000;
- unique predictions: 544;
- seen-current rows: 5,245;
- global fallback article ID: 237;
- runtime: 0.573 seconds;
- output:
  `task2/submissions/submission.csv` inside the audit worktree.

The run began with no pre-existing output at that path. It did not require a
Jupyter kernel, cached notebook state, network access, external weight, or
untracked model artifact.

## Data and output path checks

- `TASK2_DATA_DIR` resolved to the official local Task 2 data directory.
- `TASK2_SUBMISSION_PATH` wrote exactly to the requested canonical local path.
- repository-relative resolution was independently invoked against the local
  repository root and resolved the same official data directory.
- `/kaggle/input` behavior was tested with an isolated Kaggle-layout directory
  populated from the official CSV contract; exactly one dataset was found.
- local default output resolves to `task2/submissions/submission.csv`.
- when a Kaggle working directory exists, output resolves to
  `<kaggle-working>/submission.csv`; therefore the production Kaggle contract
  is `/kaggle/working/submission.csv`.
- `TASK2_SUBMISSION_PATH` remains the explicit output override.

The notebook contains equivalent repository-relative and `/kaggle/input`
discovery logic and fails when the dataset location is missing or ambiguous.

## Fail-closed output validation

The generated local output was validated with the integrated fail-closed
validator and the external local reference:

```powershell
$reference = "C:\path\to\MAIN-worktree\task2\experiments\d2-e001-baseline\submission.csv"
python -I task2/src/submission_validator.py `
  --reference $reference
```

Verified independently:

- exact columns and order: `state_id,predicted_next_article_id`;
- exactly 6,000 rows and two fields per row;
- 6,000 unique state IDs;
- state IDs and row order exactly match both `states_test.csv` and
  `sample_submission.csv`;
- every prediction is a syntactic integer;
- prediction range is 3 through 4,560 and every ID belongs to `articles.csv`;
- generated and reference CSVs match semantically and byte-for-byte;
- generated and reference SHA-256:
  `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`.

## Deferred check

Actual Kaggle `Restart Session -> Run All` remains deliberately deferred until
a competitive candidate exists, as requested. Before any eventual submission,
MAIN must rerun that Kaggle check and validate `/kaggle/working/submission.csv`
with the same fail-closed contract. The diagnostic baseline remains a
`DO NOT SUBMIT` candidate and consumed no slot during this audit.
