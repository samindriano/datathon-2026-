# d2-e013-fastlink

Verdict: `REJECT / DO NOT SUBMIT`.

This was a separately frozen runtime architecture, not a score retune. It
replaced the OCR detector with deterministic connected components from known
blue pixels and called the recognizer directly in batches of 64. On the exact
same 100-page sample, recall remained above the 85% gate (87.63%) and exact
mapping share remained above 97% (98.99%).

Runtime fell from 177.88 to 82.41 seconds, but the 4,604-page projection was
still 3,794.35 seconds, over three times the 1,200-second maximum. Kaggle
dependency/model packaging was also not independently closed. Per the stop
rule, no batch-size, morphology, GPU, or threshold rescue was attempted; no
full graph or submission was produced.

The raw diagnostic was intentionally left untracked after its stable summary
and SHA-256 were recorded in `metrics.json`.
