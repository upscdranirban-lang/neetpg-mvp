"""Infer a document's publication date, with a confidence level, using the
trust order from the design doc:

    1. date printed in the document text        (high)  -- not available to
                                                            this MVP: we never
                                                            download/OCR the PDF
    2. date in the title                          (high)
    3. timestamp printed in the PDF's filename     (medium)
    4. date in the filename (other formats)        (medium)
    5. date we first saw the listing entry         (low)

MCC filenames look like .../uploads/2026/05/2026052710250622.pdf -- the
first 8 digits are YYYYMMDD, the rest is a time/serial. We use that as our
"filename timestamp" tier.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

# "21.01.2026" or "21-01-2026" or "21/01/2026" (DD.MM.YYYY, the format MCC uses)
TITLE_DATE_RE = re.compile(r"\b(\d{1,2})[.\-/](\d{1,2})[.\-/](20\d{2})")

# .../uploads/2026/05/2026052710250622.pdf
FILENAME_TS_RE = re.compile(r"/uploads/(20\d{2})/(\d{2})/(20\d{2})(\d{2})(\d{2})\d*\.pdf", re.IGNORECASE)


@dataclass
class InferredDate:
    value: date | None
    basis: str        # 'title' | 'filename' | 'first_seen' | 'unknown'
    confidence: str    # 'high' | 'medium' | 'low'


def _try_title(title: str) -> date | None:
    m = TITLE_DATE_RE.search(title)
    if not m:
        return None
    day, month, year = (int(g) for g in m.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _try_filename(file_url: str) -> date | None:
    m = FILENAME_TS_RE.search(file_url)
    if not m:
        return None
    year_dir, month_dir, year_ts, month_ts, day_ts = m.groups()
    try:
        # Trust the timestamp embedded in the filename itself over the folder.
        return date(int(year_ts), int(month_ts), int(day_ts))
    except ValueError:
        try:
            return date(int(year_dir), int(month_dir), 1)
        except ValueError:
            return None


def infer_date(title: str, file_url: str, first_seen: datetime) -> InferredDate:
    d = _try_title(title)
    if d:
        return InferredDate(value=d, basis="title", confidence="high")

    d = _try_filename(file_url)
    if d:
        return InferredDate(value=d, basis="filename", confidence="medium")

    return InferredDate(value=first_seen.date(), basis="first_seen", confidence="low")
