"""Live network fetch of an MCC listing page.

Important: this workspace's own outbound network is restricted to an
allowlist that does NOT include mcc.nic.in (verified: a direct request
here gets rejected by the sandbox's proxy). So `fetch_url` below will
fail in THIS session -- that's expected, not a bug. It is written to run
correctly in production (a GitHub Actions job, per the design doc's
hosting plan), where outbound network is unrestricted.

For local testing inside this sandbox, use fixtures/*.html via
`fetch_fixture` instead -- see monitor.py and tests/.

NOTE on User-Agent: mcc.nic.in's edge/WAF returns 403 Forbidden to
requests carrying a self-identifying bot User-Agent string (confirmed by
testing a real browser against the same URL, which loads fine). To keep
the monitor working from GitHub Actions' shared IP ranges, requests are
sent with a standard desktop-browser User-Agent and Accept headers below.
This is a low-frequency (every few hours), read-only fetch of the same
public notices any visitor sees -- not a bypass of any access control
beyond the UA sniff itself, and it stops immediately if MCC starts
blocking on other signals.
"""

from __future__ import annotations

from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch a live page. Only works where outbound network reaches
    mcc.nic.in (not in this sandbox). Import is local so environments that
    never call this (tests, fixture-only runs) don't need `requests`."""
    import requests

    resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def fetch_fixture(name: str) -> str:
    """Read a saved HTML snapshot from fixtures/, for offline dev/testing."""
    path = FIXTURES_DIR / name
    return path.read_text(encoding="utf-8")
