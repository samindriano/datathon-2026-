# d1-e002-ridge

## Hypothesis

A fixed per-road ridge model using five causal summaries of the exact 15-step
history improves on preregistered mean15 across chronological regimes without
requiring text, graph features, or future information.

## Preregistered comparison

- Compare only `mean15` and `ridge-history` in this run.
- Use three expanding chronological folds in each independent train block.
- Use 720 validation origins per fold and purge 15 origins at every boundary.
- Aggregate m1:m2 using the observed test counts 372:168.
- Report every fold, horizon, block, mean, standard deviation, and worst fold.
- Preserve exactly-zero predictions when all 15 history values for a road are
  zero.
- Use fixed ridge alpha 0.1; do not retune it after seeing these scores.

## Acceptance gate

Mark `KEEP` only if ridge improves weighted mean MSE, does not rely on one fold,
does not materially worsen the worst fold, remains finite and credible, and is
reproducible within the competition runtime. Otherwise mark `REJECT` or
`INVESTIGATE` without spending a Kaggle slot.

## Result

- Mean15: mean `45.5482`, std `10.3820`, worst fold `54.8371`.
- Ridge-history: mean `39.0248`, std `5.4669`, worst fold `44.4867`.
- Weighted improvement: `6.5234` MSE or `14.32%`.
- Ridge fold scores: `44.4867`, `41.0327`, `31.5551`.
- Mean15 fold scores: `54.8371`, `50.7510`, `31.0566`.
- Ridge improves the weighted mean at h5, h10, and h15.
- Ridge improves folds 1 and 2 substantially, but is `0.4985` MSE worse on
  fold 3; this caveat must remain visible during review.
- Test routing reproduces exactly 372 m1-like and 168 m2-like samples.
- Preview has 2,041,200 ordered, unique, finite, nonnegative predictions in
  `[0.0, 101.5696]` and was generated in about 10 seconds.

## Recommendation

Model verdict: `KEEP` as a promising candidate for independent validation.

Submission verdict: `INVESTIGATE`. Do not spend a Kaggle slot until VALIDATION
confirms the fold construction, training-only fitting, aggregation, and the
small fold-3 regression.
