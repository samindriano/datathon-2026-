"""Build monthly Sentinel-2 feasibility statistics from cached query outputs."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

SITES = [
    "morowali-imip",
    "cilegon-industrial-coast",
    "teluk-awur-jepara",
    "nusa-lembongan",
]


def months(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        month += 1
        if month == 13:
            year += 1
            month = 1


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--clear-water", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    metadata = read_csv(args.metadata)
    clear_rows = read_csv(args.clear_water) if args.clear_water and args.clear_water.exists() else []
    metadata_by_month: dict[tuple[str, int, int], list[dict[str, str]]] = defaultdict(list)
    clear_by_month: dict[tuple[str, int, int], list[float]] = defaultdict(list)
    clear_by_site: dict[str, list[tuple[date, float]]] = defaultdict(list)
    dates_by_site: dict[str, list[date]] = defaultdict(list)
    site_names: dict[str, str] = {}
    for row in metadata:
        stamp = parse_datetime(row["acquisition_datetime"])
        key = (row["site"], stamp.year, stamp.month)
        metadata_by_month[key].append(row)
        dates_by_site[row["site"]].append(stamp.date())
        site_names[row["site"]] = row["site_name"]
    for row in clear_rows:
        if row.get("clear_water_fraction", "") == "":
            continue
        stamp = parse_datetime(
            row.get("acquisition_datetime") or row.get("interval_from", "")
        )
        clear_fraction = float(row["clear_water_fraction"])
        clear_by_month[(row["site"], stamp.year, stamp.month)].append(clear_fraction)
        clear_by_site[row["site"]].append((stamp.date(), clear_fraction))
    start = date(2021, 1, 1)
    end = max((stamp for values in dates_by_site.values() for stamp in values), default=date.today())
    longest_gap = {}
    for site, values in dates_by_site.items():
        ordered = sorted(set(values))
        longest_gap[site] = max(
            ((second - first).days for first, second in zip(ordered, ordered[1:])),
            default="",
        )
    longest_usable_gap: dict[tuple[str, float], int | str] = {}
    for site in SITES:
        for threshold in (0.5, 0.7, 0.8):
            usable_dates = sorted(
                {stamp for stamp, value in clear_by_site[site] if value >= threshold}
            )
            longest_usable_gap[(site, threshold)] = max(
                (
                    (second - first).days
                    for first, second in zip(usable_dates, usable_dates[1:])
                ),
                default="",
            )
    output_rows: list[dict[str, Any]] = []
    for site in SITES:
        for year, month in months(start, end):
            scene_rows = metadata_by_month[(site, year, month)]
            clouds = [
                float(row["scene_cloud_cover_median"])
                for row in scene_rows
                if row["scene_cloud_cover_median"] != ""
            ]
            clear_values = clear_by_month[(site, year, month)]
            clear_available = bool(clear_values)
            usable = {
                threshold: sum(value >= threshold for value in clear_values)
                for threshold in (0.5, 0.7, 0.8)
            }
            rejected = {
                threshold: (
                    f"{100.0 * (1.0 - usable[threshold] / len(clear_values)):.3f}"
                    if clear_values
                    else ""
                )
                for threshold in (0.5, 0.7, 0.8)
            }
            output_rows.append(
                {
                    "site": site,
                    "site_name": site_names.get(site, site),
                    "year": year,
                    "month": month,
                    "period": "2026_partial" if year == 2026 else "2021_2025",
                    "total_observations": len(scene_rows),
                    "scene_items": sum(int(row["scene_items"]) for row in scene_rows),
                    "median_scene_cloud_cover": (
                        f"{statistics.median(clouds):.3f}" if clouds else ""
                    ),
                    "scene_cloud_le_20_observations": sum(value <= 20 for value in clouds),
                    "scene_cloud_le_50_observations": sum(value <= 50 for value in clouds),
                    "clear_water_50_observations": usable[0.5] if clear_available else "",
                    "clear_water_70_observations": usable[0.7] if clear_available else "",
                    "clear_water_80_observations": usable[0.8] if clear_available else "",
                    "clear_water_50_rejection_pct": rejected[0.5],
                    "clear_water_70_rejection_pct": rejected[0.7],
                    "clear_water_80_rejection_pct": rejected[0.8],
                    "median_clear_water_fraction": (
                        f"{statistics.median(clear_values):.6f}" if clear_available else ""
                    ),
                    "site_longest_observation_gap_days": longest_gap.get(site, ""),
                    "site_longest_clear_water_50_gap_days": (
                        longest_usable_gap[(site, 0.5)] if clear_available else ""
                    ),
                    "site_longest_clear_water_70_gap_days": (
                        longest_usable_gap[(site, 0.7)] if clear_available else ""
                    ),
                    "site_longest_clear_water_80_gap_days": (
                        longest_usable_gap[(site, 0.8)] if clear_available else ""
                    ),
                    "clear_water_status": (
                        "AVAILABLE_CDSE_STATISTICAL_API"
                        if clear_available
                        else "BLOCKED_NO_CDSE_OAUTH"
                    ),
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0])
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} monthly rows to {args.output}")


if __name__ == "__main__":
    main()
