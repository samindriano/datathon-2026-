# Site-feasibility scripts

These scripts are dependency-free and keep Phase 0 metadata-first.

Run from the repository root:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/query_sentinel2_metadata.py `
  --aoi-dir concept-paper/dcoast/data/aoi_candidates `
  --output concept-paper/dcoast/data/sentinel2_metadata_observations.csv `
  --start 2021-01-01 `
  --end 2026-07-24

python concept-paper/dcoast/scripts/site_feasibility/build_availability_table.py `
  --metadata concept-paper/dcoast/data/sentinel2_metadata_observations.csv `
  --output concept-paper/dcoast/reports/sentinel2_monthly_availability.csv
```

If the public STAC service returns repeated `5xx` errors, use the official CDSE
OData catalogue fallback:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/query_sentinel2_odata.py `
  --aoi-dir concept-paper/dcoast/data/aoi_candidates `
  --output concept-paper/dcoast/data/sentinel2_metadata_observations.csv `
  --start 2021-01-01 `
  --end 2026-07-24
```

AOI-level clear-water sensitivity needs CDSE OAuth credentials:

```powershell
$env:CDSE_CLIENT_ID = '<local value>'
$env:CDSE_CLIENT_SECRET = '<local value>'
python concept-paper/dcoast/scripts/site_feasibility/query_clear_water_stats.py `
  --aoi-dir concept-paper/dcoast/data/aoi_candidates `
  --output concept-paper/dcoast/data/sentinel2_clear_water_daily.csv `
  --start-year 2021 `
  --end 2026-07-24

python concept-paper/dcoast/scripts/site_feasibility/build_availability_table.py `
  --metadata concept-paper/dcoast/data/sentinel2_metadata_observations.csv `
  --clear-water concept-paper/dcoast/data/sentinel2_clear_water_daily.csv `
  --output concept-paper/dcoast/reports/sentinel2_monthly_availability.csv
```

Do not commit credentials, full Sentinel-2 imagery, or large raw environmental
archives. The clear-water diagnostic uses SCL class 6 at 60 m and is not a
pollution detector.

Validate all current Phase 0 artifacts:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/validate_outputs.py `
  --root concept-paper/dcoast
```
