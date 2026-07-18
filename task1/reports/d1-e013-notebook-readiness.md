# D1 E013 Notebook Readiness

- Time: 2026-07-18 15:19 WIB
- Candidate: `d1-e013-stableblend`
- Notebook: `task1/notebooks/EnterYourTeamName_Task1_Notebook.ipynb`
- Local verdict: `READY`
- Kaggle verdict: `PENDING`

## Clean-session result

The five-cell notebook has no stored outputs or execution counts. The isolated
runner completed in approximately 18 seconds using only the official Task 1
dataset, NumPy, and pandas.

It generated 2,041,200 ordered predictions with regime routing `372:168`, all
40,250 zero-history sample-road pairs guarded, and fixed weights 75% e010 plus
25% globalstate.

## Exact comparison

The fail-closed validator compared the notebook output against the frozen e013
experiment CSV:

- status: `READY`;
- row count: 2,041,200;
- exact unique ordered IDs: yes;
- finite and nonnegative: yes;
- reference mismatch count: 0;
- maximum absolute difference: 0.0;
- exact numeric match: yes;
- speed-value SHA256:
  `8470308308efa01ab1f66745454a4f2e527bfe142adb342a05b62afad80b6e1d`.

## Remaining gate

The human Kaggle operator must import the committed notebook, use Restart
Session / Run All, download `/kaggle/working/submission.csv`, and return that
file for the same fail-closed comparison. No Kaggle slot is authorized until
the actual Kaggle output receives independent SUBMISSION `READY`.
