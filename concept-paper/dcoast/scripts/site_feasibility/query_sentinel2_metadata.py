"""Query public CDSE STAC metadata without downloading Sentinel-2 imagery."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from geometry_utils import aoi_metrics, load_aoi

STAC_SEARCH_URL = "https://stac.dataspace.copernicus.eu/v1/search"
COLLECTION = "sentinel-2-l2a"


def request_json(url: str, payload: dict[str, Any], attempts: int = 4) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "User-Agent": "dcoast-phase0/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == attempts - 1:
                raise
            print(
                f"CDSE request failed ({error}); retry {attempt + 2}/{attempts}",
                flush=True,
            )
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def query_interval(
    geometry: dict[str, Any], start: str, end: str
) -> list[dict[str, Any]]:
    ring = geometry["coordinates"][0]
    longitudes = [point[0] for point in ring]
    latitudes = [point[1] for point in ring]
    payload: dict[str, Any] = {
        "collections": [COLLECTION],
        "bbox": [
            min(longitudes),
            min(latitudes),
            max(longitudes),
            max(latitudes),
        ],
        "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
        "limit": 500,
        "fields": {
            "include": [
                "id",
                "properties.datetime",
                "properties.eo:cloud_cover",
                "properties.productType",
                "properties.processingLevel",
            ],
            "exclude": ["geometry", "assets"],
        },
    }
    features: list[dict[str, Any]] = []
    while True:
        page = request_json(STAC_SEARCH_URL, payload)
        features.extend(page.get("features", []))
        next_link = next(
            (link for link in page.get("links", []) if link.get("rel") == "next"),
            None,
        )
        if not next_link:
            break
        if next_link.get("method", "GET").upper() != "POST":
            raise RuntimeError("CDSE returned an unsupported non-POST next page")
        payload = next_link.get("body") or payload
        if len(features) > 100_000:
            raise RuntimeError("Unexpectedly large STAC response; aborting")
    return features


def query_site(geometry: dict[str, Any], start: str, end: str) -> list[dict[str, Any]]:
    first = date.fromisoformat(start)
    last = date.fromisoformat(end)
    features: list[dict[str, Any]] = []
    cursor = first
    while cursor <= last:
        interval_end = min(date(cursor.year, 12, 31), last)
        year_features = query_interval(
            geometry, cursor.isoformat(), interval_end.isoformat()
        )
        features.extend(year_features)
        print(
            f"  {cursor.year}: {len(year_features)} scene items",
            flush=True,
        )
        cursor = interval_end + timedelta(days=1)
    return features


def observation_rows(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_datetime: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in features:
        properties = feature.get("properties", {})
        acquisition = properties.get("datetime")
        if acquisition:
            by_datetime[acquisition].append(feature)
    rows: list[dict[str, Any]] = []
    for acquisition, items in sorted(by_datetime.items()):
        clouds = [
            float(item["properties"]["eo:cloud_cover"])
            for item in items
            if item.get("properties", {}).get("eo:cloud_cover") is not None
        ]
        rows.append(
            {
                "acquisition_datetime": acquisition,
                "scene_items": len(items),
                "scene_cloud_cover_median": statistics.median(clouds) if clouds else "",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument(
        "--site",
        action="append",
        help="Optional site_id filter; repeat to select multiple sites.",
    )
    parser.add_argument(
        "--end",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="Inclusive UTC end date; defaults to the run date.",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "site",
        "site_name",
        "acquisition_datetime",
        "scene_items",
        "scene_cloud_cover_median",
        "aoi_area_km2",
        "approx_coastline_length_km",
        "boundary_status",
        "collection",
        "query_start",
        "query_end",
        "queried_at_utc",
    ]
    queried_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_rows: list[dict[str, Any]] = []
    for path in sorted(args.aoi_dir.glob("*.geojson")):
        payload = load_aoi(path)
        feature = payload["features"][0]
        properties = feature["properties"]
        if args.site and properties["site_id"] not in set(args.site):
            continue
        metrics = aoi_metrics(payload)
        features = query_site(feature["geometry"], args.start, args.end)
        for row in observation_rows(features):
            output_rows.append(
                {
                    "site": properties["site_id"],
                    "site_name": properties["site_name"],
                    **row,
                    "aoi_area_km2": f"{metrics['area_km2']:.3f}",
                    "approx_coastline_length_km": f"{metrics['coastline_length_km']:.3f}",
                    "boundary_status": properties["boundary_status"],
                    "collection": COLLECTION,
                    "query_start": args.start,
                    "query_end": args.end,
                    "queried_at_utc": queried_at,
                }
            )
        print(
            f"{properties['site_id']}: {len(features)} items, "
            f"{len(observation_rows(features))} acquisitions",
            flush=True,
        )
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} acquisition rows to {args.output}")


if __name__ == "__main__":
    main()
