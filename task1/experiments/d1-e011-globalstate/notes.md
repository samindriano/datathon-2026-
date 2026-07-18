# d1-e011-globalstate

Final status: `REJECT`.

## Hypothesis

The graph audit found that graphres gains came from generic cross-road context,
not uniquely from the true topology. Five direct citywide summaries of active
roads may represent that state more cleanly. The final candidate is a fixed
50:50 average of globalstate and the already frozen textzguard prediction.

Only the causal 15-step history determines active roads and city summaries.
Folds, ridge penalties, text guard, and blend weights remain frozen. There is
no leaderboard tuning.

## Preregistered acceptance gate

The experiment is `KEEP` only if every condition holds:

1. globalstate alone has lower mean MSE than graphres;
2. globalstate/textzguard improves e010 mean MSE by at least 0.5%;
3. it improves at least two of three aggregate folds versus e010;
4. it improves at least two of three horizons versus e010;
5. its worst fold is no worse than e010;
6. it beats both of its own components on mean MSE;
7. its test-m2 mean correction versus ridge is nonpositive.

Failure of any condition means `REJECT`, no submission artifact, no audit
request, and no Kaggle slot.

## Result

The fixed blend scores `35.7488`, but globalstate alone scores `35.3894`.
Therefore the blend fails condition 6 and e011 is rejected exactly as
preregistered. No submission CSV was created.

The globalstate diagnostic is nevertheless a distinct, strong discovery:

- e010: `37.9040`; globalstate: `35.3894` (`6.63%` lower MSE);
- all 3 aggregate folds and all 3 horizons improve versus e010;
- worst fold improves `43.4387 -> 40.0654`;
- fold standard deviation improves `5.5645 -> 4.3217`;
- test-m2 mean correction versus ridge is `-0.4117` km/h.

This does not retroactively make e011 `KEEP`. Globalstate-only must be treated
as a new, explicitly post-discovery hypothesis with stricter stress testing and
independent audit before any Kaggle slot is considered.
