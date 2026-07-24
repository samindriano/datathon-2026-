# D'Coast Phase 0.5 Site-Lock Decision

> Historical Phase 0.5 decision. The Phase 1 gate is superseded by
> `phase06_clear_water_assessment.md`, which closes Cilegon as no-go for the
> current optical pipeline.

Decision date: 24 July 2026  
Final verdict: **CONDITIONAL_GO_CILEGON**  
Technical benchmark: **Teluk Awur remains confirmed**

## Decision

Cilegon is locked as the intended operational pilot for planning and targeted
access work. It is not cleared for Phase 1 imagery acquisition, preprocessing,
or model training.

Teluk Awur remains the separate technical benchmark because the published work
directly relates Sentinel-2 reflectance to in-situ TSS. It does not replace
Cilegon as the industrial operational pilot.

## Frozen gate assessment

| Cilegon gate | Required | Evidence | Result |
|---|---|---|---|
| Median usable observations at 70% clear water | at least 1/month | CDSE OAuth unavailable; no scene-cloud substitution | UNKNOWN / BLOCKED |
| Full-year usable observations at 70% | average at least 18/year | Same blocker | UNKNOWN / BLOCKED |
| Longest usable-observation gap | at most 60 days | Catalogue acquisition gap is 10 days, but usable-water gap is unknown | UNKNOWN / BLOCKED |
| Manageable water AOI | bounded water-side geometry | 84.170 km2, approx. 20.714 km coast reference; land excluded | PASS, PROVISIONAL |
| Validation or expert-review path | georeferenced source or secured review | Five-station publication and author-contact route exist; precise coordinates/data permission and reviewer are not secured | CONDITIONAL |
| Critical unresolved blocker | none | OAuth and georeferenced validation remain material | FAIL FOR PHASE 1 |

Because three optical gates cannot be measured and the validation path is not
yet secured, a full `GO_CILEGON` would overstate the evidence. The appropriate
decision is `CONDITIONAL_GO_CILEGON`.

## AOI lock

- Operational file: `data/aoi_candidates/cilegon.geojson`
- Benchmark file: `data/aoi_candidates/teluk_awur.geojson`
- Both are water-side screening polygons with explicit provisional status.
- Land is excluded from the monitoring geometry.
- Waterfront, river-mouth, port, and offshore-control roles are descriptive
  screening segments, not legal boundaries, confirmed outfalls, or source
  attribution.
- Both must be reviewed against BIG coastline data before operational use.

## Exact conditions to upgrade to GO

1. Configure local CDSE OAuth without committing credentials.
2. Produce per-acquisition valid, clear, cloud/shadow, and no-data statistics
   for 2021-2025 and 2026 partial.
3. Pass all three Cilegon 70% clear-water gates above and review the 50/70/80
   sensitivity plus seasonal rejection pattern.
4. Obtain reusable georeferenced Cilegon observations or a documented,
   committed expert-review arrangement.
5. Confirm the water polygon against BIG coastline and an appropriate official
   monitoring/jurisdiction source.
6. Obtain human approval before Phase 1.

## Stop rule

Phase 0.5 ends here. Do not bulk-download imagery, train a model, implement the
dashboard, infer pollution, or create station coordinates from the
supplementary map.
