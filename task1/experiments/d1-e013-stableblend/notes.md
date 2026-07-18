# d1-e013-stableblend

Current status: `KEEP / NEEDS_REVIEW`.

## Hypothesis

E012 exposed a large globalstate gain but failed five temporal chunks. E010 is
the audited stable anchor. A single fixed conservative blend—75% e010 and 25%
globalstate—may retain meaningful gain while shrinking the unstable component.

No weight grid or follow-up weight is allowed.

## Preregistered gate

Every condition must pass:

1. at least 1% mean MSE improvement over e010;
2. all 3 folds and all 3 horizons improve;
3. worst fold improves and fold standard deviation does not worsen;
4. at least 17/18 block-fold-horizon cells improve;
5. at least 34/36 consecutive 120-origin chunks improve;
6. median chunk gain is at least 0.5 MSE;
7. worst chunk gain is at least -0.25 MSE;
8. test-m2 correction versus ridge is nonpositive;
9. predictions are finite, nonnegative, and zero-history guarded.

Passing authorizes independent audit and notebook preparation only. It does not
authorize slot 3 by itself. Failure means immediate rejection with no weight
retuning.

## Result

All preregistered gates pass:

- mean MSE `36.5603` versus e010 `37.9040` (`3.55%` improvement);
- folds `41.7515`, `38.4076`, `29.5217`; all improve e010;
- all 3 horizons and all 18/18 block-fold-horizon cells improve;
- all 36/36 temporal chunks improve;
- chunk gains range `0.1243` to `2.7564`, median `0.9969`;
- worst fold improves `43.4387 -> 41.7515` and standard deviation falls
  `5.5645 -> 5.1609`;
- test-m2 mean correction versus ridge is `-0.2285` km/h;
- all 40,250 zero-history pairs remain exactly zero;
- validator status is `READY` for 2,041,200 exact unique IDs;
- 44 tests pass.

Recommendation: independent VALIDATION audit. Slot 3 remains unauthorized until
the audit returns `GO/KEEP`, a final notebook reproduces the frozen CSV exactly,
and SUBMISSION returns `READY`.
