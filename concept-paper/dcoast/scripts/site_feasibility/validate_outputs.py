"""Fail-closed checks for D'Coast Phase 0 feasibility artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from geometry_utils import aoi_metrics, load_aoi

SITES = {
    "morowali-imip",
    "cilegon-industrial-coast",
    "teluk-awur-jepara",
    "nusa-lembongan",
}
MONTHLY_FIELDS = [
    "site",
    "site_name",
    "year",
    "month",
    "period",
    "total_observations",
    "scene_items",
    "median_scene_cloud_cover",
    "scene_cloud_le_20_observations",
    "scene_cloud_le_50_observations",
    "clear_water_50_observations",
    "clear_water_70_observations",
    "clear_water_80_observations",
    "median_clear_water_fraction",
    "site_longest_observation_gap_days",
    "clear_water_status",
]


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    aoi_dir = args.root / "data" / "aoi_candidates"
    aoi_sites = set()
    for path in sorted(aoi_dir.glob("*.geojson")):
        payload = load_aoi(path)
        properties = payload["features"][0]["properties"]
        if properties["boundary_status"] not in {"official", "derived", "provisional_derived"}:
            raise ValueError(f"Unexpected boundary status in {path}")
        metrics = aoi_metrics(payload)
        if not 40 <= metrics["area_km2"] <= 150:
            raise ValueError(f"Implausible Phase 0 AOI area in {path}: {metrics}")
        aoi_sites.add(properties["site_id"])
    if aoi_sites != SITES:
        raise ValueError(f"AOI sites changed: {aoi_sites}")

    metadata_fields, metadata = read_csv(
        args.root / "data" / "sentinel2_metadata_observations.csv"
    )
    if not metadata_fields or not metadata:
        raise ValueError("Sentinel-2 metadata is empty")
    duplicate_keys = Counter(
        (row["site"], row["acquisition_datetime"]) for row in metadata
    )
    if any(count != 1 for count in duplicate_keys.values()):
        raise ValueError("Duplicate site/acquisition rows found")
    if {row["site"] for row in metadata} != SITES:
        raise ValueError("Metadata sites do not match AOIs")

    monthly_fields, monthly = read_csv(
        args.root / "reports" / "sentinel2_monthly_availability.csv"
    )
    if monthly_fields != MONTHLY_FIELDS:
        raise ValueError(f"Monthly schema changed: {monthly_fields}")
    if len(monthly) != 268:
        raise ValueError(f"Expected 268 site-month rows, got {len(monthly)}")
    if {row["site"] for row in monthly} != SITES:
        raise ValueError("Monthly sites do not match AOIs")
    for row in monthly:
        if row["clear_water_status"] == "BLOCKED_NO_CDSE_OAUTH":
            blocked_fields = (
                "clear_water_50_observations",
                "clear_water_70_observations",
                "clear_water_80_observations",
                "median_clear_water_fraction",
            )
            if any(row[field] != "" for field in blocked_fields):
                raise ValueError("Blocked clear-water values must remain empty")

    score_fields, scores = read_csv(args.root / "reports" / "pilot_site_scores.csv")
    expected_score_fields = [
        "site",
        "role",
        "sentinel_score",
        "validation_score",
        "relevance_score",
        "boundary_score",
        "context_score",
        "manageability_score",
        "total_score",
        "confidence",
        "major_risk",
    ]
    if score_fields != expected_score_fields or len(scores) != 4:
        raise ValueError("Score table schema or row count changed")
    for row in scores:
        component_sum = sum(
            int(row[field])
            for field in (
                "sentinel_score",
                "validation_score",
                "relevance_score",
                "boundary_score",
                "context_score",
                "manageability_score",
            )
        )
        if component_sum != int(row["total_score"]):
            raise ValueError(f"Score sum mismatch for {row['site']}")

    total_size = sum(
        path.stat().st_size for path in args.root.rglob("*") if path.is_file()
    )
    if total_size >= 500 * 1024 * 1024:
        raise ValueError(f"Phase 0 tree exceeds 500 MB: {total_size}")
    print(
        f"READY_PHASE0: 4 AOIs, {len(metadata)} acquisitions, "
        f"{len(monthly)} site-month rows, {total_size} bytes"
    )


if __name__ == "__main__":
    main()
