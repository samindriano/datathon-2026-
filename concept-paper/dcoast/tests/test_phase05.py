from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts" / "site_feasibility"
sys.path.insert(0, str(SCRIPT_DIR))

from geometry_utils import aoi_metrics, load_aoi, monitoring_water_feature
from query_clear_water_stats import parse_quality_interval, token


class Phase05Tests(unittest.TestCase):
    def test_refined_aoi_is_closed_water_polygon(self) -> None:
        for filename in ("cilegon.geojson", "teluk_awur.geojson"):
            payload = load_aoi(ROOT / "data" / "aoi_candidates" / filename)
            feature = monitoring_water_feature(payload)
            self.assertEqual(feature["properties"]["geometry_role"], "monitoring_water")
            ring = feature["geometry"]["coordinates"][0]
            self.assertEqual(ring[0], ring[-1])
            metrics = aoi_metrics(payload)
            self.assertGreaterEqual(metrics["area_km2"], 40)
            self.assertLessEqual(metrics["area_km2"], 150)

    def test_quality_counts_and_thresholds(self) -> None:
        interval = {
            "interval": {"from": "2026-01-01T00:00:00Z"},
            "outputs": {
                "quality": {
                    "bands": {
                        "B0": {"stats": {"mean": 0.56, "sampleCount": 100}},
                        "B1": {"stats": {"mean": 0.08, "sampleCount": 100}},
                        "B2": {"stats": {"mean": 0.80, "sampleCount": 100}},
                    }
                }
            },
        }
        row = parse_quality_interval("site", interval)
        self.assertEqual(row["valid_water_pixel_count"], 80)
        self.assertEqual(row["clear_water_pixel_count"], 56)
        self.assertEqual(row["cloud_shadow_pixel_count"], 8)
        self.assertEqual(row["no_data_pixel_count"], 20)
        self.assertEqual(row["clear_water_fraction"], "0.700000")
        self.assertEqual((row["quality_50"], row["quality_70"], row["quality_80"]), (1, 1, 0))

    def test_missing_api_band_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing Statistical API fields"):
            parse_quality_interval(
                "site",
                {
                    "outputs": {
                        "quality": {
                            "bands": {
                                "B0": {"stats": {"mean": 0.5, "sampleCount": 10}}
                            }
                        }
                    }
                },
            )

    def test_quality_inventory_keys_are_unique(self) -> None:
        path = ROOT / "reports" / "sentinel2_observation_quality.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        keys = {(row["site"], row["acquisition_datetime"]) for row in rows}
        self.assertEqual(len(keys), len(rows))
        self.assertEqual(len(rows), 858)
        self.assertEqual({row["status"] for row in rows}, {"BLOCKED_NO_CDSE_OAUTH"})
        self.assertTrue(all(row["clear_water_fraction"] == "" for row in rows))

    def test_local_secret_files_are_ignored(self) -> None:
        gitignore = (ROOT.parents[1] / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env.*", gitignore)

    def test_missing_oauth_fails_before_api_call(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {"CDSE_CLIENT_ID": "", "CDSE_CLIENT_SECRET": ""},
        ):
            with self.assertRaisesRegex(RuntimeError, "BLOCKED_NO_CDSE_OAUTH"):
                token()


if __name__ == "__main__":
    unittest.main()
