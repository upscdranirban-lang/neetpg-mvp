"""Export the database into the JSON shape the site consumes.

This keeps the site a plain static file with no backend: the site reads
one data.json that this script regenerates after every monitor run. In
production (GitHub Actions), this runs right after monitor.run_once for
every source, then the updated data.json is what gets published to
Cloudflare Pages -- no code changes needed to go from "fixture demo" to
"live site," only the source of the HTML monitor.run_once is fed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from engine import db

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "site" / "data.json"


def export(conn) -> dict:
    documents = [
        dict(row)
        for row in conn.execute(
            """SELECT d.*, s.url as source_url, a.name as authority_name
               FROM documents d
               JOIN sources s ON s.source_id = d.source_id
               JOIN authorities a ON a.id = s.authority_id
               ORDER BY COALESCE(d.pub_date, d.retrieved_at) DESC, d.id DESC"""
        )
    ]

    changes = [
        dict(row)
        for row in conn.execute(
            """SELECT c.*, d.title, d.doc_type, d.file_url, d.round_label, d.cycle_label
               FROM data_changes c
               JOIN documents d ON d.id = c.document_id
               ORDER BY c.detected_at DESC, c.id DESC"""
        )
    ]

    runs = [
        dict(row)
        for row in conn.execute(
            """SELECT source_id, MAX(finished_at) as last_finished_at, status
               FROM update_runs
               WHERE finished_at IS NOT NULL
               GROUP BY source_id"""
        )
    ]

    # The most recent pub_date we have high/medium confidence in, across all
    # documents -- this is what the dashboard calls "Last official update."
    # It is intentionally NOT the same as "Last checked" (below), which is
    # about US, not MCC.
    dated_docs = [d for d in documents if d.get("pub_date") and d.get("pub_date_confidence") != "low"]
    last_official_update = max((d["pub_date"] for d in dated_docs), default=None)

    last_checked = max((r["last_finished_at"] for r in runs if r["last_finished_at"]), default=None)

    cycles = sorted({d["cycle_label"] for d in documents if d.get("cycle_label")}, reverse=True)
    current_cycle = cycles[0] if cycles else None
    rounds_seen = []
    for d in documents:
        if d.get("cycle_label") == current_cycle and d.get("round_label"):
            if d["round_label"] not in rounds_seen:
                rounds_seen.append(d["round_label"])

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dashboard": {
            "current_cycle": current_cycle,
            "rounds_seen": rounds_seen,
            "last_checked": last_checked,
            "last_official_update": last_official_update,
            "sources_monitored": len(runs),
            "total_documents": len(documents),
        },
        "documents": documents,
        "changes": changes,
        "sources": runs,
    }
    return payload


def main() -> None:
    conn = db.connect()
    payload = export(conn)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(payload['documents'])} documents, {len(payload['changes'])} changes)")


if __name__ == "__main__":
    main()
