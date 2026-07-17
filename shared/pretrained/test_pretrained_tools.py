from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prepare = load_module("prepare_candidate", "prepare_candidate.py")
verify = load_module("verify_bundle", "verify_bundle.py")


class PretrainedToolsTest(unittest.TestCase):
    def test_manifest_candidates_have_required_policy_fields(self):
        manifest = prepare.load_manifest()
        self.assertFalse(manifest["policy"]["automatic_download"])
        self.assertFalse(manifest["policy"]["external_api_for_modeling"])
        self.assertFalse(manifest["policy"]["external_finetuning_data"])
        for name, candidate in manifest["candidates"].items():
            with self.subTest(name=name):
                self.assertEqual(candidate["license"], "apache-2.0")
                self.assertTrue(candidate["required_files"])
                self.assertTrue(candidate["allow_patterns"])
                self.assertTrue(candidate["model_card"].startswith("https://"))

    def test_dry_run_plan_does_not_create_bundle(self):
        manifest = prepare.load_manifest()
        plan = prepare.candidate_plan("text-minilm-l6", manifest)
        self.assertEqual(plan["repository"], "sentence-transformers/all-MiniLM-L6-v2")
        self.assertFalse(Path(plan["destination"]).exists())

    def test_incomplete_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "text-minilm-l6"
            bundle.mkdir()
            (bundle / "config.json").write_text("{}", encoding="utf-8")
            result = verify.inspect_bundle(bundle)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("model.safetensors", result["missing_required_files"])
        self.assertIn("source-metadata.json", result["missing_required_files"])

    def test_download_pins_resolved_revision_and_writes_metadata(self):
        calls = {}

        class FakeApi:
            def model_info(self, repository, revision):
                calls["model_info"] = (repository, revision)
                return types.SimpleNamespace(sha="resolved-sha")

        def fake_snapshot_download(**kwargs):
            calls["snapshot"] = kwargs
            Path(kwargs["local_dir"]).mkdir(parents=True)

        fake_hub = types.SimpleNamespace(
            HfApi=FakeApi,
            snapshot_download=fake_snapshot_download,
        )
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "text-minilm-l6"
            plan = prepare.candidate_plan("text-minilm-l6", prepare.load_manifest())
            plan["destination"] = str(destination)
            with mock.patch.dict(sys.modules, {"huggingface_hub": fake_hub}):
                prepare.download(plan)
            metadata = json.loads(
                (destination / "source-metadata.json").read_text(encoding="utf-8")
            )

        self.assertEqual(calls["snapshot"]["revision"], "resolved-sha")
        self.assertEqual(metadata["resolved_revision"], "resolved-sha")


if __name__ == "__main__":
    unittest.main()
