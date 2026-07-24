"""Create a transparent acquisition inventory when CDSE OAuth is unavailable."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

TARGET_SITES = {"cilegon-industrial-coast", "teluk-awur-jepara"}
FIELDS = [
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.metadata.open(encoding="utf-8", newline="") as handle:
        metadata = list(csv.DictReader(handle))
    counts: dict[tuple[str, str], int] = {}
    for row in metadata:
        if row["site"] not in TARGET_SITES:
            continue
        key = (row["site"], row["acquisition_datetime"][:10])
        counts[key] = counts.get(key, 0) + 1
    rows = []
    for (site, observation_date), source_count in sorted(counts.items()):
        row = {field: "" for field in FIELDS}
        row.update(
            {
                "site": site,
                "observation_date": observation_date,
                "source_acquisition_count": source_count,
                "quality_status": "BLOCKED_NO_CDSE_OAUTH",
                "rejection_reason": "CDSE_OAUTH_MISSING",
                "api_provenance": (
                    "Awaiting CDSE Statistical API; no scene-cloud substitution"
                ),
            }
        )
        rows.append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} blocked observation rows to {args.output}")


if __name__ == "__main__":
    main()
