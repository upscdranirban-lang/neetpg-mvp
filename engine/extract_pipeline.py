"""Turns one newly-detected MCC result document into a published (or
queued-for-review) dataset, end to end:

  download PDF -> detect_layout -> extract table -> build closing ranks
    -> validate -> publish to site/datasets/ (pass) or data/review_queue/ (fail)

This is what engine/run_scheduled.py calls for every document
monitor.run_once just inserted whose doc_type suggests it carries seat/
allotment data. It's also exactly what to run by hand for a document you
upload yourself, instead of hand-writing a new build_*.py script per PDF
(see the two existing hand-written ones, extract_r1r2r3_pdf.py /
extract_stray_pdf.py and their build_*.py counterparts, which this reuses
rather than replaces).
"""

from __future__ import annotations

import csv
import gc
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber

from engine import build_r1r2r3_closing_ranks, build_stray_closing_ranks, dataset_registry, detect_layout, validate
from engine.extract_r1r2r3_pdf import FIELDS as R1R2R3_FIELDS
from engine.extract_r1r2r3_pdf import normalize_row as normalize_r1r2r3_row
from engine.extract_stray_pdf import FIELDS as STRAY_FIELDS
from engine.extract_stray_pdf import normalize_row as normalize_stray_row

ROOT = Path(__file__).resolve().parent.parent
REVIEW_QUEUE_DIR = ROOT / "data" / "review_queue"
RAW_CSV_DIR = ROOT / "data" / "auto"
PAGE_CHUNK_SIZE = 250

ROUND_SLUGS = {
    "round 1": "r1", "round 2": "r2", "round 3": "r3", "round 4": "r4",
    "special stray": "special_stray", "stray": "stray",
}


def _round_slug(round_label: str | None) -> str:
    if not round_label:
        return "unknown_round"
    key = round_label.lower()
    for name, slug in ROUND_SLUGS.items():
        if name in key:
            return slug
    return re.sub(r"[^a-z0-9]+", "_", key).strip("_")


def dataset_id_for(cycle_label: str | None, round_label: str | None) -> str:
    year_match = re.search(r"20\d{2}", cycle_label or "")
    year = year_match.group(0) if year_match else "unknown"
    return f"auto{year}{_round_slug(round_label)}"


def _extract_r1r2r3_csv(pdf_path: Path, out_csv: Path) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(R1R2R3_FIELDS)

    with pdfplumber.open(pdf_path) as pdf:
        with open(out_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for start in range(0, page_count, PAGE_CHUNK_SIZE):
                end = min(start + PAGE_CHUNK_SIZE, page_count)
                for i in range(start, end):
                    page = pdf.pages[i]
                    for table in page.extract_tables():
                        for raw_row in table:
                            row = normalize_r1r2r3_row(raw_row)
                            if row is not None:
                                writer.writerow(row)
                    page.flush_cache()
                    del page
                gc.collect()


def _extract_stray_csv(pdf_path: Path, out_csv: Path) -> None:
    with pdfplumber.open(pdf_path) as pdf, open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(STRAY_FIELDS)
        for page in pdf.pages:
            for table in page.extract_tables():
                for raw_row in table:
                    row = normalize_stray_row(raw_row)
                    if row is not None:
                        writer.writerow(row)
            page.flush_cache()


def _read_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_review_entry(document: dict, reason: str, details: dict | None = None) -> Path:
    REVIEW_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    content_hash = document.get("content_hash", hashlib.sha256(document["file_url"].encode()).hexdigest()[:16])
    entry = {
        "document": document,
        "reason": reason,
        "details": details or {},
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    path = REVIEW_QUEUE_DIR / f"{content_hash}.json"
    path.write_text(json.dumps(entry, indent=2, default=str), encoding="utf-8")
    return path


def process_document(pdf_path: Path, document: dict) -> dict:
    """document: the same fields engine.db stores per document (title,
    file_url, cycle_label, round_label, content_hash, ...). Returns a
    summary dict: {"status": "published"|"review", "dataset_id"?, "path"?, "issues": [...]}."""
    layout = detect_layout.detect_layout(str(pdf_path))
    if layout == "unknown":
        path = _write_review_entry(document, "unknown_layout", {
            "note": "This document's table structure doesn't match the r1r2r3 or stray layouts this "
                    "pipeline knows how to extract. A human needs to look at it and, if it's a new "
                    "layout worth supporting, write a new extractor for it (see extract_stray_pdf.py "
                    "for the simplest example to copy).",
        })
        return {"status": "review", "reason": "unknown_layout", "path": str(path)}

    RAW_CSV_DIR.mkdir(parents=True, exist_ok=True)
    dataset_id = dataset_id_for(document.get("cycle_label"), document.get("round_label"))
    raw_csv = RAW_CSV_DIR / f"{dataset_id}.csv"

    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)

    provenance_seed = {
        "title": document.get("title"),
        "provided_by": f"MCC official document, auto-downloaded from {document.get('file_url')}",
        "authority": "Medical Counselling Committee (MCC)",
        "round": document.get("round_label") or "Unknown round",
        "cycle": document.get("cycle_label") or "Unknown cycle",
        "pages": page_count,
        "extracted": datetime.now(timezone.utc).date().isoformat(),
        "note": "This is a real MCC document, downloaded and extracted automatically by the scheduled "
                "monitor. Every number below is directly aggregated from it -- no scraping of third-party "
                "figures, no scaling, no guessing.",
    }

    if layout == "r1r2r3":
        _extract_r1r2r3_csv(pdf_path, raw_csv)
        rows = _read_rows(raw_csv)
        payload = build_r1r2r3_closing_ranks.build(str(raw_csv), provenance_seed)
        expected_fields = R1R2R3_FIELDS
    else:  # "stray"
        _extract_stray_csv(pdf_path, raw_csv)
        rows = _read_rows(raw_csv)
        payload = build_stray_closing_ranks.build(str(raw_csv), provenance_seed)
        expected_fields = STRAY_FIELDS

    previous_payload = None
    if dataset_id in dataset_registry.load_manifest():
        previous_payload = dataset_registry.load_dataset(dataset_id)

    result = validate.validate(payload, raw_rows=rows, expected_fields=expected_fields, previous_payload=previous_payload)

    if not result.passed:
        path = _write_review_entry(document, "validation_failed", {
            "dataset_id": dataset_id,
            "raw_csv": str(raw_csv),
            "issues": [str(i) for i in result.issues],
        })
        return {"status": "review", "reason": "validation_failed", "path": str(path), "issues": [str(i) for i in result.errors]}

    label = f"{provenance_seed['cycle'].replace('PG Counselling ', '')} {provenance_seed['round']} (Real MCC)"
    dataset_registry.publish_dataset(
        dataset_id=dataset_id,
        label=label,
        round_note=f"{provenance_seed['round']}, {provenance_seed['cycle'].split()[-1]}",
        warning_title=f"Real MCC data: {provenance_seed['round']}, {provenance_seed['cycle']}",
        warning_body=(
            f"Computed directly from the official {provenance_seed['round']}, {provenance_seed['cycle']} "
            f"allotment result ({page_count} pages), downloaded and extracted automatically. Every number "
            "below comes straight from it &mdash; not scraped, not scaled, not guessed."
        ),
        built_payload=payload,
    )
    return {
        "status": "published",
        "dataset_id": dataset_id,
        "warnings": [str(i) for i in result.warnings],
    }
