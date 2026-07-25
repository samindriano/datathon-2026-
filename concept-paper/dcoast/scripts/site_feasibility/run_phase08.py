"""Generate and audit D'Coast Phase 0.8 AOI redesign candidates.

This task is intentionally fail-closed. It creates water-side candidate strips
from BIG coastline anchor points and scores them, but it does not promote an AOI
to ``data/aoi_locked`` until land overlap has been independently verified with
an official land polygon or an accepted water mask and domain review is recorded.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from audit_aoi_coastline import ALIGNMENT_GATE_M, nearest_feature

EARTH_RADIUS_M = 6_371_008.8
LAND_OVERLAP_STATUS = "UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK"


@dataclass(frozen=True)
class CandidateSpec:
    site_id: str
    site_name: str
    role: str
    variant: str
    coast_north: tuple[float, float]
    coast_south: tuple[float, float]
    offshore_shift_lon: float
    relevance_score: int
    reference_score: int
    rationale: str
    source_feature_ids: tuple[int, ...]


SPECS: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        site_id="cilegon-industrial-coast",
        site_name="Cilegon industrial coast",
        role="operational_pilot_candidate",
        variant="compact",
        coast_north=(105.991740, -5.922928),
        coast_south=(105.919901, -6.053542),
        offshore_shift_lon=0.0181,
        relevance_score=18,
        reference_score=8,
        rationale=(
            "Two-kilometre-class westward screening strip anchored to the nearest "
            "BIG coastline positions identified in Phase 0.7. It is a geometry "
            "candidate only and does not claim an industrial-estate, port, outfall, "
            "or jurisdiction boundary."
        ),
        source_feature_ids=(2424,),
    ),
    CandidateSpec(
        site_id="cilegon-industrial-coast",
        site_name="Cilegon industrial coast",
        role="operational_pilot_candidate",
        variant="extended",
        coast_north=(105.991740, -5.922928),
        coast_south=(105.919901, -6.053542),
        offshore_shift_lon=0.0362,
        relevance_score=18,
        reference_score=10,
        rationale=(
            "Four-kilometre-class westward screening strip using the same BIG "
            "anchors as the compact candidate and additional offshore comparison "
            "water. Full shoreline conformance and land exclusion remain unverified."
        ),
        source_feature_ids=(2424,),
    ),
    CandidateSpec(
        site_id="teluk-awur-jepara",
        site_name="Teluk Awur, Jepara",
        role="technical_benchmark_candidate",
        variant="compact",
        coast_north=(110.645513, -6.583577),
        coast_south=(110.647297, -6.648355),
        offshore_shift_lon=0.0182,
        relevance_score=18,
        reference_score=8,
        rationale=(
            "Two-kilometre-class westward benchmark strip. The landward anchors "
            "come from BIG features inside the published 2024 map envelope; the "
            "polygon does not reproduce or infer the 110 sampling stations."
        ),
        source_feature_ids=(40273, 40267),
    ),
    CandidateSpec(
        site_id="teluk-awur-jepara",
        site_name="Teluk Awur, Jepara",
        role="technical_benchmark_candidate",
        variant="extended",
        coast_north=(110.645513, -6.583577),
        coast_south=(110.647297, -6.648355),
        offshore_shift_lon=0.0364,
        relevance_score=18,
        reference_score=10,
        rationale=(
            "Four-kilometre-class westward benchmark strip that remains within the "
            "published study envelope in longitude while adding offshore comparison "
            "water. It remains a provisional product-design geometry."
        ),
        source_feature_ids=(40273, 40267),
    ),
)


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    value = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(value))


def project(point: tuple[float, float], reference_lat: float) -> tuple[float, float]:
    lon, lat = point
    return (
        math.radians(lon) * EARTH_RADIUS_M * math.cos(math.radians(reference_lat)),
        math.radians(lat) * EARTH_RADIUS_M,
    )


def polygon_area_m2(ring: list[tuple[float, float]]) -> float:
    reference_lat = sum(lat for _, lat in ring[:-1]) / (len(ring) - 1)
    points = [project(point, reference_lat) for point in ring]
    cross_sum = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:]))
    return abs(cross_sum) / 2


def candidate_ring(spec: CandidateSpec) -> list[tuple[float, float]]:
    north = spec.coast_north
    south = spec.coast_south
    offshore_south = (south[0] - spec.offshore_shift_lon, south[1])
    offshore_north = (north[0] - spec.offshore_shift_lon, north[1])
    return [north, south, offshore_south, offshore_north, north]


def orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def proper_intersection(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    return orientation(a, b, c) * orientation(a, b, d) < 0 and orientation(c, d, a) * orientation(c, d, b) < 0


def is_simple_ring(ring: list[tuple[float, float]]) -> bool:
    if len(ring) < 4 or ring[0] != ring[-1]:
        return False
    edges = list(zip(ring, ring[1:]))
    for i, (a, b) in enumerate(edges):
        for j, (c, d) in enumerate(edges):
            if abs(i - j) <= 1 or {i, j} == {0, len(edges) - 1}:
                continue
            if proper_intersection(a, b, c, d):
                return False
    return polygon_area_m2(ring) > 0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(spec: CandidateSpec) -> dict[str, Any]:
    ring = candidate_ring(spec)
    return {
        "type": "FeatureCollection",
        "name": f"{spec.site_id}-{spec.variant}-phase08-candidate",
        "dcoast_provenance": {
            "phase": "0.8",
            "crs": "EPSG:4326",
            "official_reference": "BIG Peta Garis Pantai Skala 1:25.000, publication 2022",
            "derivation": "BIG coastline anchor points plus a fixed westward offshore translation",
            "lock_status": "NOT_LOCKED",
            "lock_blocker": LAND_OVERLAP_STATUS,
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "site_id": spec.site_id,
                    "site_name": spec.site_name,
                    "candidate_role": spec.role,
                    "candidate_variant": spec.variant,
                    "geometry_role": "monitoring_water_candidate",
                    "boundary_status": "provisional_derived_from_big_anchors",
                    "coastline_reference": [list(spec.coast_north), list(spec.coast_south)],
                    "source_big_feature_ids": list(spec.source_feature_ids),
                    "seaward_direction": "west",
                    "offshore_shift_longitude_degrees": spec.offshore_shift_lon,
                    "rationale": spec.rationale,
                    "land_overlap_status": LAND_OVERLAP_STATUS,
                    "warning": (
                        "Do not use for imagery download, quantitative modelling, or operational monitoring "
                        "until the land-overlap/water-mask gate and domain review pass."
                    ),
                },
                "geometry": {"type": "Polygon", "coordinates": [[list(point) for point in ring]]},
            }
        ],
    }


def metric_row(spec: CandidateSpec, payload: dict[str, Any], coastline: dict[str, Any]) -> dict[str, Any]:
    ring = [tuple(point) for point in payload["features"][0]["geometry"]["coordinates"][0]]
    endpoints = [list(spec.coast_north), list(spec.coast_south)]
    endpoint_results = [nearest_feature(point, coastline["features"]) for point in endpoints]
    distances = [result[0] for result in endpoint_results]
    lons = [point[0] for point in ring[:-1]]
    lats = [point[1] for point in ring[:-1]]
    mid_lat = (min(lats) + max(lats)) / 2
    mid_lon = (min(lons) + max(lons)) / 2
    bbox_width_km = haversine_m((min(lons), mid_lat), (max(lons), mid_lat)) / 1000
    bbox_height_km = haversine_m((mid_lon, min(lats)), (mid_lon, max(lats))) / 1000
    area_km2 = polygon_area_m2(ring) / 1_000_000
    coastline_km = haversine_m(spec.coast_north, spec.coast_south) / 1000
    geometry_valid = is_simple_ring(ring)
    alignment_pass = max(distances) <= ALIGNMENT_GATE_M
    manageability_score = 15 if spec.variant == "compact" else 10
    geometry_score = 12 if geometry_valid else 0
    rationale_score = 9
    alignment_score = 25 if alignment_pass else 0
    total_score = (
        alignment_score
        + spec.relevance_score
        + geometry_score
        + manageability_score
        + spec.reference_score
        + rationale_score
    )
    return {
        "site": spec.site_id,
        "variant": spec.variant,
        "role": spec.role,
        "area_km2": f"{area_km2:.3f}",
        "coastline_length_km": f"{coastline_km:.3f}",
        "bbox_width_km": f"{bbox_width_km:.3f}",
        "bbox_height_km": f"{bbox_height_km:.3f}",
        "polygon_parts": 1,
        "geometry_valid": int(geometry_valid),
        "north_endpoint_distance_m": f"{distances[0]:.2f}",
        "south_endpoint_distance_m": f"{distances[1]:.2f}",
        "max_endpoint_distance_m": f"{max(distances):.2f}",
        "alignment_gate_m": f"{ALIGNMENT_GATE_M:.0f}",
        "alignment_pass": int(alignment_pass),
        "land_overlap_status": LAND_OVERLAP_STATUS,
        "sentinel2_tile_intersections": "NOT_REQUERIED_PHASE08",
        "alignment_score": alignment_score,
        "relevance_score": spec.relevance_score,
        "water_geometry_score": geometry_score,
        "manageability_score": manageability_score,
        "reference_water_score": spec.reference_score,
        "rationale_score": rationale_score,
        "total_score": total_score,
        "preferred_candidate": int(spec.variant == "compact"),
        "lock_eligible": 0,
        "lock_blocker": LAND_OVERLAP_STATUS,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, Any]]) -> str:
    table = "\n".join(
        "| {site} | {variant} | {area_km2} | {max_endpoint_distance_m} | {total_score} | {land_overlap_status} |".format(**row)
        for row in rows
    )
    return f"""# D'Coast Phase 0.8 AOI Redesign

