# D1 E006 Text-Residual Independent Validation Audit

- Time: 2026-07-18 13:44-13:47 WIB
- Role: VALIDATION
- Reviewed commit: `c603cd967da266a4be171d914bdbc940c4959198`

## Verdict

- Text alignment and fold leakage: `GO`
- Local experiment evidence: `KEEP`
- Current test inference risk: `INVESTIGATE`
- Kaggle slot 2 for this exact version: **DO NOT SUBMIT yet**

The implementation uses only the official text at the forecast origin, checks
the exact JSON key order, and fits the scaler, base ridge, residual mean, and
residual coefficients on training origins only. No future validation text or
target, test target, external data, API, pretrained weight, embedding, graph,
or road-name translation is used.

The local gain is real under the frozen harness and is not produced by the
second-stage intercept alone. However, one text feature is severely shifted in
test m2 and drives the correction in the same direction as ridge's known
low-speed overprediction. This must be resolved or explicitly stress-tested
before spending slot 2.

## Independent reproduction

- 28 repository tests pass independently.
- Ridge reproduces at `39.024844` MSE.
- Textres reproduces at `38.345626` MSE, a `0.679218` or `1.7405%` gain.
- Folds reproduce as `44.007651`, `40.586363`, and `30.442863`.
- All 18 block-fold-horizon cells improve over ridge.
- All three aggregate horizons and the worst fold improve.
- Structural all-zero histories remain exactly zero.

The residual intercept alone scores `39.024528`, effectively identical to
ridge. Thus the reported improvement is not a hidden intercept/refit effect.

## Alignment null test

Ten deterministic random permutations of validation text were scored while
keeping the fitted model, histories, targets, and text-feature multiset fixed:

- correctly aligned text: `38.345626`;
- permuted-text mean: `38.837998` (standard deviation `0.032071`);
- `0/10` permutations beat aligned text;
- average alignment-specific advantage: `0.492372` MSE.

Random text still scores about `0.187` better than ridge, showing that some gain
comes from fold-level text-distribution/temporal effects rather than exact
sample alignment. A deterministic reversal scored `38.333973`, slightly better
than aligned text; reversal preserves slow temporal structure and is not an
independent random null, but it confirms that event counts also act as regime
proxies. The causal-alignment claim is supported by the random null test, not
proven without qualification.

## Test-distribution stress finding

The m1 text features are reasonably close to train. In m2, `89.3%` of test rows
have at least one text feature beyond `|z| > 3`. The main source is
`prohibit left turn`:

- m2 train mean count: `1.076`;
- m2 test mean count: `0.143`;
- mean standardized test value: `-3.434`;
- mean prediction contribution from this feature: `+0.442` km/h;
- all other mean feature contributions combined with the residual intercept
  reduce that to a net m2 correction of `+0.347` km/h.

This extrapolation is material because the ridge audit already found positive
low-speed m2 bias. On local validation's lowest m2 history-speed decile,
textres improves MSE from `29.9652` to `29.3415` and reduces signed bias from
`+1.991` to `+1.698` km/h. On the actual test histories, however, the shifted
text distribution makes the final model add `+0.347` km/h on average, opposite
to the locally helpful bias correction. The correction grows by horizon from
`+0.274` to `+0.415` km/h.

The low-speed stress table is otherwise encouraging: reweighting official-fold
errors to the observed test history-speed bins changes ridge `38.7365` to
textres `38.0944`. The exception is the lowest m1 decile, where textres worsens
`69.0488` to `69.5978`; that bin represents about 7.0% of m1 test samples.

## Recommendation to MAIN

1. Keep `d1-e006-textres` as valid experiment evidence, but do not submit the
   exact current inference artifact yet.
2. Preregister one narrow robustness experiment before scoring it: neutralize
   the single out-of-distribution `prohibit left turn` path (for example remove
   that feature, or apply a training-range standardized-feature guard). Do not
   try several alternatives and pick the best retrospectively.
3. Reuse the frozen folds and require the safe version to retain broad gains,
   improve the low-speed m2 stress bin, and avoid a positive mean m2 correction
   caused by feature extrapolation.
4. If that check fails, retain ridge for private robustness and save slot 2 for
   a more structurally justified candidate.

No model, official validation, notebook, or submission artifact was changed by
this audit.
