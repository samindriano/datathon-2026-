# D'Coast Phase 0.8 Entry Decision

- **CILEGON_AOI_BLOCKED**
- **TELUK_AWUR_AOI_BLOCKED**

Both preferred compact candidates pass the endpoint-alignment calculation in
this redesign (0.00 m at both landward anchors), but neither passes the
mandatory land-overlap and domain-review gate.

## Interpretation

The Phase 0.7 failure was caused by provisional coastline references that did
not follow the reviewed BIG corridor. Phase 0.8 fixes that narrow geometry
problem by anchoring the candidates to exact BIG coordinates. It does not prove
that the full polygon is water-only, because BIG's source is a coastline line
layer rather than a land polygon or accepted water mask.

## Phase 1 decision

Phase 1 remains blocked. The next allowed task is a bounded Phase 0.9 check that
uses an accepted land polygon or reproducible Sentinel-2 water/land mask to
quantify land overlap for the preferred compact candidates. It must not train a
model or bulk-download imagery.

The Teluk Awur validation-data request remains unsent and is not required to run
this geometry-only next step. Quantitative calibration and evaluation remain
blocked until georeferenced validation data pass the frozen contract.
