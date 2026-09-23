"""Parse an MCC PG listing page (Current Events / News & Events / Archive)
into raw (title, file_url) entries.

MCC's listing pages are WordPress table-plugin pages: essentially a table
where each row has a title cell and a download-link cell, newest first.
We don't hard-code exact CSS classes (those can change on a WordPress
theme update) -- instead we look for the one thing that's stable and
verifiable: every real document link points at MCC's document store,
cdnbbsr.s3waas.gov.in, and ends in a document extension. That link's
anchor text (or the nearby row text) is the title.

This is deliberately defensive: if MCC's markup changes completely, this
should return an empty list (which the monitor logs loudly) rather than
silently extracting garbage.
"""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup

DOCUMENT_HOST_HINTS = ("cdnbbsr.s3waas.gov.in", "s3waas.gov.in")
DOCUMENT_EXTENSIONS = (".pdf", ".xlsx", ".xls", ".doc", ".docx")


@dataclass
class ListingEntry:
    title: str
    file_url: str
    position: int          # 0 = newest / topmost on the page
    raw_year_column: str | None = None


def _looks_like_document_link(href: str) -> bool:
    if not href:
        return False
    href_lower = href.lower()
    has_host_hint = any(h in href_lower for h in DOCUMENT_HOST_HINTS)
    has_extension = any(href_lower.endswith(ext) for ext in DOCUMENT_EXTENSIONS)
    return has_host_hint or has_extension


def parse_listing_html(html: str) -> list[ListingEntry]:
    soup = BeautifulSoup(html, "html.parser")
    entries: list[ListingEntry] = []
    seen_urls: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        if not _looks_like_document_link(href):
            continue
        if href in seen_urls:
            continue

        # Prefer the link's own text; if it's just "Download" or empty,
        # fall back to the title-looking cell in the row it sits in
        # (skip cells that are the link itself, or that are bare numbers --
        # those are the S.No / Year columns, not the title).
        link_text = link.get_text(strip=True)
        row = link.find_parent("tr")

        title = link_text
        if not title or title.lower() in {"download", "click here", "view", "pdf"}:
            title = ""
            if row:
                link_cell = link.find_parent("td")
                for cell in row.find_all("td"):
                    if cell is link_cell:
                        continue
                    cell_text = cell.get_text(strip=True)
                    if not cell_text or cell_text.isdigit():
                        continue
                    title = cell_text
                    break
            if not title and row:
                title = row.get_text(" ", strip=True)
        if not title:
            title = href

        # Try to spot a bare 4-digit "year" column MCC sometimes prints
        # alongside the title (this is a display label, not necessarily
        # the academic year -- see dateinfer / classifier for the real date).
        raw_year_column = None
        if row:
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            for cell in cells:
                if cell.isdigit() and len(cell) == 4 and cell.startswith("20"):
                    raw_year_column = cell
                    break

        entries.append(
            ListingEntry(
                title=title,
                file_url=href,
                position=len(entries),
                raw_year_column=raw_year_column,
            )
        )
        seen_urls.add(href)

    return entries
