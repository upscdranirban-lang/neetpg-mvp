"""Auto-detect which known table layout a newly-downloaded MCC result PDF
uses, so the automated pipeline can pick the right extractor without a
human having to open the file first.

Only two layouts are known so far (see extract_r1r2r3_pdf.py and
extract_stray_pdf.py) -- both were reverse-engineered from real MCC PDFs
the user uploaded. A document that matches neither is routed to human
review rather than guessed at: this project's own rule is "never blindly
publish AI-extracted data," and that starts with never blindly assuming a
layout that hasn't been verified.
"""

from __future__ import annotations

import pdfplumber

R1R2R3_CELL_COUNTS = (16, 17)
STRAY_CELL_COUNTS = (8,)
# How many of the first few pages with a table to sample before giving up
# and calling the layout unknown -- MCC PDFs sometimes open with a cover
# page or legend before the real data table starts.
PAGES_TO_SAMPLE = 8


def _first_data_row_cell_count(pdf_path: str) -> int | None:
    """Return the cell count of the first row, across the first few pages,
    that looks like real data (starts with a digit -- an SNo or rank), or
    None if no such row was found in the sampled pages."""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:PAGES_TO_SAMPLE]:
            for table in page.extract_tables():
                for row in table:
                    cells = [(c or "").strip() for c in row]
                    if cells and cells[0].isdigit():
                        return len(cells)
            page.flush_cache()
    return None


def detect_layout(pdf_path: str) -> str:
    """Returns "r1r2r3", "stray", or "unknown"."""
    cell_count = _first_data_row_cell_count(pdf_path)
    if cell_count is None:
        return "unknown"
    if cell_count in R1R2R3_CELL_COUNTS:
        return "r1r2r3"
    if cell_count in STRAY_CELL_COUNTS:
        return "stray"
    return "unknown"


if __name__ == "__main__":
    import sys

    for path in sys.argv[1:]:
        print(f"{path}: {detect_layout(path)}")
