# D'Coast Phase 0 - Pilot-Site Feasibility Study

Date of assessment: 24 July 2026  
Satellite inventory period: 1 January 2021-31 December 2025, plus
1 January-24 July 2026 as a partial year  
Decision status: conditional recommendation; no pilot is approved for Phase 1
until the human owner accepts it

## Executive summary

This feasibility study compares four Indonesian coastal areas without training
a model or downloading a multi-year image archive.

**Recommended operational pilot: Cilegon industrial coast.** It offers the best
current balance of industrial relevance, a manageable 18.4 km screening strip,
regular Sentinel-2 acquisition cadence, and a peer-reviewed 2022 seawater study
that can become a validation lead. The recommendation is conditional: the
proposed polygon is provisional, AOI-level clear-water statistics still need
CDSE OAuth access, and the study's station coordinates/raw results must be
obtained or independently replaced.

**Recommended technical benchmark: Teluk Awur, Jepara.** A peer-reviewed 2025
study reports 112 in-situ samples paired with Sentinel-2 for TSS work. This is
the strongest available basis for testing atmospheric/water preprocessing,
proxy extraction, and validation logic. Teluk Awur is not selected as the
operational industrial pilot because its industrial-monitoring relevance is
much weaker.

**Morowali remains the highest-need candidate, not the best first MVP site.**
The official KLH/BPLH inspection establishes strong operational relevance, but
the current feasibility evidence is weaker on optical quality, boundary
clarity, reusable coastal measurements, and processing simplicity. It should
be reconsidered after an official monitoring boundary and validation
partnership are available.

Nusa Lembongan is retained only as an additional optical benchmark. It is not
an industrial pilot candidate.

The total scores are decision aids, not measurements of pollution, model
accuracy, or expected business impact.

## Scope and product boundary

D'Coast screens unusual coastal-water change, ranks areas for inspection, and
proposes initial sampling roles for human review. An optical anomaly is not a
pollution finding. This study does not identify a responsible company, infer an
outfall, or trace a plume to a source.

No model was trained. No raw Sentinel-2 image archive, industrial boundary,
discharge point, or field measurement was invented or adopted without
provenance.

## Methodology

### Candidate freeze

The following set was fixed before scoring:

1. Morowali industrial coast near the IMIP context - operational candidate.
2. Cilegon industrial coast - evidence-based industrial alternative.
3. Teluk Awur, Jepara - primary technical TSS benchmark.
4. Nusa Lembongan - additional optical benchmark only.

### AOI construction

Each GeoJSON is a small provisional screening polygon rather than an
administrative, estate, permit, or discharge boundary. Areas use a local
equirectangular approximation; coastline lengths use a haversine distance
between documented provisional endpoints. These are suitable for Phase 0 cost
and catalogue screening, not legal or field navigation.

| Site | Approx. area | Approx. coastline | Boundary status | Reason |
|---|---:|---:|---|---|
| Morowali IMIP context | 81.802 km2 | 16.574 km | Provisional/derived | Covers a compact Bahodopi industrial waterfront context without claiming the IMIP estate or an outfall. |
| Cilegon industrial coast | 83.616 km2 | 18.443 km | Provisional/derived | Covers a manageable industrial coastal strip facing the Sunda Strait. |
| Teluk Awur, Jepara | 77.118 km2 | 16.397 km | Provisional/derived | Provides a nearshore test area around the published TSS setting without claiming the paper's exact study polygon. |
| Nusa Lembongan | 92.893 km2 | 7.190 km | Provisional/derived | Compact island-water optical benchmark; the coastline reference is shorter than the normal 10 km guideline and is explicitly treated as an exception. |

Polygon rings, in longitude/latitude order:

- Morowali:
  `[[122.130,-2.758],[122.202,-2.908],[122.238,-2.891],[122.166,-2.741],[122.130,-2.758]]`
- Cilegon:
  `[[105.978,-5.910],[105.950,-6.095],[105.986,-6.100],[106.014,-5.915],[105.978,-5.910]]`
- Teluk Awur:
  `[[110.625,-6.535],[110.596,-6.700],[110.633,-6.706],[110.662,-6.541],[110.625,-6.535]]`
- Nusa Lembongan:
  `[[115.410,-8.640],[115.505,-8.640],[115.505,-8.720],[115.410,-8.720],[115.410,-8.640]]`

The Morowali context is anchored by the Ministry of Transportation's official
IMIP Airport location in Fatufia, Bahodopi. That point is a location reference,
not an industrial or monitoring boundary.

Before Phase 1, the selected polygon must be reviewed against BIG's 1:25,000
coastline and any public official jurisdiction/estate boundary. BIG describes
its 2022 product as containing both definitive and indicative coastline
segments, so that status must be preserved rather than flattened.

