"""Generalized closing-rank builder for MCC "Round 3" style CSVs (the
16-column R1/R2/R3 layout produced by extract_r1r2r3_pdf.py). Generalizes
build_2024_closing_ranks.py so the same tested logic builds every such
dataset (2024 Round 3, 2025 Round 3, and any future upload) instead of
copy-pasting it per year.

Methodology (same rule for every dataset this produces):
  - opening rank = MIN candidate rank allotted that institute+course+category
  - closing rank = MAX candidate rank allotted that institute+course+category
  - category used is the ALLOTTED category (the seat's category), never
    the candidate's own category -- an OBC candidate can get an Open
    seat, and that seat's closing rank belongs to Open, not OBC.
  - "Open PwD" / "OBC PwD" / etc. are EXCLUDED from their base category's
    opening/closing rank (PwD is a horizontal reservation with much easier
    ranks; folding it in was inflating the base category's closing rank --
    see is_pwd_category() in mcc_cleaning.py for a real example).
  - A seat is counted whether or not the candidate ultimately "Reported"
    for admission -- MCC's own closing-rank convention is allotment-based.

Usage: python3 build_r1r2r3_closing_ranks.py <csv_path> <out_json_path> <provenance_json_path>
where provenance_json_path is a small JSON file with the SOURCE_DOCUMENT
fields (title, provided_by, authority, round, cycle, pages, extracted, note).
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    from engine.mcc_cleaning import (
        clean_category, clean_course, clean_institute, clean_specialty,
        is_pwd_category, is_service_bond_institute,
    )
except ImportError:  # run directly as a script (python3 build_r1r2r3_closing_ranks.py ...) from engine/
    from mcc_cleaning import (
        clean_category, clean_course, clean_institute, clean_specialty,
        is_pwd_category, is_service_bond_institute,
    )


def build(csv_path: str, provenance_seed: dict) -> dict:
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    r3_rows = [r for r in rows if r["r3_institute"] not in ("-", "")]

    by_college_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    by_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    institutes_by_specialty: dict[str, set[str]] = defaultdict(set)

    for row in r3_rows:
        raw_category = row["r3_alloted_category"]
        if is_pwd_category(raw_category):
            # PwD is a horizontal reservation with a much easier rank cutoff;
            # counting it toward the base category's MAX-rank closing rank
            # would badly inflate what a non-PwD candidate can actually get.
            continue
        rank = int(row["rank"])
        institute = clean_institute(row["r3_institute"])
        if is_service_bond_institute(institute):
            # Armed Forces/Command Hospital seats carry a mandatory service
            # bond most civilian candidates won't take -- see
            # is_service_bond_institute() in mcc_cleaning.py.
            continue
        specialty = clean_specialty(clean_course(row["r3_course"]))
        category = clean_category(raw_category)
        if not category:
            continue

        by_college_specialty_category[(institute, specialty, category)].append(rank)
        by_specialty_category[(specialty, category)].append(rank)
        institutes_by_specialty[specialty].add(institute)

    college_table = [
        {
            "institute": institute, "specialty": specialty, "category": category,
            "opening_rank": min(ranks), "closing_rank": max(ranks), "seats_counted": len(ranks),
        }
        for (institute, specialty, category), ranks in by_college_specialty_category.items()
    ]
    specialty_table = [
        {
            "specialty": specialty, "category": category,
            "opening_rank": min(ranks), "closing_rank": max(ranks), "seats_counted": len(ranks),
            "institutes_counted": len(institutes_by_specialty[specialty]),
        }
        for (specialty, category), ranks in by_specialty_category.items()
    ]

    provenance = dict(provenance_seed)
    provenance["candidate_rows_seen"] = len(rows)
    provenance["round3_allotment_rows"] = len(r3_rows)

    return {
        "provenance": provenance,
        "methodology": (
            "Opening/closing rank computed directly from every candidate row "
            "with a real Round 3 allotment in the source PDF, grouped by "
            "institute + specialty + ALLOTTED category (not candidate "
            "category). Specialty labels merge M.D./M.S. wording variants "
            "of the same subject, but keep NBEMS/DNB and Diploma tracks "
            "separate from the MD/MS track, since those are different "
            "training pathways with different closing ranks. PwD-reserved "
            "allotments (a horizontal reservation cutting across every "
            "category, with much easier ranks) are EXCLUDED from these "
            "figures rather than folded into their base category -- folding "
            "them in was inflating the base category's closing rank. Armed "
            "Forces/Command Hospital seats (a mandatory service bond few "
            "civilian candidates take) are EXCLUDED entirely -- see "
            "is_service_bond_institute() in mcc_cleaning.py. Not "
            "split by quota (AI/state/ "
            "management etc.) -- most college+specialty+category cells "
            "already have very few candidates, and splitting further would "
            "fragment them past usefulness."
        ),
        "college_specialty_category": college_table,
        "specialty_category": specialty_table,
    }


def main(csv_path: str, out_path: str, provenance_path: str) -> None:
    provenance_seed = json.loads(Path(provenance_path).read_text(encoding="utf-8"))
    payload = build(csv_path, provenance_seed)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    ct, st = payload["college_specialty_category"], payload["specialty_category"]
    print(f"Institutes: {len(set(r['institute'] for r in ct))}")
    print(f"Specialties (cleaned): {len(set(r['specialty'] for r in st))}")
    print(f"college_specialty_category combinations: {len(ct)}")
    print(f"specialty_category combinations: {len(st)}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
