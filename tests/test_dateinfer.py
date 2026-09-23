from datetime import date, datetime, timezone

from engine.dateinfer import infer_date


def test_title_date_wins_over_filename():
    d = infer_date(
        "21.01.2026_UPDATED CLEAR VACANCY ROUND 3 (MD MS AND DNB)",
        "https://cdnbbsr.s3waas.gov.in/.../uploads/2026/01/20260121202622395.pdf",
        datetime(2026, 9, 21, tzinfo=timezone.utc),
    )
    assert d.value == date(2026, 1, 21)
    assert d.basis == "title"
    assert d.confidence == "high"


def test_filename_timestamp_used_when_no_title_date():
    d = infer_date(
        "PG VACANT SEATS FOR STRAY ROUND PG 2025",
        "https://cdnbbsr.s3waas.gov.in/.../uploads/2026/02/202602161795622621.pdf",
        datetime(2026, 9, 21, tzinfo=timezone.utc),
    )
    assert d.value == date(2026, 2, 16)
    assert d.basis == "filename"
    assert d.confidence == "medium"


def test_falls_back_to_first_seen():
    seen_at = datetime(2026, 9, 21, tzinfo=timezone.utc)
    d = infer_date("A title with no date anywhere", "https://example.com/doc", seen_at)
    assert d.value == seen_at.date()
    assert d.basis == "first_seen"
    assert d.confidence == "low"
