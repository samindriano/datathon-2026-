# Teluk Awur Validation Data Contract

Status: **required before quantitative Phase 1 modeling**

This contract separates a reproducible technical benchmark from an operational
coastal-monitoring claim. Receiving a table does not itself authorize Phase 1.

## Minimum row-level fields

| Field | Required form | Why it is needed |
|---|---|---|
| `sample_id` | stable unique identifier | Traceability and duplicate checks |
| `latitude`, `longitude` | decimal degrees plus stated CRS | Spatial match to Sentinel-2 pixels |
| `sampling_datetime` | date, local time, and timezone | Temporal match to satellite acquisition |
| `tss_mg_l` | finite numeric value in mg/L | Direct optical-proxy target |
| `sampling_depth_m` | numeric or documented constant | Surface-water comparability |
| `laboratory_method` | gravimetric protocol and filter details | Measurement provenance |
| `sentinel_product_id` | exact product/granule where available | Reproducible imagery linkage |
| `b2` through `b8` | BOA reflectance or documented scale factor | Published algorithm reproduction |
| `quality_flag` | retained/excluded plus reason | Fail-closed quality control |
| `study_split` | tuning/validation assignment if published | Reproduce reported metrics |

Requested metadata:

- sampling team and instrument/laboratory provenance;
- coordinate collection method and expected accuracy;
- atmospheric correction and SNAP processing settings;
- pixel extraction/resampling method and spatial window;
- cloud, glint, land-adjacency, and shallow-bottom exclusions;
- permission, licence, citation, and redistribution limits.

## Frozen acceptance gates

### Technical benchmark gate

- At least 100 uniquely georeferenced, dated rows from the reported campaign.
- At least 90% of rows complete for coordinates, TSS, sampling time, and the
  reflectance variable used by the published model.
- Coordinates fall within the published map extent and no station coordinate
  is inferred solely from a figure.
- Units, scale factors, exclusions, and tuning/validation membership are
  unambiguous.
- Written permission covers internal reproduction and clearly states whether
  derived results may be published.
- Reported baseline can be reproduced within reasonable rounding tolerance
  before any new model is tried.

### Operational-validation gate

A single 22 July 2023 spatial campaign is insufficient for temporal monitoring.
Operational claims additionally require at least three independent acquisition
dates spanning materially different conditions, with a preregistered
date-held-out evaluation. Until then, results must be labelled a technical
spatial benchmark only.

## Known discrepancies to clarify

- The open 2024 paper reports 110 in-situ stations but 112 reflectance samples.
- Its validation table reports 54 in-situ observations versus 55 predicted
  observations for B4/B5.
- The 2025 paper describes 112 samples split equally for tuning and validation.

These may be legitimate filtering or extraction differences, but they must be
resolved from the original table rather than guessed.
