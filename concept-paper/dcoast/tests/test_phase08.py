from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts" / "site_feasibility"
sys.path.insert(0, str(SCRIPT_DIR))

from run_phase08 import LAND_OVERLAP_STATUS, SPECS, build_payload, candidate_ring, is_simple_ring


class Phase08Tests(unittest.TestCase):
    def test_candidate_payloads_are_valid_closed_epsg4326_polygons(self) -> None:
        for spec in SPECS:
            payload = build_payload(spec)
            self.assertEqual(payload["type"], "FeatureCollection")
            self.assertEqual(payload["dcoast_provenance"]["crs"], "EPSG:4326")
            feature = payload["features"][0]
            self.assertEqual(feature["geometry"]["type"], "Polygon")
            ring = [tuple(point) for point in feature["geometry"]["coordinates"][0]]
            self.assertEqual(ring[0], ring[-1])
            self.assertTrue(is_simple_ring(ring))
            for lon, lat in ring:
                self.assertGreaterEqual(lon, -180)
                self.assertLessEqual(lon, 180)
                self.assertGreaterEqual(lat, -90)
                self.assertLessEqual(lat, 90)

    def test_candidates_preserve_exact_big_anchor_points(self) -> None:
        for spec in SPECS:
            ring = candidate_ring(spec)
            self.assertEqual(ring[0], spec.coast_north)
            self.assertEqual(ring[1], spec.coast_south)

    def test_generated_candidate_files_match_runner_payloads(self) -> None:
        for spec in SPECS:
            stem = "teluk_awur" if spec.site_id == "teluk-awur-jepara" else "cilegon"
            path = ROOT / "data" / "aoi_candidates_v2" / f"{stem}_{spec.variant}.geojson"
            actual = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(actual, build_payload(spec))

    def test_all_candidates_remain_fail_closed(self) -> None:
        directory = ROOT / "data" / "aoi_candidates_v2"
        for path in directory.glob("*.geojson"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["dcoast_provenance"]["lock_status"], "NOT_LOCKED")
            self.assertEqual(payload["dcoast_provenance"]["lock_blocker"], LAND_OVERLAP_STATUS)
            properties = payload["features"][0]["properties"]
            self.assertEqual(properties["land_overlap_status"], LAND_OVERLAP_STATUS)
            self.assertIn("Do not use", properties["warning"])

    def test_metrics_are_monotonic_and_not_lock_eligible(self) -> None:
        path = ROOT / "reports" / "phase08_aoi_candidate_metrics.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 4)
        grouped: dict[str, dict[str, dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row["site"], {})[row["variant"]] = row
            self.assertEqual(row["geometry_valid"], "1")
            self.assertEqual(row["alignment_pass"], "1")
            self.assertEqual(row["lock_eligible"], "0")
            self.assertEqual(row["lock_blocker"], LAND_OVERLAP_STATUS)
            self.assertLessEqual(float(row["max_endpoint_distance_m"]), float(row["alignment_gate_m"]))
        for site_rows in grouped.values():
            self.assertLess(float(site_rows["compact"]["area_km2"]), float(site_rows["extended"]["area_km2"]))
            self.assertEqual(site_rows["compact"]["preferred_candidate"], "1")
            self.assertEqual(site_rows["extended"]["preferred_candidate"], "0")

    def test_no_locked_aoi_is_published(self) -> None:
        locked = ROOT / "data" / "aoi_locked"
        self.assertFalse(locked.exists() and any(locked.iterdir()))


if __name__ == "__main__":
    unittest.main()
