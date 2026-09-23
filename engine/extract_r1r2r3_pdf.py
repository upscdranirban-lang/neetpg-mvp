"""Generalized extraction for MCC "Round 3" style PDFs -- documents that
show a candidate's Round 1 / Round 2 / Round 3 allotment side by side,
16 cells per row, same layout as the 2024 Round 3 file this was first
written for (see extract_2024_round3.py, which this generalizes).

Only the Round 3 columns carry an "Alloted Category" (the seat's own
category, which can differ from the candidate's own category), so only
Round 3 can be aggregated into closing ranks from this layout.

Row shape from pdfplumber is inconsistent (16 or 17 cells -- an extra
stray None cell appears in a small fraction of rows), so every row is
normalized to a fixed 16-cell layout before parsing:
  0 rank
  1-4   Round 1: quota, institute, course, remarks
  5-8   Round 2: quota, institute, course, remarks
  9-15  Round 3: quota, institute, course, alloted_category,
                 candidate_category, option_no, remarks

Usage: python3 extract_r1r2r3_pdf.py <pdf_path> <out_csv_path> <start> <end> <w|a>
Run in bounded page-range chunks (e.g. 250 pages at a time) for a large
PDF -- a single in-process run over 1500+ pages risks the OOM killer.
"""

from __future__ import annotations

import csv
import gc
import sys
import time
from pathlib import Path

import pdfplumber

FIELDS = [
    "rank",
    "r1_quota", "r1_institute", "r1_course", "r1_remarks",
    "r2_quota", "r2_institute", "r2_course", "r2_remarks",
    "r3_quota", "r3_institute", "r3_course", "r3_alloted_category",
    "r3_candidate_category", "r3_option_no", "r3_remarks",
]


def normalize_row(row: list) -> list | None:
    """Return a clean 16-cell row, or None if this isn't a data row
    (legend rows, stray page furniture)."""
    cells = [(c or "").replace("\n", " ").strip() for c in row]

    if len(cells) == 17:
        for i in range(9, len(cells)):
            if cells[i] == "":
                del cells[i]
                break
        else:
            del cells[-1]
    if len(cells) != 16:
        return None
    if not cells[0].isdigit():
        return None
    return cells


def main(pdf_path: str, out_path: str, start: int, end: int, mode: str) -> None:
    t0 = time.time()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    kept_rows = 0

    with pdfplumber.open(pdf_path) as pdf, open(out, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(FIELDS)

        for i in range(start, min(end, len(pdf.pages))):
            page = pdf.pages[i]
            for table in page.extract_tables():
                for raw_row in table:
                    total_rows += 1
                    row = normalize_row(raw_row)
                    if row is None:
                        continue
                    writer.writerow(row)
                    kept_rows += 1
            page.flush_cache()
            del page
            if (i - start) % 100 == 0:
                gc.collect()

    print(f"Pages {start}-{end}: {kept_rows}/{total_rows} data rows kept in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    pdf_path = sys.argv[1]
    out_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])
    mode = sys.argv[5] if len(sys.argv) > 5 else "a"
    main(pdf_path, out_path, start, end, mode)