### Sentinel-2 inventory

The public Copernicus Data Space OData catalogue was queried for `S2MSI2A`
products intersecting each polygon. Products sharing the same acquisition
timestamp were collapsed into one observation so that overlapping tiles are
not counted as independent dates. Both L1C and L2A are available in CDSE; L2A
is the Phase 0 and prospective MVP default because it supplies surface
reflectance and Scene Classification (SCL).

The STAC endpoint was attempted first but repeatedly returned HTTP 500/504 for
long requests. The official OData catalogue was used as the reproducible
fallback. Only JSON metadata was downloaded.

Scene-level `cloudCover` is reported as a diagnostic proxy. It is not a
measurement of clear water inside the AOI.

### AOI clear-water method and blocker

The reproducible clear-water script uses the CDSE Statistical API, Sentinel-2
L2A SCL class 6 (water), a 60 m diagnostic grid, and daily least-cloud mosaics.
It is designed to calculate the clear-water fraction in the actual polygon and
support 50%, 70%, and 80% sensitivity counts.

The API requires an OAuth client. No `CDSE_CLIENT_ID` or
`CDSE_CLIENT_SECRET` was available in the environment. Consequently:

- the AOI clear-water fraction is unavailable;
- usable observations at 50%, 70%, and 80% are unavailable;
- usable observations per month/year and the longest usable gap are
  unavailable;
- rejection percentage by AOI quality screening is unavailable.

These fields are empty in `sentinel2_monthly_availability.csv` and carry
`BLOCKED_NO_CDSE_OAUTH`. Whole-tile cloud metadata is not substituted.

The initial threshold remains **70% clear water**, subject to the required
50/70/80 sensitivity run. It balances spatial confidence against tropical
cloud scarcity, but it is not frozen for Phase 1 until real AOI statistics are
reviewed.

## Candidate descriptions and evidence

### Cilegon industrial coast

Why it is credible:

- Cilegon is a major industrial and port coast with direct operational
  relevance.
- A peer-reviewed 2026 article reports February 2022 surface seawater
  sampling, in-situ temperature/salinity/pH, and Cd/Cu/Pb measurement in an ISO
  17025:2017 accredited laboratory.
- The study is licensed CC BY 4.0 and gives a concrete route to contact authors
  for station coordinates or reusable records.
- The provisional strip intersects only about two Sentinel tiles per
  acquisition, making it simpler than Morowali's four-tile intersection.

Important limitations:

- Heavy metals are not directly observable from Sentinel-2 reflectance.
- The publication is a contextual/validation lead, not automatic labels for
  every satellite observation.
- Station coordinates and a reusable data table were not adopted in this
  assessment.
- The industrial/jurisdiction boundary remains provisional.

### Teluk Awur, Jepara

Why it is the strongest benchmark:

- A peer-reviewed 2025 study explicitly connects Sentinel-2 reflectance and
  in-situ TSS.
- It reports 112 samples, with half used for algorithm tuning and half for
  validation.
- The setting is directly relevant to testing coastal optical preprocessing,
  TSS proxy extraction, seasonal baselines, and false positives related to
  river sediment.
- It has the strongest scene-cloud diagnostic among the two Java candidates.

Important limitations:

- Published results do not by themselves grant access to the georeferenced
  sample table.
- The study's pollution-index terminology must not be copied into D'Coast as an
  automated verdict.
- Teluk Awur has low relevance as an industrial operational pilot.

### Morowali industrial coast near IMIP

Why it remains strategically important:

- KLH/BPLH's 17 June 2025 release documents direct environmental supervision
  and serious compliance findings in the IMIP industrial area.
- The Ministry of Transportation lists IMIP Airport in Fatufia, Bahodopi at
  02 48 05 S, 122 08 28 E, giving a reproducible official geographic anchor.
- Industrial monitoring relevance is the highest of all candidates.

Why it is not recommended first:

- Only 94 of 423 acquisitions have median whole-scene cloud cover at or below
  50%; just 16 are at or below 20%. These are imperfect proxies, but they flag
  material optical risk.
- The polygon intersects four products per typical acquisition, increasing
  mosaicking complexity.
- No official coastal monitoring boundary or reusable spatially aligned
  in-situ dataset was found and adopted.
- The official inspection evidence establishes need, not a satellite
  validation set.

### Nusa Lembongan

Why it remains useful:

- A 2025 study used Sentinel-2A/B L1C and the C2RCC processor to examine
  chlorophyll-a seasonality in Nusa Lembongan waters.
