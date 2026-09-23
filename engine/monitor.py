"""Orchestrates one monitoring pass over one MCC listing source:

    read HTML (live fetch or fixture)
      -> parse_listing_html            (engine/parser_listing.py)
      -> classify each entry           (engine/classifier.py)
      -> infer a publication date      (engine/dateinfer.py)
      -> hash it, compare to the DB
      -> insert new documents + a data_changes row for each
      -> record an update_runs row either way

This mirrors stages 1-4 and 7 of the 8-stage pipeline in the design doc
(source monitor, document detector, downloader [n/a for listings],
normalizer/classifier, change detector). Validation and human review
(stages 6-7 in the doc) apply to structured seat/result data, which this
MVP doesn't parse yet -- classification confidence is the only "quality"
signal at this stage, and it's stored plainly rather than hidden.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone

from engine import classifier, dateinfer
from engine.parser_listing import ListingEntry, parse_listing_html


def _hash_entry(title: str, file_url: str) -> str:
    return hashlib.sha256(f"{title}|{file_url}".encode("utf-8")).hexdigest()


def run_once(conn: sqlite3.Connection, source_id: str, html: str) -> dict:
    now = datetime.now(timezone.utc)
    started_at = now.isoformat()

    cur = conn.execute(
        "INSERT INTO update_runs (source_id, started_at, status) VALUES (?, ?, 'running')",
        (source_id, started_at),
    )
    run_id = cur.lastrowid

    try:
        entries: list[ListingEntry] = parse_listing_html(html)
        new_count = 0
        new_document_rows: list[dict] = []

        for entry in entries:
            content_hash = _hash_entry(entry.title, entry.file_url)
            existing = conn.execute(
                "SELECT id FROM documents WHERE content_hash = ?", (content_hash,)
            ).fetchone()
            if existing:
                continue  # already known, nothing to do

            cls = classifier.classify(entry.title)
            inferred = dateinfer.infer_date(entry.title, entry.file_url, now)

            doc_cur = conn.execute(
                """INSERT INTO documents
                   (source_id, content_hash, title, file_url, doc_type,
                    doc_type_confidence, cycle_label, round_label,
                    pub_date, pub_date_basis, pub_date_confidence,
                    retrieved_at, listing_position, raw_year_column)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source_id,
                    content_hash,
                    entry.title,
                    entry.file_url,
                    cls.doc_type,
                    cls.doc_type_confidence,
                    cls.cycle_label,
                    cls.round_label,
                    inferred.value.isoformat() if inferred.value else None,
                    inferred.basis,
                    inferred.confidence,
                    now.isoformat(),
                    entry.position,
                    entry.raw_year_column,
                ),
            )
            document_id = doc_cur.lastrowid

            summary = f"New {cls.doc_type.replace('_', ' ')}: {entry.title}"
            conn.execute(
                """INSERT INTO data_changes
                   (document_id, change_type, detected_at, run_id, summary)
                   VALUES (?, 'new_document', ?, ?, ?)""",
                (document_id, now.isoformat(), run_id, summary),
            )
            new_count += 1
            new_document_rows.append({
                "id": document_id,
                "content_hash": content_hash,
                "title": entry.title,
                "file_url": entry.file_url,
                "doc_type": cls.doc_type,
                "cycle_label": cls.cycle_label,
                "round_label": cls.round_label,
            })

        conn.execute(
            """UPDATE update_runs
               SET finished_at = ?, status = ?, entries_seen = ?, new_documents = ?
               WHERE id = ?""",
            (
                datetime.now(timezone.utc).isoformat(),
                "ok" if entries else "error",
                len(entries),
                new_count,
                run_id,
            ),
        )
        if not entries:
            conn.execute(
                "UPDATE update_runs SET error_message = ? WHERE id = ?",
                ("Parser found zero document links -- page structure may have changed", run_id),
            )
        conn.commit()

        return {
            "run_id": run_id,
            "entries_seen": len(entries),
            "new_documents": new_count,
            "new_document_rows": new_document_rows,
        }

    except Exception as exc:  # noqa: BLE001 -- we want to record any failure
        conn.execute(
            """UPDATE update_runs
               SET finished_at = ?, status = 'error', error_message = ?
               WHERE id = ?""",
            (datetime.now(timezone.utc).isoformat(), str(exc), run_id),
        )
        conn.commit()
        raise
