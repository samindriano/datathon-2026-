# Cilegon Validation Inventory

Assessment date: 24 July 2026  
Purpose: classify what can and cannot validate a satellite-assisted coastal
screening system.

## Sources inspected

1. Fikri et al., *Heavy Metals Contamination in Seawater in Cilegon City,
   Banten, Indonesia*, Journal of Bioresources and Environmental Sciences,
   including the full article PDF and both supplementary files.
2. Supplementary `Peta Lokasi`, JPEG, 29,219 by 20,677 pixels, no EXIF
   geospatial metadata, SHA-256
   `3e5c443dd7fa7faca318cf78e6657e0208ea9c9f74bea945cbccc1d11a334b39`.
3. Supplementary `Data Analysis`, XLSX workbook, SHA-256
   `494d93c7baa059cde3a743a7e99a45eaaf0132f5204c98327cd84314290b1892`.

The temporary source files were inspected outside the repository and were not
committed.

## What the publication supports

- Five purposively selected surface-water stations sampled in February 2022.
- Stations 1-2 represent residential/tourism context; stations 3-5 represent
  port/industrial context.
- Surface sampling depth of 0-50 cm.
- In-situ temperature, salinity, pH, and water brightness, plus laboratory
  dissolved Cd, Cu, and Pb.
- Accredited laboratory analysis reported under ISO/IEC 17025:2017.
- Station measurements reported in the article:

| Variable | Station 1 | Station 2 | Station 3 | Station 4 | Station 5 |
|---|---:|---:|---:|---:|---:|
| Temperature (C) | 30.2 | 29.6 | 28.8 | 30.4 | 29.5 |
| Salinity | 30 | 30 | 31 | 29 | 30 |
| pH | 8.4 | 8.1 | 7.7 | 7.9 | 8.0 |
| Brightness (m) | 0.27 | 0.42 | 0.74 | 0.52 | 0.68 |
| Dissolved Cd | below 0.00003 at all stations |  |  |  |  |
| Dissolved Cu | below 0.006 | below 0.006 | 0.0024 | 0.0121 | 0.0129 |
| Dissolved Pb | below 0.00012 | 0.0018 | below 0.00012 | 0.0153 | 0.0170 |

The supplementary workbook contains the authors' per-station pollution-index
calculation inputs and formulas. It is useful for understanding the published
assessment but is not a satellite training-label table.

## Spatial limitation

The supplementary map shows five red station symbols along a schematic
north-south Cilegon coast and identifies general land-use layers. It has no
graticule, coordinate labels, named station table, or embedded geospatial
metadata. A scale bar and WGS 1984 note do not make the raster independently
georeferenceable.

Therefore:

- no station coordinates are inferred;
- no `cilegon_station_candidates.geojson` is created;
- the map is not used to tune the Phase 0.5 AOI;
- the next defensible step is to request the original coordinates/GIS layer
  from the corresponding author or replace it with an official georeferenced
  monitoring source.

## Validation classification

| Evidence | Category | Permitted role | Prohibited interpretation |
|---|---|---|---|
| Sentinel-2 reflectance paired with an optical water property | A - direct optical proxy | Quantitative proxy validation after temporal/spatial matching | None is currently available for Cilegon |
| Water brightness | B - indirect proxy | Qualitative or carefully matched turbidity/clarity comparison | Do not treat as equivalent to a calibrated Sentinel-2 TSS label |
| Temperature, salinity, pH | B/C - supporting context | Explain water-mass or event conditions; expert review | Do not train a generic pollution detector from these five values |
| Cd, Cu, Pb and pollution index | C - event/context evidence | Event annotation, prioritization, or expert-review context | Never use as direct optical labels; Sentinel-2 does not directly measure dissolved heavy metals |
| Supplementary location map | C - contextual spatial evidence | Confirm five relative coastal sampling positions | Do not derive precise coordinates or sampling buffers |

## Alignment and expert-review plan

1. Obtain original station coordinates, sampling timestamps, units, detection
   limits, and reuse permission.
2. Pair only temporally appropriate Sentinel-2 observations after the
   50/70/80 clear-water screen.
3. Use brightness as an indirect comparison and heavy metals only as an event
   annotation.
4. Ask a coastal-water specialist to review false alerts around river mouths,
   ports, dredging, sediment resuspension, and cloud/glint artefacts.
5. Keep D'Coast output as inspection prioritization, not a pollution verdict or
   source attribution.

## Current disposition

Cilegon has a credible validation-acquisition path, but no reusable
georeferenced direct optical validation set has been secured. This supports a
conditional site lock only.

Sources:

- Journal record: <https://jbes.cbiore.id/index.php/jbes/article/view/19977/0>
- Full article: <https://jbes.cbiore.id/index.php/jbes/article/download/19977/pdf>
- Supplementary map:
  <https://jbes.cbiore.id/index.php/jbes/article/downloadSuppFile/19977/4952>
- Supplementary data analysis:
  <https://jbes.cbiore.id/index.php/jbes/article/downloadSuppFile/19977/4953>
