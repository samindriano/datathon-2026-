# d2-e014-prelink

Verdict: `REJECT / DO NOT SUBMIT`.

E014 tested a materially different delivery architecture: precompute the
outgoing-link candidates from official screenshots once, store a compact model
artifact, and avoid OCR in final inference. Extraction and title mapping were
kept identical to rejected E013; no score or OCR threshold was retuned.

The frozen four-worker benchmark read 200/200 pages and accepted 4,866 mappings,
99.28% of them exact normalized official-title matches. It required 249.68
seconds and projected to 5,383.06 seconds (89.72 minutes) for the 4,312 unique
train/test current pages. That exceeds the preregistered 3,600-second precompute
maximum, so the experiment stopped before full extraction, full-fold scoring,
artifact construction, notebook work, or a Kaggle slot.

The human subsequently supplied a panitia clarification that all preprocessing
before modeling must execute end-to-end in the submitted notebook and may not
load externally preprocessed data. That independently closes E014's
artifact-first delivery architecture even if local precomputation had finished.

This does not invalidate the screenshot signal: the earlier fixed diagnostic
improved E002 by +0.0708 accuracy on 226 covered validation rows and won 5/5
diagnostic folds. It means the available OCR/runtime/reproducibility path is not
competition-ready before the deadline. E002 remains the only audited final.

After the competition decision was frozen, the human requested a local research
notebook so the full hypothesis could be tested without deadline pressure.
`task2/notebooks/d2-e014-prelink-local.ipynb` now provides resumable extraction,
the unchanged five-fold target-group comparison, a separate local CSV, and
fail-closed submission validation. This tooling does not revise the stored
`REJECT` verdict: E014 remains diagnostic until a complete run and independent
audit exist.

## Post-competition diagnostic result

The resumable notebook subsequently completed all 4,312 required current pages
using only official Task 2 screenshots. It mapped 101,300 outgoing-link rows,
with 99.25% coming from exact normalized title matches. The frozen target-group
validation improved from E002 accuracy 0.285333 to E014 accuracy 0.369556,
winning all 5 folds with a 0.358889 worst fold. The generated CSV passed the
fail-closed local validator and changed 31.55% of E002 predictions.

The human submitted this CSV only through Kaggle's post-deadline diagnostic
path. Kaggle displayed public accuracy 0.375 versus E002's official 0.321.
Because it was explicitly marked `after deadline`, this score is research
evidence rather than an official competition result. E002 remains the selected
official submission and E014 remains unaudited for final-use purposes.

The repository intentionally excludes the 4.1 GB official ZIP, extracted
screenshots, resumable checkpoint shards, compact link JSON, and generated CSV.
They are reproducible from the notebook and are ignored by Git.
