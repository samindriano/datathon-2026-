"""Fail-closed validation for D'Coast Phase 0.7 AOI-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from audit_aoi_coastline import ALIGNMENT_GATE_M, SITES, audit_site

ALIGNMENT_FIELDS = [
    "site",
    "reference_point",
    "aoi_longitude",
    "aoi_latitude",
    "nearest_big_longitude",
    "nearest_big_latitude",
    "distance_m",
    "alignment_gate_m",
    "alignment_pass",
    "big_objectid",
    "big_name",
    "big_remark",
    "big_coastline_type_code",
    "big_coastline_type",
    "big_source_code",
    "big_source",
    "big_source_year",
    "big_publication_year",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    aoi_dir = args.root / "data" / "aoi_candidates"
    coastline_dir = args.root / "data" / "big_coastline"
    fields, rows = read_csv(args.root / "reports" / "phase07_aoi_alignment.csv")
    if fields != ALIGNMENT_FIELDS or len(rows) != 4:
        raise ValueError("Phase 0.7 alignment schema or row count changed")
    if {(row["site"], row["reference_point"]) for row in rows} != {
        (site, endpoint) for site in SITES for endpoint in ("north", "south")
    }:
        raise ValueError("Phase 0.7 endpoint inventory changed")
    if any(float(row["alignment_gate_m"]) != ALIGNMENT_GATE_M for row in rows):
        raise ValueError("Phase 0.7 alignment gate changed")

    recomputed_rows = []
    feature_counts = {}
    for site, filename in SITES.items():
        coastline_path = coastline_dir / f"{site}.geojson"
        coastline = json.loads(coastline_path.read_text(encoding="utf-8"))
        if coastline.get("type") != "FeatureCollection" or not coastline.get("features"):
            raise ValueError(f"Missing BIG coastline features for {site}")
        provenance = coastline.get("dcoast_provenance", {})
        if provenance.get("source") != "Badan Informasi Geospasial":
            raise ValueError(f"Missing BIG provenance for {site}")
        site_rows, summary = audit_site(
            site,
            aoi_dir / filename,
            coastline_path,
        )
        recomputed_rows.extend(site_rows)
        feature_counts[site] = summary["feature_count"]
    expected = {
        (row["site"], row["reference_point"]): row for row in recomputed_rows
    }
    for row in rows:
        reference = expected[(row["site"], row["reference_point"])]
        if abs(float(row["distance_m"]) - float(reference["distance_m"])) > 0.01:
            raise ValueError("Stored AOI alignment distance does not reproduce")
        if int(row["alignment_pass"]) != int(reference["alignment_pass"]):
            raise ValueError("Stored AOI alignment verdict does not reproduce")
    if any(int(row["alignment_pass"]) for row in rows):
        raise ValueError("Current provisional AOIs unexpectedly pass the frozen gate")

    extent_path = (
        args.root
        / "data"
        / "reference_extents"
        / "teluk_awur_published_study_extent.geojson"
    )
    extent = json.loads(extent_path.read_text(encoding="utf-8"))
    feature = extent["features"][0]
    properties = feature["properties"]
    ring = feature["geometry"]["coordinates"][0]
    if (
        properties["geometry_role"] != "published_study_extent"
        or properties["reported_station_count"] != 110
        or ring[0] != ring[-1]
    ):
        raise ValueError("Published Teluk Awur study extent contract changed")
    longitudes = {round(point[0], 8) for point in ring}
    latitudes = {round(point[1], 8) for point in ring}
    if longitudes != {110.58333333, 110.7} or latitudes != {-6.65, -6.58333333}:
        raise ValueError("Published Teluk Awur map envelope changed")

    contract = (
        args.root / "docs" / "teluk_awur_validation_data_contract.md"
    ).read_text(encoding="utf-8")
    request = (
        args.root / "docs" / "teluk_awur_data_request_draft.md"
    ).read_text(encoding="utf-8")
    if "At least 100 uniquely georeferenced" not in contract:
        raise ValueError("Technical benchmark acceptance gate is missing")
    if "draft only; not sent" not in request.lower():
        raise ValueError("Data request must remain explicitly unsent")
    report = (args.root / "reports" / "phase07_aoi_review.md").read_text(
        encoding="utf-8"
    )
    if "NOT PHASE 1 AUTHORIZATION" not in report:
        raise ValueError("Phase 0.7 report scope warning is missing")

    total_size = sum(
        path.stat().st_size for path in args.root.rglob("*") if path.is_file()
    )
    if total_size >= 500 * 1024 * 1024:
        raise ValueError(f"D'Coast tree exceeds 500 MB: {total_size}")
    print(
        "READY_PHASE07: "
        f"BIG features={feature_counts}, 4 endpoint checks, "
        f"both provisional AOIs fail <= {ALIGNMENT_GATE_M:.0f} m gate, "
        f"{total_size} bytes"
    )


if __name__ == "__main__":
    main()
