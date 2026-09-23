"""Validation rules applied before any extracted dataset (a real MCC
seat/allotment result, auto-downloaded and parsed) is allowed to go live.

This is stage 6 of the project's own pipeline:
  OFFICIAL SOURCE -> DETECTION -> DOWNLOAD -> EXTRACTION -> PARSING
    -> VALIDATION -> DIFFERENCE DETECTION -> HUMAN REVIEW WHEN NECESSARY
    -> PUBLISH

`validate_extraction()` covers the raw-extraction checks (malformed PDF,
missing columns, unexpected category/round values, impossible ranks,
duplicate rows, invalid college/course combos). `diff_against_previous()`
covers "unexplained large changes" by comparing a newly-built dataset
against the previous version of the SAME round (if one exists) --
different rounds/years are expected to differ a lot, so this only compares
like-for-like re-extractions (e.g. a corrected re-run of the same PDF).

Every check returns ValidationIssue objects rather than raising, so the
caller can decide what "pass" means (currently: zero ERROR-severity
issues; WARNING-severity issues are recorded but don't block publish) and
always has the full list to write into the review queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field

KNOWN_CATEGORIES = {"Open", "OBC", "EWS", "SC", "ST"}
KNOWN_ROUND_KEYWORDS = (
    "round 1", "round 2", "round 3", "round 4",
    "special stray", "stray",
)
# Sanity bound, not a hard cap tied to any specific year's candidate count --
# NEET-PG typically has on the order of 200,000-250,000 candidates; a rank
# far beyond that in a real allotment row means something was misread
# (e.g. a rollno or a page number scraped into the rank column).
MAX_PLAUSIBLE_RANK = 400_000
# A closing rank more than this multiple away from the same
# institute+specialty+category cell's previous value is flagged for human
# eyes -- it might be real (a popular seat added/removed) but it might also
# be a parsing error, and the project's own rule is "never blindly publish".
LARGE_CHANGE_RATIO = 3.0


@dataclass
class ValidationIssue:
    severity: str          # "error" | "warning"
    rule: str               # short machine-readable rule name
    message: str            # human-readable explanation
    context: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def passed(self) -> bool:
        """Passes if there are zero ERROR-severity issues. Warnings are
        recorded but don't block publish -- they're surfaced to the human
        reviewer either way, in the dataset's own provenance."""
        return len(self.errors) == 0


def _err(rule: str, message: str, **context) -> ValidationIssue:
    return ValidationIssue(severity="error", rule=rule, message=message, context=context)


def _warn(rule: str, message: str, **context) -> ValidationIssue:
    return ValidationIssue(severity="warning", rule=rule, message=message, context=context)


def validate_raw_rows(rows: list[dict], expected_fields: list[str]) -> list[ValidationIssue]:
    """Row-level checks on the raw extracted CSV rows, before cleaning /
    aggregation. Catches a malformed PDF (extraction produced nothing, or
    rows missing the columns the layout requires) early, before it can
    poison anything downstream."""
    issues: list[ValidationIssue] = []

    if not rows:
        issues.append(_err("malformed_pdf", "Extraction produced zero rows -- the PDF may not match the expected layout, or pdfplumber found no tables."))
        return issues

    missing_col_rows = [r for r in rows if any(f not in r or r[f] is None for f in expected_fields)]
    if missing_col_rows:
        issues.append(_err(
            "missing_columns",
            f"{len(missing_col_rows)} of {len(rows)} rows are missing one or more expected columns "
            f"({expected_fields}) -- the table layout may have shifted.",
            bad_row_count=len(missing_col_rows),
        ))

    seen_snos: dict[str, int] = {}
    for r in rows:
        sno = r.get("sno") or r.get("SNo")
        if sno:
            seen_snos[sno] = seen_snos.get(sno, 0) + 1
    dupes = {k: v for k, v in seen_snos.items() if v > 1}
    if dupes:
        issues.append(_warn(
            "duplicate_row_numbers",
            f"{len(dupes)} S.No value(s) appear more than once in the raw extraction "
            "(a table header row or footer may have been captured as data).",
            examples=list(dupes)[:5],
        ))

    return issues


