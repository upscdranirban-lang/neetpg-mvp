"""Extraction for MCC "Stray Vacancy Round" style PDFs -- a single-round
allotment list, structurally simpler than the Round-1/2/3 layout (see
extract_r1r2r3_pdf.py): one row per allotment, 8 columns:
  SNo, Rank, Allotted Quota, Allotted Institute, Course,
  Alloted Category, Candidate Category, Remarks

Stray round documents are much shorter (~100-150 pages) than a full
Round 3 result, so this runs in a single pass -- no chunking needed.

Usage: python3 extract_stray_pdf.py <pdf_path> <out_csv_path>
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pdfplumber

FIELDS = ["sno", "rank", "quota", "institute", "course", "alloted_category", "candidate_category", "remarks"]


def normalize_row(row: list) -> list | None:
    cells = [(c or "").replace("\n", " ").strip() for c in row]
    if len(cells) != 8:
        return None
    if not cells[0].isdigit():
        return None  # header/legend/title rows
    return cells


def main(pdf_path: str, out_path: str) -> None:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    kept_rows = 0

    with pdfplumber.open(pdf_path) as pdf, open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        for page in pdf.pages:
            for table in page.extract_tables():
                for raw_row in table:
                    total_rows += 1
                    row = normalize_row(raw_row)
                    if row is None:
                        continue
                    writer.writerow(row)
                    kept_rows += 1
            page.flush_cache()

    print(f"{kept_rows}/{total_rows} data rows kept -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
