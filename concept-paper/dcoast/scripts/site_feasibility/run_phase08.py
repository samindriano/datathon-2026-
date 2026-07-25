"""Generate and audit D'Coast Phase 0.8 AOI redesign candidates.

Phase 0.8 is fail-closed. It traces landward boundaries along connected BIG
coastline segments, builds provisional offshore closures, and reports geometry
and alignment evidence. It never promotes a candidate into ``data/aoi_locked``.
"""

from __future__ import annotations

import csv
import hashlib
import heapq
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from audit_aoi_coastline import ALIGNMENT_GATE_M, line_strings, nearest_feature

EARTH_RADIUS_M = 6_371_008.8
COORDINATE_DECIMALS = 6
ALIGNMENT_SAMPLE_INTERVAL_M = 100.0
CAP_MARGIN_LAT_DEGREES = 0.0005
LAND_OVERLAP_STATUS = "UNVERIFIED_NO_ACCEPTED_LAND_POLYGON_OR_WATER_MASK"
DOMAIN_REVIEW_STATUS = "NOT_REVIEWED"
COINCIDENT_RULE = (
    "For coincident undirected BIG segments, prefer coastline type "
    "highest-tide, mean-sea-level, lowest-tide, indicative, then other; "
    "break remaining ties by the lowest OBJECTID."
)
TYPE_PRIORITY = {2: 0, 1: 1, 3: 2, 4: 3, 999: 4}


Point = tuple[float, float]
EdgeKey = tuple[Point, Point]


@dataclass(frozen=True)
class CandidateSpec:
    site_id: str
    site_name: str
    role: str
    variant: str
    north_anchor: Point
    south_anchor: Point
    offshore_margin_lon: float
    relevance_score: int
    reference_score: int
    rationale: str


@dataclass(frozen=True)
class GraphEdge:
    start: Point
    end: Point
    length_m: float
    feature_id: int
    feature_rank: tuple[int, int]


@dataclass(frozen=True)
class CoastlineTrace:
    points: tuple[Point, ...]
    edge_feature_ids: tuple[int, ...]
    source_feature_ids: tuple[int, ...]
    length_m: float
    coincident_edge_count: int


SPECS: tuple[CandidateSpec, ...] = (
    CandidateSpec(
        site_id="cilegon-industrial-coast",
        site_name="Cilegon industrial coast",
        role="operational_pilot_candidate",
        variant="compact",
        north_anchor=(105.991740, -5.922928),
        south_anchor=(105.919901, -6.053542),
        offshore_margin_lon=0.0181,
        relevance_score=18,
        reference_score=8,
        rationale=(
            "Compact provisional closure around the reviewed BIG coastline trace. "
            "It is a geometry candidate only and does not claim an industrial-estate, "
            "port, outfall, monitoring, or jurisdiction boundary."
        ),
    ),
    CandidateSpec(
        site_id="cilegon-industrial-coast",
        site_name="Cilegon industrial coast",
        role="operational_pilot_candidate",
        variant="extended",
        north_anchor=(105.991740, -5.922928),
        south_anchor=(105.919901, -6.053542),
        offshore_margin_lon=0.0362,
        relevance_score=18,
        reference_score=10,
        rationale=(
            "Extended provisional closure around the same reviewed BIG trace. "
            "Land exclusion and optical suitability remain unverified."
        ),
    ),
    CandidateSpec(
        site_id="teluk-awur-jepara",
        site_name="Teluk Awur, Jepara",
        role="technical_benchmark_candidate",
        variant="compact",
        north_anchor=(110.645513, -6.583577),
        south_anchor=(110.647297, -6.648355),
        offshore_margin_lon=0.0182,
        relevance_score=18,
        reference_score=8,
        rationale=(
            "Compact provisional closure around a connected BIG trace inside the "
            "published study envelope. It does not infer sampling-station coordinates."
        ),
    ),
    CandidateSpec(
        site_id="teluk-awur-jepara",
        site_name="Teluk Awur, Jepara",
        role="technical_benchmark_candidate",
        variant="extended",
        north_anchor=(110.645513, -6.583577),
        south_anchor=(110.647297, -6.648355),
        offshore_margin_lon=0.0364,
        relevance_score=18,
        reference_score=10,
        rationale=(
            "Extended provisional closure around the same connected BIG trace. "
            "It remains a product-design geometry rather than a published study boundary."
        ),
    ),
)


