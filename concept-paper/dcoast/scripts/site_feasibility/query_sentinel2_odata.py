"""Query Sentinel-2 L2A metadata through the public CDSE OData catalogue.

This is the stable fallback when the CDSE STAC endpoint returns 5xx errors.
It downloads JSON metadata only and writes the same acquisition-level schema
used by the Phase 0 availability builder.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from geometry_utils import aoi_metrics, load_aoi

ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"


def get_json(url: str, attempts: int = 4) -> dict[str, Any]:
    for attempt in range(attempts):
        request = urllib.request.Request(
            url, headers={"User-Agent": "dcoast-phase0/1.0"}
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == attempts - 1:
                raise
            print(
                f"CDSE OData request failed ({error}); retry {attempt + 2}/{attempts}",
                flush=True,
            )
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def polygon_wkt(geometry: dict[str, Any]) -> str:
    ring = geometry["coordinates"][0]
    return "POLYGON((" + ",".join(f"{lon} {lat}" for lon, lat in ring) + "))"


def query_site(
    geometry: dict[str, Any], start: str, end: str
) -> list[dict[str, Any]]:
    area = polygon_wkt(geometry)
    filter_value = (
        "Collection/Name eq 'SENTINEL-2' and "
        "Attributes/OData.CSC.StringAttribute/any(att:"
        "att/Name eq 'productType' and "
        "att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;{area}') and "
        f"ContentDate/Start ge {start}T00:00:00.000Z and "
        f"ContentDate/Start le {end}T23:59:59.999Z"
    )
    params = {
        "$filter": filter_value,
        "$expand": "Attributes",
        "$orderby": "ContentDate/Start asc",
        "$top": "1000",
    }
    url = ODATA_URL + "?" + urllib.parse.urlencode(
        params, quote_via=urllib.parse.quote
    )
    products: list[dict[str, Any]] = []
    while url:
        page = get_json(url)
        products.extend(page.get("value", []))
        url = page.get("@odata.nextLink", "")
        if len(products) > 100_000:
            raise RuntimeError("Unexpectedly large OData response; aborting")
    return products


def attribute_value(product: dict[str, Any], name: str) -> Any:
    for attribute in product.get("Attributes", []):
        if attribute.get("Name") == name:
            return attribute.get("Value", "")
    return ""


def observation_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_datetime: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in products:
        acquisition = product.get("ContentDate", {}).get("Start")
        if acquisition:
            by_datetime[acquisition].append(product)
    rows = []
    for acquisition, items in sorted(by_datetime.items()):
        clouds = [
            float(value)
            for item in items
            if (value := attribute_value(item, "cloudCover")) != ""
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
        "--end", default=datetime.now(timezone.utc).date().isoformat()
    )
    args = parser.parse_args()
    queried_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    fields = [
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
    rows = []
    for path in sorted(args.aoi_dir.glob("*.geojson")):
        payload = load_aoi(path)
        feature = payload["features"][0]
        properties = feature["properties"]
        metrics = aoi_metrics(payload)
        products = query_site(feature["geometry"], args.start, args.end)
        observations = observation_rows(products)
        for row in observations:
            rows.append(
                {
                    "site": properties["site_id"],
                    "site_name": properties["site_name"],
                    **row,
                    "aoi_area_km2": f"{metrics['area_km2']:.3f}",
                    "approx_coastline_length_km": (
                        f"{metrics['coastline_length_km']:.3f}"
                    ),
                    "boundary_status": properties["boundary_status"],
                    "collection": "SENTINEL-2/S2MSI2A",
                    "query_start": args.start,
                    "query_end": args.end,
                    "queried_at_utc": queried_at,
                }
            )
        print(
            f"{properties['site_id']}: {len(products)} products, "
            f"{len(observations)} acquisitions",
            flush=True,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} acquisition rows to {args.output}")


if __name__ == "__main__":
    main()
