# D'Coast Phase 0.8 Entry Decision

- **CILEGON_AOI_BLOCKED**
- **TELUK_AWUR_AOI_BLOCKED**

The complete BIG-derived landward traces pass the frozen alignment gate:

- `cilegon-industrial-coast`: 320 samples at 100 m; minimum 0.00 m, mean 0.00 m, p95 0.00 m, maximum 0.00 m; BIG features `2424`.
- `teluk-awur-jepara`: 111 samples at 100 m; minimum 0.00 m, mean 0.00 m, p95 0.00 m, maximum 0.00 m; BIG features `40267;40268;40269;40270;40271;40272;40280;40281;40433;40434;40435;40436;40437;40438;40439;40440;40441;40442;40443;40444;40445;40446`.

These zero-distance results confirm conformance of the persisted full boundary
to the selected contributing BIG segments. They are not independent evidence
of shoreline accuracy, water coverage, or land exclusion.

Both compact polygons pass polygon validity, but neither passes land-overlap or
domain-review gates. Their descriptive scores cannot override those mandatory
fail-closed gates.

## Next-phase verdict

**GO_FOR_PHASE09_GEOMETRY_CHECK_ONLY**

This verdict allows only a separately approved, bounded land-overlap/water-mask
verification. Phase 0.9 has not been started here. Phase 1, model training, bulk
imagery download, source attribution, and operational claims remain blocked.
The Teluk Awur data-request draft remains unsent.
