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
