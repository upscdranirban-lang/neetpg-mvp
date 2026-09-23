# Fixtures

These HTML files are **hand-built snapshots**, not raw page saves (this
workspace's shell cannot reach mcc.nic.in directly -- only the WebFetch
tool can, and it returns summarized text, not raw HTML). Every title, PDF
link and date in these fixtures was copied verbatim from real MCC pages
fetched on **2026-09-21**, so the content is real, only the markup
wrapper around it is reconstructed to match MCC's typical WordPress
table-listing structure.

They exist so the engine (`engine/parser_listing.py` onward) can be
developed and tested end-to-end today, without needing production
network access. Once this runs on GitHub Actions (see the design doc's
hosting plan), `engine/fetch.py:fetch_url` reads the real, live page
instead of these files -- no code changes needed elsewhere, since the
monitor only cares about the HTML string it receives.

Files:
- `mcc_current_events_pg.html` -- mcc.nic.in/current-events-pg/, page 1
- `mcc_news_events_pg.html` -- mcc.nic.in/news-events-pg/, page 1
- `mcc_archive_pg.html` -- mcc.nic.in/archive-pg/, 2026 section
