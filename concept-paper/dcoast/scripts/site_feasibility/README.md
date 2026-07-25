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

AOI-level clear-water sensitivity needs CDSE OAuth credentials. After setting
them in a private PowerShell session, run the complete Phase 0.6 workflow with
one command:

```powershell
$env:CDSE_CLIENT_ID = '<local value>'
$env:CDSE_CLIENT_SECRET = '<local value>'
python concept-paper/dcoast/scripts/site_feasibility/run_phase06.py
```

Do not commit credentials, full Sentinel-2 imagery, or large raw environmental
archives. The clear-water diagnostic uses SCL class 6 and cloud/shadow classes
3, 8, 9, 10, and 11 at an approximate 60 m diagnostic grid
(`0.00054` degree WGS84) over the water-only AOIs. It is not a pollution
detector. The runner makes one daily mosaic per unique site-date, retries only
transient API failures, rebuilds the monthly and frozen-gate assessment tables,
writes the Phase 0.6 decision report, and validates all outputs.

If OAuth is unavailable, rebuild the transparent blocked work queue:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/build_blocked_observation_quality.py `
  --metadata concept-paper/dcoast/data/sentinel2_metadata_observations.csv `
  --output concept-paper/dcoast/reports/sentinel2_observation_quality.csv
```

Validate all current Phase 0 artifacts:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/validate_outputs.py `
  --root concept-paper/dcoast

python -m unittest discover `
  -s concept-paper/dcoast/tests `
  -p "test_*.py"
```

Phase 0.7 uses only small, bounded vector queries from BIG's public 1:25,000
coastline service. It does not download satellite imagery, contact study
authors, alter the provisional monitoring AOIs, or start Phase 1:

```powershell
python concept-paper/dcoast/scripts/site_feasibility/run_phase07.py
```

The resulting endpoint-distance screen is intentionally conservative. A pass
would establish only broad coastline alignment; a fail requires AOI redesign
and review rather than silently snapping the existing polygon.
