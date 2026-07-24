# D'Coast Phase 0 - Data Access Requirements

Status: feasibility inventory only. No source below is evidence of pollution or
source attribution.

## Access summary

| Source | Intended use | Coverage / resolution | Access and format | Account | Automation | Important limitation |
|---|---|---|---|---|---|---|
| Copernicus Data Space STAC, `sentinel-2-l2a` | Acquisition inventory and scene metadata | Sentinel-2 archive; nominal 10-60 m bands | Public STAC JSON at `https://stac.dataspace.copernicus.eu/v1/` | No for catalogue | Yes | Scene cloud cover is not AOI clear-water coverage. |
| CDSE Sentinel Hub Statistical API | AOI-level SCL clear-water fraction | Server-side user AOI; Phase 0 script requests 60 m diagnostic statistics | JSON API | Yes; OAuth client | Yes after credentials | Free-account quota applies. SCL class 6 is a screening proxy and mixed land-water AOIs need a stable water mask later. |
| Sentinel-2 L1C / L2A | Optical imagery | L1C TOA; L2A surface reflectance and SCL | CDSE browser, APIs, S3/object access | Catalogue no; most data access yes | Yes | Do not bulk-download in Phase 0. Prefer L2A; compare L1C only for documented gaps. |
| GPM IMERG V07 | Minimum rainfall context | June 2000 to delayed present; 0.1 degree, half-hourly | NASA Earthdata files/services | Usually NASA Earthdata account for download | Yes | Coarse relative to a narrow coast; rainfall is context, not a causal verdict. |
| ERA5 single levels | Rainfall, wind and broad meteorology | 1940-present; hourly, 0.25 degree | CDS API; GRIB | Yes | Yes | Coarser than the pilot AOI and not a replacement for local observations. |
| BMKG marine weather public API | Indonesian marine forecast context | Current/forecast products; product-dependent | JSON at `https://maritim.bmkg.go.id/public_api/perairan` | No credential observed for public endpoint | Potentially | Historical stability, identifiers and reuse terms must be confirmed before making it an MVP dependency. Attribution to BMKG is required. |
| BMKG Ocean Forecast System | Currents and ocean context | Model/product-dependent | Web viewer and some OPeNDAP/netCDF services | Product-dependent | Investigate per dataset | Forecast currents are too coarse/uncertain for precise plume or source tracing. |
| Copernicus Marine Global Ocean Physics Analysis and Forecast | Broad current, sea-level and temperature context | Global 1/12 degree; hourly/daily/monthly product outputs | Copernicus Marine Toolbox/API, netCDF | Yes | Yes | Global model context only; do not infer an exact discharge source. |
| BIG Garis Pantai Indonesia 1:25,000 (2022) | Official coastline review and water-side AOI refinement | Indonesia, 1:25,000 | Data.go.id / BIG download, vector format dependent on package | Check download workflow | Likely manual then scriptable | Dataset distinguishes definitive and indicative segments; preserve that status. |
| HydroRIVERS / HydroBASINS | River-mouth and catchment screening | Global; HydroRIVERS derived at 15 arc-second support | Shapefile / geodatabase | No account generally | Yes | Global HydroRIVERS file is about 544 MB and therefore exceeds this Phase 0 budget by itself. Download only a permitted regional extract later. Product-specific license must be retained. |
| Official industrial-estate or port boundary | Monitoring-jurisdiction refinement | Site-specific | Government/estate GIS or official document | Unknown | Unknown | None was found and adopted during Phase 0. Current AOIs are explicitly provisional. |
| Official outfall/discharge points | Inspection context only | Site-specific | Permit, inspection, or agency record | Unknown | Usually manual | Do not invent or infer an outfall from imagery. No point is included in the Phase 0 AOIs. |

## Official source links

- CDSE STAC API: <https://documentation.dataspace.copernicus.eu/APIs/STAC.html>
- CDSE Sentinel-2 L2A: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html>
- CDSE Statistical API: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Statistical.html>
- CDSE OAuth: <https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html>
- GPM IMERG V07 documentation: <https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation>
- ERA5 single levels: <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels>
- Copernicus Marine global physics product: <https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description>
- BMKG Ocean Forecast System: <https://maritim.bmkg.go.id/ofs/>
- BMKG marine public API: <https://maritim.bmkg.go.id/public_api/perairan>
- BIG coastline dataset: <https://data.go.id/dataset/dataset/garis-pantai-indonesia-skala-1-25000-tahun-2022>
- HydroRIVERS: <https://www.hydrosheds.org/products/hydrorivers>
- HydroBASINS: <https://www.hydrosheds.org/products/hydrobasins>

## Credentials and environment variables

The public metadata script needs no credential.

The AOI clear-water script requires a CDSE OAuth client created in the user's
CDSE account:

```text
CDSE_CLIENT_ID
CDSE_CLIENT_SECRET
```

Never put these values in Git, a notebook, a screenshot, a report, or a shell
history that will be shared. Set them only in the local process environment.

Later optional sources may use:

```text
CDSAPI_URL
CDSAPI_KEY
EARTHDATA_USERNAME
EARTHDATA_PASSWORD
```

These are not required for the Phase 0 metadata inventory and must not be
created merely to make the current report look complete.

## Exact current blocker

On 24 July 2026 the public CDSE STAC catalogue was accessible, but no
`CDSE_CLIENT_ID` or `CDSE_CLIENT_SECRET` was available in the working
environment. AOI-level clear-water fractions therefore could not be obtained
from the Statistical API. The report leaves the 50%, 70% and 80% clear-water
fields empty with status `BLOCKED_NO_CDSE_OAUTH`.

Whole-tile scene cloud metadata is retained only as a diagnostic proxy. It is
not silently substituted for the requested AOI pixel statistic.

## Manual steps before Phase 1

1. Create a free CDSE account and OAuth client.
2. Run the clear-water script with credentials set only in the process
   environment.
3. Review processing-unit use before requesting the full date range.
4. Obtain and cite the BIG coastline package; refine each provisional polygon
   without losing provenance.
5. Ask the relevant agency or site owner for an official estate/jurisdiction
   boundary and any public monitoring or sampling record.
6. Acquire published station coordinates or data-use permission for the chosen
   benchmark before claiming validation.

