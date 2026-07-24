"""Small dependency-free geometry helpers for Phase 0 feasibility AOIs."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

EARTH_RADIUS_KM = 6371.0088


def haversine_km(first: list[float], second: list[float]) -> float:
    lon1, lat1 = map(math.radians, first)
    lon2, lat2 = map(math.radians, second)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    value = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(value))


def polygon_area_km2(ring: list[list[float]]) -> float:
    """Approximate a small lon/lat polygon in a local equirectangular plane."""
    points = ring[:-1] if ring and ring[0] == ring[-1] else ring
    if len(points) < 3:
        return 0.0
    mean_lat = math.radians(sum(point[1] for point in points) / len(points))
    projected = [
        (
            EARTH_RADIUS_KM * math.radians(point[0]) * math.cos(mean_lat),
            EARTH_RADIUS_KM * math.radians(point[1]),
        )
        for point in points
    ]
    twice_area = 0.0
    for index, (x1, y1) in enumerate(projected):
        x2, y2 = projected[(index + 1) % len(projected)]
        twice_area += x1 * y2 - x2 * y1
    return abs(twice_area) / 2.0


def load_aoi(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection" or len(payload.get("features", [])) != 1:
        raise ValueError(f"{path} must contain exactly one GeoJSON feature")
    feature = payload["features"][0]
    geometry = feature.get("geometry", {})
    if geometry.get("type") != "Polygon":
        raise ValueError(f"{path} must contain a Polygon")
    ring = geometry.get("coordinates", [[]])[0]
    if len(ring) < 4 or ring[0] != ring[-1]:
        raise ValueError(f"{path} polygon must be closed")
    return payload


def aoi_metrics(payload: dict[str, Any]) -> dict[str, float]:
    feature = payload["features"][0]
    ring = feature["geometry"]["coordinates"][0]
    coastline = feature["properties"]["coastline_reference"]
    return {
        "area_km2": polygon_area_km2(ring),
        "coastline_length_km": haversine_km(coastline[0], coastline[1]),
    }
