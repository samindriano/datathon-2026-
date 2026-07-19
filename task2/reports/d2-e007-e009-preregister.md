# Task 2 parallel challengers E007-E009

Frozen before implementation or scoring on 2026-07-19. These candidates do
not overlap the separate scout's E004 pairwise ranker, E005 shortest-path
graph, or E006 screenshot/OCR scan.

All candidates branch from immutable E002 model commit `8365193`, use the
unchanged `d2-targetgroup-v1` folds, and reproduce E002 inside the same run.
No notebook, official validation, raw data, submission registry, or Kaggle
slot may be changed.

## Shared promotion gate against E002

Every check is binding:

- mean accuracy at least `0.290333` (`0.285333 + 0.005`);
- beat E002 on at least 4/5 folds;
- worst fold at least `0.273333`;
- pooled current-unseen accuracy at least `0.118539`;
- entirely-unseen-target-category accuracy at least `0.310200`;
- predictions exactly invariant to validation `state_id` and held-out-label
  mutation;
- test top-prediction share at most `0.3252` and at least 337 unique labels;
- candidate-specific runtime limit and fail-closed validator `READY`.

One failed check means `REJECT`. There is no grid search, fallback rescue,
blend, ensemble, or post-score retuning. Disagreement with E002 is diagnostic
only.

## d2-e007-catroute

Hypothesis: within one current article, the broad category of the unseen goal
changes which outgoing transition is most likely.

For each training fold, build exact-current edge counts and
`(current, target_broad_category, next)` counts. For a seen current and query
category `b`, score each observed next candidate with the fixed posterior:

```text
(n(current,b,next) + 5 * n(current,next)/n(current))
/ (n(current,b) + 5)
```

The prior strength is fixed at five equivalent observations. Missing category
falls back algebraically to the current-specific distribution. Ties use
current edge count, global next count, then smallest article ID. Unseen
currents use the fold-training global mode exactly as E002. Runtime limit:
180 seconds.

## d2-e008-routeproto

Hypothesis: titles of historical goals that used an edge form a supervised
semantic prototype for that `current -> next` route.

Fit a word TF-IDF vectorizer on training-fold target titles only, with fixed
word n-grams `(1,2)`, lowercase, `sublinear_tf=True`, `min_df=1`, and L2
normalization. For every exact-current observed next candidate, average and
L2-normalize the vectors of training targets whose label used that edge.
Choose the candidate with highest cosine similarity to the query target title.
Ties use current edge count, global next count, then smallest article ID.
Unseen currents use the fold-training global mode. Runtime limit: 300 seconds.

## d2-e009-nextproto

Hypothesis: a global next-label prototype can recover next articles never
observed for the exact current, exceeding E002's current-candidate coverage.

Create one state document from prefixed tokens for current title/categories
and target title/categories. Fit a word TF-IDF vectorizer on training-fold
state documents only with fixed n-grams `(1,2)`, lowercase,
`sublinear_tf=True`, `min_df=1`, and L2 normalization. Average and L2-normalize
documents per fold-training `next_article_id`; predict the globally observed
next label with maximum cosine similarity. Ties use global next count then
smallest article ID. No current-specific candidate restriction or ID feature
is used. Runtime limit: 600 seconds.

## Isolated ownership

- E007 agent: only `task2/src/catroute.py`, its runner/test, and
  `task2/experiments/d2-e007-catroute/` in branch `exp/d2-e007-catroute`.
- E008 agent: only `task2/src/routeproto.py`, its runner/test, and
  `task2/experiments/d2-e008-routeproto/` in branch `exp/d2-e008-routeproto`.
- E009 agent: only `task2/src/nextproto.py`, its runner/test, and
  `task2/experiments/d2-e009-nextproto/` in branch `exp/d2-e009-nextproto`.

Agents must not edit `coordination/TEAM_STATUS.md`; MAIN integrates only
immutable evidence after each agent finishes.