- Scene-level optical conditions are comparatively favorable.
- It can test water preprocessing in reef, mangrove, and seaweed-cultivation
  contexts.

Why it is not the operational pilot:

- It does not represent the industrial coastal monitoring problem.
- The current compact coastline reference is only 7.2 km.
- The cited study is method evidence, not yet a reusable validation dataset.

## Sentinel-2 availability results

### Acquisition cadence

| Site | 2021-2025 observations | 2026 partial | Median observations/calendar month | Longest acquisition gap | AOI clear-water status |
|---|---:|---:|---:|---:|---|
| Cilegon | 380 | 47 | 6 | 10 days | Blocked: OAuth required |
| Teluk Awur | 380 | 51 | 6 | 10 days | Blocked: OAuth required |
| Morowali | 376 | 47 | 6 | 10 days | Blocked: OAuth required |
| Nusa Lembongan | 376 | 47 | 6 | 10 days | Blocked: OAuth required |

The catalogue cadence is adequate at all four sites. Cadence is not the
bottleneck; tropical clouds and valid water pixels are.

### Yearly observation counts

| Site | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 partial |
|---|---:|---:|---:|---:|---:|---:|
| Cilegon | 73 | 72 | 72 | 77 | 86 | 47 |
| Teluk Awur | 73 | 73 | 73 | 76 | 85 | 51 |
| Morowali | 73 | 73 | 71 | 75 | 84 | 47 |
| Nusa Lembongan | 73 | 72 | 72 | 74 | 85 | 47 |

### Scene-cloud diagnostic

| Site | Scene cloud <=20% | Scene cloud <=50% | Share <=50% | Indicative poorer season |
|---|---:|---:|---:|---|
| Cilegon | 57 | 144 | 33.7% | Approximately November-March |
| Teluk Awur | 109 | 196 | 45.5% | Approximately November-February |
| Morowali | 16 | 94 | 22.2% | Broad risk; weakest in January-February and December in this proxy |
| Nusa Lembongan | 108 | 238 | 56.3% | Relatively weaker December-February |

These figures use median cloud cover of intersecting full scenes. They support
relative risk screening only. They must not be called usable-water counts.

Monthly source rows, including zero/poor months and the 2026 partial-year flag,
are in `sentinel2_monthly_availability.csv`.

## Validation-source assessment

| Site | Available evidence | Current usefulness | Missing before validation |
|---|---|---|---|
| Cilegon | Peer-reviewed February 2022 surface seawater sampling; accredited laboratory; in-situ supporting parameters | Strong lead for contextual and event-based validation | Station coordinates, dates/times, reusable measurements, and an optical target that can legitimately be compared with Sentinel-2 |
| Teluk Awur | Peer-reviewed Sentinel-2 TSS method with 112 in-situ samples | Strongest technical benchmark | Georeferenced sample table or author partnership; independent reproduction protocol |
| Morowali | Official 2025 KLH/BPLH inspection and compliance findings | Strong operational-need evidence; potential expert-event review | Water sampling locations/results aligned with imagery, official monitoring boundary, field partner |
| Nusa Lembongan | Published Sentinel-2 chlorophyll-a seasonal analysis | Useful preprocessing comparison | Reusable in-situ validation, exact study AOI, industrial relevance |

No article or inspection report is converted into a pixel label in Phase 0.

## Environmental-context and geospatial data

The following sources are feasible for any candidate:

- **GPM IMERG V07:** 0.1 degree, half-hourly rainfall from June 2000 to delayed
  present. Good minimum rainfall context; coarse relative to an 80 km2 AOI.
- **ERA5 single levels:** hourly data from 1940 at 0.25 degree. Useful for wind
  and broad meteorology; requires a CDS account.
- **Copernicus Marine Global Ocean Physics:** global 1/12 degree model
  analysis/forecast with current fields. Useful as broad context only, not
  precise plume/source tracing; account required.
- **BMKG marine products:** a public marine-weather API and Ocean Forecast
  System exist. Product identifiers, historical continuity, attribution, and
  reuse terms need confirmation before an automated dependency is frozen.
- **BIG coastline 1:25,000 (2022):** preferred source for AOI review. Preserve
  definitive versus indicative status.
- **HydroRIVERS/HydroBASINS:** useful for river and catchment screening, but the
  544 MB global HydroRIVERS file exceeds the Phase 0 limit by itself. Use a
  licensed regional extract later.

No official industrial-estate boundary or outfall point was included. Full
access details and official URLs are in `docs/data_access_requirements.md`.
The machine-readable source-by-source inventory, including temporal coverage,
resolution, format, account, usage, automation, and limitations, is
`reports/data_source_inventory.csv`.

## Scoring