Verdict: **CANDIDATES_CREATED; AOI LOCK REMAINS BLOCKED**

## Method

Four water-side candidates were created from BIG coastline anchor points already
identified in Phase 0.7. The candidate polygons extend westward from those
anchors by approximately two kilometres (compact) or four kilometres
(extended). Existing Phase 0.7 AOIs were preserved unchanged.

The endpoint alignment gate remains frozen at <= {ALIGNMENT_GATE_M:.0f} metres.
The score is descriptive and cannot override a failed mandatory gate.

## Candidate comparison

| Site | Variant | Area km2 | Max endpoint distance m | Score / 100 | Land-overlap status |
|---|---:|---:|---:|---:|---|
{table}

## Selection

- Cilegon compact is the preferred Cilegon geometry candidate because it has the
  smaller processing footprint. It is **not locked**.
- Teluk Awur compact is the preferred benchmark geometry candidate because it
  covers the published study corridor with a smaller processing footprint. It
  is **not locked** and does not infer station coordinates.

## Why no AOI is locked

The official BIG source used here is a coastline line layer, not a land polygon
or validated water mask. Endpoint alignment therefore cannot establish that the
entire straight landward chord and polygon are free of land, port structures,
islands, or unsuitable shallow-bottom areas. Domain review is also absent.

