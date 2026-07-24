"""Query AOI-level clear-water statistics through CDSE Statistical API.

This script intentionally fails closed unless CDSE OAuth credentials are
provided. It uses Sentinel-2 L2A Scene Classification (SCL class 6) at a
diagnostic 60 m resolution; it does not infer pollution.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
import urllib.error
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
STATS_URL = "https://sh.dataspace.copernicus.eu/statistics/v1"
WGS84_CRS_URI = "http://www.opengis.net/def/crs/EPSG/0/4326"
DIAGNOSTIC_RESOLUTION_DEGREES = 0.00054
API_PROVENANCE = (
    "CDSE Statistical API; sentinel-2-l2a; SCL; approx 60m "
    "(0.00054 degree WGS84); P1D; leastCC; "
    "clear=SCL6; cloud-shadow=SCL3,8,9,10,11; water-only AOI"
)
FIELDS = [
    "site",
    "observation_date",
    "source_acquisition_count",
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
    "quality_status",
    "rejection_reason",
    "processed_at_utc",
    "api_provenance",
]
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


def request_json(
    request: urllib.request.Request,
    *,
    timeout: int,
    attempts: int = 4,
    sleep_fn=time.sleep,
) -> dict[str, Any]:
    """Return JSON with bounded retries for transient CDSE failures."""

    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt == attempts:
                if exc.code == 401:
                    raise
                detail = exc.read(2000).decode("utf-8", errors="replace").strip()
                if detail:
                    raise RuntimeError(
                        f"CDSE_API_HTTP_{exc.code}: {detail}"
                    ) from exc
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts:
                raise
        sleep_fn(2 ** attempt)
    raise RuntimeError("Unreachable retry state")


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
    try:
        payload = request_json(request, timeout=90)
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise RuntimeError(
                "INVALID_CDSE_OAUTH_CLIENT: CDSE rejected the client ID/secret. "
                "Create a Sentinel Hub OAuth client under CDSE Dashboard > "
                "User Settings > OAuth clients; account login credentials are "
                "not API client credentials."
            ) from exc
        raise
    access_token = payload.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("CDSE token response did not contain an access token")
    return access_token


def post_statistics(access_token: str, geometry: dict[str, Any], start: str, end: str) -> dict[str, Any]:
    payload = {
        "input": {
            "bounds": {
                "geometry": geometry,
                "properties": {"crs": WGS84_CRS_URI},
            },
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
            "resx": DIAGNOSTIC_RESOLUTION_DEGREES,
            "resy": DIAGNOSTIC_RESOLUTION_DEGREES,
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
            "User-Agent": "dcoast-phase06/1.0",
        },
    )
    return request_json(request, timeout=300)


def yearly_ranges(start_year: int, end: date) -> list[tuple[str, str]]:
    ranges = []
    for year in range(start_year, end.year + 1):
        start = date(year, 1, 1)
        stop = min(date(year + 1, 1, 1), end)
        if start < stop:
            ranges.append((start.isoformat(), stop.isoformat()))
    return ranges


def parse_quality_interval(
    site: str,
    interval: dict[str, Any],
    *,
    source_acquisition_count: int = 1,
    processed_at_utc: str = "",
) -> dict[str, Any]:
    bands = interval.get("outputs", {}).get("quality", {}).get("bands", {})
    required = {}
    for band in ("B0", "B1", "B2"):
        stats = bands.get(band, {}).get("stats", {})
        if "mean" not in stats or "sampleCount" not in stats:
            raise ValueError(f"Missing Statistical API fields for {site} {band}")
        required[band] = stats
    sample_counts = {int(required[band]["sampleCount"]) for band in required}
    if len(sample_counts) != 1:
        raise ValueError(f"Inconsistent sample counts for {site}")
    means = {band: float(required[band]["mean"]) for band in required}
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in means.values()):
        raise ValueError(f"Invalid Statistical API mean for {site}")
    support = sample_counts.pop()
    if support < 0:
        raise ValueError(f"Negative sample count for {site}")
    valid = round(support * means["B2"])
    clear = round(support * means["B0"])
    cloud_shadow = round(support * means["B1"])
    no_data = support - valid
    if clear > valid or cloud_shadow > valid or no_data < 0:
        raise ValueError(f"Inconsistent quality counts for {site}")
    clear_fraction = clear / valid if valid else 0.0
    cloud_shadow_fraction = cloud_shadow / valid if valid else 0.0
    quality_50 = int(valid > 0 and clear_fraction >= 0.50)
    quality_70 = int(valid > 0 and clear_fraction >= 0.70)
    quality_80 = int(valid > 0 and clear_fraction >= 0.80)
    if valid == 0:
        quality_status = "NO_VALID_WATER"
        rejection_reason = "ZERO_VALID_WATER"
    elif quality_80:
        quality_status = "USABLE_80"
        rejection_reason = ""
    elif quality_70:
        quality_status = "USABLE_70"
        rejection_reason = "CLEAR_WATER_BELOW_80"
    elif quality_50:
        quality_status = "USABLE_50"
        rejection_reason = "CLEAR_WATER_BELOW_70"
    else:
        quality_status = "REJECTED"
        rejection_reason = "CLEAR_WATER_BELOW_50"
    return {
        "site": site,
        "observation_date": interval.get("interval", {}).get("from", "")[:10],
        "source_acquisition_count": source_acquisition_count,
        "water_support_pixel_count": support,
        "valid_water_pixel_count": valid,
        "clear_water_pixel_count": clear,
        "cloud_shadow_pixel_count": cloud_shadow,
        "no_data_pixel_count": no_data,
        "clear_water_fraction": f"{clear_fraction:.6f}",
        "cloud_shadow_fraction": f"{cloud_shadow_fraction:.6f}",
        "no_data_fraction": f"{(no_data / support if support else 1.0):.6f}",
        "quality_50": quality_50,
        "quality_70": quality_70,
        "quality_80": quality_80,
        "quality_status": quality_status,
        "rejection_reason": rejection_reason,
        "processed_at_utc": processed_at_utc,
        "api_provenance": API_PROVENANCE,
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
    acquisition_counts: dict[str, dict[str, int]] = {}
    for row in metadata:
        site_dates = acquisition_counts.setdefault(row["site"], {})
        observation_date = row["acquisition_datetime"][:10]
        site_dates[observation_date] = site_dates.get(observation_date, 0) + 1
    rows = []
    selected_sites: set[str] = set()
    processed_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
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
                source_count = acquisition_counts.get(site, {}).get(stamp[:10], 0)
                if source_count:
                    rows.append(
                        parse_quality_interval(
                            site,
                            interval,
                            source_acquisition_count=source_count,
                            processed_at_utc=processed_at_utc,
                        )
                    )
            print(f"{site} {start[:4]}: {len(result.get('data', []))} daily intervals")
    actual_keys = {(row["site"], row["observation_date"]) for row in rows}
    if len(actual_keys) != len(rows):
        raise RuntimeError("Duplicate site-date rows returned by Statistical API")
    start_date = date(args.start_year, 1, 1).isoformat()
    end_date = date.fromisoformat(args.end).isoformat()
    expected_keys = {
        (row["site"], row["acquisition_datetime"][:10])
        for row in metadata
        if row["site"] in selected_sites
        and start_date <= row["acquisition_datetime"][:10] <= end_date
    }
    if actual_keys != expected_keys:
        missing = len(expected_keys - actual_keys)
        extra = len(actual_keys - expected_keys)
        raise RuntimeError(
            f"Statistical API site-date coverage mismatch: missing={missing}, extra={extra}"
        )
    rows.sort(key=lambda row: (row["site"], row["observation_date"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
