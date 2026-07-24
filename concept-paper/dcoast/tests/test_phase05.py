from __future__ import annotations

import csv
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts" / "site_feasibility"
sys.path.insert(0, str(SCRIPT_DIR))

from geometry_utils import aoi_metrics, load_aoi, monitoring_water_feature
from query_clear_water_stats import (
    DIAGNOSTIC_RESOLUTION_DEGREES,
    WGS84_CRS_URI,
    parse_quality_interval,
    post_statistics,
    request_json,
    token,
)
from build_phase06_assessment import build_seasonality, build_summary


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
        row = parse_quality_interval(
            "site",
            interval,
            source_acquisition_count=2,
            processed_at_utc="2026-07-25T02:00:00+00:00",
        )
        self.assertEqual(row["observation_date"], "2026-01-01")
        self.assertEqual(row["source_acquisition_count"], 2)
        self.assertEqual(row["valid_water_pixel_count"], 80)
        self.assertEqual(row["clear_water_pixel_count"], 56)
        self.assertEqual(row["cloud_shadow_pixel_count"], 8)
        self.assertEqual(row["no_data_pixel_count"], 20)
        self.assertEqual(row["clear_water_fraction"], "0.700000")
        self.assertEqual((row["quality_50"], row["quality_70"], row["quality_80"]), (1, 1, 0))
        self.assertEqual(row["quality_status"], "USABLE_70")
        self.assertEqual(row["rejection_reason"], "CLEAR_WATER_BELOW_80")

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
        keys = {(row["site"], row["observation_date"]) for row in rows}
        self.assertEqual(len(keys), len(rows))
        self.assertEqual(len(rows), 848)
        statuses = {row["quality_status"] for row in rows}
        self.assertTrue(
            statuses == {"BLOCKED_NO_CDSE_OAUTH"}
            or statuses
            <= {"USABLE_80", "USABLE_70", "USABLE_50", "REJECTED", "NO_VALID_WATER"}
        )
        if statuses != {"BLOCKED_NO_CDSE_OAUTH"}:
            self.assertTrue(all(row["clear_water_fraction"] != "" for row in rows))
        self.assertEqual(sum(int(row["source_acquisition_count"]) for row in rows), 858)

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

    def test_unauthorized_oauth_has_actionable_error(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {"CDSE_CLIENT_ID": "filled", "CDSE_CLIENT_SECRET": "filled"},
        ):
            with mock.patch(
                "query_clear_water_stats.request_json",
                side_effect=urllib.error.HTTPError(
                    "https://example.invalid",
                    401,
                    "Unauthorized",
                    {},
                    None,
                ),
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "INVALID_CDSE_OAUTH_CLIENT",
                ):
                    token()

    def test_zero_valid_water_fails_quality_gates(self) -> None:
        interval = {
            "interval": {"from": "2026-01-01T00:00:00Z"},
            "outputs": {
                "quality": {
                    "bands": {
                        "B0": {"stats": {"mean": 0.0, "sampleCount": 100}},
                        "B1": {"stats": {"mean": 0.0, "sampleCount": 100}},
                        "B2": {"stats": {"mean": 0.0, "sampleCount": 100}},
                    }
                }
            },
        }
        row = parse_quality_interval("site", interval)
        self.assertEqual(row["quality_status"], "NO_VALID_WATER")
        self.assertEqual(row["rejection_reason"], "ZERO_VALID_WATER")
        self.assertEqual((row["quality_50"], row["quality_70"], row["quality_80"]), (0, 0, 0))

    def test_transient_api_failure_is_retried(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value = response
        with mock.patch(
            "urllib.request.urlopen",
            side_effect=[urllib.error.URLError("temporary"), response],
        ) as urlopen:
            with mock.patch("json.load", return_value={"ok": True}):
                result = request_json(
                    mock.MagicMock(),
                    timeout=1,
                    attempts=2,
                    sleep_fn=lambda _: None,
                )
        self.assertEqual(result, {"ok": True})
        self.assertEqual(urlopen.call_count, 2)

    def test_statistics_payload_uses_wgs84_coordinate_resolution(self) -> None:
        geometry = {
            "type": "Polygon",
            "coordinates": [[[106.0, -6.0], [106.1, -6.0], [106.0, -6.1], [106.0, -6.0]]],
        }
        with mock.patch(
            "query_clear_water_stats.request_json",
            return_value={"data": []},
        ) as request_json_mock:
            post_statistics("not-a-real-token", geometry, "2021-01-01", "2021-02-01")
        request = request_json_mock.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(
            payload["input"]["bounds"]["properties"]["crs"],
            WGS84_CRS_URI,
        )
        self.assertEqual(
            payload["aggregation"]["resx"],
            DIAGNOSTIC_RESOLUTION_DEGREES,
        )
        self.assertEqual(
            payload["aggregation"]["resy"],
            DIAGNOSTIC_RESOLUTION_DEGREES,
        )

    def test_phase06_frozen_gate_summary_matches_verified_output(self) -> None:
        path = ROOT / "reports" / "sentinel2_observation_quality.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        summary = {
            (row["site"], row["threshold_pct"]): row
            for row in build_summary(rows)
        }
        cilegon = summary[("cilegon-industrial-coast", 70)]
        teluk = summary[("teluk-awur-jepara", 70)]
        self.assertEqual(cilegon["all_period_usable"], 0)
        self.assertEqual(
            (
                cilegon["gate_median_month_pass"],
                cilegon["gate_average_year_pass"],
                cilegon["gate_max_gap_pass"],
            ),
            (0, 0, 0),
        )
        self.assertEqual(teluk["all_period_usable"], 167)
        self.assertEqual(teluk["full_year_average_usable"], "29.000")
        self.assertEqual(teluk["full_year_median_usable_per_month"], "2.000")
        self.assertEqual(teluk["full_year_longest_gap_days"], 120)
        self.assertEqual(
            (
                teluk["gate_median_month_pass"],
                teluk["gate_average_year_pass"],
                teluk["gate_max_gap_pass"],
            ),
            (1, 1, 0),
        )

    def test_phase06_seasonality_has_every_site_month(self) -> None:
        path = ROOT / "reports" / "sentinel2_observation_quality.csv"
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        seasonality = build_seasonality(rows)
        self.assertEqual(len(seasonality), 24)
        self.assertEqual(
            {(row["site"], row["month"]) for row in seasonality},
            {
                (site, month)
                for site in ("cilegon-industrial-coast", "teluk-awur-jepara")
                for month in range(1, 13)
            },
        )


if __name__ == "__main__":
    unittest.main()
