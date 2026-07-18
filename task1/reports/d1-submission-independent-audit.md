# D1 Independent Submission and Leakage Audit

- Time: 2026-07-18 12:49-12:53 WIB
- Role: SUBMISSION
- Reviewed commits: `2729d39`, `6284c0b`
- Candidate: `d1-e002-ridge`

## Verdicts

- Data-leakage verdict: `GO` (no leakage found)
- Committed notebook local reproduction: `PASS`
- Submission readiness: `NOT READY`
- Kaggle-slot verdict: `DO NOT SUBMIT`

The committed notebook reproduces the frozen audited ridge predictions exactly
from competition train speeds and test histories. No target, future-test value,
external data, API, credential, repository module, pretrained weight, text, or
graph input is used. Submission readiness remains blocked by concrete artifact
and external-environment gates listed below.

## Leakage audit

### Data used by inference

The notebook reads only:

- both official `train_speed_*.npy` continuous blocks;
- official `test/test_X_hist.npy`;
- official `sample_submission.csv`.

Training histories and h5/h10/h15 targets are constructed entirely inside each
train block. The final training origin is `len(block) - 16`, so its h15 target
is the final row of that train block. Test data is used only as the supplied
15-step inference history and for regime routing based on all-zero roads.

No test target or future test row exists in or is inferred from the notebook.
The 372:168 routing uses only observable test covariates; it is not target
leakage. The notebook performs no model selection or validation tuning.

### Forbidden or hidden dependencies

The committed notebook has four plain-Python code cells, cleared outputs, and
no repository imports. Source scanning found no OpenAI/external model API,
network call, URL, credential, secret, pretrained weight, pickle/joblib model,
external data, text input, or graph input. Runtime dependencies are only Python,
NumPy, and pandas.

The optional audited ridge reference CSV is used by the external validator only
and is not read by the notebook.

## Independent reproduction

The notebook was independently executed through `python -I` in a fresh
interpreter process. Output:

- runtime: 5.88 seconds;
- rows: 2,041,200;
- regime counts: 372 and 168;
- zero-history sample-road pairs: 40,250;
- prediction range: `[0.0, 101.5695571899414]`;
- prediction mean: `52.88264083862305`;
- float32 prediction SHA-256:
  `f2ca7d1732e008b86704421a93e288fbb5278756dd82115be51259221cbefa9a`.

The full CSV passes the validator:

- exact columns `id,speed`;
- exactly 2,041,200 rows and unique canonical IDs;
- finite and nonnegative values;
- 120,750 exact zeros;
- zero differences versus the independently audited ridge submission;
- CSV float64 speed hash:
  `c5cf88e87b6558f4d4c055289a84532cd1695aef656032dbf4b81fd200c6f00e`.

All relevant tests pass: `10 passed`.

## Blocking findings

### 1. Reference mismatch is fail-open

`submission_validator.py` always reports `status: READY` after structural
checks. When a reference CSV is supplied but every numeric value differs, it
reports `reference_exact_numeric_match: false` while still returning `READY`
and a successful process exit.

This does not invalidate the current evidence because the actual mismatch count
is zero and was independently reproduced. It does make the reusable readiness
validator unsafe against future model/notebook drift. It must raise
`SubmissionValidationError` (or otherwise return a non-ready/nonzero result)
when an explicitly requested reference comparison differs, with a regression
test covering the failure.

### 2. Official notebook filename is not final

The current file is `d1-ridge-inference.ipynb`. Project rules require the final
artifact name `TeamName_TaskName_Notebook.ipynb`. MAIN or the designated
Submission Manager must create the final clean copy using the registered team
and task names before upload.

### 3. Actual Kaggle Run All is unverified

Local clean-process execution cannot prove `/kaggle/input` discovery,
Kaggle-installed dependency compatibility, or `/kaggle/working/submission.csv`
creation. A real clean Kaggle session must run `Restart Session` / `Run All`,
then validate the generated output before readiness can become `READY`.

### 4. Local working notebook contains saved outputs

The committed notebook at `6284c0b` is clean and has no outputs. The current
working copy has execution counts and output text containing local Windows
paths from the user's VS Code run. Source cells are identical to the commit,
but this dirty working copy must not be committed or uploaded. Clear all outputs
or reload the clean committed notebook first.

## Required actions

1. Make reference mismatch fail closed and add a regression test.
2. Clear notebook outputs and verify a clean working tree.
3. Produce the competition-named final notebook using the registered team name.
4. Run the clean notebook in Kaggle and validate the Kaggle-generated CSV.
5. Return the Kaggle execution evidence to SUBMISSION for the final `READY` or
   `NOT READY` verdict.

No competition submission slot was used during this audit.
