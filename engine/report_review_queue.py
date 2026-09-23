"""Turns anything sitting in data/review_queue/ into a GitHub Issue, so you
get notified (GitHub emails watchers on a new issue) without needing any
extra notification service. Skips a document that already has an open
issue with the same title, so reruns of the scheduled job don't spam
duplicates. Run by .github/workflows/monitor.yml after every scheduled
pipeline run; safe to run by hand too (e.g. `python3 -m engine.report_review_queue`).

Requires the `gh` CLI to be authenticated (GitHub Actions runners have it
pre-installed and pass GH_TOKEN automatically; see the workflow file).
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_QUEUE_DIR = ROOT / "data" / "review_queue"


def _issue_title(entry: dict) -> str:
    title = entry["document"].get("title", "Untitled document")
    return f"Needs review: {title} ({entry['reason']})"


def _issue_body(entry: dict) -> str:
    lines = [
        "This document was downloaded and processed by the automated monitor, "
        "but did not pass validation and was NOT published to the live site.",
        "",
        f"**Document:** {entry['document'].get('title')}",
        f"**Source link:** {entry['document'].get('file_url')}",
        f"**Reason:** {entry['reason']}",
        "",
    ]
    details = entry.get("details", {})
    if details.get("issues"):
        lines.append("**Issues found:**")
        lines += [f"- {issue}" for issue in details["issues"]]
        lines.append("")
    if details.get("note"):
        lines.append(details["note"])
        lines.append("")
    lines.append(f"Queued at: {entry.get('queued_at')}")
    return "\n".join(lines)


def _run_gh(args: list[str]) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None


def _existing_open_issue_titles() -> set[str]:
    result = _run_gh(["issue", "list", "--state", "open", "--limit", "200", "--json", "title"])
    if result is None:
        print("(gh CLI not found -- not in a GitHub Actions runner; skipping issue reporting)")
        return set()
    if result.returncode != 0:
        print(f"(couldn't list existing issues, will not dedupe: {result.stderr.strip()})")
        return set()
    return {row["title"] for row in json.loads(result.stdout)}


def main() -> None:
    if not REVIEW_QUEUE_DIR.exists():
        print("No review queue directory -- nothing to report.")
        return

    files = sorted(REVIEW_QUEUE_DIR.glob("*.json"))
    if not files:
        print("Review queue is empty -- nothing to report.")
        return

    existing_titles = _existing_open_issue_titles()

    for path in files:
        entry = json.loads(path.read_text())
        title = _issue_title(entry)
        if title in existing_titles:
            print(f"Issue already open for: {title}")
            continue
        body = _issue_body(entry)
        # Pass the body via a temp file (--body-file), not as a raw CLI
        # argument (--body). With hundreds of queued documents in one run,
        # a long body can push the process's argv past the OS's argument
        # length limit ("Argument list too long"), which crashed this
        # script and, in turn, aborted the whole workflow before it
        # reached the GitHub Pages deploy step further down.
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False, encoding="utf-8"
            ) as f:
                f.write(body)
                body_path = f.name
            result = _run_gh(["issue", "create", "--title", title, "--body-file", body_path])
        finally:
            Path(body_path).unlink(missing_ok=True)
        if result is None:
            print(f"(gh CLI not found -- cannot open issue for: {title})")
        elif result.returncode == 0:
            print(f"Opened issue: {title}\n  {result.stdout.strip()}")
        else:
            print(f"Failed to open issue for {title}: {result.stderr.strip()}")


if __name__ == "__main__":
    main()
