"""Opt-in downloader for approved open-weight candidates.

This script downloads files only. It does not train, infer, or call a hosted
model API. Run with --dry-run first and --download only after reviewing the
candidate's model card and competition rules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "candidates.json"
BUNDLES = ROOT / "bundles"


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return json.load(handle)


def candidate_plan(name: str, manifest: dict) -> dict:
    try:
        candidate = manifest["candidates"][name]
    except KeyError as exc:
        available = ", ".join(sorted(manifest.get("candidates", {})))
        raise ValueError(f"Unknown candidate {name!r}. Available: {available}") from exc

    return {
        "name": name,
        "repository": candidate["repository"],
        "revision": candidate["revision"],
        "license": candidate["license"],
        "destination": str(BUNDLES / name),
        "allow_patterns": candidate["allow_patterns"],
        "model_card": candidate["model_card"],
        "warning": "Preparation only; task suitability must be decided tomorrow.",
    }


def download(plan: dict) -> Path:
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            "Install shared/pretrained/requirements-download.txt first."
        ) from exc

    destination = Path(plan["destination"])
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")

    resolved_revision = HfApi().model_info(
        plan["repository"], revision=plan["revision"]
    ).sha
    snapshot_download(
        repo_id=plan["repository"],
        revision=resolved_revision,
        local_dir=destination,
        allow_patterns=plan["allow_patterns"],
    )
    source_metadata = {
        "repository": plan["repository"],
        "requested_revision": plan["revision"],
        "resolved_revision": resolved_revision,
        "license": plan["license"],
        "model_card": plan["model_card"],
    }
    (destination / "source-metadata.json").write_text(
        json.dumps(source_metadata, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", help="Candidate key from candidates.json")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print plan only")
    mode.add_argument("--download", action="store_true", help="Download approved files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = candidate_plan(args.candidate, load_manifest())
    print(json.dumps(plan, indent=2))
    if args.dry_run:
        return 0
    destination = download(plan)
    print(f"Downloaded to {destination}")
    print("Run verify_bundle.py before uploading to Kaggle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
