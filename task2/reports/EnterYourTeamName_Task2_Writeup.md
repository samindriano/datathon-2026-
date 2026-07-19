# Enter Your Team Name
## Task 2 - Wiki Article Next Click Prediction

> Final method: deterministic target-aware reranking of observed next-click candidates using official article titles and categories. No screenshot OCR, external data, pretrained weights, or model API is used.

### 1. Problem and data

Each row describes a navigator's current Wikipedia article and target article. The task is to predict the exact article clicked next, so the official metric is accuracy. The official data contains 9,000 labeled training states, 6,000 test states, 4,604 article titles, and 129 categories. Train has 360 unique target articles and test has 240, with zero target-ID overlap.

This zero-overlap structure is the key modeling constraint: validation must measure generalization toward unseen goals, rather than memorization of target IDs. We use only the official `states`, `articles`, and `categories` tables. Screenshots are not needed by the final method.

### 2. Validation

We freeze `d2-targetgroup-v1`: five deterministic, category-balanced folds grouped by `target_article_id` with seed 20260719. Each fold holds out 72 complete target groups and 1,800 rows, and every held-out target is absent from its training fold. Accuracy is reported for every fold, together with the mean, worst fold, current-seen/current-unseen subsets, unseen-target-category rows, prediction distribution, and runtime.

All label-derived candidate sets and transition frequencies are rebuilt from the training side of each fold. Article titles and categories are static official metadata available at test time. Mutation checks confirm that changing validation `state_id` or `next_article_id` does not change predictions.

### 3. Final model: d2-e002-metarank

For a seen current article, the candidate set contains only next articles observed for that current article in the training fold. Each candidate is compared with the target using two fixed similarities:

`score = 2 * Jaccard(candidate categories, target categories) + Jaccard(candidate title tokens, target title tokens)`

Titles are tokenized into lowercase ASCII-alphanumeric sets. The fixed 2:1 weights were preregistered and were not grid-searched. Ties are broken by current-specific transition frequency, global next-click frequency, and then smaller article ID. If the current article was never seen in training, the model returns the deterministic global next-click mode from the training fold.

This design is deliberately small and auditable. It adds goal awareness to the strong current-specific frequency baseline while keeping inference deterministic and dependency-light.

### 4. Results

| Model | Mean accuracy | Worst fold | Fold standard deviation |
| --- | ---: | ---: | ---: |
| Current-specific mode baseline | 0.261333 | 0.255000 | 0.005195 |
| Final MetaRank | 0.285333 | 0.278333 | 0.006142 |

The absolute local gain is +0.024000 accuracy. MetaRank improves all five folds: 0.290556, 0.282778, 0.278333, 0.280556, and 0.294444. The smallest fold gain is +0.012778, so the improvement is not concentrated in one split. Accuracy on 1,797 current-unseen rows remains unchanged at 0.123539. On 625 rows whose target categories are entirely unseen in the training fold, accuracy improves from 0.280000 to 0.315200.

The final test prediction has 449 unique article IDs and a top-prediction share of 0.275167, avoiding a single-label collapse. The first Kaggle submission scored 0.321 public accuracy. Because the public leaderboard covers only 30% of test rows, this score is treated as diagnostic; model selection is based primarily on the frozen local validation and independent audits.

<!-- pagebreak -->

### 5. Leakage control and reproducibility

- Five target-disjoint folds reproduce exactly from their stored target hashes.
- Candidate sets and frequency tie-breaks are fit only on each training fold.
- Validation labels and state IDs are never model inputs.
- Predictions for seen currents always belong to the corresponding training-fold candidate set.
- No external data, network call, credential, pretrained weight, or external API is used.
- Independent review reproduced the stored metrics and submission exactly; all 10 frozen acceptance gates passed.
- The final notebook passes 14 portability/submission tests and an isolated clean-session smoke run.

The clean inference notebook is `EnterYourTeamName_Task2_Notebook.ipynb`. It locates the official Task 2 data either under Kaggle input or through a local relative path, then writes exactly 6,000 rows with columns `state_id,predicted_next_article_id`. The canonical prediction-array SHA-256 is `292bb1567ac81cd70b87b1f4730468830640388919b72126aef69f198e9d1ba0`. Recorded full inference runtime is about 12 seconds on the local environment.

### 6. Candidate selection

All challengers used the same frozen validation. Route retrieval and graph-style prototypes improved the simple baseline in some diagnostics but did not beat MetaRank consistently.

| Candidate | Mean accuracy | Wins vs. MetaRank | Decision |
| --- | ---: | ---: | --- |
| `d2-e002-metarank` | 0.285333 | anchor | KEEP |
| `d2-e003-routeknn` | 0.272556 | 0/5 | REJECT |
| `d2-e007-catroute` | 0.275111 | 0/5 | REJECT |
| `d2-e008-routeproto` | 0.282111 | 0/5 | REJECT |
| `d2-e009-nextproto` | 0.042667 | 0/5 | REJECT |
| `d2-e010-treerank` | 0.255556 | 0/5 | REJECT |

No rejected candidate was rescued by post-hoc threshold, seed, or public-leaderboard tuning.

### 7. Limitations

Observed transition candidates cover only about 30.5% of held-out next clicks, and unseen current articles fall back to a global mode. Screenshot-derived outgoing links could expand candidate coverage, but OCR dependency, model-weight provenance, and Kaggle reproducibility were not sufficiently verified before the deadline. We therefore prefer the smaller audited model over a higher-risk pipeline that could not be reproduced cleanly.

### Final selection

`d2-e002-metarank` is selected because it improves every validation fold, improves the worst fold and category-OOD subset, reproduces exactly, and runs safely in the required Kaggle environment.
