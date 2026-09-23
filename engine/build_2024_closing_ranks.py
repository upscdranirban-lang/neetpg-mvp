"""Build real, MCC-sourced closing-rank tables from the extracted 2024
Round 3 allotment data (data/mcc_2024_round3_allotments.csv), which came
from an actual MCC result PDF the user provided ("Counselling Seats
Allotment -2024 Round 3", 1,732 pages, staged from their Desktop as
2025012533.pdf).

This REPLACES the third-party-estimate predictor data for everything it
covers: real 2024 Round 3, by institute + course + allotted category.
It does NOT cover Round 1, Round 2, Stray, or any other year -- the
source PDF only carries an "Alloted Category" column for the Round 3
block (Round 1 and Round 2 columns in the same PDF don't record a
category), so only Round 3 can be aggregated this way from this file.

Methodology (matches the design doc's "cutoffs are derived, not
official" rule):
  - opening rank = MIN candidate rank allotted that institute+course+category
  - closing rank = MAX candidate rank allotted that institute+course+category
  - category used is the ALLOTTED category (the seat's category), never
    the candidate's own category -- an OBC candidate can get an Open
    seat, and that seat's closing rank belongs to Open, not OBC.
  - "Open PwD" / "OBC PwD" / etc. are folded into their base category
    (Open, OBC, ...) for aggregation -- PwD is a horizontal reservation
    cutting across categories, and keeping it separate would fragment
    already-thin per-institute samples. This simplification is recorded
    in the output's provenance block.
  - A seat is counted whether or not the candidate ultimately "Reported"
    for admission -- MCC's own closing-rank convention is allotment-based,
    matching every third-party source checked earlier.

Institute names in the source are duplicated with their own address
("Short Name,Short Name, Full Address, State, PIN") -- cleaned by taking
the text before the first comma.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "mcc_2024_round3_allotments.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "site" / "mcc_2024_round3_closing_ranks.json"

SOURCE_DOCUMENT = {
    "title": "Counselling Seats Allotment - 2024 Round 3",
    "provided_by": "user upload (Desktop file 2025012533.pdf)",
    "authority": "Medical Counselling Committee (MCC)",
    "round": "Round 3",
    "cycle": "PG Counselling 2024",
    "pages": 1732,
    "candidate_rows_seen": None,   # filled in at build time
    "round3_allotment_rows": None,  # filled in at build time
    "extracted": "2026-09-21",
    "note": (
        "This is a real MCC document, not a third-party estimate. Every "
        "number below is directly aggregated from it -- no scraping, no "
        "scaling, no guessing."
    ),
}


def clean_institute(raw: str) -> str:
    name = raw.split(",")[0].strip()
    name = re.sub(r"\s+", " ", name)
    return name


def clean_category(raw: str) -> str:
    return raw.replace(" PwD", "").strip()


def clean_course(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.replace("\n", " ")).strip()


# Course strings that bundle several alternate wordings of the same
# specialty (separated by "/") defeat the generic parser below -- it just
# grabs whatever sits after the last "/", which for these produced garbage
# like "(Venere Ology". Special-cased here instead of patched around,
# since more such bundled strings may turn up in future documents.
_SPECIAL_CASE_SPECIALTIES = [
    (("VENERE", "DERM"), "Dermatology & Venereology"),
    (("VENERE", "LEPROSY"), "Dermatology & Venereology"),
]


def _fix_unbalanced_parens(s: str) -> str:
    """Drop one stray, unmatched paren from an edge of the string. Some raw
    course strings have a "(...)" aside (e.g. "Otorhinolaryngology
    (E.N.T.)", "(Direct 6 Years Course)") that survives prefix-stripping
    with only one of its two parens left dangling at the edge -- rather
    than blindly trimming both edges (which corrupts genuinely balanced
    names), only trim an edge paren when the string's overall count is
    actually unbalanced."""
    opens, closes = s.count("("), s.count(")")
    if opens == closes:
        return s
    if opens > closes and s.startswith("("):
        s = s[1:]
    if closes > opens and s.endswith(")"):
        s = s[:-1]
    return s.strip()


def clean_specialty(course: str) -> str:
    """Turn a raw course string into a clean 'Specialty (Track)' label,
    merging M.D./M.S. wording differences but keeping DNB (NBEMS) and
    Diploma tracks separate from the MD/MS track -- they're different
    training pathways with very different closing ranks, and merging
    them would be misleading, not simplifying."""
    c = course.strip()
    upper_c = c.upper()

    if c.startswith("(NBEMS-DIPLOMA)"):
        track = "Diploma"
        base = c[len("(NBEMS-DIPLOMA)"):].strip()
    elif re.match(r"^DIP\.?\s*IN\b", c, re.I):
        # e.g. "DIP. IN DERM. VENEREOLOGY and LEPROSY/..." -- a Diploma
        # course that doesn't use the "(NBEMS-DIPLOMA)" prefix, so it
        # would otherwise fall through to the MD/MS branch below.
        track = "Diploma"
        base = re.sub(r"^DIP\.?\s*IN\b", "", c, flags=re.I).strip()
    elif c.startswith("(NBEMS)"):
        track = "DNB"
        base = c[len("(NBEMS)"):].strip()
    else:
        track = "MD/MS"
        # Combined-degree courses list several alternate wordings separated
        # by "/", e.g. "M.D. (Obst. and Gynae)/MS (Obstetrics and
        # Gynaecology)" or "M.D. (Emergency and Critical Care)/M.D.
        # (Emergency Medicine)". Split first, THEN strip the M.D./M.S.
        # prefix off whichever segment we keep -- stripping only once
        # before splitting left a stray "M.D. (" on the front of any
        # segment after the first (e.g. "M.D. (Emergency Medicine").
        segments = [s.strip() for s in c.split("/") if s.strip()]
        base = segments[-1] if segments else c
        base = re.sub(r"^(?:M\.D\.|M\.S\.|M\.P\.H\.|MD|MS|MPH)\s*\(?", "", base, flags=re.I)

    for keywords, clean_name in _SPECIAL_CASE_SPECIALTIES:
        if all(k in upper_c for k in keywords):
            return f"{clean_name} ({track})"

    base = re.sub(r"\s+", " ", base).strip()
    base = _fix_unbalanced_parens(base)
    if base.isupper():
        base = base.title()
    return f"{base} ({track})"


def main() -> None:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    r3_rows = [r for r in rows if r["r3_institute"] not in ("-", "")]

    # (institute, specialty, category) -> list of ranks -- college table
    # groups by the clean *specialty* label (merging MD/MS wording) so a
    # college's "General Medicine" seats aren't split across "M.D.
    # (GENERAL MEDICINE)" vs any stray wording variant.
    by_college_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    # (specialty, category) -> list of ranks  (for the Branch Predictor)
    by_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    institutes_by_specialty: dict[str, set[str]] = defaultdict(set)

    for row in r3_rows:
        rank = int(row["rank"])
        institute = clean_institute(row["r3_institute"])
        specialty = clean_specialty(clean_course(row["r3_course"]))
        category = clean_category(row["r3_alloted_category"])
        if not category:
            continue

        by_college_specialty_category[(institute, specialty, category)].append(rank)
        by_specialty_category[(specialty, category)].append(rank)
        institutes_by_specialty[specialty].add(institute)

    college_table = []
    for (institute, specialty, category), ranks in by_college_specialty_category.items():
        college_table.append(
            {
                "institute": institute,
                "specialty": specialty,
                "category": category,
                "opening_rank": min(ranks),
                "closing_rank": max(ranks),
                "seats_counted": len(ranks),
            }
        )

    specialty_table = []
    for (specialty, category), ranks in by_specialty_category.items():
        specialty_table.append(
            {
                "specialty": specialty,
                "category": category,
                "opening_rank": min(ranks),
                "closing_rank": max(ranks),
                "seats_counted": len(ranks),
                "institutes_counted": len(institutes_by_specialty[specialty]),
            }
        )

    provenance = dict(SOURCE_DOCUMENT)
    provenance["candidate_rows_seen"] = len(rows)
    provenance["round3_allotment_rows"] = len(r3_rows)

    payload = {
        "provenance": provenance,
        "methodology": (
            "Opening/closing rank computed directly from every candidate row "
            "with a real Round 3 allotment in the source PDF, grouped by "
            "institute + specialty + ALLOTTED category (not candidate "
            "category). Specialty labels merge M.D./M.S. wording variants "
            "of the same subject, but keep NBEMS/DNB and Diploma tracks "
            "separate from the MD/MS track, since those are different "
            "training pathways with different closing ranks. PwD variants "
            "folded into their base category. Not split by quota (AI/state/ "
            "management etc.) -- most college+specialty+category cells "
            "already have very few candidates, and splitting further would "
            "fragment them past usefulness. See "
            "engine/build_2024_closing_ranks.py for the exact code."
        ),
        "college_specialty_category": college_table,
        "specialty_category": specialty_table,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Institutes: {len(set(clean_institute(r['r3_institute']) for r in r3_rows))}")
    print(f"Specialties (cleaned): {len(set(clean_specialty(clean_course(r['r3_course'])) for r in r3_rows))}")
    print(f"college_specialty_category combinations: {len(college_table)}")
    print(f"specialty_category combinations: {len(specialty_table)}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
