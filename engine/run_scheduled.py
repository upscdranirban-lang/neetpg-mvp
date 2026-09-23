"""Production entry point: this is what the scheduled GitHub Actions job
runs. Live-fetches MCC's real listing pages (this only works where
outbound network reaches mcc.nic.in -- NOT inside a Claude sandbox, see
engine/fetch.py), runs the monitor against each one, downloads and
extracts any newly-found result-type document, and regenerates the site.

Usage: python3 -m engine.run_scheduled
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

from engine import build_site, db, export_json, export_predictor_json, extract_pipeline, fetch, monitor

ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = ROOT / "data" / "downloads"

SOURCE_URLS = {
    "mcc_pg_current_events": "https://mcc.nic.in/current-events-pg/",
    "mcc_pg_news_events": "https://mcc.nic.in/news-events-pg/",
    "mcc_pg_archive": "https://mcc.nic.in/archive-pg/",
}

# Only these doc types carry seat/allotment tables worth running through
# the extraction pipeline -- everything else (notices, schedules, vacancy
# lists that are prose not tables, etc.) is just cataloged as a document,
# which is already low-risk (title + link, no numbers we computed).
RESULT_DOC_TYPES = {"final_result", "provisional_result", "revised_result", "result"}


def download_pdf(url: str, dest: Path) -> bool:
    """Best-effort download. Returns False (and leaves the document for
    manual/next-run retry) rather than raising, so one bad link doesn't
    abort the whole scheduled run."""
    try:
        resp = requests.get(url, headers={"User-Agent": fetch.USER_AGENT}, timeout=120, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        return True
    except Exception as exc:  # noqa: BLE001 -- log and move on, don't crash the whole run
        print(f"  ! failed to download {url}: {exc}")
        return False


def main() -> int:
    conn = db.connect()
    db.init_db(conn)
    db.seed_mcc(conn)

    published: list[str] = []
    queued_for_review: list[str] = []

    for source_id, url in SOURCE_URLS.items():
        try:
            html = fetch.fetch_url(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[{source_id}] FETCH FAILED: {exc}")
            continue

        result = monitor.run_once(conn, source_id, html)
        print(f"[{source_id}] entries_seen={result['entries_seen']} new_documents={result['new_documents']}")

        for doc in result["new_document_rows"]:
            if doc["doc_type"] not in RESULT_DOC_TYPES:
                continue
            print(f"  -> new {doc['doc_type']}: {doc['title']}")
            pdf_path = DOWNLOAD_DIR / f"{doc['content_hash']}.pdf"
            if not download_pdf(doc["file_url"], pdf_path):
                queued_for_review.append(f"{doc['title']} (download failed)")
                continue

            outcome = extract_pipeline.process_document(pdf_path, doc)
            if outcome["status"] == "published":
                print(f"     published as dataset '{outcome['dataset_id']}'")
                published.append(outcome["dataset_id"])
            else:
                print(f"     queued for review: {outcome['reason']} -> {outcome['path']}")
                queued_for_review.append(doc["title"])

    conn.close()

    export_json.main()
    export_predictor_json.main()
    build_site.main()

    print(f"\nDone. {len(published)} dataset(s) published, {len(queued_for_review)} item(s) need review.")
    if queued_for_review:
        print("Needs review:")
        for item in queued_for_review:
            print(f"  - {item}")

    # Always exit 0 for an orderly run, even when something is queued for
    # review -- that's an expected, handled outcome (the workflow checks
    # data/review_queue/ itself and opens a GitHub Issue if anything's
    # there), not a failure. A non-zero exit here should mean the run
    # itself crashed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