Creating `data/aoi_locked/` would overstate the available evidence. The next
bounded step is a land-overlap and water-mask verification of the preferred
compact candidates, followed by human/domain review. This is still Phase 0;
model training and bulk imagery download remain prohibited.
"""


def build_provenance() -> str:
    return """# D'Coast AOI v2 provenance

## Official reference

- Badan Informasi Geospasial (BIG), Peta Garis Pantai Skala 1:25.000,
  publication year 2022.
- Repository extracts: `data/big_coastline/`.
- CRS: EPSG:4326.

## Derived operations

- Phase 0.7 nearest-coastline anchor points were retained exactly.
- Candidate water strips were constructed by translating the two anchor points
  westward by a fixed longitude offset.
- `compact` uses an approximately two-kilometre-class offshore width.
- `extended` uses an approximately four-kilometre-class offshore width.

## Assumptions and limits

- West is treated as the seaward direction for both reviewed corridors.
- The BIG layer is a line reference, not an official monitoring jurisdiction,
  industrial-estate boundary, land polygon, outfall inventory, or water mask.
- The Teluk Awur published extent is reference evidence only. No sample station
  coordinate was inferred from the paper figure.
- No candidate is promoted to `data/aoi_locked/` until land overlap is verified
  and domain review is recorded.
"""


def build_entry_decision(rows: list[dict[str, Any]]) -> str:
    cilegon = next(row for row in rows if row["site"] == "cilegon-industrial-coast" and row["variant"] == "compact")
    teluk = next(row for row in rows if row["site"] == "teluk-awur-jepara" and row["variant"] == "compact")
    return f"""# D'Coast Phase 0.8 Entry Decision

- **CILEGON_AOI_BLOCKED**
- **TELUK_AWUR_AOI_BLOCKED**

Both preferred compact candidates pass the endpoint-alignment calculation in
this redesign (`{cilegon['max_endpoint_distance_m']} m` for Cilegon and
`{teluk['max_endpoint_distance_m']} m` for Teluk Awur), but neither passes the
mandatory land-overlap/domain-review gate.

## Phase 1 decision

Phase 1 remains blocked. The next allowed task is a bounded Phase 0.9 check that
uses an accepted land polygon or reproducible Sentinel-2 water/land mask to
quantify land overlap for the preferred compact candidates. It must not train a
model or bulk-download imagery.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    candidate_dir = root / "data" / "aoi_candidates_v2"
    report_dir = root / "reports"
    docs_dir = root / "docs"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for spec in SPECS:
        payload = build_payload(spec)
        filename = f"{'teluk_awur' if spec.site_id == 'teluk-awur-jepara' else 'cilegon'}_{spec.variant}.geojson"
        (candidate_dir / filename).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        coastline = load_json(root / "data" / "big_coastline" / f"{spec.site_id}.geojson")
        rows.append(metric_row(spec, payload, coastline))

    write_csv(report_dir / "phase08_aoi_candidate_metrics.csv", rows)
    (report_dir / "phase08_aoi_redesign.md").write_text(build_report(rows), encoding="utf-8")
    (report_dir / "phase08_entry_decision.md").write_text(build_entry_decision(rows), encoding="utf-8")
    (docs_dir / "aoi_provenance.md").write_text(build_provenance(), encoding="utf-8")

    locked_dir = root / "data" / "aoi_locked"
    if locked_dir.exists() and any(locked_dir.iterdir()):
        raise RuntimeError("Phase 0.8 is fail-closed: data/aoi_locked must remain empty")
    print("Phase 0.8 candidates and reports written; AOI lock remains blocked")


if __name__ == "__main__":
    main()
