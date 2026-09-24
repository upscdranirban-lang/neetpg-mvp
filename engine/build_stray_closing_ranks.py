"""Closing-rank builder for MCC "Stray Vacancy Round" style CSVs (the
8-column single-round layout produced by extract_stray_pdf.py): SNo,
rank, quota, institute, course, alloted_category, candidate_category,
remarks -- every row IS a real allotment (there's no "-" placeholder like
the Round 1/2/3 layout, since a stray-round list only lists seats that
were actually allotted in that round).

Same methodology as build_r1r2r3_closing_ranks.py: opening/closing rank
by institute + specialty + ALLOTTED category, PwD-reserved allotments
EXCLUDED from their base category (folding them in inflates the base
category's closing rank -- see is_pwd_category() in mcc_cleaning.py),
counted regardless of "Reported"/"Not Reported" status.

Usage: python3 build_stray_closing_ranks.py <csv_path> <out_json_path> <provenance_json_path>
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
except ImportError:  # run directly as a script (python3 build_stray_closing_ranks.py ...) from engine/
    from mcc_cleaning import (
        clean_category, clean_course, clean_institute, clean_specialty,
        is_pwd_category, is_service_bond_institute,
    )


def build(csv_path: str, provenance_seed: dict) -> dict:
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    by_college_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    by_specialty_category: dict[tuple, list[int]] = defaultdict(list)
    institutes_by_specialty: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if not row.get("institute") or row["institute"] == "-":
            continue
        raw_category = row["alloted_category"]
        if is_pwd_category(raw_category):
            # PwD is a horizontal reservation with a much easier rank cutoff;
            # counting it toward the base category's MAX-rank closing rank
            # would badly inflate what a non-PwD candidate can actually get.
            continue
        rank = int(row["rank"])
        institute = clean_institute(row["institute"])
        if is_service_bond_institute(institute):
            # Armed Forces/Command Hospital seats carry a mandatory service
            # bond most civilian candidates won't take -- see
            # is_service_bond_institute() in mcc_cleaning.py.
            continue
        specialty = clean_specialty(clean_course(row["course"]))
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
    provenance["allotment_rows"] = len(rows)

    return {
        "provenance": provenance,
        "methodology": (
            "Opening/closing rank computed directly from every allotment row "
            "in the source PDF (a stray-vacancy list only contains rows that "
            "were actually allotted), grouped by institute + specialty + "
            "ALLOTTED category (not candidate category). Specialty labels "
            "merge M.D./M.S. wording variants of the same subject, but keep "
            "NBEMS/DNB and Diploma tracks separate from the MD/MS track. "
            "PwD-reserved allotments (a horizontal reservation with much "
            "easier ranks) are EXCLUDED from these figures rather than "
            "folded into their base category -- folding them in was "
            "inflating the base category's closing rank. Armed Forces/"
            "Command Hospital seats (a mandatory service bond few civilian "
            "candidates take) are EXCLUDED entirely -- see "
            "is_service_bond_institute() in mcc_cleaning.py. This is a single, "
            "separate round -- its ranks are not comparable to Round 3's, "
            "since stray vacancy seats are filled from a different, later "
            "pool of candidates."
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
