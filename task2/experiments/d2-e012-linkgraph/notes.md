# d2-e012-linkgraph

Verdict: `REJECT / DO NOT SUBMIT`.

The hypothesis is supported but the implementation fails the frozen feasibility
gate. On 100 deterministic training-current pages, blue-only OCR recovered
168/186 unique observed next edges (90.32%). Of 2,887 accepted mappings, 99.06%
were exact normalized official-title matches. A leakage-safe, target-group-fold
diagnostic on the 226 validation rows covered by those pages improved E002 from
0.3053 to 0.3761 and won all five diagnostic folds.

Those positive numbers are not sufficient for promotion. OCR took 177.88
seconds for 100 pages, projecting to 8,189.74 seconds for all 4,604 pages versus
the preregistered 1,200-second maximum. RapidOCR/PaddleOCR model provenance is
open, but the exact dependency/model bundle was not made available and
reproduced in Kaggle. Both are hard failures. No full graph, submission, weight
grid, threshold rescue, or Kaggle slot was run.

The raw 781 KB diagnostic was intentionally left untracked after its stable
summary and SHA-256 were recorded in `metrics.json`.
