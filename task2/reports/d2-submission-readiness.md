# Task 2 Submission Readiness

## Verdict

`READY` for CSV contract validation. This verdict does not approve a model,
final notebook, or Kaggle submission, and no submission slot was used.

## Audited source contract

- `states_test.csv`: SHA-256
  `4b19f77540afd1ece48eef7d194b6a6d297676375954099144459d97b8784c6c`,
  6,000 rows, exact columns `state_id,current_article_id,target_article_id`, no
  nulls, and unique `state_id` values.
- `sample_submission.csv`: SHA-256
  `397b84b7f38dbadb57ee799716bcdc23a323e59bdadb8b2b5a37935fca6b6162`,
  6,000 rows, exact columns `state_id,predicted_next_article_id`, no nulls,
  and `state_id` values identical to `states_test.csv` in the same order.
- `articles.csv`: SHA-256
  `2d2f8336f341b547849a1757485be4b31258ad63ad75b32a5e79a5a2ce406c81`,
  4,604 rows, exact columns `article_id,title`, unique article IDs 0 through
  4,603, and no nulls.
- Every current/target article ID in `states_test.csv` and every prediction in
  the supplied sample are members of the `articles.csv` universe.

The `state_id` sequence is non-contiguous (0 through 14,997 across 6,000
rows). It must be copied without sorting from test/sample into the submission.

## Validator contract

`task2/src/submission_validator.py` fails closed unless all of these hold:

- columns are exactly `state_id,predicted_next_article_id` in that order;
- there are exactly 6,000 data rows;
- `state_id` values are unique and exactly match test/sample values and order;
- predictions are present, finite, syntactic integers, and within the
  `articles.csv` article-ID universe;
- when `--reference` is supplied, the validated integer prediction sequence
  exactly matches that reference.

Article-universe validation does not prove that an article is a clickable link
from a particular screenshot. That stricter candidate-link check requires a
separate link-universe artifact and is outside this CSV validator contract.

## Data and output paths

Data resolution order:

1. explicit `--data-dir` or function argument;
2. `TASK2_DATA_DIR`;
3. repository-relative `task2/data/competition/dataset-task2`;
4. one unambiguous matching dataset below `/kaggle/input`.

The validator rejects missing or ambiguous data locations. The output contract
helper returns:

- local: `task2/submissions/submission.csv`;
- Kaggle: `/kaggle/working/submission.csv`;
- override: `TASK2_SUBMISSION_PATH`.

## Commands

Run regression tests from the repository root:

```powershell
python -m unittest discover -s task2/tests -p "test_*.py" -v
```

Validate the canonical local output:

```powershell
$env:TASK2_DATA_DIR = "task2/data/competition/dataset-task2"
python task2/src/submission_validator.py
```

Validate an explicit artifact and optional reproducibility reference:

```powershell
python task2/src/submission_validator.py path/to/submission.csv `
  --data-dir path/to/dataset-task2 `
  --reference path/to/reference.csv
```

## Remaining final-artifact checks for MAIN

Before any Kaggle use, MAIN must still run the final notebook from a clean
Kaggle session, validate its generated `/kaggle/working/submission.csv`, verify
all packaged dependencies/weights, and confirm any required click-candidate
constraint. This report does not authorize a Kaggle submission.
