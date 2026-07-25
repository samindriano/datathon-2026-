# D'Coast Phase 0.8 AOI Redesign

Verdict: **CANDIDATES_CREATED; AOI LOCK REMAINS BLOCKED**

## Method

Four water-side candidates were created from BIG coastline anchor points already
identified in Phase 0.7. The candidate polygons extend westward from those
anchors by approximately two kilometres (compact) or four kilometres
(extended). Existing Phase 0.7 AOIs were preserved unchanged.

The endpoint alignment gate remains frozen at <= 1,000 metres. The score is
descriptive and cannot override a failed mandatory gate.

## Candidate comparison

| Site | Variant | Area km2 | Max endpoint distance m | Score / 100 | Land-overlap status |
|---|---:|---:|---:|---:|---|
| cilegon-industrial-coast | compact | 29.071 | 0.00 | 87 | UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK |
| cilegon-industrial-coast | extended | 58.142 | 0.00 | 84 | UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK |
| teluk-awur-jepara | compact | 14.480 | 0.00 | 87 | UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK |
| teluk-awur-jepara | extended | 28.960 | 0.00 | 84 | UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK |

## Selection

- Cilegon compact is the preferred Cilegon geometry candidate because it has the
  smaller processing footprint. It is **not locked**.
- Teluk Awur compact is the preferred benchmark geometry candidate because it
  covers the published study corridor with a smaller processing footprint. It
  is **not locked** and does not infer station coordinates.

## Boundary provenance

The landward endpoints are exact BIG coastline coordinates from the bounded
Phase 0.7 extracts. The offshore edge is a derived fixed westward translation.
No candidate is labelled as an official industrial-estate, port, jurisdiction,
outfall, or published-sampling boundary.

For Teluk Awur, the 2024 paper's labelled map envelope is used only as supporting
context. It is not treated as a water-only AOI and no station coordinate is
inferred from the figure.

## Why no AOI is locked

The official BIG source used here is a coastline line layer, not a land polygon
or validated water mask. Endpoint alignment therefore cannot establish that the
entire straight landward chord and polygon are free of land, port structures,
islands, or unsuitable shallow-bottom areas. Domain review is also absent.

Creating `data/aoi_locked/` would overstate the available evidence. The next
bounded step is a land-overlap and water-mask verification of the preferred
compact candidates, followed by human/domain review. This remains Phase 0;
model training and bulk imagery download remain prohibited.
