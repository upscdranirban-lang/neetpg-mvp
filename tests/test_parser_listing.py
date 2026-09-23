import re

from engine.fetch import fetch_fixture
from engine.parser_listing import parse_listing_html


def test_current_events_fixture_parses_all_rows():
    html = fetch_fixture("mcc_current_events_pg.html")
    entries = parse_listing_html(html)
    assert len(entries) == 12
    # Title must NOT include the leaked row-number (S.No) or bare year
    # column -- real MCC titles do legitimately start with a date like
    # "21.01.2026_...", so we check for the specific leak pattern
    # (a lone 1-2 digit S.No followed by a space) rather than banning
    # digit-led titles outright.
    titles = [e.title for e in entries]
    leaked_row_number = re.compile(r"^\d{1,2}\s")
    assert not any(leaked_row_number.match(t) for t in titles)
    assert any("Final Result for Round-III" in t for t in titles)
    assert all(e.file_url.startswith("https://cdnbbsr.s3waas.gov.in/") for e in entries)


def test_no_document_links_returns_empty_not_crash():
    entries = parse_listing_html("<html><body><p>nothing here</p></body></html>")
    assert entries == []


def test_positions_are_in_page_order():
    html = fetch_fixture("mcc_news_events_pg.html")
    entries = parse_listing_html(html)
    positions = [e.position for e in entries]
    assert positions == sorted(positions)
