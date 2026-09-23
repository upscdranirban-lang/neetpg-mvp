"""NEET-PG counselling data engine.

Package layout:
  db.py         - SQLite schema + connection helper
  classifier.py - guesses document type / cycle / round from a title
  dateinfer.py  - infers a publication date + confidence for a document
  parser_listing.py - turns an MCC listing page (HTML) into raw entries
  monitor.py    - orchestrates: fetch/read listing -> parse -> classify ->
                   infer date -> hash -> diff against DB -> record changes
  fetch.py      - network fetch of a live MCC page (only works where the
                   outbound network allows it, e.g. GitHub Actions; not in
                   this sandbox, see fixtures/ for offline testing)
"""
