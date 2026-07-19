from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from sklearn.feature_extraction.text import TfidfVectorizer


SEED = "20260719"
SAMPLE_PAGES = 100
MIN_OCR_CONFIDENCE = 0.65
MIN_FUZZY_SCORE = 0.90
MIN_FUZZY_MARGIN = 0.10


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold().replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def sample_current_ids(train: pd.DataFrame) -> list[int]:
    current_ids = sorted({int(value) for value in train["current_article_id"]})
    return sorted(
        current_ids,
        key=lambda article_id: hashlib.sha256(
            f"{SEED}:{article_id}".encode("ascii")
        ).digest(),
    )[:SAMPLE_PAGES]


def compact_blue_text(image: np.ndarray) -> tuple[np.ndarray | None, int]:
    red = image[:, :, 0].astype(np.int16)
    green = image[:, :, 1].astype(np.int16)
    blue = image[:, :, 2].astype(np.int16)
    mask = (
        (blue >= 140)
        & (red <= 150)
        & (green <= 130)
        & ((blue - red) >= 60)
        & ((blue - green) >= 50)
    )
    blue_pixels = int(mask.sum())
    if blue_pixels == 0:
        return None, 0

    active_rows = mask.any(axis=1)
    padded_rows = np.convolve(active_rows.astype(np.uint8), np.ones(9), mode="same") > 0
    positions = np.flatnonzero(padded_rows)
    cuts = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, cuts)

    strips: list[np.ndarray] = []
    for group in groups:
        y0, y1 = int(group[0]), int(group[-1]) + 1
        local_mask = mask[y0:y1]
        occupied_columns = np.flatnonzero(local_mask.any(axis=0))
        if not len(occupied_columns):
            continue
        x0 = max(0, int(occupied_columns[0]) - 8)
        x1 = min(image.shape[1], int(occupied_columns[-1]) + 9)
        strip = np.full((y1 - y0, x1 - x0, 3), 255, dtype=np.uint8)
        source = image[y0:y1, x0:x1]
        keep = local_mask[:, x0:x1]
        strip[keep] = source[keep]
        canvas = np.full((strip.shape[0], image.shape[1], 3), 255, dtype=np.uint8)
        canvas[:, x0:x1] = strip
        strips.append(canvas)

    if not strips:
        return None, blue_pixels
    separator = np.full((8, image.shape[1], 3), 255, dtype=np.uint8)
    stacked: list[np.ndarray] = []
    for index, strip in enumerate(strips):
        if index:
            stacked.append(separator)
        stacked.append(strip)
    return np.concatenate(stacked, axis=0), blue_pixels


class TitleMapper:
    def __init__(self, articles: pd.DataFrame) -> None:
        aliases_by_id: dict[int, set[str]] = {}
        alias_owners: dict[str, set[int]] = {}
        for row in articles.itertuples(index=False):
            article_id = int(row.article_id)
            full = normalize_title(row.title)
            aliases = {full}
            stripped = normalize_title(re.sub(r"\s*\([^)]*\)\s*$", "", str(row.title)))
            if stripped:
                aliases.add(stripped)
            aliases_by_id[article_id] = aliases
            for alias in aliases:
                alias_owners.setdefault(alias, set()).add(article_id)

        self.exact = {
            alias: next(iter(owners))
            for alias, owners in alias_owners.items()
            if len(owners) == 1 and len(alias) >= 3
        }
        self.aliases: list[str] = []
        self.alias_ids: list[int] = []
        for article_id, aliases in aliases_by_id.items():
            for alias in sorted(aliases):
                if len(alias) >= 3:
                    self.aliases.append(alias)
                    self.alias_ids.append(article_id)
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.matrix = self.vectorizer.fit_transform(self.aliases)

    def map(self, text: str, confidence: float) -> dict[str, object] | None:
        normalized = normalize_title(text)
        if confidence < MIN_OCR_CONFIDENCE or len(normalized) < 3:
            return None
        if normalized in self.exact:
            return {
                "article_id": self.exact[normalized],
                "method": "exact",
                "score": 1.0,
                "margin": 1.0,
                "normalized": normalized,
            }

        query = self.vectorizer.transform([normalized])
        similarities = (query @ self.matrix.T).toarray()[0]
        if len(similarities) < 2:
            return None
        top_two = np.argpartition(similarities, -2)[-2:]
        top_two = top_two[np.argsort(similarities[top_two])[::-1]]
        best, second = int(top_two[0]), int(top_two[1])
        score = float(similarities[best])
        margin = score - float(similarities[second])
        if score < MIN_FUZZY_SCORE or margin < MIN_FUZZY_MARGIN:
            return None
        return {
            "article_id": self.alias_ids[best],
            "method": "fuzzy",
            "score": score,
            "margin": margin,
            "normalized": normalized,
        }


