"""Download small, site-bounded BIG 1:25,000 coastline extracts."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

SERVICE_URL = (
    "https://geoservices.big.go.id/rbi/rest/services/"
    "GARISPANTAI/GarisPantai_25K/MapServer/0/query"
)
SERVICE_LAYER_URL = SERVICE_URL.removesuffix("/query")
SITE_BOUNDS = {
    "cilegon-industrial-coast": (105.90, -6.13, 106.01, -5.88),
    "teluk-awur-jepara": (110.54, -6.73, 110.66, -6.51),
}
OUT_FIELDS = ",".join(
    (
        "OBJECTID",
        "NAMOBJ",
        "REMARK",
        "METADATA",
        "DTMVER",
        "KARGPN",
        "TIPGPN",
        "KODGPN",
        "THNSBDATA",
        "SBDATA",
        "SKL",
        "THNPBL",
        "KET",
    )
)


def clip_segment(
    start: list[float],
    end: list[float],
    bounds: tuple[float, float, float, float],
) -> list[list[float]] | None:
    """Clip one WGS84 segment to an axis-aligned query envelope."""

    xmin, ymin, xmax, ymax = bounds

    def code(point: list[float]) -> int:
        value = 0
        if point[0] < xmin:
            value |= 1
        elif point[0] > xmax:
            value |= 2
        if point[1] < ymin:
            value |= 4
        elif point[1] > ymax:
            value |= 8
        return value

    first = [float(start[0]), float(start[1])]
    second = [float(end[0]), float(end[1])]
    while True:
        first_code, second_code = code(first), code(second)
        if not (first_code | second_code):
            return [first, second]
        if first_code & second_code:
            return None
        outside = first_code or second_code
        if outside & 8:
            x = first[0] + (second[0] - first[0]) * (ymax - first[1]) / (
                second[1] - first[1]
            )
            point = [x, ymax]
        elif outside & 4:
            x = first[0] + (second[0] - first[0]) * (ymin - first[1]) / (
                second[1] - first[1]
            )
            point = [x, ymin]
        elif outside & 2:
            y = first[1] + (second[1] - first[1]) * (xmax - first[0]) / (
                second[0] - first[0]
            )
            point = [xmax, y]
        else:
            y = first[1] + (second[1] - first[1]) * (xmin - first[0]) / (
                second[0] - first[0]
            )
            point = [xmin, y]
        if outside == first_code:
            first = point
        else:
            second = point


def geometry_lines(geometry: dict[str, Any]) -> list[list[list[float]]]:
    if geometry["type"] == "LineString":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiLineString":
        return geometry["coordinates"]
    raise ValueError(f"Unexpected BIG geometry: {geometry['type']}")


def clip_to_bounds(
    result: dict[str, Any],
    bounds: tuple[float, float, float, float],
) -> dict[str, Any]:
    features = []
    for feature in result["features"]:
        segments = []
        for line in geometry_lines(feature["geometry"]):
            for start, end in zip(line, line[1:]):
                clipped = clip_segment(start, end, bounds)
                if clipped is not None:
                    segments.append(clipped)
        if not segments:
            continue
        feature["geometry"] = {
            "type": "MultiLineString",
            "coordinates": segments,
        }
        features.append(feature)
    if not features:
        raise RuntimeError("All BIG coastline features disappeared during clipping")
    result["features"] = features
    return result


def request_geojson(bounds: tuple[float, float, float, float]) -> dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            "where": "1=1",
            "geometry": ",".join(str(value) for value in bounds),
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": OUT_FIELDS,
            "returnGeometry": "true",
            "outSR": "4326",
            "maxAllowableOffset": "0.00001",
            "geometryPrecision": "6",
            "f": "geojson",
        }
    ).encode("ascii")
    request = urllib.request.Request(
        SERVICE_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "dcoast-phase07/1.0",
        },
    )
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.load(response)
            if result.get("type") != "FeatureCollection":
                raise RuntimeError(f"Unexpected BIG response: {result}")
            if not result.get("features"):
                raise RuntimeError("BIG query returned no coastline features")
            return result
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Unreachable BIG request retry state")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for site, bounds in SITE_BOUNDS.items():
        result = clip_to_bounds(request_geojson(bounds), bounds)
        result["name"] = f"{site}-big-coastline-25k"
        result["dcoast_provenance"] = {
            "source": "Badan Informasi Geospasial",
            "service_layer": SERVICE_LAYER_URL,
            "query_bounds_wgs84": list(bounds),
            "query_crs": "EPSG:4326",
            "output_crs": "EPSG:4326",
            "retrieval_scope": "bounded Phase 0.7 AOI review",
            "geometry_processing": "client-side segment clipping to query bounds",
            "server_geometry_tolerance_degrees": 0.00001,
        }
        output = args.output_dir / f"{site}.geojson"
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{site}: {len(result['features'])} BIG coastline features -> {output}")


if __name__ == "__main__":
    main()
