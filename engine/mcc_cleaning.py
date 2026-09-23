"""Shared cleaning helpers for turning raw MCC allotment-PDF text into
clean institute/specialty/category labels. Used by every
build_*_closing_ranks.py script so all real-MCC datasets (2024 Round 3,
2025 Round 3, 2025 Stray, and any future upload) get identical, tested
cleaning logic rather than copy-pasted drift.
"""

from __future__ import annotations

import re

# Course strings that bundle several alternate wordings of the same
# specialty (separated by "/") defeat the generic parser below -- it just
# grabs whatever sits after the last "/", which for these produced garbage
# like "(Venere Ology". Special-cased here instead of patched around,
# since more such bundled strings may turn up in future documents.
_SPECIAL_CASE_SPECIALTIES = [
    (("VENERE", "DERM"), "Dermatology & Venereology"),
    (("VENERE", "LEPROSY"), "Dermatology & Venereology"),
]


def clean_institute(raw: str) -> str:
    name = raw.split(",")[0].strip()
    name = re.sub(r"\s+", " ", name)
    return name


def clean_category(raw: str) -> str:
    return raw.replace(" PwD", "").strip()


def clean_course(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.replace("\n", " ")).strip()


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
        track = "Diploma"
        base = re.sub(r"^DIP\.?\s*IN\b", "", c, flags=re.I).strip()
    elif c.startswith("(NBEMS)"):
        track = "DNB"
        base = c[len("(NBEMS)"):].strip()
    else:
        track = "MD/MS"
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