def validate_built_dataset(payload: dict) -> list[ValidationIssue]:
    """Checks on the aggregated dataset (after cleaning + grouping into
    college_specialty_category / specialty_category), the same shape every
    build_*_closing_ranks.py script produces."""
    issues: list[ValidationIssue] = []

    college_rows = payload.get("college_specialty_category", [])
    specialty_rows = payload.get("specialty_category", [])

    if not college_rows and not specialty_rows:
        issues.append(_err("malformed_pdf", "The built dataset has zero rows in either table -- nothing survived aggregation."))
        return issues

    seen_keys: set[tuple] = set()
    for row in college_rows:
        key = (row.get("institute"), row.get("specialty"), row.get("category"))

        if key in seen_keys:
            issues.append(_err(
                "duplicate_allotment_key",
                f"institute+specialty+category {key} appears more than once in college_specialty_category "
                "-- aggregation should have merged these into one row.",
                key=list(key),
            ))
        seen_keys.add(key)

        if not row.get("institute") or not str(row.get("institute")).strip():
            issues.append(_err("invalid_college_combo", "A row has an empty institute name.", row=row))
        if not row.get("specialty") or not str(row.get("specialty")).strip():
            issues.append(_err("invalid_college_combo", "A row has an empty specialty/course name.", row=row))

        category = row.get("category")
        if category not in KNOWN_CATEGORIES:
            issues.append(_err(
                "unexpected_category",
                f"Category {category!r} is not one of the known values {sorted(KNOWN_CATEGORIES)}.",
                row=row,
            ))

        for rank_field in ("opening_rank", "closing_rank"):
            rank = row.get(rank_field)
            if not isinstance(rank, int) or rank <= 0:
                issues.append(_err("impossible_rank", f"{rank_field}={rank!r} is not a positive integer.", row=row))
            elif rank > MAX_PLAUSIBLE_RANK:
                issues.append(_warn(
                    "impossible_rank",
                    f"{rank_field}={rank} is implausibly large for a NEET-PG rank (> {MAX_PLAUSIBLE_RANK:,}) -- check for a mis-scraped value.",
                    row=row,
                ))

        if isinstance(row.get("opening_rank"), int) and isinstance(row.get("closing_rank"), int):
            if row["opening_rank"] > row["closing_rank"]:
                issues.append(_err(
                    "impossible_rank",
                    f"opening_rank ({row['opening_rank']}) is greater than closing_rank ({row['closing_rank']}) "
                    "for the same institute+specialty+category -- opening should never exceed closing.",
                    row=row,
                ))

        seats = row.get("seats_counted")
        if not isinstance(seats, int) or seats <= 0:
            issues.append(_err("duplicate_seats", f"seats_counted={seats!r} should be a positive integer.", row=row))

    round_note = payload.get("provenance", {}).get("round", "") or ""
    if round_note and not any(k in round_note.lower() for k in KNOWN_ROUND_KEYWORDS):
        issues.append(_warn(
            "unexpected_round_name",
            f"provenance.round={round_note!r} doesn't match any known round name/keyword -- double-check it wasn't misread from the document title.",
        ))

    return issues


def diff_against_previous(new_payload: dict, previous_payload: dict | None) -> list[ValidationIssue]:
    """Flags large, unexplained jumps in closing rank for the SAME
    institute+specialty+category between two versions of what should be
    the SAME round (e.g. a corrected re-extraction of the same PDF, not a
    genuinely different round/year -- comparing across different rounds is
    expected to differ a lot and would just be noise here)."""
    if not previous_payload:
        return []

    issues: list[ValidationIssue] = []
    prev_by_key = {
        (r.get("institute"), r.get("specialty"), r.get("category")): r
        for r in previous_payload.get("college_specialty_category", [])
    }
    for row in new_payload.get("college_specialty_category", []):
        key = (row.get("institute"), row.get("specialty"), row.get("category"))
        prev = prev_by_key.get(key)
        if not prev:
            continue
        old_rank, new_rank = prev.get("closing_rank"), row.get("closing_rank")
        if not (isinstance(old_rank, int) and isinstance(new_rank, int)) or old_rank == 0:
            continue
        ratio = max(new_rank, old_rank) / max(min(new_rank, old_rank), 1)
        if ratio >= LARGE_CHANGE_RATIO:
            issues.append(_warn(
                "unexplained_large_change",
                f"{key}: closing rank moved from {old_rank} to {new_rank} ({ratio:.1f}x) between versions of the same round.",
                key=list(key), old_rank=old_rank, new_rank=new_rank,
            ))
    return issues


def validate(
    payload: dict,
    raw_rows: list[dict] | None = None,
    expected_fields: list[str] | None = None,
    previous_payload: dict | None = None,
) -> ValidationResult:
    """Run every applicable check and return one ValidationResult.
    raw_rows/expected_fields are optional -- pass them when you have the
    pre-aggregation rows available, for the earliest possible catch of a
    malformed PDF or missing columns."""
    issues: list[ValidationIssue] = []
    if raw_rows is not None and expected_fields is not None:
        issues += validate_raw_rows(raw_rows, expected_fields)
    issues += validate_built_dataset(payload)
    issues += diff_against_previous(payload, previous_payload)
    return ValidationResult(issues=issues)
