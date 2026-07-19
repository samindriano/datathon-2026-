from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from run_fastlink_feasibility import component_crops
from run_linkgraph_feasibility import TitleMapper


_ENGINE: RapidOCR | None = None
_MAPPER: TitleMapper | None = None
_ZIP_PATH: Path | None = None


def resolve_zip_path(explicit: Path | None = None) -> Path:
    """Resolve the official Task 2 ZIP for local or Kaggle execution."""

    if explicit is not None:
        candidates = [explicit]
    else:
        candidates = []
        configured = os.environ.get("TASK2_ZIP_PATH")
        if configured:
            candidates.append(Path(configured))
        candidates.extend(
            [
                Path("task2/data/competition/datathon-task-2.zip"),
                Path.home() / "Downloads" / "datathon-task-2.zip",
            ]
        )
        kaggle_input = Path("/kaggle/input")
        if kaggle_input.is_dir():
            candidates.extend(kaggle_input.rglob("datathon-task-2.zip"))

    matches = sorted(
        {
            candidate.expanduser().resolve()
            for candidate in candidates
            if candidate.is_file()
        },
        key=str,
    )
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(
            "Task 2 ZIP not found. Set TASK2_ZIP_PATH or pass --zip-path."
        )
    raise RuntimeError(
        "multiple Task 2 ZIP files found; set TASK2_ZIP_PATH explicitly: "
        + ", ".join(str(path) for path in matches)
    )


