"""Live network fetch of an MCC listing page.

Important: this workspace's own outbound network is restricted to an
allowlist that does NOT include mcc.nic.in (verified: a direct request
here gets rejected by the sandbox's proxy). So `fetch_url` below will
fail in THIS session -- that's expected, not a bug. It is written to run
correctly in production (a GitHub Actions job, per the design doc's
hosting plan), where outbound network is unrestricted.

For local testing inside this sandbox, use fixtures/*.html via
`fetch_fixture` instead -- see monitor.py and tests/.
"""

from __future__ import annotations

from pathlib import Path

USER_AGENT = (
    "NEETPGHelp-Monitor/0.1 (+https://mcc.nic.in independent tracker; "
    "contact: staranirban363@gmail.com)"
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch a live page. Only works where outbound network reaches
    mcc.nic.in (not in this sandbox). Import is local so environments that
    never call this (tests, fixture-only runs) don't need `requests`."""
    import requests

    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def fetch_fixture(name: str) -> str:
    """Read a saved HTML snapshot from fixtures/, for offline dev/testing."""
    path = FIXTURES_DIR / name
    return path.read_text(encoding="utf-8")
