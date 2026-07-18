# D1 Ridge Submission Readiness

- Time: 2026-07-18 12:36-12:40 WIB
- Owner: MAIN
- Candidate: `d1-e002-ridge`
- Audited model commit: `e2136b6269db4dc9618a3003df4d44fc63dc63d4`
- Validation harness: frozen `d1-multifold-v1` (`GO`)

## Implemented artifacts

- Self-contained Kaggle inference notebook:
  `task1/notebooks/d1-ridge-inference.ipynb`.
- Chunked submission validator: `task1/src/submission_validator.py`.
- Clean-process notebook runner: `task1/src/clean_notebook_runner.py`.
- Regression tests: `task1/src/test_submission_readiness.py`.
- Machine-readable readiness result:
  `task1/reports/d1-submission-readiness.json`.

The notebook contains the complete feature extraction, per-road ridge fitting,
regime routing, zero-history guard, prediction, ID validation, and CSV writing
logic. It does not import repository modules and contains no local absolute
path, credential, API call, network call, external data, or pretrained weight.
On Kaggle it discovers the dataset below `/kaggle/input` and writes
`/kaggle/working/submission.csv`.

## Clean-session reproduction

The notebook was executed in a fresh isolated interpreter using `python -I`.
Only the portable environment variables `DATATHON_DATA_ROOT` and
`DATATHON_OUTPUT_PATH` were supplied for the local check. All notebook code
cells ran sequentially without Jupyter-specific magic or repository imports.

Result:

- runtime: 4.95 seconds;
- samples by regime: 372 m1-like and 168 m2-like;
- zero-history sample-road pairs: 40,250;
- rows: 2,041,200;
- prediction range: 0.0 to 101.569557;
- prediction mean: 52.882641;
- float32 tensor SHA-256:
  `f2ca7d1732e008b86704421a93e288fbb5278756dd82115be51259221cbefa9a`.

## Submission validation

The generated CSV was checked in chunks against the official template and the
previously audited ridge CSV.

- columns are exactly `id,speed`;
- all 2,041,200 IDs match the required order and are unique;
- all speeds are finite and nonnegative;
- 120,750 horizon-road predictions are exactly zero, corresponding to the
  40,250 zero-history sample-road pairs across three horizons;
- reference mismatch count: 0;
- maximum absolute reference difference: 0.0;
- numeric values match the audited ridge submission exactly.

## Readiness verdict

Implementation verdict: `READY FOR SUBMISSION REVIEW`.

Kaggle submission verdict: `INVESTIGATE`. No slot is authorized until the
SUBMISSION role independently reviews these artifacts and performs the actual
Kaggle clean-session `Run All` check. MAIN did not upload a notebook or submit a
CSV to Kaggle.