def _init_worker(
    data_root: str,
    zip_path: str,
    cpu_threads: int,
) -> None:
    global _ENGINE, _MAPPER, _ZIP_PATH
    if cpu_threads < 1:
        raise ValueError("cpu_threads must be positive")
    os.environ["OMP_NUM_THREADS"] = str(cpu_threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(cpu_threads)
    os.environ["MKL_NUM_THREADS"] = str(cpu_threads)
    articles = pd.read_csv(Path(data_root) / "articles.csv")
    _MAPPER = TitleMapper(articles)
    _ENGINE = RapidOCR(
        use_text_det=False,
        use_angle_cls=False,
        rec_batch_num=64,
        rec_model_path="",
    )
    _ZIP_PATH = Path(zip_path)


def _recognize_page_batch(
    archive: zipfile.ZipFile, page_ids: list[int]
) -> tuple[dict[int, set[int]], dict[str, int]]:
    if _ENGINE is None or _MAPPER is None:
        raise RuntimeError("worker was not initialized")
    crops: list[np.ndarray] = []
    crop_page_ids: list[int] = []
    readable_pages = 0
    for article_id in page_ids:
        image = np.asarray(
            Image.open(
                io.BytesIO(
                    archive.read(f"dataset-task2/screenshots/{article_id}.png")
                )
            ).convert("RGB")
        )
        page_crops, blue_pixels = component_crops(image)
        readable_pages += blue_pixels > 0
        crops.extend(page_crops)
        crop_page_ids.extend([article_id] * len(page_crops))

    candidates = {article_id: set() for article_id in page_ids}
    exact = 0
    fuzzy = 0
    if crops:
        recognition, _ = _ENGINE.text_recognizer(crops)
        for article_id, (text, confidence) in zip(
            crop_page_ids, recognition, strict=True
        ):
            match = _MAPPER.map(str(text), float(confidence))
            if match is None:
                continue
            candidates[article_id].add(int(match["article_id"]))
            exact += match["method"] == "exact"
            fuzzy += match["method"] == "fuzzy"
    return candidates, {
        "pages": len(page_ids),
        "readable_pages": readable_pages,
        "component_crops": len(crops),
        "exact_mapping_rows": exact,
        "fuzzy_mapping_rows": fuzzy,
    }


def _extract_shard(article_ids: list[int]) -> dict[str, object]:
    if _ZIP_PATH is None:
        raise RuntimeError("worker was not initialized")
    started = time.perf_counter()
    links: dict[int, set[int]] = {}
    totals = {
        "pages": 0,
        "readable_pages": 0,
        "component_crops": 0,
        "exact_mapping_rows": 0,
        "fuzzy_mapping_rows": 0,
    }
    with zipfile.ZipFile(_ZIP_PATH) as archive:
        for start in range(0, len(article_ids), 20):
            page_ids = article_ids[start : start + 20]
            batch_links, batch_totals = _recognize_page_batch(archive, page_ids)
            links.update(batch_links)
            for key in totals:
                totals[key] += int(batch_totals[key])
    return {
        "links": {str(key): sorted(value) for key, value in links.items()},
        "totals": totals,
        "runtime_seconds": time.perf_counter() - started,
    }


def source_article_ids(data_root: Path) -> list[int]:
    train = pd.read_csv(data_root / "states_train.csv", usecols=["current_article_id"])
    test = pd.read_csv(data_root / "states_test.csv", usecols=["current_article_id"])
    return sorted(
        set(train["current_article_id"].astype(np.int64))
        | set(test["current_article_id"].astype(np.int64))
    )


def _shard_cache_path(resume_dir: Path, article_ids: list[int]) -> Path:
    digest = hashlib.sha256(
        np.asarray(article_ids, dtype="<i8").tobytes()
    ).hexdigest()[:16]
    return resume_dir / f"shard-{article_ids[0]:05d}-{len(article_ids):04d}-{digest}.json"


def _read_cached_shard(path: Path, expected_ids: list[int]) -> dict[str, object]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if {int(value) for value in result.get("links", {})} != set(expected_ids):
        raise ValueError(f"checkpoint does not match expected shard: {path}")
    return result


def _write_cached_shard(
    resume_dir: Path, article_ids: list[int], result: dict[str, object]
) -> None:
    resume_dir.mkdir(parents=True, exist_ok=True)
    destination = _shard_cache_path(resume_dir, article_ids)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    temporary.replace(destination)


def run(
    data_root: Path,
    zip_path: Path,
    workers: int,
    shard_pages: int,
    limit: int | None,
    resume_dir: Path | None = None,
    cpu_threads: int = 1,
) -> dict[str, object]:
    article_ids = source_article_ids(data_root)
    if limit is not None:
        article_ids = sorted(
            article_ids,
            key=lambda article_id: hashlib.sha256(
                f"prelink:{article_id}".encode("ascii")
            ).digest(),
        )[:limit]
    shards = [
        article_ids[start : start + shard_pages]
        for start in range(0, len(article_ids), shard_pages)
    ]
    started = time.perf_counter()
    links: dict[str, list[int]] = {}
    totals = {
        "pages": 0,
        "readable_pages": 0,
        "component_crops": 0,
        "exact_mapping_rows": 0,
        "fuzzy_mapping_rows": 0,
    }
    shard_runtimes: list[float] = []
    completed_pages = 0

    def merge_result(result: dict[str, object]) -> None:
        nonlocal completed_pages
        links.update(result["links"])
        for key in totals:
            totals[key] += int(result["totals"][key])
        completed_pages += int(result["totals"]["pages"])
        shard_runtimes.append(float(result["runtime_seconds"]))
        print(f"prelink pages {completed_pages}/{len(article_ids)}", flush=True)

    pending: list[list[int]] = []
    cached_shards = 0
    for shard in shards:
        checkpoint = None if resume_dir is None else _shard_cache_path(resume_dir, shard)
        if checkpoint is not None and checkpoint.is_file():
            merge_result(_read_cached_shard(checkpoint, shard))
            cached_shards += 1
        else:
            pending.append(shard)

    if pending:
        with ProcessPoolExecutor(
            max_workers=workers,
            initializer=_init_worker,
            initargs=(str(data_root), str(zip_path), cpu_threads),
        ) as executor:
            futures = {
                executor.submit(_extract_shard, shard): shard for shard in pending
            }
            for future in as_completed(futures):
                shard = futures[future]
                result = future.result()
                if resume_dir is not None:
                    _write_cached_shard(resume_dir, shard, result)
                merge_result(result)
    runtime = time.perf_counter() - started
    mapping_rows = totals["exact_mapping_rows"] + totals["fuzzy_mapping_rows"]
    payload = {
        "experiment_id": "d2-e014-prelink",
        "source": "official Task 2 screenshots",
        "article_ids": article_ids,
        "article_ids_sha256": hashlib.sha256(
            np.asarray(article_ids, dtype="<i8").tobytes()
        ).hexdigest(),
        "links": dict(sorted(links.items(), key=lambda item: int(item[0]))),
        "diagnostics": {
            **totals,
            "accepted_mapping_rows": mapping_rows,
            "exact_mapping_share": (
                totals["exact_mapping_rows"] / mapping_rows if mapping_rows else 0.0
            ),
            "workers": workers,
            "device": "cpu",
            "cpu_threads_per_worker": cpu_threads,
            "shard_pages": shard_pages,
            "shard_runtimes": shard_runtimes,
            "cached_shards": cached_shards,
            "computed_shards": len(pending),
            "runtime_seconds": runtime,
            "runtime_seconds_per_page": runtime / len(article_ids),
            "runtime_projection_available": cached_shards == 0,
            "projected_union_runtime_seconds": (
                runtime if limit is None else runtime / len(article_ids) * 4312
            )
            if cached_shards == 0
            else None,
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("task2/data/competition/dataset-task2"),
    )
    parser.add_argument("--zip-path", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cpu-threads", type=int, default=1)
    parser.add_argument("--shard-pages", type=int, default=128)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume-dir", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()
    payload = run(
        args.data_root.resolve(),
        resolve_zip_path(args.zip_path),
        args.workers,
        args.shard_pages,
        args.limit,
        None if args.resume_dir is None else args.resume_dir.resolve(),
        args.cpu_threads,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload["diagnostics"], indent=2), flush=True)


if __name__ == "__main__":
    main()
