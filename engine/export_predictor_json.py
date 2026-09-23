"""Export engine/predictor_data.py into site/predictor_data.json, in the
shape the site's Predictor tab consumes. Kept as a separate export/file
from export_json.py on purpose -- this data has a different, weaker
provenance (third-party, not MCC) and must never merge with the real
documents feed."""

from __future__ import annotations

import json
from pathlib import Path

from engine import predictor_data as pd

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "site" / "predictor_data.json"


CATEGORIES = ["Open", "OBC", "EWS", "SC", "ST"]


def build_payload() -> dict:
    specialties = []
    # index: specialty -> {category: {R1: x, R2: y}}
    specialty_index: dict[str, dict] = {}

    for row in pd.SPECIALTY_ALL_CATEGORIES:
        name = row[0]
        vals = row[1:]  # Open_R1, Open_R2, OBC_R1, OBC_R2, EWS_R1, EWS_R2, SC_R1, SC_R2, ST_R1, ST_R2
        by_cat = {}
        for i, cat in enumerate(CATEGORIES):
            r1, r2 = vals[i * 2], vals[i * 2 + 1]
            by_cat[cat] = {"R1": r1, "R2": r2}
        specialty_index[name] = by_cat
        specialties.append({"specialty": name, "categories": by_cat})

    # College tables: real (Open, "reported") + calculated estimates for
    # the other categories, scaled from the specialty-level Round 1
    # category-vs-Open ratio. Every calculated row is tagged so the site
    # can visibly distinguish it from a directly reported number.
    colleges_by_specialty = {}
    for specialty, rows in pd.COLLEGE_RANKS.items():
        cats = specialty_index.get(specialty, {})
        open_r1 = cats.get("Open", {}).get("R1")
        entry = {"Open": [{"college": n, "opening_rank": o, "closing_rank": c, "basis": "reported"} for n, o, c in rows]}

        for cat in ["OBC", "EWS", "SC", "ST"]:
            cat_r1 = cats.get(cat, {}).get("R1")
            if not open_r1 or not cat_r1:
                entry[cat] = []  # no specialty-level ratio available to scale with
                continue
            ratio = cat_r1 / open_r1
            entry[cat] = [
                {
                    "college": n,
                    "opening_rank": round(o * ratio),
                    "closing_rank": round(c * ratio),
                    "basis": "calculated",
                }
                for n, o, c in rows
            ]
        colleges_by_specialty[specialty] = entry

    return {
        "disclaimer": (
            "ESTIMATE ONLY -- not official MCC data. These numbers come from "
            "third-party exam-prep sites, not from MCC's own result documents. "
            "Real counselling results can differ significantly. Use this only "
            "as a rough starting point, never as a guarantee."
        ),
        "sources": pd.SOURCES,
        "not_used": pd.NOT_USED,
        "category_adjustment_note": pd.CATEGORY_ADJUSTMENT_NOTE,
        "coverage_note": (
            "Round 1 & Round 2: Open/OBC/EWS/SC/ST at specialty level. "
            "Round 3 / Stray: no category-wise data found on any source "
            "checked -- not available in this demo. College-level tables "
            "exist only for Open (reported); other categories shown there "
            "are calculated estimates, not reported figures -- see the "
            "'Calculated' label on each result."
        ),
        "specialties": specialties,
        "colleges_by_specialty": colleges_by_specialty,
    }


def main() -> None:
    payload = build_payload()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(payload['specialties'])} specialties, "
          f"{len(payload['colleges_by_specialty'])} specialties with college tables)")


if __name__ == "__main__":
    main()