def run(data_root: Path, zip_path: Path) -> dict[str, object]:
    train = pd.read_csv(data_root / "states_train.csv")
    articles = pd.read_csv(data_root / "articles.csv")
    sample_ids = sample_current_ids(train)
    true_edges = {
        (int(row.current_article_id), int(row.next_article_id))
        for row in train[train["current_article_id"].isin(sample_ids)].itertuples(index=False)
    }
    mapper = TitleMapper(articles)
    engine = RapidOCR()

    mapped_by_page: dict[int, set[int]] = {}
    mapping_rows: list[dict[str, object]] = []
    page_rows: list[dict[str, object]] = []
    started = time.perf_counter()
    with zipfile.ZipFile(zip_path) as archive:
        for article_id in sample_ids:
            page_started = time.perf_counter()
            member = f"dataset-task2/screenshots/{article_id}.png"
            image = np.asarray(
                Image.open(io.BytesIO(archive.read(member))).convert("RGB")
            )
            compact, blue_pixels = compact_blue_text(image)
            results = []
            if compact is not None:
                raw_results, _ = engine(compact)
                results = raw_results or []

            mapped: set[int] = set()
            exact_count = 0
            fuzzy_count = 0
            for result in results:
                text = str(result[1])
                confidence = float(result[2])
                match = mapper.map(text, confidence)
                if match is None:
                    continue
                mapped_id = int(match["article_id"])
                mapped.add(mapped_id)
                exact_count += match["method"] == "exact"
                fuzzy_count += match["method"] == "fuzzy"
                mapping_rows.append(
                    {
                        "current_article_id": article_id,
                        "ocr_text": text,
                        "ocr_confidence": confidence,
                        **match,
                    }
                )
            mapped_by_page[article_id] = mapped
            page_rows.append(
                {
                    "current_article_id": article_id,
                    "height": int(image.shape[0]),
                    "blue_pixels": blue_pixels,
                    "compact_height": 0 if compact is None else int(compact.shape[0]),
                    "ocr_results": len(results),
                    "mapped_unique": len(mapped),
                    "exact_mappings": exact_count,
                    "fuzzy_mappings": fuzzy_count,
                    "runtime_seconds": time.perf_counter() - page_started,
                }
            )
    runtime = time.perf_counter() - started

    recovered_edges = {
        edge for edge in true_edges if edge[1] in mapped_by_page.get(edge[0], set())
    }
    mapping_total = len(mapping_rows)
    exact_total = sum(row["method"] == "exact" for row in mapping_rows)
    metrics = {
        "experiment_id": "d2-e012-linkgraph",
        "sample_pages": len(sample_ids),
        "readable_pages": sum(row["blue_pixels"] > 0 for row in page_rows),
        "sample_current_ids_sha256": hashlib.sha256(
            np.asarray(sample_ids, dtype="<i8").tobytes()
        ).hexdigest(),
        "unique_true_edges": len(true_edges),
        "recovered_true_edges": len(recovered_edges),
        "unique_true_next_candidate_recall": (
            len(recovered_edges) / len(true_edges) if true_edges else 0.0
        ),
        "accepted_mapping_rows": mapping_total,
        "accepted_unique_article_ids": len({int(row["article_id"]) for row in mapping_rows}),
        "exact_mapping_rows": exact_total,
        "fuzzy_mapping_rows": mapping_total - exact_total,
        "exact_mapping_share_precision_proxy": (
            exact_total / mapping_total if mapping_total else 0.0
        ),
        "runtime_seconds": runtime,
        "runtime_seconds_per_page": runtime / len(sample_ids),
        "projected_full_runtime_seconds": runtime / len(sample_ids) * 4604,
        "page_diagnostics": page_rows,
        "accepted_mappings": mapping_rows,
        "recovered_edges": sorted([list(edge) for edge in recovered_edges]),
        "missed_edges": sorted([list(edge) for edge in true_edges - recovered_edges]),
    }
    return metrics


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
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