def canonical_point(point: Iterable[float]) -> Point:
    lon, lat = point
    return round(float(lon), COORDINATE_DECIMALS), round(
        float(lat), COORDINATE_DECIMALS
    )


def canonical_edge_key(start: Point, end: Point) -> EdgeKey:
    return (start, end) if start <= end else (end, start)


def haversine_m(start: Point, end: Point) -> float:
    lon1, lat1 = map(math.radians, start)
    lon2, lat2 = map(math.radians, end)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    value = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(value))


def project(point: Point, reference_lat: float) -> Point:
    lon, lat = point
    return (
        math.radians(lon)
        * EARTH_RADIUS_M
        * math.cos(math.radians(reference_lat)),
        math.radians(lat) * EARTH_RADIUS_M,
    )


def polygon_area_m2(ring: list[Point]) -> float:
    if len(ring) < 4 or ring[0] != ring[-1]:
        return 0.0
    reference_lat = sum(lat for _, lat in ring[:-1]) / (len(ring) - 1)
    points = [project(point, reference_lat) for point in ring]
    cross_sum = sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:])
    )
    return abs(cross_sum) / 2


def feature_rank(feature: dict[str, Any]) -> tuple[int, int]:
    properties = feature["properties"]
    object_id = int(properties["OBJECTID"])
    coastline_type = int(properties.get("TIPGPN") or 999)
    return TYPE_PRIORITY.get(coastline_type, 5), object_id


def build_coastline_graph(
    coastline: dict[str, Any],
) -> tuple[
    dict[Point, list[GraphEdge]],
    dict[EdgeKey, GraphEdge],
    dict[EdgeKey, tuple[int, ...]],
    set[int],
]:
    """Build a deterministic undirected graph from BIG coastline segments."""

    selected_edges: dict[EdgeKey, GraphEdge] = {}
    coincident_ids: dict[EdgeKey, set[int]] = {}
    available_feature_ids: set[int] = set()
    for feature in coastline["features"]:
        object_id = int(feature["properties"]["OBJECTID"])
        available_feature_ids.add(object_id)
        rank = feature_rank(feature)
        for line in line_strings(feature["geometry"]):
            for raw_start, raw_end in zip(line, line[1:]):
                start = canonical_point(raw_start)
                end = canonical_point(raw_end)
                if start == end:
                    continue
                key = canonical_edge_key(start, end)
                coincident_ids.setdefault(key, set()).add(object_id)
                edge = GraphEdge(
                    start=start,
                    end=end,
                    length_m=haversine_m(start, end),
                    feature_id=object_id,
                    feature_rank=rank,
                )
                current = selected_edges.get(key)
                if current is None or (edge.feature_rank, key) < (
                    current.feature_rank,
                    key,
                ):
                    selected_edges[key] = edge

    adjacency: dict[Point, list[GraphEdge]] = {}
    for edge in selected_edges.values():
        adjacency.setdefault(edge.start, []).append(edge)
        adjacency.setdefault(edge.end, []).append(edge)
    for point, edges in adjacency.items():
        edges.sort(
            key=lambda edge: (
                other_endpoint(edge, point),
                edge.feature_id,
            )
        )
    coincident = {
        key: tuple(sorted(ids)) for key, ids in coincident_ids.items() if len(ids) > 1
    }
    return adjacency, selected_edges, coincident, available_feature_ids


def other_endpoint(edge: GraphEdge, point: Point) -> Point:
    if point == edge.start:
        return edge.end
    if point == edge.end:
        return edge.start
    raise ValueError("Graph edge does not contain the requested point")


