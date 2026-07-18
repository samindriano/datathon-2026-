# D1 E010 Public-to-Private Risk Audit

- Time: 2026-07-18 14:35 WIB
- Role: VALIDATION
- Candidate: `d1-e010-graphtextblend`
- Reference: `d1-e002-ridge`
- Public leaderboard fraction: approximately 30%; private fraction: approximately 70%

## Verdict

- Leakage and implementation: `GO`; no new issue found.
- Candidate evidence: `KEEP`.
- Final-selection recommendation: prefer `d1-e010-graphtextblend` over ridge.
- Confidence: moderately high that the blend also beats ridge on private, but
  this is not guaranteed because private labels and split composition remain
  unknown.

No additional Kaggle submission is justified by this audit alone.

## Public versus local evidence

| Comparison | Ridge | Blend | Blend gain |
|---|---:|---:|---:|
| Frozen local MSE | 39.024844 | 37.904035 | 1.120809 (2.872%) |
| Public MSE | 45.980 | 45.168 | 0.812 (1.766%) |

The public improvement retains 72.45% of the paired local improvement. This is
shrinkage, but it is directional confirmation rather than a collapse. Absolute
score calibration remains optimistic: the public-minus-local gap is 6.9552 for
ridge and 7.2640 for the blend.

## Paired temporal stability

The exact frozen models were refit on all six official block-fold windows and
compared per validation origin without changing folds or parameters.

- Weighted gain versus ridge by fold: `1.0480`, `1.0514`, `1.2630` MSE.
- Gain by m1 fold: `1.2993`, `1.2163`, `1.3600`.
- Gain by m2 fold: `0.4916`, `0.6862`, `1.0482`.
- The blend improves ridge in all `18/18` block-fold-horizon cells.
- It improves ridge in all `36/36` consecutive 120-origin chunks. Chunk gains
  range from `0.0762` to `2.3854`, with median `1.0914`.
- Per-origin win rates across the six block-fold windows range from `72.36%` to
  `89.58%`.
- A 10,000-repeat circular moving-block bootstrap with block length 30 origins
  gives a diagnostic 95% gain interval of `[0.9204, 1.3355]`; every repeat is
  positive.

The bootstrap quantifies robustness within the observed historical windows. It
must not be interpreted as a calibrated probability for the hidden private
split because test chronology and the leaderboard masking unit are unknown.

## Consistency interpretation

The blend is not uniformly more stable under every definition. Its raw
three-fold score standard deviation is `5.5645`, slightly above ridge's
`5.4669`. However, the paired improvement is highly consistent: every fold,
regime, horizon, and 120-origin time chunk improves versus ridge, and the worst
fold drops from `44.4867` to `43.4387`.

Therefore the defensible claim is that the blend has a consistent incremental
advantage over ridge, not that its absolute MSE varies less across periods.

## Private-score assessment

The most likely outcome is that the blend remains better than ridge on private:

1. the gain was preregistered and not fitted to the public score;
2. all official temporal cells improve against ridge;
3. both observed regimes improve, including the shifted m2 regime;
4. public data independently confirms the expected direction;
5. the private split is larger, so a broad stable signal should generally be
   less dominated by small-split noise.

If the unknown full-test gain equalled the local paired gain, the observed
public result would imply a private gain of about `1.2532` MSE. This is only a
scenario calculation, not a private-score prediction. Algebraically, private
would be worse than ridge only if the unknown full-test gain collapsed below
`0.2436` MSE, or below 21.73% of the local gain.

## Retained risks

- The public gain is smaller than local, so absolute validation calibration is
  still imperfect.
- The text z-guard is test-distribution-aware and activates on 144 of 168 test
  m2 samples, while local guard activation is concentrated in m2 fold 3.
- The graph component's gain is cross-road/global context rather than proven
  road-topology causality.
- Hidden private composition may contain dynamics absent from both train
  blocks; no audit can remove that uncertainty without private labels.

No model, notebook, validation fold, or submission artifact was changed.
