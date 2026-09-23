"""Guess a document's type, counselling cycle and round purely from its
title text. MCC's listing pages give us only a title and a link -- no
structured type field -- so this has to be pattern matching, and it has to
be tolerant of the inconsistent, occasionally misspelled way MCC titles
things ("VACANY" instead of "VACANCY" has actually appeared).

Every guess carries a confidence score. Low-confidence guesses should be
routed to human review before anything is built on top of them (e.g. a
predictor); for this MVP we just display the guess and the confidence
plainly, we don't hide the uncertainty.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Ordered so more specific patterns are checked before generic ones.
# Each pattern list is tried in order; the first match wins.
DOC_TYPE_RULES: list[tuple[str, list[str]]] = [
    ("revised_result", [r"revis(ed|ion)\s+result", r"revised.*result"]),
    ("final_result", [r"final\s+result"]),
    ("provisional_result", [r"provisional.*result"]),
    ("result", [r"\bresult\b"]),
    ("seat_addition_deletion", [
        r"addition\s+of\s+seat", r"deletion\s+of\s+seat", r"withdraw(al)?\s+of\s+seat",
        r"withdrawal\s+seat", r"add\s+or\s+removal\s+of\s+seat", r"verification\s+for\s+newly\s+added\s+seat",
    ]),
    ("vacancy", [r"vaca(n|nc)?y", r"vacant\s+seat"]),  # tolerant of "VACANY" typo
    ("seat_matrix", [r"seat\s+matrix"]),
    ("admitted_candidates", [r"admitted\s+candidate", r"joined\s+candidate"]),
    ("choice_filling_notice", [r"choice\s+filling"]),
    ("counselling_schedule", [r"schedule\s+(for|of)\b", r"counselling\s+schedule", r"information\s+bulletin"]),
    ("refund_notice", [r"refund\s+of\s+security\s+deposit", r"refund.*deposit"]),
    ("nri_notice", [r"\bnri\b"]),
    ("public_notice", [r"public\s+notice", r"^notice\b"]),
    ("news_event", [r"press\s+release", r"advertisement", r"guidelines?\b"]),
]

ROUND_RULES: list[tuple[str, list[str]]] = [
    ("Round 1", [r"round[\s-]*(1|i)\b", r"round\s*one"]),
    ("Round 2", [r"round[\s-]*(2|ii)\b", r"round\s*two"]),
    ("Round 3", [r"round[\s-]*(3|iii)\b", r"round\s*three"]),
    ("Round 4", [r"round[\s-]*(4|iv)\b", r"round\s*four"]),
    ("Stray", [r"stray"]),
    ("Special Stray", [r"special\s+stray"]),
]

# e.g. "PG Counselling 2025", "PG 2025". Deliberately NOT matching
# "Academic Year 2026-27" -- MCC's own listing "year" (an academic/session
# year) is a different concept from the counselling *cycle* label, and
# conflating them would invent a cycle ("PG Counselling 2026") that does
# not exist yet just because a document mentions the upcoming academic
# year. See the design doc's "year vs cycle label" finding.
CYCLE_RE = re.compile(r"(pg\s+counselling\s+20\d{2}|pg\s*20\d{2})", re.IGNORECASE)


@dataclass
class Classification:
    doc_type: str
    doc_type_confidence: float
    round_label: str | None
    cycle_label: str | None


def classify(title: str) -> Classification:
    t = title.lower()

    doc_type = "unclassified"
    confidence = 0.3  # default: we genuinely don't know
    for label, patterns in DOC_TYPE_RULES:
        if any(re.search(p, t) for p in patterns):
            doc_type = label
            confidence = 0.9
            break

    round_label = None
    for label, patterns in ROUND_RULES:
        if any(re.search(p, t) for p in patterns):
            round_label = label
            break

    cycle_match = CYCLE_RE.search(t)
    cycle_label = None
    if cycle_match:
        raw = cycle_match.group(1)
        year_match = re.search(r"20\d{2}", raw)
        if year_match:
            cycle_label = f"PG Counselling {year_match.group(0)}"

    return Classification(
        doc_type=doc_type,
        doc_type_confidence=confidence,
        round_label=round_label,
        cycle_label=cycle_label,
    )


DOC_TYPES = [label for label, _ in DOC_TYPE_RULES] + ["unclassified"]
