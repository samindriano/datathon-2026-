# d1-e012-globalstate-only

Final status: `REJECT`.

## Selection disclosure

Globalstate's aggregate MSE `35.3894` was already observed as a diagnostic in
the rejected e011 blend experiment. E012 does not treat a repeated aggregate
score as new confirmation. Its new evidence is the preregistered temporal-chunk
stress test below.

## Frozen model

The model is exactly the e011 globalstate component: five local ridge history
features plus the same five features computed from the active-road city mean.
Active roads and all features use only the causal 15-step history. Alpha remains
`0.1`; no parameter, fold, threshold, or blend is tuned.

## Preregistered gate

All conditions must pass:

1. at least 3% aggregate mean improvement over e010;
2. all 3 aggregate folds and all 3 horizons improve;
3. worst fold improves and fold standard deviation does not worsen;
4. at least 15/18 block-fold-horizon cells improve;
5. at least 34/36 consecutive 120-origin chunks improve;
6. median chunk gain is at least 1.0 MSE;
7. worst chunk gain is at least -0.25 MSE;
8. test-m2 mean correction versus ridge is nonpositive;
9. predictions are finite, nonnegative, and preserve all-zero histories.

Passing creates a local candidate for independent audit only. Slot 3 remains
unauthorized until exact reproduction, notebook readiness, and audit all pass.

## Result

The known aggregate result reproduced exactly, but the new unseen stress gate
failed:

- aggregate MSE `35.3894` versus e010 `37.9040`;
- 3/3 folds, 3/3 horizons, and 17/18 block-fold-horizon cells improve;
- only 31/36 temporal chunks improve (required 34/36);
- median chunk gain is `1.9871` MSE;
- worst chunk gain is `-1.9517` MSE (required at least `-0.25`);
- the weakest block-fold origin win rate is `49.44%`;
- test-m2 correction remains nonpositive at `-0.4117` km/h;
- finite, nonnegative, and all 40,250 zero-history pairs remain guarded.

The model is rejected without changing the preregistered thresholds. No
submission CSV was created and no Kaggle slot is justified. E010 remains the
more defensible final-selection candidate because its paired audit won all
36/36 corresponding temporal chunks versus ridge.
