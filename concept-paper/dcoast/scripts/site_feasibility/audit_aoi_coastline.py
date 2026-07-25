"""Audit provisional D'Coast coastline references against bounded BIG data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

EARTH_RADIUS_M = 6_371_008.8
ALIGNMENT_GATE_M = 1_000.0
BIG_LAYER_URL = (
    "https://geoservices.big.go.id/rbi/rest/services/"
    "GARISPANTAI/GarisPantai_25K/MapServer/0"
)
SITES = {
    "cilegon-industrial-coast": "cilegon.geojson",
    "teluk-awur-jepara": "teluk_awur.geojson",
}
TIPGPN = {
    1: "mean-sea-level",
    2: "highest-tide",
    3: "lowest-tide",
    4: "indicative",
    999: "other",
}
SBDATA = {
    1: "terrestrial-shoreline-transect",
    2: "hydrographic-survey",
    3: "sar",
    4: "lidar",
    5: "stereo-model",
    6: "ortho-photo-imagery",
    999: "other",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def line_strings(geometry: dict[str, Any]) -> Iterator[list[list[float]]]:
    if geometry["type"] == "LineString":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        yield from geometry["coordinates"]
    else:
        raise ValueError(f"Unexpected BIG coastline geometry: {geometry['type']}")


def project(point: list[float], reference_lat: float) -> tuple[float, float]:
    lon, lat = point
    return (
        math.radians(lon) * EARTH_RADIUS_M * math.cos(math.radians(reference_lat)),
        math.radians(lat) * EARTH_RADIUS_M,
    )


def unproject(x: float, y: float, reference_lat: float) -> tuple[float, float]:
    return (
        math.degrees(x / (EARTH_RADIUS_M * math.cos(math.radians(reference_lat)))),
        math.degrees(y / EARTH_RADIUS_M),
    )


def point_segment_distance(
    point: list[float],
    start: list[float],
    end: list[float],
) -> tuple[float, tuple[float, float]]:
    reference_lat = point[1]
    px, py = project(point, reference_lat)
    ax, ay = project(start, reference_lat)
    bx, by = project(end, reference_lat)
    dx, dy = bx - ax, by - ay
    denominator = dx * dx + dy * dy
    fraction = 0.0 if denominator == 0 else ((px - ax) * dx + (py - ay) * dy) / denominator
    fraction = max(0.0, min(1.0, fraction))
    nearest_x, nearest_y = ax + fraction * dx, ay + fraction * dy
    return math.hypot(px - nearest_x, py - nearest_y), unproject(
        nearest_x,
        nearest_y,
        reference_lat,
    )


def nearest_feature(
    point: list[float],
    features: list[dict[str, Any]],
) -> tuple[float, tuple[float, float], dict[str, Any]]:
    best: tuple[float, tuple[float, float], dict[str, Any]] | None = None
    for feature in features:
        for line in line_strings(feature["geometry"]):
            for start, end in zip(line, line[1:]):
                distance, nearest = point_segment_distance(point, start, end)
                if best is None or distance < best[0]:
                    best = distance, nearest, feature
    if best is None:
        raise ValueError("BIG coastline extract contains no line segments")
    return best


def audit_site(
    site: str,
    aoi_path: Path,
    coastline_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    aoi = load_json(aoi_path)
    coastline = load_json(coastline_path)
    properties = aoi["features"][0]["properties"]
    if properties["site_id"] != site:
        raise ValueError(f"AOI site mismatch for {site}")
    features = coastline["features"]
    rows = []
    for index, point in enumerate(properties["coastline_reference"]):
        distance, nearest, feature = nearest_feature(point, features)
        attributes = feature["properties"]
        rows.append(
            {
                "site": site,
                "reference_point": "north" if index == 0 else "south",
                "aoi_longitude": f"{point[0]:.8f}",
                "aoi_latitude": f"{point[1]:.8f}",
                "nearest_big_longitude": f"{nearest[0]:.8f}",
                "nearest_big_latitude": f"{nearest[1]:.8f}",
                "distance_m": f"{distance:.2f}",
                "alignment_gate_m": f"{ALIGNMENT_GATE_M:.0f}",
                "alignment_pass": int(distance <= ALIGNMENT_GATE_M),
                "big_objectid": attributes["OBJECTID"],
                "big_name": attributes.get("NAMOBJ") or "",
                "big_remark": attributes.get("REMARK") or "",
                "big_coastline_type_code": attributes.get("TIPGPN") or "",
                "big_coastline_type": TIPGPN.get(attributes.get("TIPGPN"), "unknown"),
                "big_source_code": attributes.get("SBDATA") or "",
                "big_source": SBDATA.get(attributes.get("SBDATA"), "unknown"),
                "big_source_year": attributes.get("THNSBDATA") or "",
                "big_publication_year": attributes.get("THNPBL") or "",
            }
        )
    type_counts = Counter(
        TIPGPN.get(feature["properties"].get("TIPGPN"), "unknown")
        for feature in features
    )
    source_counts = Counter(
        SBDATA.get(feature["properties"].get("SBDATA"), "unknown")
        for feature in features
    )
    summary = {
        "site": site,
        "feature_count": len(features),
        "type_counts": dict(sorted(type_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "max_reference_distance_m": max(float(row["distance_m"]) for row in rows),
        "alignment_pass": all(int(row["alignment_pass"]) for row in rows),
    }
    return rows, summary


def build_report(summaries: list[dict[str, Any]], rows: list[dict[str, Any]]) -> str:
    sections = []
    for summary in summaries:
        site_rows = [row for row in rows if row["site"] == summary["site"]]
        endpoint_lines = "\n".join(
            f"- {row['reference_point']}: {row['distance_m']} m to BIG feature "
            f"{row['big_objectid']} ({row['big_coastline_type']}, "
            f"{row['big_source']}, source year {row['big_source_year']})."
            for row in site_rows
        )
        sections.append(
            f"""### {summary["site"]}