Rubric: Sentinel-2 quality 25, validation 25, industrial relevance 20, boundary
clarity 10, environmental context 10, and manageability/cost 10.

| Site | Proposed role | Sentinel | Validation | Relevance | Boundary | Context | Manageability | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Cilegon | Operational pilot | 13 | 18 | 19 | 7 | 8 | 8 | **73** |
| Teluk Awur | Technical benchmark | 16 | 24 | 7 | 7 | 8 | 9 | **71** |
| Morowali | Operational candidate | 10 | 12 | 20 | 6 | 7 | 6 | **61** |
| Nusa Lembongan | Additional benchmark | 17 | 14 | 2 | 6 | 8 | 8 | **55** |

Sentinel scores are intentionally conservative and provisional because the
requested AOI clear-water sensitivity is blocked. Strong cadence alone cannot
earn a high score.

### Trade-offs behind the totals

- Cilegon wins operationally because validation access and manageability offset
  middling optical conditions.
- Teluk Awur nearly matches Cilegon overall because it is a much better
  technical benchmark, but its industrial relevance is low.
- Morowali's maximum relevance cannot compensate for unresolved optical,
  boundary, validation, and processing risks in a first MVP.
- Nusa Lembongan has the best scene-cloud proxy but fails the core operational
  relevance test.

## Risks and unresolved questions

1. Will the 50/70/80 AOI clear-water sensitivity preserve enough monthly
   observations at Cilegon and Teluk Awur?
2. Can the Cilegon and Teluk Awur authors provide georeferenced, dated samples
   under usable terms?
3. Which official agency/estate boundary should define the Cilegon monitoring
   jurisdiction?
4. Can BIG coastline segments be retrieved with their definitive/indicative
   attribute intact?
5. Is rainfall alone sufficient for the first baseline, or is local tidal
   phase essential to suppress false alerts?
6. Which optical variables are defensible for the available validation target?
   Heavy metals must not be treated as directly observable.
7. Can a Morowali agency or academic partner supply an official boundary and
   matched field observations for a later expansion?

## Recommendation and stopping decision

**Conditional GO for planning only:** use Cilegon as the proposed operational
pilot and Teluk Awur as the separate technical benchmark.

**NO-GO for Phase 1 implementation yet.** Before image download or model work:

1. obtain CDSE OAuth credentials and complete the AOI clear-water 50/70/80 run;
2. refine Cilegon and Teluk Awur against the BIG coastline;
3. confirm an official Cilegon monitoring boundary;
4. secure at least one reusable, georeferenced validation source;
5. have the human owner approve the final site and polygon.

Confidence:

- operational pilot recommendation: **medium**;
- technical benchmark recommendation: **medium-high**;
- AOI clear-water sufficiency: **unknown until OAuth-backed statistics run**.

This is the Phase 0 stopping point. Do not begin bulk download, preprocessing,
dashboard implementation, or model training without approval.

## Sources

Satellite and environmental access:

- CDSE STAC API: <https://documentation.dataspace.copernicus.eu/APIs/STAC.html>
- CDSE OData API: <https://documentation.dataspace.copernicus.eu/APIs/OData.html>
- Sentinel-2 L2A and SCL: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html>
- CDSE Statistical API: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Statistical.html>
- CDSE OAuth: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html>
- GPM IMERG V07: <https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation>
- ERA5 single levels: <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels>
- Copernicus Marine Global Ocean Physics:
  <https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description>
- BMKG Ocean Forecast System: <https://maritim.bmkg.go.id/ofs/>
- BMKG marine public API: <https://maritim.bmkg.go.id/public_api/perairan>
- BIG coastline: <https://data.go.id/dataset/dataset/garis-pantai-indonesia-skala-1-25000-tahun-2022>
- HydroRIVERS: <https://www.hydrosheds.org/products/hydrorivers>
- HydroBASINS: <https://www.hydrosheds.org/products/hydrobasins>

Site evidence:

- KLH/BPLH IMIP inspection release:
  <https://kemenlh.go.id/news/detail/klhbplh-temukan-pelanggaran-lingkungan-serius-di-kawasan-industri-pt-imip>
- Ministry of Transportation IMIP Airport record:
  <https://hubud.kemenhub.go.id/hubud/website/bandara/479>
- Fikri et al. (2026), Cilegon seawater study:
  <https://doi.org/10.61435/jbes.2025.19977>
- Sabila et al. (2025), Teluk Awur Sentinel-2 TSS study:
  <https://doi.org/10.1002/tqem.70154>
- Astiti et al. (2025), Nusa Lembongan Sentinel-2 chlorophyll-a study:
  <https://doi.org/10.30595/jrst.v9i2.24323>
