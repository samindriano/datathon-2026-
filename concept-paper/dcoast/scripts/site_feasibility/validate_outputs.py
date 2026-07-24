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
    "clear_water_50_rejection_pct",
    "clear_water_70_rejection_pct",
    "clear_water_80_rejection_pct",
    "median_clear_water_fraction",
    "site_longest_observation_gap_days",
    "site_longest_clear_water_50_gap_days",
    "site_longest_clear_water_70_gap_days",
    "site_longest_clear_water_80_gap_days",
    "clear_water_status",
]
QUALITY_FIELDS = [
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
SUMMARY_FIELDS = [
    "site",
    "threshold_pct",
    "all_period_observations",
    "all_period_usable",
    "all_period_rejection_pct",
    "usable_2021",
    "usable_2022",
    "usable_2023",
    "usable_2024",
    "usable_2025",
    "full_year_average_usable",
    "full_year_median_usable_per_month",
    "full_year_longest_gap_days",
    "gate_median_month_pass",
    "gate_average_year_pass",
    "gate_max_gap_pass",
]
SEASONALITY_FIELDS = [
    "site",
    "month",
    "observations",
    "usable_50",
    "usable_70",
    "usable_80",
    "median_clear_water_fraction",
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

    quality_fields, quality = read_csv(
        args.root / "reports" / "sentinel2_observation_quality.csv"
    )
    if quality_fields != QUALITY_FIELDS or len(quality) != 848:
        raise ValueError("Observation-quality schema or row count changed")
    quality_keys = Counter(
        (row["site"], row["observation_date"]) for row in quality
    )
    if any(count != 1 for count in quality_keys.values()):
        raise ValueError("Duplicate observation-quality rows found")
    if {row["site"] for row in quality} != {
        "cilegon-industrial-coast",
        "teluk-awur-jepara",
    }:
        raise ValueError("Observation-quality inventory must cover the two locked sites")
    for row in quality:
        if int(row["source_acquisition_count"]) < 1:
            raise ValueError("Source acquisition count must be positive")
        if row["quality_status"] == "BLOCKED_NO_CDSE_OAUTH":
            numeric_fields = QUALITY_FIELDS[3:14]
            if any(row[field] != "" for field in numeric_fields):
                raise ValueError("Blocked observation-quality values must remain empty")
            continue
        counts = [
            int(row[field])
            for field in (
                "water_support_pixel_count",
                "valid_water_pixel_count",
                "clear_water_pixel_count",
                "cloud_shadow_pixel_count",
                "no_data_pixel_count",
            )
        ]
        support, valid, clear, cloud_shadow, no_data = counts
        if min(counts) < 0 or valid > support or clear > valid or cloud_shadow > valid:
            raise ValueError("Invalid observation-quality pixel counts")
        if valid + no_data != support:
            raise ValueError("Valid and no-data pixels do not sum to support")
        fractions = [
            float(row[field])
            for field in (
                "clear_water_fraction",
                "cloud_shadow_fraction",
                "no_data_fraction",
            )
        ]
        if any(not 0.0 <= value <= 1.0 for value in fractions):
            raise ValueError("Observation-quality fraction outside [0, 1]")
        flags = tuple(int(row[field]) for field in ("quality_50", "quality_70", "quality_80"))
        if not flags[0] >= flags[1] >= flags[2]:
            raise ValueError("Observation-quality threshold flags are not monotonic")

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
                "clear_water_50_rejection_pct",
                "clear_water_70_rejection_pct",
                "clear_water_80_rejection_pct",
                "median_clear_water_fraction",
                "site_longest_clear_water_50_gap_days",
                "site_longest_clear_water_70_gap_days",
                "site_longest_clear_water_80_gap_days",
            )
            if any(row[field] != "" for field in blocked_fields):
                raise ValueError("Blocked clear-water values must remain empty")

    summary_fields, summary = read_csv(
        args.root / "reports" / "phase06_site_quality_summary.csv"
    )
    if summary_fields != SUMMARY_FIELDS or len(summary) != 6:
        raise ValueError("Phase 0.6 summary schema or row count changed")
    summary_keys = {(row["site"], int(row["threshold_pct"])) for row in summary}
    expected_summary_keys = {
        (site, threshold)
        for site in ("cilegon-industrial-coast", "teluk-awur-jepara")
        for threshold in (50, 70, 80)
    }
    if summary_keys != expected_summary_keys:
        raise ValueError("Phase 0.6 summary site-threshold inventory changed")
    for site in ("cilegon-industrial-coast", "teluk-awur-jepara"):
        site_rows = sorted(
            (row for row in summary if row["site"] == site),
            key=lambda row: int(row["threshold_pct"]),
        )
        usable = [int(row["all_period_usable"]) for row in site_rows]
        if not usable[0] >= usable[1] >= usable[2]:
            raise ValueError(f"Summary threshold counts are not monotonic for {site}")
    frozen_70 = {
        row["site"]: row
        for row in summary
        if int(row["threshold_pct"]) == 70
    }
    if (
        int(frozen_70["cilegon-industrial-coast"]["all_period_usable"]) != 0
        or tuple(
            int(frozen_70["cilegon-industrial-coast"][field])
            for field in (
                "gate_median_month_pass",
                "gate_average_year_pass",
                "gate_max_gap_pass",
            )
        )
        != (0, 0, 0)
    ):
        raise ValueError("Frozen Cilegon 70% no-go evidence changed")
    if tuple(
        int(frozen_70["teluk-awur-jepara"][field])
        for field in (
            "gate_median_month_pass",
            "gate_average_year_pass",
            "gate_max_gap_pass",
        )
    ) != (1, 1, 0):
        raise ValueError("Frozen Teluk Awur 70% benchmark evidence changed")

    seasonality_fields, seasonality = read_csv(
        args.root / "reports" / "phase06_monthly_seasonality.csv"
    )
    if seasonality_fields != SEASONALITY_FIELDS or len(seasonality) != 24:
        raise ValueError("Phase 0.6 seasonality schema or row count changed")
    seasonality_keys = {
        (row["site"], int(row["month"])) for row in seasonality
    }
    expected_seasonality_keys = {
        (site, month)
        for site in ("cilegon-industrial-coast", "teluk-awur-jepara")
        for month in range(1, 13)
    }
    if seasonality_keys != expected_seasonality_keys:
        raise ValueError("Phase 0.6 seasonality inventory changed")
    assessment = args.root / "reports" / "phase06_clear_water_assessment.md"
    assessment_text = assessment.read_text(encoding="utf-8")
    if "NO_GO_CILEGON_FOR_PHASE1" not in assessment_text:
        raise ValueError("Phase 0.6 assessment verdict is missing")

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
        f"READY_PHASE06: 4 AOIs, {len(metadata)} acquisitions, "
        f"{len(quality)} quality rows, {len(monthly)} site-month rows, {total_size} bytes"
    )


if __name__ == "__main__":
    main()
