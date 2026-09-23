"""Convenience entry point: init the DB, seed MCC sources, run the monitor
against each fixture snapshot, and print a summary. This is what stands in
for the scheduled job while we're developing inside this sandbox (no
network to mcc.nic.in). On GitHub Actions, the same monitor.run_once is
called with engine.fetch.fetch_url(source.url) instead of a fixture.

Usage: python3 -m engine.run_local
"""

from __future__ import annotations

from engine import db, fetch, monitor

SOURCE_FIXTURES = {
    "mcc_pg_current_events": "mcc_current_events_pg.html",
    "mcc_pg_news_events": "mcc_news_events_pg.html",
    "mcc_pg_archive": "mcc_archive_pg.html",
}


def main() -> None:
    conn = db.connect()
    db.init_db(conn)
    db.seed_mcc(conn)

    for source_id, fixture_name in SOURCE_FIXTURES.items():
        html = fetch.fetch_fixture(fixture_name)
        result = monitor.run_once(conn, source_id, html)
        print(
            f"[{source_id}] entries_seen={result['entries_seen']} "
            f"new_documents={result['new_documents']}"
        )

    total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    print(f"\nTotal documents in database: {total_docs}")
    conn.close()


if __name__ == "__main__":
    main()
