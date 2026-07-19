from __future__ import annotations

import argparse
import hashlib
import io
import json
import time
import zipfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from run_linkgraph_feasibility import TitleMapper, sample_current_ids


def blue_mask(image: np.ndarray) -> np.ndarray:
    red = image[:, :, 0].astype(np.int16)
    green = image[:, :, 1].astype(np.int16)
    blue = image[:, :, 2].astype(np.int16)
    return (
        (blue >= 140)
        & (red <= 150)
        & (green <= 130)
        & ((blue - red) >= 60)
        & ((blue - green) >= 50)
    )


def component_crops(image: np.ndarray) -> tuple[list[np.ndarray], int]:
    mask = blue_mask(image)
    blue_pixels = int(mask.sum())
    if blue_pixels == 0:
        return [], 0
    joined = cv2.dilate(
        mask.astype(np.uint8), np.ones((3, 25), dtype=np.uint8), iterations=1
    )
    _, _, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    records: list[tuple[int, int, np.ndarray]] = []
    for x, y, width, height, area in stats[1:]:
        if area < 12 or width < 8 or height < 5:
            continue
        x0 = max(0, int(x) - 13)
        x1 = min(image.shape[1], int(x + width) + 13)
        y0 = max(0, int(y) - 4)
        y1 = min(image.shape[0], int(y + height) + 4)
        crop = np.full((y1 - y0, x1 - x0, 3), 255, dtype=np.uint8)
        keep = mask[y0:y1, x0:x1]
        source = image[y0:y1, x0:x1]
        crop[keep] = source[keep]
        records.append((y0, x0, crop))
    records.sort(key=lambda item: (item[0], item[1]))
    return [record[2] for record in records], blue_pixels


def run(data_root: Path, zip_path: Path) -> dict[str, object]:
    train = pd.read_csv(data_root / "states_train.csv")
    articles = pd.read_csv(data_root / "articles.csv")
    sample_ids = sample_current_ids(train)
    true_edges = {
        (int(row.current_article_id), int(row.next_article_id))
        for row in train[train["current_article_id"].isin(sample_ids)].itertuples(index=False)
    }
    mapper = TitleMapper(articles)
    engine = RapidOCR(
        use_text_det=False,
        use_angle_cls=False,
        rec_batch_num=64,
        rec_model_path="",
    )

    started = time.perf_counter()
    all_crops: list[np.ndarray] = []
    crop_page_ids: list[int] = []
    page_diagnostics: dict[int, dict[str, object]] = {}
    with zipfile.ZipFile(zip_path) as archive:
        for article_id in sample_ids:
            image = np.asarray(
                Image.open(
                    io.BytesIO(
                        archive.read(f"dataset-task2/screenshots/{article_id}.png")
                    )
                ).convert("RGB")
            )
            crops, blue_pixels = component_crops(image)
            all_crops.extend(crops)
            crop_page_ids.extend([article_id] * len(crops))
            page_diagnostics[article_id] = {
                "current_article_id": article_id,
                "height": int(image.shape[0]),
                "blue_pixels": blue_pixels,
                "component_crops": len(crops),
            }

    recognition, recognition_seconds = engine.text_recognizer(all_crops)
    mapped_by_page = {article_id: set() for article_id in sample_ids}
    mapping_rows: list[dict[str, object]] = []
    for article_id, (text, confidence) in zip(
        crop_page_ids, recognition, strict=True
    ):
        match = mapper.map(str(text), float(confidence))
        if match is None:
            continue
        mapped_id = int(match["article_id"])
        mapped_by_page[article_id].add(mapped_id)
        mapping_rows.append(
            {
                "current_article_id": article_id,
                "ocr_text": str(text),
                "ocr_confidence": float(confidence),
                **match,
            }
        )
    runtime = time.perf_counter() - started
    recovered_edges = {
        edge for edge in true_edges if edge[1] in mapped_by_page.get(edge[0], set())
    }
    mapping_total = len(mapping_rows)
    exact_total = sum(row["method"] == "exact" for row in mapping_rows)
    return {
        "experiment_id": "d2-e013-fastlink",
        "sample_pages": len(sample_ids),
        "readable_pages": sum(
            int(row["blue_pixels"]) > 0 for row in page_diagnostics.values()
        ),
        "sample_current_ids_sha256": hashlib.sha256(
            np.asarray(sample_ids, dtype="<i8").tobytes()
        ).hexdigest(),
        "component_crops": len(all_crops),
        "unique_true_edges": len(true_edges),
        "recovered_true_edges": len(recovered_edges),
        "unique_true_next_candidate_recall": len(recovered_edges) / len(true_edges),
        "accepted_mapping_rows": mapping_total,
        "accepted_unique_article_ids": len(
            {int(row["article_id"]) for row in mapping_rows}
        ),
        "exact_mapping_rows": exact_total,
        "fuzzy_mapping_rows": mapping_total - exact_total,
        "exact_mapping_share_precision_proxy": exact_total / mapping_total,
        "recognition_seconds": float(recognition_seconds),
        "runtime_seconds": runtime,
        "runtime_seconds_per_page": runtime / len(sample_ids),
        "projected_full_runtime_seconds": runtime / len(sample_ids) * 4604,
        "page_diagnostics": list(page_diagnostics.values()),
        "accepted_mappings": mapping_rows,
        "recovered_edges": sorted([list(edge) for edge in recovered_edges]),
        "missed_edges": sorted([list(edge) for edge in true_edges - recovered_edges]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("task2/data/competition/dataset-task2"),
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=Path(r"C:\Users\Sam\Downloads\datathon-task-2.zip"),
    )
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(args.data_root, args.zip_path), indent=2)
    if args.output_json is None:
        print(rendered)
    else:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
