"""Run the bounded D'Coast Phase 0.7 AOI-review workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    scripts = root / "scripts" / "site_feasibility"
    coastline_dir = root / "data" / "big_coastline"
    run(
        [
            sys.executable,
            str(scripts / "query_big_coastline.py"),
            "--output-dir",
            str(coastline_dir),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "audit_aoi_coastline.py"),
            "--aoi-dir",
            str(root / "data" / "aoi_candidates"),
            "--coastline-dir",
            str(coastline_dir),
            "--output",
            str(root / "reports" / "phase07_aoi_alignment.csv"),
            "--report",
            str(root / "reports" / "phase07_aoi_review.md"),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "validate_phase07.py"),
            "--root",
            str(root),
        ]
    )
    print("PHASE07_COMPLETE: AOI review rebuilt; no Phase 1 work was started")


if __name__ == "__main__":
    main()