def trace_coastline(
    coastline: dict[str, Any],
    north_anchor: Point,
    south_anchor: Point,
) -> CoastlineTrace:
    """Return the deterministic shortest connected BIG trace between anchors."""

    adjacency, _, coincident, available_ids = build_coastline_graph(coastline)
    start = canonical_point(north_anchor)
    end = canonical_point(south_anchor)
    if start not in adjacency or end not in adjacency:
        raise ValueError("A configured anchor is not a vertex in the BIG extract")

    distances: dict[Point, float] = {start: 0.0}
    parents: dict[Point, tuple[Point, int]] = {}
    queue: list[tuple[float, Point]] = [(0.0, start)]
    while queue:
        current_distance, point = heapq.heappop(queue)
        if current_distance != distances.get(point):
            continue
        if point == end:
            break
        neighbors = sorted(
            (
                other_endpoint(edge, point),
                edge.length_m,
                edge.feature_id,
            )
            for edge in adjacency[point]
        )
        for neighbor, edge_length, feature_id in neighbors:
            candidate_distance = current_distance + edge_length
            if candidate_distance < distances.get(neighbor, math.inf) - 1e-9:
                distances[neighbor] = candidate_distance
                parents[neighbor] = point, feature_id
                heapq.heappush(queue, (candidate_distance, neighbor))

    if end not in distances:
        raise ValueError("No connected BIG coastline trace joins the configured anchors")

    points_reversed = [end]
    edge_ids_reversed: list[int] = []
    cursor = end
    while cursor != start:
        parent, feature_id = parents[cursor]
        edge_ids_reversed.append(feature_id)
        points_reversed.append(parent)
        cursor = parent
    points = tuple(reversed(points_reversed))
    edge_feature_ids = tuple(reversed(edge_ids_reversed))
    source_feature_ids = tuple(sorted(set(edge_feature_ids)))
    if not set(source_feature_ids).issubset(available_ids):
        raise ValueError("Selected trace cites a feature absent from the BIG extract")
    if any(feature_id not in edge_feature_ids for feature_id in source_feature_ids):
        raise ValueError("Selected source feature does not contribute a trace edge")
    return CoastlineTrace(
        points=points,
        edge_feature_ids=edge_feature_ids,
        source_feature_ids=source_feature_ids,
        length_m=distances[end],
        coincident_edge_count=len(coincident),
    )


