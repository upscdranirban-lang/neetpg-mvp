"""SQLite schema for the MVP thin slice.

This is deliberately a small subset of the full design (see the
"NEET-PG Counselling Platform - Data Engine Design v1" doc). The MVP only
needs to monitor listing pages, classify documents, infer a date, and show
Dashboard / Latest Updates / Archive on the site -- so we only store what
those need. Seats, allotments, cutoffs and the rest of the 20-table schema
come later, once real PDFs can be parsed (Phase 3+).

Nothing here is ever UPDATEd in a way that destroys history: a document
row is only ever inserted once (keyed by content_hash); if MCC edits a
title or re-publishes under a new hash, that is a NEW row plus a
data_changes entry linking it to what came before.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS authorities (
    id          INTEGER PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,      -- e.g. 'mcc'
    name        TEXT NOT NULL,             -- 'Medical Counselling Committee'
    website     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY,
    authority_id    INTEGER NOT NULL REFERENCES authorities(id),
    source_id       TEXT UNIQUE NOT NULL,   -- e.g. 'mcc_pg_current_events'
    url             TEXT NOT NULL,
    kind            TEXT NOT NULL,          -- 'html_listing'
    emits           TEXT NOT NULL,          -- 'documents'
    check_every_idle_minutes INTEGER DEFAULT 360,
    active          INTEGER DEFAULT 1,
    verified_on     TEXT
);

-- One row per scrape attempt of a source, whether or not it found anything new.
CREATE TABLE IF NOT EXISTS update_runs (
    id              INTEGER PRIMARY KEY,
    source_id       TEXT NOT NULL REFERENCES sources(source_id),
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    status          TEXT NOT NULL,          -- 'ok' | 'error' | 'no_change'
    entries_seen    INTEGER DEFAULT 0,
    new_documents   INTEGER DEFAULT 0,
    error_message   TEXT
);

-- One row per distinct document MCC has published (by content hash).
CREATE TABLE IF NOT EXISTS documents (
    id                  INTEGER PRIMARY KEY,
    source_id           TEXT NOT NULL REFERENCES sources(source_id),
    content_hash        TEXT UNIQUE NOT NULL,   -- sha256(title + '|' + url)
    title               TEXT NOT NULL,
    file_url            TEXT NOT NULL,
    doc_type            TEXT NOT NULL,          -- see classifier.DOC_TYPES
    doc_type_confidence REAL NOT NULL,
    cycle_label         TEXT,                   -- e.g. 'PG Counselling 2025'
    round_label         TEXT,                   -- e.g. 'Round 3' | 'Stray'
    pub_date            TEXT,                   -- ISO date, may be NULL
    pub_date_basis      TEXT,                   -- 'title' | 'filename' | 'first_seen' | ...
    pub_date_confidence TEXT,                   -- 'high' | 'medium' | 'low'
    retrieved_at        TEXT NOT NULL,          -- when WE first saw it
    listing_position    INTEGER,                -- row order on the listing page (newest first)
    raw_year_column     TEXT,                   -- the (unreliable) 'year' MCC prints in the listing
    superseded_by_id    INTEGER REFERENCES documents(id)
);

-- One event per newly-detected document (drives the "Latest Updates" feed).
CREATE TABLE IF NOT EXISTS data_changes (
    id              INTEGER PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES documents(id),
    change_type     TEXT NOT NULL,          -- 'new_document' | 'superseded'
    detected_at     TEXT NOT NULL,
    run_id          INTEGER REFERENCES update_runs(id),
    summary         TEXT NOT NULL           -- human-readable one-liner
);

CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_doctype ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_changes_detected_at ON data_changes(detected_at);
"""

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "neetpg.db"


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed_mcc(conn: sqlite3.Connection) -> None:
    """Insert the MCC authority and the three PG listing sources we monitor,
    if they aren't already there. URLs verified live on 2026-09-21."""
    conn.execute(
        """INSERT OR IGNORE INTO authorities (code, name, website)
           VALUES ('mcc', 'Medical Counselling Committee', 'https://mcc.nic.in')"""
    )
    sources = [
        (
            "mcc_pg_current_events",
            "https://mcc.nic.in/current-events-pg/",
            "html_listing",
            "documents",
            "2026-09-21",
        ),
        (
            "mcc_pg_news_events",
            "https://mcc.nic.in/news-events-pg/",
            "html_listing",
            "documents",
            "2026-09-21",
        ),
        (
            "mcc_pg_archive",
            "https://mcc.nic.in/archive-pg/",
            "html_listing",
            "documents",
            "2026-09-21",
        ),
    ]
    for source_id, url, kind, emits, verified_on in sources:
        conn.execute(
            """INSERT OR IGNORE INTO sources
               (authority_id, source_id, url, kind, emits, verified_on)
               VALUES ((SELECT id FROM authorities WHERE code='mcc'), ?, ?, ?, ?, ?)""",
            (source_id, url, kind, emits, verified_on),
        )
    conn.commit()


if __name__ == "__main__":
    conn = connect()
    init_db(conn)
    seed_mcc(conn)
    print(f"Initialized database at {DEFAULT_DB_PATH}")
