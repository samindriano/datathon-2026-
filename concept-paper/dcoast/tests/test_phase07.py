from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts" / "site_feasibility"
sys.path.insert(0, str(SCRIPT_DIR))

from audit_aoi_coastline import ALIGNMENT_GATE_M, audit_site


class Phase07Tests(unittest.TestCase):
    def test_big_extracts_have_bounded_provenance(self) -> None:
        expected_counts = {
            "cilegon-industrial-coast": 5,
            "teluk-awur-jepara": 62,
        }
        for site, count in expected_counts.items():
            path = ROOT / "data" / "big_coastline" / f"{site}.geojson"
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["features"]), count)
            self.assertEqual(
                payload["dcoast_provenance"]["source"],
                "Badan Informasi Geospasial",
            )
            self.assertEqual(
                payload["dcoast_provenance"]["retrieval_scope"],
                "bounded Phase 0.7 AOI review",
            )

    def test_provisional_aoi_endpoints_fail_frozen_alignment_gate(self) -> None:
        cases = {
            "cilegon-industrial-coast": "cilegon.geojson",
            "teluk-awur-jepara": "teluk_awur.geojson",
        }
        for site, filename in cases.items():
            rows, summary = audit_site(
                site,
                ROOT / "data" / "aoi_candidates" / filename,
                ROOT / "data" / "big_coastline" / f"{site}.geojson",
            )
            self.assertEqual(len(rows), 2)
            self.assertFalse(summary["alignment_pass"])
            self.assertGreater(summary["max_reference_distance_m"], ALIGNMENT_GATE_M)

    def test_published_extent_is_not_labelled_as_station_geometry(self) -> None:
        path = (
            ROOT
            / "data"
            / "reference_extents"
            / "teluk_awur_published_study_extent.geojson"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        properties = payload["features"][0]["properties"]
        self.assertEqual(properties["geometry_role"], "published_study_extent")
        self.assertIn("Do not interpret", properties["prohibited_use"])
        self.assertNotEqual(properties["geometry_role"], "station_geometry")


if __name__ == "__main__":
    unittest.main()