- Extracted BIG features: {summary["feature_count"]}
- Coastline types: `{json.dumps(summary["type_counts"], sort_keys=True)}`
- Source methods: `{json.dumps(summary["source_counts"], sort_keys=True)}`
- Maximum endpoint distance: {summary["max_reference_distance_m"]:.2f} m
- Frozen <= {ALIGNMENT_GATE_M:.0f} m endpoint gate: {"PASS" if summary["alignment_pass"] else "FAIL"}

{endpoint_lines}
"""
        )
    return f"""# D'Coast Phase 0.7 AOI-Coastline Review

Verdict scope: **GEOMETRY SCREEN ONLY - NOT PHASE 1 AUTHORIZATION**

## Method

The two endpoints of each provisional AOI's landward `coastline_reference`
were compared with the nearest line segment in BIG's official Peta Garis
Pantai Skala 1:25.000 feature service. Before measuring, the endpoint gate was
frozen at <= {ALIGNMENT_GATE_M:.0f} metres. The service's coastline type and
source-method codes are preserved; indicative lines are not relabelled as
definitive.

{"".join(sections)}
## Interpretation

Passing this endpoint screen means only that the provisional landward
reference follows the same broad coastal corridor as the BIG extract. It does
not validate the offshore width, river-mouth segmentation, control-water
assumption, monitoring jurisdiction, published sampling stations, or water
quality model. Those require domain review and georeferenced validation data.

## Source

- BIG layer: `{BIG_LAYER_URL}`
- Layer publication: 2022; query/output CRS: EPSG:4326.
- Bounded extracts are stored under `data/big_coastline/`.
"""


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aoi-dir", type=Path, required=True)
    parser.add_argument("--coastline-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    summaries = []
    for site, filename in SITES.items():
        site_rows, summary = audit_site(
            site,
            args.aoi_dir / filename,
            args.coastline_dir / f"{site}.geojson",
        )
        rows.extend(site_rows)
        summaries.append(summary)
    write_csv(args.output, rows)
    args.report.write_text(build_report(summaries, rows), encoding="utf-8")
    gate_text = ", ".join(
        f"{item['site']}: {item['alignment_pass']}" for item in summaries
    )
    print(f"Wrote {len(rows)} endpoint checks; site gates={{{gate_text}}}")


if __name__ == "__main__":
    main()