def sample_polyline(points: tuple[Point, ...], interval_m: float) -> tuple[Point, ...]:
    if interval_m <= 0:
        raise ValueError("Sampling interval must be positive")
    segment_lengths = [
        haversine_m(start, end) for start, end in zip(points, points[1:])
    ]
    total_length = sum(segment_lengths)
    targets = [index * interval_m for index in range(int(total_length // interval_m) + 1)]
    if not targets or total_length - targets[-1] > 1e-6:
        targets.append(total_length)

    samples: list[Point] = []
    segment_index = 0
    traversed = 0.0
    for target in targets:
        while (
            segment_index < len(segment_lengths) - 1
            and traversed + segment_lengths[segment_index] < target - 1e-9
        ):
            traversed += segment_lengths[segment_index]
            segment_index += 1
        length = segment_lengths[segment_index]
        fraction = 0.0 if length == 0 else (target - traversed) / length
        start = points[segment_index]
        end = points[segment_index + 1]
        samples.append(
            (
                start[0] + fraction * (end[0] - start[0]),
                start[1] + fraction * (end[1] - start[1]),
            )
        )
    return tuple(samples)


def percentile_nearest_rank(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("Cannot calculate a percentile from no values")
    index = max(0, math.ceil(quantile * len(values)) - 1)
    return sorted(values)[index]


def full_boundary_alignment(
    trace: CoastlineTrace,
    coastline: dict[str, Any],
) -> dict[str, float | int]:
    samples = sample_polyline(trace.points, ALIGNMENT_SAMPLE_INTERVAL_M)
    distances = [
        nearest_feature(list(point), coastline["features"])[0] for point in samples
    ]
    return {
        "sample_interval_m": ALIGNMENT_SAMPLE_INTERVAL_M,
        "sample_count": len(samples),
        "minimum_m": min(distances),
        "mean_m": sum(distances) / len(distances),
        "p95_m": percentile_nearest_rank(distances, 0.95),
        "maximum_m": max(distances),
    }


def candidate_ring(trace: CoastlineTrace, offshore_margin_lon: float) -> list[Point]:
    """Close the BIG trace with a documented provisional western meridian."""

    west_lon = round(
        min(lon for lon, _ in trace.points) - offshore_margin_lon,
        COORDINATE_DECIMALS,
    )
    north_cap = round(
        max(lat for _, lat in trace.points) + CAP_MARGIN_LAT_DEGREES,
        COORDINATE_DECIMALS,
    )
    south_cap = round(
        min(lat for _, lat in trace.points) - CAP_MARGIN_LAT_DEGREES,
        COORDINATE_DECIMALS,
    )
    start = trace.points[0]
    end = trace.points[-1]
    return list(trace.points) + [
        (end[0], south_cap),
        (west_lon, south_cap),
        (west_lon, north_cap),
        (start[0], north_cap),
        start,
    ]


def orientation(start: Point, end: Point, point: Point) -> float:
    return (end[0] - start[0]) * (point[1] - start[1]) - (
        end[1] - start[1]
    ) * (point[0] - start[0])


def on_segment(start: Point, end: Point, point: Point, epsilon: float = 1e-12) -> bool:
    return (
        min(start[0], end[0]) - epsilon
        <= point[0]
        <= max(start[0], end[0]) + epsilon
        and min(start[1], end[1]) - epsilon
        <= point[1]
        <= max(start[1], end[1]) + epsilon
    )


def segments_intersect(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
    epsilon: float = 1e-12,
) -> bool:
    values = (
        orientation(first_start, first_end, second_start),
        orientation(first_start, first_end, second_end),
        orientation(second_start, second_end, first_start),
        orientation(second_start, second_end, first_end),
    )
    if values[0] * values[1] < -epsilon and values[2] * values[3] < -epsilon:
        return True
    return any(
        abs(value) <= epsilon and on_segment(start, end, point, epsilon)
        for value, start, end, point in (
            (values[0], first_start, first_end, second_start),
            (values[1], first_start, first_end, second_end),
            (values[2], second_start, second_end, first_start),
            (values[3], second_start, second_end, first_end),
        )
    )


def has_self_intersection(ring: list[Point]) -> bool:
    """Check non-adjacent segment intersections with a lightweight spatial grid."""

    reference_lat = sum(lat for _, lat in ring[:-1]) / (len(ring) - 1)
    projected = [project(point, reference_lat) for point in ring]
    segments = list(zip(projected, projected[1:]))
    grid_size = 500.0
    buckets: dict[tuple[int, int], list[int]] = {}
    candidate_pairs: set[tuple[int, int]] = set()
    for index, (start, end) in enumerate(segments):
        min_x = math.floor(min(start[0], end[0]) / grid_size)
        max_x = math.floor(max(start[0], end[0]) / grid_size)
        min_y = math.floor(min(start[1], end[1]) / grid_size)
        max_y = math.floor(max(start[1], end[1]) / grid_size)
        for cell_x in range(min_x, max_x + 1):
            for cell_y in range(min_y, max_y + 1):
                cell = (cell_x, cell_y)
                for other in buckets.get(cell, []):
                    candidate_pairs.add((other, index))
                buckets.setdefault(cell, []).append(index)

    last_index = len(segments) - 1
    for first, second in sorted(candidate_pairs):
        if abs(first - second) <= 1 or {first, second} == {0, last_index}:
            continue
        if segments_intersect(*segments[first], *segments[second]):
            return True
    return False


def polygon_validity(ring: list[Point]) -> dict[str, bool]:
    closed = len(ring) >= 4 and ring[0] == ring[-1]
    nonzero_area = polygon_area_m2(ring) > 0
    non_self_intersection = closed and not has_self_intersection(ring)
    return {
        "closed": closed,
        "nonzero_area": nonzero_area,
        "non_self_intersection": non_self_intersection,
        "valid": closed and nonzero_area and non_self_intersection,
    }


def mandatory_lock_eligible(
    *,
    alignment_pass: bool,
    geometry_valid: bool,
    land_overlap_status: str,
    domain_review_status: str,
) -> bool:
    return (
        alignment_pass
        and geometry_valid
        and land_overlap_status == "VERIFIED_NO_MATERIAL_LAND_OVERLAP"
        and domain_review_status == "APPROVED"
    )


def build_payload(
    spec: CandidateSpec,
    trace: CoastlineTrace,
) -> dict[str, Any]:
    ring = candidate_ring(trace, spec.offshore_margin_lon)
    return {
        "type": "FeatureCollection",
        "name": f"{spec.site_id}-{spec.variant}-phase08-candidate",
        "dcoast_provenance": {
            "phase": "0.8",
            "crs": "EPSG:4326",
            "official_reference": (
                "BIG Peta Garis Pantai Skala 1:25.000, publication 2022"
            ),
            "landward_boundary_method": (
                "Deterministic shortest connected trace over actual BIG segments"
            ),
            "coincident_segment_rule": COINCIDENT_RULE,
            "offshore_boundary_method": (
                "Provisional western meridian placed beyond the westernmost trace "
                "longitude, with fixed 0.0005-degree north/south caps"
            ),
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
                    "geometry_role": "provisional_monitoring_candidate",
                    "boundary_status": "provisional_derived_from_big_trace",
                    "coastline_reference": [list(point) for point in trace.points],
                    "coastline_trace_point_count": len(trace.points),
                    "source_big_feature_ids": list(trace.source_feature_ids),
                    "coincident_edge_count": trace.coincident_edge_count,
                    "seaward_direction_assumption": "west",
                    "offshore_margin_longitude_degrees": spec.offshore_margin_lon,
                    "rationale": spec.rationale,
                    "land_overlap_status": LAND_OVERLAP_STATUS,
                    "domain_review_status": DOMAIN_REVIEW_STATUS,
                    "warning": (
                        "Do not use for imagery download, quantitative modelling, "
                        "or operational monitoring until land-overlap and domain-review "
                        "gates pass."
                    ),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[list(point) for point in ring]],
                },
            }
        ],
    }


def metric_row(
    spec: CandidateSpec,
    payload: dict[str, Any],
    trace: CoastlineTrace,
    alignment: dict[str, float | int],
) -> dict[str, Any]:
    ring = [
        tuple(point)
        for point in payload["features"][0]["geometry"]["coordinates"][0]
    ]
    validity = polygon_validity(ring)
    lons = [point[0] for point in ring[:-1]]
    lats = [point[1] for point in ring[:-1]]
    mid_lat = (min(lats) + max(lats)) / 2
    mid_lon = (min(lons) + max(lons)) / 2
    bbox_width_km = (
        haversine_m((min(lons), mid_lat), (max(lons), mid_lat)) / 1000
    )
    bbox_height_km = (
        haversine_m((mid_lon, min(lats)), (mid_lon, max(lats))) / 1000
    )
    area_km2 = polygon_area_m2(ring) / 1_000_000
    chord_km = haversine_m(trace.points[0], trace.points[-1]) / 1000
    alignment_pass = float(alignment["maximum_m"]) <= ALIGNMENT_GATE_M
    manageability_score = 15 if spec.variant == "compact" else 10
    validity_score = 12 if validity["valid"] else 0
    rationale_score = 9
    alignment_score = 25 if alignment_pass else 0
    total_score = (
        alignment_score
        + spec.relevance_score
        + validity_score
        + manageability_score
        + spec.reference_score
        + rationale_score
    )
    lock_eligible = mandatory_lock_eligible(
        alignment_pass=alignment_pass,
        geometry_valid=validity["valid"],
        land_overlap_status=LAND_OVERLAP_STATUS,
        domain_review_status=DOMAIN_REVIEW_STATUS,
    )
    return {
        "site": spec.site_id,
        "variant": spec.variant,
        "role": spec.role,
        "area_km2": f"{area_km2:.3f}",
        "coastline_trace_length_km": f"{trace.length_m / 1000:.3f}",
        "straight_chord_length_km": f"{chord_km:.3f}",
        "trace_to_chord_ratio": f"{trace.length_m / 1000 / chord_km:.3f}",
        "bbox_width_km": f"{bbox_width_km:.3f}",
        "bbox_height_km": f"{bbox_height_km:.3f}",
        "polygon_parts": 1,
        "geometry_closed": int(validity["closed"]),
        "geometry_nonzero_area": int(validity["nonzero_area"]),
        "geometry_non_self_intersection": int(
            validity["non_self_intersection"]
        ),
        "geometry_valid": int(validity["valid"]),
        "alignment_sample_interval_m": f"{float(alignment['sample_interval_m']):.0f}",
        "alignment_sample_count": int(alignment["sample_count"]),
        "alignment_minimum_m": f"{float(alignment['minimum_m']):.2f}",
        "alignment_mean_m": f"{float(alignment['mean_m']):.2f}",
        "alignment_p95_m": f"{float(alignment['p95_m']):.2f}",
        "alignment_maximum_m": f"{float(alignment['maximum_m']):.2f}",
        "alignment_gate_m": f"{ALIGNMENT_GATE_M:.0f}",
        "alignment_pass": int(alignment_pass),
        "source_big_feature_ids": ";".join(
            str(feature_id) for feature_id in trace.source_feature_ids
        ),
        "coincident_edge_count": trace.coincident_edge_count,
        "land_overlap_status": LAND_OVERLAP_STATUS,
        "domain_review_status": DOMAIN_REVIEW_STATUS,
        "sentinel2_tile_intersections": "NOT_REQUERIED_PHASE08",
        "alignment_score": alignment_score,
        "relevance_score": spec.relevance_score,
        "polygon_validity_score": validity_score,
        "manageability_score": manageability_score,
        "reference_score": spec.reference_score,
        "rationale_score": rationale_score,
        "total_score": total_score,
        "preferred_candidate": int(spec.variant == "compact" and validity["valid"]),
        "lock_eligible": int(lock_eligible),
        "lock_blocker": LAND_OVERLAP_STATUS,
    }


def csv_text(rows: list[dict[str, Any]]) -> str:
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=list(rows[0]),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build_report(rows: list[dict[str, Any]]) -> str:
    table = "\n".join(
        "| {site} | {variant} | {area_km2} | {coastline_trace_length_km} | "
        "{alignment_sample_count} | {alignment_minimum_m} | "
        "{alignment_mean_m} | {alignment_p95_m} | {alignment_maximum_m} | "
        "{source_big_feature_ids} | {geometry_valid} | {total_score} |".format(
            **row
        )
        for row in rows
    )
    return f"""# D'Coast Phase 0.8 AOI Redesign

Verdict: **CANDIDATES_REBUILT; AOI LOCK REMAINS BLOCKED**

## Method

The landward boundary is no longer a straight chord. For each site, the runner
builds an undirected graph from the bounded BIG extract and selects the
deterministic shortest connected trace between the reviewed north and south
anchors. Coincident segments use this frozen rule: {COINCIDENT_RULE}

Every complete landward trace is sampled at a fixed
{ALIGNMENT_SAMPLE_INTERVAL_M:.0f} m interval. The frozen <=
{ALIGNMENT_GATE_M:.0f} m gate applies to the maximum sampled distance, while
minimum, mean, p95, maximum, sample count, and interval are all persisted.
Because the boundary is constructed from the selected BIG segments, these
statistics are a full-boundary conformance check, not independent evidence of
shoreline accuracy or water coverage.

The offshore closure remains provisional: a western meridian is placed beyond
the westernmost point of the trace, with fixed north/south caps. This is not a
water mask, official monitoring boundary, industrial-estate boundary, port,
outfall, or jurisdiction boundary.

## Candidate comparison

| Site | Variant | Area km2 | BIG trace km | Samples | Min m | Mean m | P95 m | Max m | BIG feature IDs | Valid | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
{table}

## Selection

- The compact candidate remains the preferred geometry within each site because
  it has the smaller provisional processing footprint.
- Cilegon remains no-go for the current optical pipeline under Phase 0.6; this
  geometry work does not reverse that decision.
- Teluk Awur remains a technical benchmark candidate and does not infer any
  published sampling-station coordinate.

## Why no AOI is locked

`polygon_validity_score` covers only closure, non-zero area, and absence of
self-intersection. It does not prove water coverage or land exclusion. The
official BIG source is a coastline line layer, not an accepted land polygon or
water mask, and domain review remains absent. Mandatory gates set
`lock_eligible=0` regardless of the descriptive total score.
"""


def build_provenance(rows: list[dict[str, Any]]) -> str:
    source_lines = "\n".join(
        f"- `{row['site']}`: BIG feature IDs `{row['source_big_feature_ids']}`; "
        f"{row['alignment_sample_count']} samples at "
        f"{row['alignment_sample_interval_m']} m."
        for row in rows
        if row["variant"] == "compact"
    )
    return f"""# D'Coast AOI v2 provenance

## Official reference

- Badan Informasi Geospasial (BIG), Peta Garis Pantai Skala 1:25.000,
  publication year 2022.
- Repository extracts: `data/big_coastline/`.
- CRS: EPSG:4326.

## Deterministic landward trace

- All BIG line segments are canonicalized to six decimal places.
- The landward edge is the shortest connected graph trace between reviewed
  anchors, not a straight endpoint chord.
- {COINCIDENT_RULE}
- Every persisted source feature ID exists in the site extract and contributes
  at least one selected trace edge.

{source_lines}

## Provisional offshore closure

- `compact` and `extended` place a fixed western meridian beyond the westernmost
  trace longitude.
- Fixed 0.0005-degree caps are added beyond the trace latitude extrema to avoid
  substituting a coastline chord.
- This derivation is provisional and does not prove land exclusion or official
  monitoring relevance.

## Versioning and limits

- Phase 0.6 and Phase 0.7 artifacts remain unchanged.
- Phase 0.8 candidates live only under `data/aoi_candidates_v2/`.
- No candidate is promoted to `data/aoi_locked/`.
- Any future lock must identify the source candidate, land/water verification,
  domain reviewer, and decision commit.
"""


def build_entry_decision(rows: list[dict[str, Any]]) -> str:
    compact_rows = [row for row in rows if row["variant"] == "compact"]
    evidence = "\n".join(
        f"- `{row['site']}`: {row['alignment_sample_count']} samples at "
        f"{row['alignment_sample_interval_m']} m; minimum "
        f"{row['alignment_minimum_m']} m, mean "
        f"{row['alignment_mean_m']} m, p95 {row['alignment_p95_m']} m, "
        f"maximum {row['alignment_maximum_m']} m; BIG features "
        f"`{row['source_big_feature_ids']}`."
        for row in compact_rows
    )
    return f"""# D'Coast Phase 0.8 Entry Decision

- **CILEGON_AOI_BLOCKED**
- **TELUK_AWUR_AOI_BLOCKED**

The complete BIG-derived landward traces pass the frozen alignment gate:

{evidence}

These zero-distance results confirm conformance of the persisted full boundary
to the selected contributing BIG segments. They are not independent evidence
of shoreline accuracy, water coverage, or land exclusion.

Both compact polygons pass polygon validity, but neither passes land-overlap or
domain-review gates. Their descriptive scores cannot override those mandatory
fail-closed gates.

## Next-phase verdict

**GO_FOR_PHASE09_GEOMETRY_CHECK_ONLY**

This verdict allows only a separately approved, bounded land-overlap/water-mask
verification. Phase 0.9 has not been started here. Phase 1, model training, bulk
imagery download, source attribution, and operational claims remain blocked.
The Teluk Awur data-request draft remains unsent.
"""


def canonical_json(payload: dict[str, Any]) -> str:
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


def generate_artifacts(root: Path) -> dict[Path, str]:
    rows: list[dict[str, Any]] = []
    artifacts: dict[Path, str] = {}
    trace_cache: dict[
        tuple[str, Point, Point],
        tuple[CoastlineTrace, dict[str, float | int]],
    ] = {}
    for spec in SPECS:
        coastline = json.loads(
            (
                root / "data" / "big_coastline" / f"{spec.site_id}.geojson"
            ).read_text(encoding="utf-8")
        )
        cache_key = (spec.site_id, spec.north_anchor, spec.south_anchor)
        if cache_key not in trace_cache:
            trace = trace_coastline(
                coastline,
                spec.north_anchor,
                spec.south_anchor,
            )
            trace_cache[cache_key] = (
                trace,
                full_boundary_alignment(trace, coastline),
            )
        trace, alignment = trace_cache[cache_key]
        payload = build_payload(spec, trace)
        stem = (
            "teluk_awur"
            if spec.site_id == "teluk-awur-jepara"
            else "cilegon"
        )
        artifacts[
            Path("data") / "aoi_candidates_v2" / f"{stem}_{spec.variant}.geojson"
        ] = canonical_json(payload)
        rows.append(metric_row(spec, payload, trace, alignment))

    artifacts[
        Path("reports") / "phase08_aoi_candidate_metrics.csv"
    ] = csv_text(rows)
    artifacts[Path("reports") / "phase08_aoi_redesign.md"] = build_report(rows)
    artifacts[
        Path("reports") / "phase08_entry_decision.md"
    ] = build_entry_decision(rows)
    artifacts[Path("docs") / "aoi_provenance.md"] = build_provenance(rows)
    return artifacts


def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content.replace("\r\n", "\n"))


def write_artifacts(root: Path) -> dict[Path, str]:
    artifacts = generate_artifacts(root)
    hashes: dict[Path, str] = {}
    for relative_path, content in sorted(
        artifacts.items(),
        key=lambda item: item[0].as_posix(),
    ):
        path = root / relative_path
        write_text_lf(path, content)
        hashes[relative_path] = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()
    return hashes


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    hashes = write_artifacts(root)
    locked_dir = root / "data" / "aoi_locked"
    if locked_dir.exists() and any(locked_dir.iterdir()):
        raise RuntimeError(
            "Phase 0.8 is fail-closed: data/aoi_locked must remain empty"
        )
    print(
        "PHASE08_COMPLETE: "
        f"{len(hashes)} canonical artifacts; AOI lock remains blocked"
    )


if __name__ == "__main__":
    main()
