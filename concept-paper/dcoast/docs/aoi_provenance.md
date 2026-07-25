# D'Coast AOI v2 provenance

## Official reference

- Badan Informasi Geospasial (BIG), Peta Garis Pantai Skala 1:25.000,
  publication year 2022.
- Repository extracts: `data/big_coastline/`.
- CRS: EPSG:4326.

## Deterministic landward trace

- All BIG line segments are canonicalized to six decimal places.
- The landward edge is the shortest connected graph trace between reviewed
  anchors, not a straight endpoint chord.
- For coincident undirected BIG segments, prefer coastline type highest-tide, mean-sea-level, lowest-tide, indicative, then other; break remaining ties by the lowest OBJECTID.
- Every persisted source feature ID exists in the site extract and contributes
  at least one selected trace edge.

- `cilegon-industrial-coast`: BIG feature IDs `2424`; 320 samples at 100 m.
- `teluk-awur-jepara`: BIG feature IDs `40267;40268;40269;40270;40271;40272;40280;40281;40433;40434;40435;40436;40437;40438;40439;40440;40441;40442;40443;40444;40445;40446`; 111 samples at 100 m.

## Provisional offshore closure

- `compact` and `extended` place a fixed western meridian beyond the westernmost
  trace longitude.
- Fixed 0.0005-degree caps are added beyond the trace latitude extrema to avoid
  substituting a coastline chord.
- This derivation is provisional and does not prove land exclusion or official
  monitoring relevance.

## Versioning and limits

- Phase 0.6 and Phase 0.7 artifacts remain unchanged.
- Phase 0.8 candidates live only under `data/aoi_candidates_v2/`.
- No candidate is promoted to `data/aoi_locked/`.
- Any future lock must identify the source candidate, land/water verification,
  domain reviewer, and decision commit.
