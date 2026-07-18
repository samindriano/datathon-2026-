"""Inspect Task 1 competition files without modifying raw data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def summarize_json(path: Path) -> None:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    print(f"JSON {path.name}: type={type(value).__name__}, len={len(value)}")
    if isinstance(value, list) and value:
        sample = json.dumps(value[0], ensure_ascii=True, default=str)
        print(f"  sample={sample}"[:1000])
    elif isinstance(value, dict):
        print(f"  keys={list(value)[:20]}")
        if value:
            first = json.dumps(next(iter(value.items())), ensure_ascii=True, default=str)
            print(f"  first={first}"[:1000])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", type=Path)
    args = parser.parse_args()
    root = args.data_root.resolve()

    for path in sorted(root.rglob("*.npy")):
        array = np.load(path, mmap_mode="r")
        finite = np.isfinite(array)
        print(
            f"NPY {path.relative_to(root)}: shape={array.shape}, "
            f"dtype={array.dtype}, finite={finite.mean():.6f}, "
            f"min={np.nanmin(array):.3f}, max={np.nanmax(array):.3f}, "
            f"mean={np.nanmean(array):.3f}"
        )

    for path in sorted(root.rglob("*.json")):
        summarize_json(path)

    sample = pd.read_csv(root / "sample_submission.csv")
    print(
        f"SUBMISSION shape={sample.shape}, columns={sample.columns.tolist()}, "
        f"dtypes={sample.dtypes.astype(str).to_dict()}"
    )
    print(f"  head={sample.head(3).to_dict(orient='records')}")
    print(f"  tail={sample.tail(3).to_dict(orient='records')}")

    parts = sample["id"].str.extract(r"test_(\d+)_h(5|10|15)_r(\d+)")
    invalid_ids = int(parts.isna().any(axis=1).sum())
    parsed = parts.dropna().astype(int)
    print(
        f"  invalid_ids={invalid_ids}, samples={parsed[0].nunique()}, "
        f"horizons={sorted(parsed[1].unique())}, roads={parsed[2].nunique()}, "
        f"road_range=({parsed[2].min()}, {parsed[2].max()})"
    )

    adjacency = np.load(root / "static" / "matrix.npy", mmap_mode="r")
    print(
        f"ADJ symmetric={np.allclose(adjacency, adjacency.T)}, "
        f"nonzero={np.count_nonzero(adjacency)}, "
        f"diag_nonzero={np.count_nonzero(np.diag(adjacency))}, "
        f"values={np.unique(adjacency)[:20]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
