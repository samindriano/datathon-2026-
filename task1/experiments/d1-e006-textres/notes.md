# d1-e006-textres

## Hypothesis

Counts of official event types at the forecast origin explain systematic
road-level residuals that speed-history ridge alone cannot capture.

## Preregistered comparison

- Use frozen `d1-multifold-v1` folds and unchanged ridge base model.
- Parse only seven fixed causal features: counts of accident, closure,
  construction, traffic control, announcement, turn restriction, and total
  event sentences.
- Fit feature scaling and per-road residual coefficients on training origins
  only.
- Use fixed base alpha `0.1` and residual alpha `1.0`.
- Preserve all-zero history predictions as zero and floor predictions at zero.
- Use only official JSON text; no API, embedding, pretrained weights, external
  translation, or road-name mapping.
- Do not tune keywords, alpha, folds, or gates after scores.

## Acceptance gate

Mark `KEEP` only if all of these hold against ridge:

- weighted mean MSE improves by at least 0.5%;
- at least two of three aggregate folds improve;
- at least two of three horizons improve;
- worst-fold MSE is no more than 1% worse.

Otherwise mark `REJECT` and do not create or submit a Kaggle candidate. Public
leaderboard score `45.980` is diagnostic only and is not used for selection.

## Result

- Text residual mean MSE: `38.3456` versus ridge `39.0248`.
- Improvement: `0.6792` MSE or `1.74%`.
- Text residual fold scores: `44.0077`, `40.5864`, `30.4429`.
- All `3/3` folds and `3/3` aggregate horizons improve.
- Worst fold improves from `44.4867` to `44.0077`.
- All four preregistered acceptance checks pass.
- Runtime: `22.76s`.
- Test predictions differ from ridge by mean absolute `0.4604` km/h and RMS
  `0.6668` km/h; maximum absolute correction is `11.4025` km/h.
- Submission validator reports `READY`: 2,041,200 exact unique IDs, finite,
  nonnegative, and all 40,250 structural zero sample-road pairs remain zero.

## Recommendation

Model verdict: `KEEP`, pending independent text-alignment and leakage audit.

Submission verdict: `INVESTIGATE`. Do not use slot 2 until VALIDATION confirms
training-only feature scaling, residual fitting, and exact text alignment.
