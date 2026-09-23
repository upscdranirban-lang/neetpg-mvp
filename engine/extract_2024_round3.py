"""One-time extraction of the real MCC 'Counselling Seats Allotment -2024
Round 3' PDF the user provided (their Desktop file 2025012533.pdf,
staged into this session at /mnt/user-data/uploads/Desktop/2025012533.pdf).

This is a genuine official MCC document -- 1,732 pages, one row per
candidate rank, showing that candidate's Round 1 / Round 2 / Round 3
allotment side by side. Only the Round 3 columns carry an "Alloted
Category" (the category of the SEAT, which can differ from the
candidate's own category -- e.g. an OBC candidate taking an Open seat).
Per the design doc's own rule, closing rank must be computed against the
ALLOTTED category, never the candidate's category.

Row shape from pdfplumber is inconsistent (16 or 17 cells -- an extra
stray None cell appears in ~4% of rows, evidently a table-detection
artifact), so every row is normalized to a fixed 16-cell layout before
parsing:
  0 rank
  1-4   Round 1: quota, institute, course, remarks
  5-8   Round 2: quota, institute, course, remarks
  9-15  Round 3: quota, institute, course, alloted_category,
                 candidate_category, option_no, remarks

Output: data/mcc_2024_round3_allotments.csv (one row per candidate rank
with a real Round 3 allotment) -- this feeds engine/build_2024_closing_ranks.py.
"""

from __future__ import annotations

import csv
import gc
import sys
import time
from pathlib import Path

import pdfplumber

PDF_PATH = "/mnt/user-data/uploads/Desktop/2025012533.pdf"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "mcc_2024_round3_allotments.csv"

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
        # Drop exactly one stray empty cell to get back to 16. It can
        # appear at different positions, so remove the first empty cell
        # found after index 8 (inside the Round 3 block) rather than a
        # fixed index.
        for i in range(9, len(cells)):
            if cells[i] == "":
                del cells[i]
                break
        else:
            del cells[-1]  # fallback: trim from the end
    if len(cells) != 16:
        return None
    if not cells[0].isdigit():
        return None  # header/legend/title rows
    return cells


def main(start: int, end: int, mode: str) -> None:
    """Process pages [start, end) (0-indexed, half-open) and append to
    the CSV. Run in bounded chunks from the shell (see run_extraction.sh)
    so peak memory stays low across a 1732-page file -- a single
    in-process run over the whole file was killed by the OOM killer."""
    t0 = time.time()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_rows = 0
    kept_rows = 0

    with pdfplumber.open(PDF_PATH) as pdf, open(OUT_PATH, mode, newline="", encoding="utf-8") as f:
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
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    mode = sys.argv[3] if len(sys.argv) > 3 else "a"
    main(start, end, mode)
