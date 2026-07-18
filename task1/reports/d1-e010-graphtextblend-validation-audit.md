# D1 E010 Graph-Text Blend Validation Audit

- Time received: 2026-07-18 14:16 WIB
- Role: VALIDATION (read-only audit supplied by the user)
- Reviewed commit: `e99d6d6`

## Verdict

- Leakage: `GO` — no material leakage found.
- Candidate: `KEEP`.
- Submission now: `INVESTIGATE — DO NOT SUBMIT` until actual Kaggle Run All
  and SUBMISSION `READY`.
- Conditional recommendation: `SUBMIT` as slot 2 after the exact frozen
  notebook output passes those gates.

## Reproduced evidence

| Candidate | Mean MSE | Fold 1 | Fold 2 | Fold 3 |
|---|---:|---:|---:|---:|
| Ridge | 39.0248 | 44.4867 | 41.0327 | 31.5551 |
| Graphres | 38.1750 | 43.7473 | 39.9422 | 30.8355 |
| Text z-guard | 38.2840 | 44.0077 | 40.5864 | 30.2579 |
| Graph-text blend | 37.9040 | 43.4387 | 39.9813 | 30.2920 |

The blend improves graphres by `0.2710` MSE (`0.71%`), improves `15/18`
block-fold-horizon cells, all three aggregate horizons, and the worst fold.
The fixed `0.5:0.5` weights were preregistered; no alternative weight search,
leaderboard tuning, validation change, API, external data, or pretrained model
was found.

## Retained risks

- Fold 2 regresses by `+0.0391` MSE versus graphres; all three regressing cells
  are m1 fold 2.
- Blend standard deviation `5.5645` is slightly above graphres `5.4173`.
- The text z-guard is test-distribution-aware and has local activation support
  only in 390 m2 fold-3 samples, although it uses no test label.
- Component error correlation is high (`0.983`), so complementarity is real but
  modest.

Test-m2 correction remains in the safer direction at `-0.1674 km/h`; large
corrections are rare and all structural-zero predictions remain zero.

## Required next gate

The clean notebook must reproduce frozen commit `e99d6d6` using actual Kaggle
`Run All`, and SUBMISSION must verify the generated CSV before MAIN authorizes
slot 2.
