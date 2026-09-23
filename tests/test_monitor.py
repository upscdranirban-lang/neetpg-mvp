import sqlite3

from engine import db, fetch, monitor


def _make_conn() -> sqlite3.Connection:
    """Not a pytest fixture (pytest isn't importable in this sandbox
    alongside bs4/requests -- see tests/run_all.py) -- just a plain
    helper each test calls for a fresh in-memory database."""
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    db.init_db(c)
    db.seed_mcc(c)
    return c


def test_first_run_inserts_all_as_new():
    conn = _make_conn()
    html = fetch.fetch_fixture("mcc_current_events_pg.html")
    result = monitor.run_once(conn, "mcc_pg_current_events", html)
    assert result["entries_seen"] == 12
    assert result["new_documents"] == 12

    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    change_count = conn.execute("SELECT COUNT(*) FROM data_changes").fetchone()[0]
    assert doc_count == 12
    assert change_count == 12


def test_second_run_with_same_html_finds_nothing_new():
    conn = _make_conn()
    html = fetch.fetch_fixture("mcc_current_events_pg.html")
    monitor.run_once(conn, "mcc_pg_current_events", html)
    result = monitor.run_once(conn, "mcc_pg_current_events", html)
    assert result["new_documents"] == 0

    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    assert doc_count == 12  # not duplicated


def test_one_new_document_appended_is_detected():
    conn = _make_conn()
    html = fetch.fetch_fixture("mcc_current_events_pg.html")
    monitor.run_once(conn, "mcc_pg_current_events", html)

    extra_row = (
        '<tr><td>13</td><td>Brand New Notice for Round 4 of PG 2025</td>'
        '<td>2026</td><td><a href="https://cdnbbsr.s3waas.gov.in/x/uploads/2026/09/2026090112000000.pdf">'
        "Download</a></td></tr></tbody>"
    )
    updated_html = html.replace("</tbody>", extra_row)
    result = monitor.run_once(conn, "mcc_pg_current_events", updated_html)
    assert result["new_documents"] == 1

    new_doc = conn.execute(
        "SELECT * FROM documents WHERE title LIKE 'Brand New Notice%'"
    ).fetchone()
    assert new_doc is not None
    assert new_doc["round_label"] == "Round 4"


def test_update_run_is_recorded():
    conn = _make_conn()
    html = fetch.fetch_fixture("mcc_current_events_pg.html")
    monitor.run_once(conn, "mcc_pg_current_events", html)
    run = conn.execute(
        "SELECT * FROM update_runs WHERE source_id = 'mcc_pg_current_events'"
    ).fetchone()
    assert run["status"] == "ok"
    assert run["new_documents"] == 12
