# d2-e003-routeknn

Status before scoring: `RUNNING`. Submission verdict: `DO NOT SUBMIT` until the
fixed gate and independent review are complete.

## Frozen hypothesis

States with the same current article and similar target metadata may share the
same next route even when the held-out target article ID is unseen. For an
unseen current, static title/category similarity selects one proxy current.

The model uses one neighbor only. Similarity is fixed at:

```text
2 * Jaccard(article categories) + 1 * Jaccard(title tokens)
```

No value of k, similarity weight, tokenizer, seed, or blend is searched after
scoring. Label-derived routes and frequencies are fit within each training
fold. Official article metadata is static and contains no target labels.

## Acceptance gate frozen before scoring

- mean accuracy gain at least `+0.015` over `d2-e001-baseline`;
- improve at least `4/5` folds over baseline;
- pooled seen-current accuracy gain at least `+0.010` over baseline;
- worst fold no more than `0.005` below baseline;
- entirely-unseen-target-category accuracy no more than `0.005` below baseline;
- target seen rate is zero and state-ID ablation is exact;
- full five-fold runtime under 600 seconds;
- output passes the fail-closed submission validator.

Passing this gate permits `KEEP`, not a Kaggle submission. Comparison and OOF
disagreement against E002 are diagnostics only and cannot change the gate.

## Result

Verdict: `REJECT / DO NOT SUBMIT`.

- mean accuracy `0.272556`, a `+0.011222` gain over baseline but below the
  frozen `+0.015` requirement;
- folds `0.277222`, `0.266111`, `0.271667`, `0.271667`, `0.276111`;
- improved all `5/5` folds over baseline and worst fold improved to `0.266111`;
- pooled seen-current accuracy improved `0.295710 -> 0.323199`;
- pooled unseen-current accuracy fell `0.123539 -> 0.069560` because the
  metadata proxy-current rule transferred poorly;
- mean accuracy was `0.012778` below E002 and won `0/5` folds against E002;
- output passed the validator and total runtime was about 25.1 seconds.

The failed mean-gain gate is binding. No k, fallback, similarity weight, or
blend was retuned after scoring. The CSV is retained locally for provenance
only and must not consume a Kaggle slot.
