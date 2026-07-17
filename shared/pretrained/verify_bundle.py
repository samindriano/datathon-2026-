"""Validate a downloaded candidate bundle and emit a checksum receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "candidates.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_bundle(bundle: Path) -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    name = bundle.name
    if name not in manifest["candidates"]:
        raise ValueError(f"Bundle directory must match a candidate key: {name!r}")

    candidate = manifest["candidates"][name]
    required_files = [*candidate["required_files"], "source-metadata.json"]
    missing = [item for item in required_files if not (bundle / item).is_file()]
    source_metadata = None
    metadata_path = bundle / "source-metadata.json"
    if metadata_path.is_file():
        source_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    files = []
    for path in sorted(item for item in bundle.rglob("*") if item.is_file()):
        if path.name == "bundle-receipt.json":
            continue
        files.append(
            {
                "path": path.relative_to(bundle).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    return {
        "candidate": name,
        "repository": candidate["repository"],
        "requested_revision": candidate["revision"],
        "resolved_revision": (
            source_metadata.get("resolved_revision") if source_metadata else None
        ),
        "license": candidate["license"],
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_KAGGLE_UPLOAD" if not missing else "INCOMPLETE",
        "missing_required_files": missing,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    if not bundle.is_dir():
        parser.error(f"Not a directory: {bundle}")

    receipt = inspect_bundle(bundle)
    receipt_path = bundle / "bundle-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "READY_FOR_KAGGLE_UPLOAD" else 1


if __name__ == "__main__":
    raise SystemExit(main())
