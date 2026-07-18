# d1-e014-diststate

Final status: `REJECT`.

## Hypothesis

City mean cannot distinguish widespread congestion from localized low-speed
pockets. A causal per-road ridge using local history plus city mean, city speed
standard deviation, fraction of active roads below 30 km/h, and fraction below
50 km/h may add congestion-shape information. The final candidate keeps the
same fixed 75% e010 anchor and 25% state-model weight as e013.

No blend-weight or slow-threshold search is allowed.

## Preregistered gate versus e013

All conditions must pass:

1. at least 1% mean MSE improvement;
2. all 3 folds and all 3 horizons improve;
3. worst fold improves and fold standard deviation does not worsen;
4. at least 17/18 block-fold-horizon cells improve;
5. at least 34/36 temporal chunks improve;
6. median chunk gain is at least 0.25 MSE;
7. worst chunk gain is at least -0.25 MSE;
8. test-m2 correction versus ridge is nonpositive;
9. test RMS change versus e013 is at most 1.0 km/h;
10. predictions are finite, nonnegative, and zero-history guarded.

Failure means immediate `REJECT`, no retuning, no audit, no notebook, and no
Kaggle slot. E013 remains selected throughout.

## Result

E014 improves e013 broadly but fails the preregistered materiality gate:

- mean MSE `36.2602` versus e013 `36.5603`, a `0.82%` gain (required 1%);
- all 3 folds, all 3 horizons, and all 18/18 block-fold-horizon cells improve;
- 34/36 temporal chunks improve;
- median chunk gain is `0.2714` MSE and worst is `-0.1055`;
- worst fold improves `41.7515 -> 41.4014` and std falls `5.1609 -> 5.0737`;
- test-m2 correction remains nonpositive at `-0.1683` km/h;
- test RMS change versus e013 is only `0.2600` km/h;
- all 40,250 zero-history pairs remain guarded.

The 1% threshold is not relaxed after observing the result. No submission CSV,
audit request, or notebook is produced. E013 remains the final candidate.
