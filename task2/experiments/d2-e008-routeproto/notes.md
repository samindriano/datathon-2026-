# d2-e008-routeproto

Frozen supervised title-prototype route scorer. Fold-local TF-IDF is fit only
on training target titles; edge prototypes average vectors for each exact
current -> next route. Unseen currents use the training global mode.

Result: REJECT / DO NOT SUBMIT. Mean accuracy 0.282111 (folds
0.287222, 0.276111, 0.277778, 0.279444, 0.290000), below binding 0.290333
gate despite 5/5 fold wins. Worst fold 0.276111 passes; current-unseen
0.123539 and category-OOD 0.315200 pass; test distribution 432 unique,
top-share 0.275333 passes; validator READY; runtime 180.35s passes.
No state_id or held-out-label mutation effect. The failed mean gate is
binding; no retune, blend, fallback, or submission is permitted.

Comparator repair: RouteProto beats E002 on 0/5 folds (all five E002 reference scores exceed RouteProto). The runner's prior 5/5 wins were versus current-mode baseline, not E002. E002 was not refit; exact frozen E002 fold scores are recorded as references. RouteProto prediction and int64 hash remain unchanged (1578e5b9...).
