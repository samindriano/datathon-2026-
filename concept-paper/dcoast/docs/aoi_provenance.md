# D'Coast AOI v2 provenance

## Official reference

- Badan Informasi Geospasial (BIG), Peta Garis Pantai Skala 1:25.000,
  publication year 2022.
- Repository extracts: `data/big_coastline/`.
- CRS: EPSG:4326.

## Derived operations

- Phase 0.7 nearest-coastline anchor points were retained exactly.
- Candidate water strips were constructed by translating the two anchor points
  westward by a fixed longitude offset.
- `compact` uses an approximately two-kilometre-class offshore width.
- `extended` uses an approximately four-kilometre-class offshore width.

## Assumptions and limits

- West is treated as the seaward direction for both reviewed corridors.
- The BIG layer is a line reference, not an official monitoring jurisdiction,
  industrial-estate boundary, land polygon, outfall inventory, or water mask.
- The Teluk Awur published extent is reference evidence only. No sample station
  coordinate was inferred from the paper figure.
- No candidate is promoted to `data/aoi_locked/` until land overlap is verified
  and domain review is recorded.

## Versioning

- Phase 0.7 AOIs remain historical artifacts under `data/aoi_candidates/`.
- Phase 0.8 candidates are stored separately under `data/aoi_candidates_v2/`.
- Any future locked AOI must identify the exact source candidate, land/water
  verification method, reviewer, and decision commit.
