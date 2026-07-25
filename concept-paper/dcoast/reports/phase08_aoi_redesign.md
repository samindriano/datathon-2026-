# D'Coast Phase 0.8 AOI Redesign

Verdict: **CANDIDATES_REBUILT; AOI LOCK REMAINS BLOCKED**

## Method

The landward boundary is no longer a straight chord. For each site, the runner
builds an undirected graph from the bounded BIG extract and selects the
deterministic shortest connected trace between the reviewed north and south
anchors. Coincident segments use this frozen rule: For coincident undirected BIG segments, prefer coastline type highest-tide, mean-sea-level, lowest-tide, indicative, then other; break remaining ties by the lowest OBJECTID.

Every complete landward trace is sampled at a fixed
100 m interval. The frozen <=
1000 m gate applies to the maximum sampled distance, while
minimum, mean, p95, maximum, sample count, and interval are all persisted.
Because the boundary is constructed from the selected BIG segments, these
statistics are a full-boundary conformance check, not independent evidence of
shoreline accuracy or water coverage.

The offshore closure remains provisional: a western meridian is placed beyond
the westernmost point of the trace, with fixed north/south caps. This is not a
water mask, official monitoring boundary, industrial-estate boundary, port,
outfall, or jurisdiction boundary.

## Candidate comparison

| Site | Variant | Area km2 | BIG trace km | Samples | Min m | Mean m | P95 m | Max m | BIG feature IDs | Valid | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| cilegon-industrial-coast | compact | 115.920 | 31.831 | 320 | 0.00 | 0.00 | 0.00 | 0.00 | 2424 | 1 | 87 |
| cilegon-industrial-coast | extended | 145.214 | 31.831 | 320 | 0.00 | 0.00 | 0.00 | 0.00 | 2424 | 1 | 84 |
| teluk-awur-jepara | compact | 21.860 | 10.947 | 111 | 0.00 | 0.00 | 0.00 | 0.00 | 40267;40268;40269;40270;40271;40272;40280;40281;40433;40434;40435;40436;40437;40438;40439;40440;40441;40442;40443;40444;40445;40446 | 1 | 87 |
| teluk-awur-jepara | extended | 36.654 | 10.947 | 111 | 0.00 | 0.00 | 0.00 | 0.00 | 40267;40268;40269;40270;40271;40272;40280;40281;40433;40434;40435;40436;40437;40438;40439;40440;40441;40442;40443;40444;40445;40446 | 1 | 84 |

## Selection

- The compact candidate remains the preferred geometry within each site because
  it has the smaller provisional processing footprint.
- Cilegon remains no-go for the current optical pipeline under Phase 0.6; this
  geometry work does not reverse that decision.
- Teluk Awur remains a technical benchmark candidate and does not infer any
  published sampling-station coordinate.

## Why no AOI is locked

`polygon_validity_score` covers only closure, non-zero area, and absence of
self-intersection. It does not prove water coverage or land exclusion. The
official BIG source is a coastline line layer, not an accepted land polygon or
water mask, and domain review remains absent. Mandatory gates set
`lock_eligible=0` regardless of the descriptive total score.
