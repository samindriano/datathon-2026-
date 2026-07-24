"""Create a transparent acquisition inventory when CDSE OAuth is unavailable."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

TARGET_SITES = {"cilegon-industrial-coast", "teluk-awur-jepara"}
FIELDS = [
    "site",
    "acquisition_datetime",
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
    "status",
    "method",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.metadata.open(encoding="utf-8", newline="") as handle:
        metadata = list(csv.DictReader(handle))
    keys = sorted(
        {
            (row["site"], row["acquisition_datetime"])
            for row in metadata
            if row["site"] in TARGET_SITES
        }
    )
    rows = []
    for site, stamp in keys:
        row = {field: "" for field in FIELDS}
        row.update(
            {
                "site": site,
                "acquisition_datetime": stamp,
                "status": "BLOCKED_NO_CDSE_OAUTH",
                "method": (
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
