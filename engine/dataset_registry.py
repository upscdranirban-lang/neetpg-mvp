"""Registry for the Predictor's real-MCC datasets.

Each dataset (one specific round of one specific counselling cycle, e.g.
"Round 3, PG Counselling 2025") lives as one self-describing JSON file
under site/datasets/<id>.json. site/datasets_manifest.json lists which
ids exist and in what order the Predictor's dropdown should default
(newest cycle first, then earliest round first within a cycle) -- this is
the ONLY place that needs to change when a new round is added, whether by
hand or by the automated pipeline. engine/build_site.py reads the
manifest and embeds every listed dataset; it does not know or care how
many there are.

A dataset file's shape:
{
  "id": "real2025r3",
  "label": "2025 Round 3 (Real MCC)",           # dropdown option text
  "roundNote": "Round 3, 2025",                  # short in-line label
  "warningTitle": "...",                         # predictor warning banner
  "warningBody": "...",                          # predictor warning banner
  "provenance": {...},                           # from the builder script
  "methodology": "...",                          # from the builder script
  "specialty_category": [...],
  "college_specialty_category": [...]
}
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATASETS_DIR = SITE / "datasets"
MANIFEST_PATH = SITE / "datasets_manifest.json"

# Lower = shown/defaulted-to earlier within the same cycle year.
ROUND_SORT_RANK = {
    "round 1": 10,
    "round 2": 20,
    "round 3": 30,
    "round 4": 40,
    "special stray": 80,
    "stray": 90,
    "stray vacancy round": 90,
}


def _round_rank(round_note: str) -> int:
    key = round_note.lower()
    for name, rank in ROUND_SORT_RANK.items():
        if name in key:
            return rank
    return 50  # unknown round: sort in the middle rather than first or last


def _cycle_year(provenance: dict, round_note: str) -> int:
    cycle = provenance.get("cycle") or ""
    m = re.search(r"20\d{2}", cycle) or re.search(r"20\d{2}", round_note)
    return int(m.group(0)) if m else 0


def load_manifest() -> list[str]:
    if not MANIFEST_PATH.exists():
        return []
    return [d["id"] for d in json.loads(MANIFEST_PATH.read_text())["datasets"]]


def load_dataset(dataset_id: str) -> dict:
    return json.loads((DATASETS_DIR / f"{dataset_id}.json").read_text(encoding="utf-8"))


def publish_dataset(
    dataset_id: str,
    label: str,
    round_note: str,
    warning_title: str,
    warning_body: str,
    built_payload: dict,
) -> None:
    """Write site/datasets/<id>.json and (re)insert it into the manifest in
    the correct newest-cycle-first, earliest-round-first order. Safe to call
    again for the same id (e.g. a corrected re-extraction) -- it overwrites
    the file and re-sorts rather than duplicating the manifest entry."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    doc = {
        "id": dataset_id,
        "label": label,
        "roundNote": round_note,
        "warningTitle": warning_title,
        "warningBody": warning_body,
        "provenance": built_payload["provenance"],
        "methodology": built_payload["methodology"],
        "specialty_category": built_payload["specialty_category"],
        "college_specialty_category": built_payload["college_specialty_category"],
    }
    (DATASETS_DIR / f"{dataset_id}.json").write_text(json.dumps(doc), encoding="utf-8")

    ids = [i for i in load_manifest() if i != dataset_id]
    ids.append(dataset_id)

    def sort_key(i: str) -> tuple[int, int]:
        d = load_dataset(i)
        cycle_year = _cycle_year(d["provenance"], d["roundNote"])
        return (-cycle_year, _round_rank(d["roundNote"]))

    ids.sort(key=sort_key)
    MANIFEST_PATH.write_text(
        json.dumps({"datasets": [{"id": i, "source_file": f"datasets/{i}.json"} for i in ids]}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    print("Datasets currently in the manifest, in default order:")
    for i in load_manifest():
        d = load_dataset(i)
        print(f"  {i}: {d['label']}")
