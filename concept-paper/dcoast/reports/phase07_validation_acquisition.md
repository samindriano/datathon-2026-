# D'Coast Phase 0.7 Validation-Acquisition Review

Verdict: **READY_TO_REQUEST_DATA; PHASE 1 REMAINS BLOCKED**

## What the published studies establish

The open 2024 Teluk Awur study reports a spatial campaign on 22 July 2023
covering 110 in-situ stations and provides a map with an approximate graticule.
That map supports a study-area envelope for source review, but it is not a
station-coordinate table and must not be digitized into invented observations.

The paper also contains count differences that require clarification from the
original data: 110 in-situ stations versus 112 reflectance samples, and 54
in-situ observations versus 55 predicted observations in the validation
summary. The 2025 follow-up reports 112 samples divided equally between tuning
and validation and states that supporting data are available from the
corresponding author upon reasonable request.

## Artifacts prepared

- `data/reference_extents/teluk_awur_published_study_extent.geojson` records
  only the approximate published map envelope and sampling date.
- `docs/teluk_awur_validation_data_contract.md` freezes the minimum row-level
  schema, provenance, quality controls, permissions, and acceptance gates.
- `docs/teluk_awur_data_request_draft.md` is a reviewable message addressed to
  the publicly listed corresponding author. It remains unsent.

## Decision boundary

The requested table can support a technical spatial-reproduction benchmark if
it passes the frozen contract. It cannot by itself validate operational
monitoring through time because the reported campaign represents one date.
Operational claims require at least three independent acquisition dates and a
preregistered date-held-out evaluation.

The provisional Teluk Awur monitoring AOI also fails the separate official
coastline-alignment screen. The published study envelope is therefore retained
only as reference evidence; it does not replace, snap, or authorize a new
monitoring AOI.

## Required human decisions

1. Review and explicitly authorize sending the draft data request.
2. Decide whether a new Teluk Awur monitoring AOI may be designed in a separate
   preregistered step using official coastline evidence and domain review.
3. Do not begin model training until the received data pass the technical
   benchmark contract.

## Sources

- Sabila et al. (2024), DOI:
  `https://doi.org/10.14710/ik.ijms.29.4.495-502`
- Sabila et al. (2025), DOI:
  `https://doi.org/10.1002/tqem.70154`
- BIG Peta Garis Pantai Skala 1:25.000:
  `https://geoservices.big.go.id/rbi/rest/services/GARISPANTAI/GarisPantai_25K/MapServer/0`
