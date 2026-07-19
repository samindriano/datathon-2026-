# d2-e001-baseline

Status after scoring: `KEEP` as the stable end-to-end floor. Submission verdict:
`DO NOT SUBMIT`; this baseline is for comparison and format verification, not a
competitive use of a Kaggle slot.

## Hypothesis

Test targets are entirely unseen, while most test current articles occur in
train. The cheapest transferable baseline is therefore the most frequent
observed next click per current article, with the global next-click mode as the
fallback for unseen current articles.

## Validation

Five fixed folds hold out whole `target_article_id` groups. Broad target
categories are balanced deterministically across folds. No target-derived
statistics may be fitted outside the training side of a fold.

Random row validation is prohibited because it does not reproduce the fully
target-disjoint train/test structure.

## Baseline gate

- target groups are disjoint in every fold;
- current-mode mean accuracy exceeds global-mode accuracy;
- current-mode mean accuracy exceeds the sample current-article prediction;
- generated submission passes the fail-closed schema validator.

Passing establishes an end-to-end baseline only. It does not authorize a
Kaggle submission slot.

## Result

- current-mode mean accuracy: `0.261333`;
- fold accuracy: `0.267778`, `0.255556`, `0.265556`, `0.255000`, `0.262778`;
- worst fold: `0.255000`;
- fold standard deviation: `0.005195`;
- observed training-candidate coverage in validation: `0.298333` to `0.310000`;
- test current seen rate: `0.874167`;
- runtime: about 4.1 seconds;
- submission validator: `READY`.

All baseline gates passed. The low candidate coverage shows why the next model
must use target semantics or recover outgoing links rather than merely retune
the current-mode prior.

## Reproducibility

- fail-closed validator handoff `be28757` was integrated;
- 12 validator regression tests and 3 baseline/validation tests pass;
- the clean local notebook smoke run produces 6,000 rows and SHA-256
  `20e629735bb22da17e46c707d0a7ffb0560c00db3c9703b385c22d7503b70b96`;
- notebook output exactly matches the runner artifact under reference
  validation;
- actual Kaggle `Restart Session -> Run All` remains for a later competitive
  candidate, because this diagnostic baseline must not consume a slot.
