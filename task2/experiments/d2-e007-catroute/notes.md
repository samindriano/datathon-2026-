# d2-e007-catroute

Frozen broad-category posterior for exact current-to-next transitions. The
candidate was scored against the unchanged target-group folds and reproduces
E002 in the same runner. No tuning, fallback rescue, blending, or submission
slot was used.

Result: **REJECT / DO NOT SUBMIT**. Mean accuracy 0.275111 (E002 0.285333),
0/5 fold wins, worst fold 0.268333. Current-unseen accuracy 0.123539 and
category-OOD accuracy 0.312000 pass their subset floors, but mean, fold-win,
and worst-fold gates fail. Test distribution has 503 unique predictions and
top share 0.266000. Validator status READY; runtime 41.85s.
