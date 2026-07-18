# d1-e010-graphtextblend

## Hypothesis

The audited graph model and the guarded text model use complementary official
signals. A fixed equal-weight prediction average can reduce their distinct
errors without tuning a blend on validation or the public leaderboard.

## Preregistered comparison

- Keep `d1-multifold-v1` and both component implementations/parameters frozen.
- Fit graphres and textzguard independently on the same training origins.
- Average their predictions with fixed weights `0.5:0.5`.
- Do not test alternative weights, graph relabels, seeds, folds, or thresholds.
- Preserve component nonnegative floors, regime routing, and structural-zero
  behavior.

## Acceptance gate

- Improve graphres mean MSE by at least 0.2%.
- Improve graphres on at least two folds and two horizons.
- Do not worsen graphres worst fold.
- Beat both component means and keep test-m2 correction versus ridge
  nonpositive.

Otherwise mark `REJECT` and create no submission. A `KEEP` result still needs
independent validation and clean-notebook review before any Kaggle slot.

## Result

`KEEP`, pending independent audit.

- Mean MSE: `37.904035` versus graphres `38.175014`, textzguard `38.283964`,
  and ridge `39.024844`.
- Fold MSE: `43.438742`, `39.981316`, `30.292048`; folds 1 and 3 improve over
  graphres, while fold 2 regresses by `0.039116`.
- Worst fold improves from graphres `43.747325` to `43.438742`.
- Horizon MSE: `32.050536`, `38.536492`, `43.125077`; all three improve over
  graphres.
- Test-m2 mean correction versus ridge is `-0.167410` km/h, between graphres
  `-0.244966` and guarded text `-0.089853`.
- Submission validator reports `READY`; all 2,041,200 IDs are exact/unique,
  values are finite/nonnegative, and all 40,250 structural-zero pairs remain
  zero across three horizons.
- Runtime: `37.25s`; full Task 1 suite: `34 passed`.

Do not submit before independent validation and clean Kaggle notebook
reproduction. Preserve the visible fold-2 regression in any recommendation.
