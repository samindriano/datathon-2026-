# D1 E010 Notebook Readiness

- Time: 2026-07-18 14:11 WIB
- Role: MAIN
- Branch: `exp/d1-e010-notebook`
- Frozen model commit: `e99d6d6`
- Notebook: `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`

## Local verdict

`READY` for independent review; `DO NOT SUBMIT` until model audit and actual
Kaggle clean-session Run All are complete.

The self-contained notebook uses only official train speeds, train event text,
official adjacency, test histories/text, and sample submission. Dependencies
are limited to Python, NumPy, and pandas. It contains no API/network calls,
credentials, external data, pretrained weights, or local-only required files.

## Reproduction evidence

- Clean isolated execution: `python -I`, completed in `16.18s`.
- Output rows: `2,041,200`.
- Regime routing: `372:168`.
- Structural-zero pairs: all `40,250` remain zero across all three horizons.
- Prediction range: `0.0` to `101.636009`; mean `52.844913`.
- Float32 prediction SHA256:
  `0533a98dd0b436d798b3098a3c8831b6262dd6b23410d88ad85cd2384841076a`.
- Submission value SHA256:
  `a1e1f9f9296022fea70682333145f3a798dc33a4472e93f7f822e51c87d4644e`.
- Exact numeric comparison with frozen experiment CSV: zero mismatches and
  maximum absolute difference `0.0`.
- Task 1 test suite: `34 passed`.
- All notebook code cells have null execution counts and empty saved outputs.

Machine-readable validation is in `d1-e010-notebook-readiness.json`.

## Remaining gates

1. VALIDATION must audit `d1-e009-textzguard` and `d1-e010-graphtextblend`.
2. SUBMISSION must inspect this notebook and run `Restart Session` then
   `Run All` in Kaggle.
3. The generated `/kaggle/working/submission.csv` must match the frozen
   candidate exactly before MAIN may issue `SUBMIT`.
