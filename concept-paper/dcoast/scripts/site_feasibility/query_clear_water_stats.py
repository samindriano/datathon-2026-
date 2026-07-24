"""Query AOI-level clear-water statistics through CDSE Statistical API.

This script intentionally fails closed unless CDSE OAuth credentials are
provided. It uses Sentinel-2 L2A Scene Classification (SCL class 6) at a
diagnostic 60 m resolution; it does not infer pollution.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from geometry_utils import load_aoi, monitoring_water_feature

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)
STATS_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: [{bands: ["SCL", "dataMask"]}],
    output: [
      {id: "quality", bands: 3, sampleType: "FLOAT32"},
      {id: "dataMask", bands: 1}
    ]
  };
}
function evaluatePixel(s) {
  const clearWater = s.dataMask === 1 && s.SCL === 6 ? 1 : 0;
  const cloudShadow = s.dataMask === 1 && [3, 8, 9, 10, 11].includes(s.SCL) ? 1 : 0;
  return {
    quality: [clearWater, cloudShadow, s.dataMask],
    dataMask: [1]
  };
}
"""


def token() -> str:
    client_id = os.environ.get("CDSE_CLIENT_ID")
    client_secret = os.environ.get("CDSE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "BLOCKED_NO_CDSE_OAUTH: set CDSE_CLIENT_ID and CDSE_CLIENT_SECRET; "
            "do not commit either value."
        )
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(TOKEN_URL, data=body, method="POST")
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)["access_token"]


def post_statistics(access_token: str, geometry: dict[str, Any], start: str, end: str) -> dict[str, Any]:
    payload = {
        "input": {
            "bounds": {"geometry": geometry},
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {"mosaickingOrder": "leastCC"},
                }
            ],
        },
        "aggregation": {
            "timeRange": {"from": f"{start}T00:00:00Z", "to": f"{end}T00:00:00Z"},
            "aggregationInterval": {"of": "P1D"},
            "resx": 60,
            "resy": 60,
            "evalscript": EVALSCRIPT,
        },
        "calculations": {"quality": {"statistics": {"default": {}}}},
    }
    request = urllib.request.Request(
        STATS_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "dcoast-phase0/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def yearly_ranges(start_year: int, end: date) -> list[tuple[str, str]]:
    ranges = []
    for year in range(start_year, end.year + 1):
        start = date(year, 1, 1)
        stop = min(date(year + 1, 1, 1), end)
        if start < stop:
            ranges.append((start.isoformat(), stop.isoformat()))
    return ranges


def parse_quality_interval(site: str, interval: dict[str, Any]) -> dict[str, Any]:
    bands = interval.get("outputs", {}).get("quality", {}).get("bands", {})
    required = {}
    for band in ("B0", "B1", "B2"):
        stats = bands.get(band, {}).get("stats", {})
        if "mean" not in stats or "sampleCount" not in stats:
            raise ValueError(f"Missing Statistical API fields for {site} {band}")
        required[band] = stats
    support = int(required["B2"]["sampleCount"])
    valid = round(support * float(required["B2"]["mean"]))
    clear = round(support * float(required["B0"]["mean"]))
    cloud_shadow = round(support * float(required["B1"]["mean"]))
    no_data = support - valid
    clear_fraction = clear / valid if valid else 0.0
    cloud_shadow_fraction = cloud_shadow / valid if valid else 0.0
    return {
        "site": site,
        "acquisition_datetime": interval.get("interval", {}).get("from", ""),
        "water_support_pixel_count": support,
        "valid_water_pixel_count": valid,
        "clear_water_pixel_count": clear,
        "cloud_shadow_pixel_count": cloud_shadow,
        "no_data_pixel_count": no_data,
        "clear_water_fraction": f"{clear_fraction:.6f}",
        "cloud_shadow_fraction": f"{cloud_shadow_fraction:.6f}",
        "no_data_fraction": f"{(no_data / support if support else 1.0):.6f}",
        "quality_50": int(clear_fraction >= 0.50),
        "quality_70": int(clear_fraction >= 0.70),
        "quality_80": int(clear_fraction >= 0.80),
        "status": "AVAILABLE_CDSE_STATISTICAL_API",
        "method": (
            "CDSE Statistical API; S2 L2A SCL; 60m; one-day leastCC mosaic; "
            "clear=SCL6; cloud/shadow=SCL3,8,9,10,11; water-only AOI"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi-dir", type=Path, required=True)
    parser.add_argument(
        "--metadata",
        type=Path,
        required=True,
        help="Deduplicated Sentinel-2 acquisition inventory",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--end", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument(
        "--site",
        action="append",
        help="Optional site_id filter; repeat for multiple sites",
    )
    args = parser.parse_args()
    access_token = token()
    end = date.fromisoformat(args.end) + timedelta(days=1)
    with args.metadata.open(encoding="utf-8", newline="") as handle:
        metadata = list(csv.DictReader(handle))
    acquisition_stamps: dict[str, dict[str, list[str]]] = {}
    for row in metadata:
        site_dates = acquisition_stamps.setdefault(row["site"], {})
        site_dates.setdefault(row["acquisition_datetime"][:10], []).append(
            row["acquisition_datetime"]
        )
    rows = []
    selected_sites: set[str] = set()
    for path in sorted(args.aoi_dir.glob("*.geojson")):
        payload = load_aoi(path)
        feature = monitoring_water_feature(payload)
        site = feature["properties"]["site_id"]
        if args.site and site not in set(args.site):
            continue
        selected_sites.add(site)
        for start, stop in yearly_ranges(args.start_year, end):
            result = post_statistics(access_token, feature["geometry"], start, stop)
            for interval in result.get("data", []):
                stamp = interval.get("interval", {}).get("from", "")
                matching_stamps = acquisition_stamps.get(site, {}).get(stamp[:10], [])
                if matching_stamps:
                    parsed = parse_quality_interval(site, interval)
                    for acquisition_stamp in matching_stamps:
                        row = dict(parsed)
                        row["acquisition_datetime"] = acquisition_stamp
                        rows.append(row)
            print(f"{site} {start[:4]}: {len(result.get('data', []))} daily intervals")
    actual_keys = {(row["site"], row["acquisition_datetime"]) for row in rows}
    if len(actual_keys) != len(rows):
        raise RuntimeError("Duplicate site/acquisition rows returned by Statistical API")
    start_date = date(args.start_year, 1, 1).isoformat()
    end_date = date.fromisoformat(args.end).isoformat()
    expected_keys = {
        (row["site"], row["acquisition_datetime"])
        for row in metadata
        if row["site"] in selected_sites
        and start_date <= row["acquisition_datetime"][:10] <= end_date
    }
    if actual_keys != expected_keys:
        missing = len(expected_keys - actual_keys)
        extra = len(actual_keys - expected_keys)
        raise RuntimeError(
            f"Statistical API acquisition coverage mismatch: missing={missing}, extra={extra}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "site",
        "acquisition_datetime",
        "water_support_pixel_count",
        "valid_water_pixel_count",
        "clear_water_pixel_count",
        "cloud_shadow_pixel_count",
        "no_data_pixel_count",
        "clear_water_fraction",
        "cloud_shadow_fraction",
        "no_data_fraction",
        "quality_50",
        "quality_70",
        "quality_80",
        "status",
        "method",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
