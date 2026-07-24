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

from geometry_utils import load_aoi

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
      {id: "clear_water", bands: 1, sampleType: "FLOAT32"},
      {id: "dataMask", bands: 1}
    ]
  };
}
function evaluatePixel(s) {
  return {
    clear_water: [s.SCL === 6 ? 1 : 0],
    dataMask: [s.dataMask]
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
        "calculations": {"clear_water": {"statistics": {"default": {"percentiles": {"k": [50]}}}}},
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--end", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()
    access_token = token()
    end = date.fromisoformat(args.end) + timedelta(days=1)
    rows = []
    for path in sorted(args.aoi_dir.glob("*.geojson")):
        payload = load_aoi(path)
        feature = payload["features"][0]
        site = feature["properties"]["site_id"]
        for start, stop in yearly_ranges(args.start_year, end):
            result = post_statistics(access_token, feature["geometry"], start, stop)
            for interval in result.get("data", []):
                stats = (
                    interval.get("outputs", {})
                    .get("clear_water", {})
                    .get("bands", {})
                    .get("B0", {})
                    .get("stats", {})
                )
                rows.append(
                    {
                        "site": site,
                        "interval_from": interval.get("interval", {}).get("from", ""),
                        "interval_to": interval.get("interval", {}).get("to", ""),
                        "clear_water_fraction": stats.get("mean", ""),
                        "sample_count": stats.get("sampleCount", ""),
                        "no_data_count": stats.get("noDataCount", ""),
                        "method": "CDSE Statistical API; S2 L2A SCL==6; 60m; leastCC daily mosaic",
                    }
                )
            print(f"{site} {start[:4]}: {len(result.get('data', []))} daily intervals")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "site",
        "interval_from",
        "interval_to",
        "clear_water_fraction",
        "sample_count",
        "no_data_count",
        "method",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
