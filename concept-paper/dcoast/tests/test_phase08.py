from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts" / "site_feasibility"
sys.path.insert(0, str(SCRIPT_DIR))

from run_phase08 import (
    ALIGNMENT_GATE_M,
    ALIGNMENT_SAMPLE_INTERVAL_M,
    COINCIDENT_RULE,
    DOMAIN_REVIEW_STATUS,
    LAND_OVERLAP_STATUS,
    SPECS,
    build_coastline_graph,
    build_payload,
    candidate_ring,
    feature_rank,
    full_boundary_alignment,
    generate_artifacts,
    mandatory_lock_eligible,
    metric_row,
    polygon_validity,
    trace_coastline,
    write_artifacts,
)


class Phase08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coastlines = {
            site: json.loads(
                (
                    ROOT / "data" / "big_coastline" / f"{site}.geojson"
                ).read_text(encoding="utf-8")
            )
            for site in {spec.site_id for spec in SPECS}
        }

    def trace_for(self, spec):
        return trace_coastline(
            self.coastlines[spec.site_id],
            spec.north_anchor,
            spec.south_anchor,
        )

    def test_committed_artifacts_match_canonical_generation_exactly(self) -> None:
        artifacts = generate_artifacts(ROOT)
        self.assertEqual(len(artifacts), 8)
        for relative_path, expected in artifacts.items():
            actual = (ROOT / relative_path).read_bytes()
            self.assertEqual(actual, expected.encode("utf-8"), relative_path)

    def test_second_runner_write_is_byte_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = ROOT / "data" / "big_coastline"
            target = root / "data" / "big_coastline"
            target.mkdir(parents=True)
            for path in source.glob("*.geojson"):
                shutil.copy2(path, target / path.name)
            first = write_artifacts(root)
            first_bytes = {
                path: (root / path).read_bytes() for path in first
            }
            second = write_artifacts(root)
            second_bytes = {
                path: (root / path).read_bytes() for path in second
            }
            self.assertEqual(first, second)
            self.assertEqual(first_bytes, second_bytes)

    def test_full_boundary_alignment_uses_fixed_interval_and_maximum_gate(self) -> None:
        for spec in SPECS[::2]:
            trace = self.trace_for(spec)
            statistics = full_boundary_alignment(
                trace,
                self.coastlines[spec.site_id],
            )
            self.assertEqual(
                statistics["sample_interval_m"],
                ALIGNMENT_SAMPLE_INTERVAL_M,
            )
            self.assertGreater(statistics["sample_count"], 2)
            self.assertLessEqual(statistics["minimum_m"], statistics["mean_m"])
            self.assertLessEqual(statistics["mean_m"], statistics["p95_m"])
            self.assertLessEqual(statistics["p95_m"], statistics["maximum_m"])
            self.assertLessEqual(statistics["maximum_m"], ALIGNMENT_GATE_M)

    def test_landward_boundary_is_complete_big_trace_not_straight_chord(self) -> None:
        for spec in SPECS:
            trace = self.trace_for(spec)
            self.assertGreater(len(trace.points), 2)
            chord = ((spec.north_anchor, spec.south_anchor))
            self.assertNotEqual(trace.points, chord)
            payload = build_payload(spec, trace)
            persisted = tuple(
                tuple(point)
                for point in payload["features"][0]["properties"][
                    "coastline_reference"
                ]
            )
            ring = tuple(
                tuple(point)
                for point in payload["features"][0]["geometry"]["coordinates"][0]
            )
            self.assertEqual(persisted, trace.points)
            self.assertEqual(ring[: len(trace.points)], trace.points)

    def test_source_feature_ids_exist_and_contribute_trace_edges(self) -> None:
        for spec in SPECS[::2]:
            coastline = self.coastlines[spec.site_id]
            available = {
                int(feature["properties"]["OBJECTID"])
                for feature in coastline["features"]
            }
            trace = self.trace_for(spec)
            self.assertTrue(set(trace.source_feature_ids).issubset(available))
            for feature_id in trace.source_feature_ids:
                self.assertIn(feature_id, trace.edge_feature_ids)
            payload = build_payload(spec, trace)
            persisted = payload["features"][0]["properties"][
                "source_big_feature_ids"
            ]
            self.assertEqual(persisted, list(trace.source_feature_ids))
        teluk = self.trace_for(
            next(spec for spec in SPECS if spec.site_id == "teluk-awur-jepara")
        )
        self.assertIn(40433, teluk.source_feature_ids)
        self.assertNotIn(40273, teluk.source_feature_ids)

    def test_coincident_feature_resolution_is_deterministic(self) -> None:
        features = []
        for object_id, coastline_type in ((30, 999), (20, 4), (10, 4), (40, 2)):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "OBJECTID": object_id,
                        "TIPGPN": coastline_type,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[110.0, -6.0], [110.1, -6.1]],
                    },
                }
            )
        adjacency, selected, coincident, _ = build_coastline_graph(
            {"type": "FeatureCollection", "features": features}
        )
        self.assertTrue(adjacency)
        self.assertEqual(len(selected), 1)
        edge = next(iter(selected.values()))
        self.assertEqual(edge.feature_id, 40)
        self.assertEqual(feature_rank(features[-1]), (0, 40))
        self.assertEqual(next(iter(coincident.values())), (10, 20, 30, 40))
        self.assertIn("lowest OBJECTID", COINCIDENT_RULE)

    def test_polygon_validity_score_has_narrow_semantics_and_name(self) -> None:
        artifacts = generate_artifacts(ROOT)
        metrics_text = artifacts[
            Path("reports") / "phase08_aoi_candidate_metrics.csv"
        ]
        rows = list(csv.DictReader(metrics_text.splitlines()))
        self.assertNotIn("water_geometry_score", rows[0])
        self.assertIn("polygon_validity_score", rows[0])
        for spec, row in zip(SPECS, rows):
            trace = self.trace_for(spec)
            validity = polygon_validity(
                candidate_ring(trace, spec.offshore_margin_lon)
            )
            expected = "12" if validity["valid"] else "0"
            self.assertEqual(row["polygon_validity_score"], expected)
            self.assertEqual(row["geometry_valid"], str(int(validity["valid"])))

    def test_descriptive_total_score_cannot_override_mandatory_gates(self) -> None:
        self.assertFalse(
            mandatory_lock_eligible(
                alignment_pass=True,
                geometry_valid=True,
                land_overlap_status=LAND_OVERLAP_STATUS,
                domain_review_status=DOMAIN_REVIEW_STATUS,
            )
        )
        for spec in SPECS:
            trace = self.trace_for(spec)
            alignment = full_boundary_alignment(
                trace,
                self.coastlines[spec.site_id],
            )
            payload = build_payload(spec, trace)
            row = metric_row(spec, payload, trace, alignment)
            self.assertGreater(int(row["total_score"]), 0)
            self.assertEqual(row["lock_eligible"], 0)

    def test_candidate_polygons_are_closed_valid_and_not_locked(self) -> None:
        for spec in SPECS:
            trace = self.trace_for(spec)
            payload = build_payload(spec, trace)
            ring = [
                tuple(point)
                for point in payload["features"][0]["geometry"]["coordinates"][0]
            ]
            validity = polygon_validity(ring)
            self.assertTrue(validity["closed"])
            self.assertTrue(validity["nonzero_area"])
            self.assertTrue(validity["non_self_intersection"])
            self.assertTrue(validity["valid"])
            provenance = payload["dcoast_provenance"]
            self.assertEqual(provenance["lock_status"], "NOT_LOCKED")
            self.assertEqual(provenance["lock_blocker"], LAND_OVERLAP_STATUS)

    def test_no_locked_aoi_or_secret_is_published(self) -> None:
        locked = ROOT / "data" / "aoi_locked"
        self.assertFalse(locked.exists() and any(locked.iterdir()))
        private_key_marker = "BEGIN " + "PRIVATE KEY"
        secret_name = "CDSE_CLIENT_" + "SECRET"
        reviewable_suffixes = {
            ".csv",
            ".geojson",
            ".json",
            ".md",
            ".pem",
            ".py",
            ".toml",
            ".txt",
            ".yaml",
            ".yml",
        }
        for path in ROOT.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in reviewable_suffixes
                and path.stat().st_size < 2_000_000
            ):
                text = path.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn(private_key_marker, text)
                self.assertNotRegex(
                    text,
                    rf"{secret_name}\s*=\s*['\"][^<]",
                )


if __name__ == "__main__":
    unittest.main()
