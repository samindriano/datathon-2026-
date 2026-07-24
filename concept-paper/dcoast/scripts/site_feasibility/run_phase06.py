"""Run the bounded D'Coast Phase 0.6 clear-water workflow end to end."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    if not os.environ.get("CDSE_CLIENT_ID") or not os.environ.get("CDSE_CLIENT_SECRET"):
        raise RuntimeError(
            "BLOCKED_NO_CDSE_OAUTH: run this command in the PowerShell session "
            "where CDSE_CLIENT_ID and CDSE_CLIENT_SECRET are already set."
        )
    root = Path(__file__).resolve().parents[2]
    scripts = root / "scripts" / "site_feasibility"
    metadata = root / "data" / "sentinel2_metadata_observations.csv"
    quality = root / "reports" / "sentinel2_observation_quality.csv"
    monthly = root / "reports" / "sentinel2_monthly_availability.csv"
    summary = root / "reports" / "phase06_site_quality_summary.csv"
    seasonality = root / "reports" / "phase06_monthly_seasonality.csv"
    assessment = root / "reports" / "phase06_clear_water_assessment.md"
    run(
        [
            sys.executable,
            str(scripts / "query_clear_water_stats.py"),
            "--aoi-dir",
            str(root / "data" / "aoi_candidates"),
            "--metadata",
            str(metadata),
            "--site",
            "cilegon-industrial-coast",
            "--site",
            "teluk-awur-jepara",
            "--output",
            str(quality),
            "--start-year",
            "2021",
            "--end",
            "2026-07-24",
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "build_availability_table.py"),
            "--metadata",
            str(metadata),
            "--clear-water",
            str(quality),
            "--output",
            str(monthly),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "build_phase06_assessment.py"),
            "--quality",
            str(quality),
            "--summary",
            str(summary),
            "--seasonality",
            str(seasonality),
            "--report",
            str(assessment),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "validate_outputs.py"),
            "--root",
            str(root),
        ]
    )
    print("PHASE06_QUERY_COMPLETE: outputs rebuilt and fail-closed validation passed")


if __name__ == "__main__":
    main()
