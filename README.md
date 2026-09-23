# NEET-PG Help — MVP + automated pipeline (Phase 4)

A working demonstration of the data-engine design, built against **real**
MCC PG counselling content. It monitors MCC's PG listing pages, classifies
each document, infers a publication date, keeps a full audit trail of
every change, and shows the result on a mobile-first website. As of
Phase 4, this also includes an automated pipeline: a scheduled job
downloads new result documents, extracts their seat/rank tables, runs
them through validation, and either publishes them automatically or opens
a GitHub Issue for human review -- see **SETUP.md** for how to turn this
on for real (a one-time, no-coding setup).

## What's here

```
engine/     the data engine (Python)
  db.py                       SQLite schema + seed data (MCC + its 3 listing sources)
  parser_listing.py           turns a listing page's HTML into (title, file_url) entries
  classifier.py               guesses document type / round / cycle from the title
  dateinfer.py                infers a publication date, with a confidence level
  monitor.py                  ties it together: parse -> classify -> date -> hash -> diff -> record
  fetch.py                    live network fetch (fetch_url) + fixture reader (fetch_fixture)
  export_json.py              exports the database to site/data.json
  export_predictor_json.py    exports the third-party estimate data to site/predictor_data.json
  run_local.py                runs the whole engine against the fixtures, end to end (dev/testing)
  run_scheduled.py            PRODUCTION entry point: live-fetches MCC, runs everything below,
                               rebuilds the site -- this is what GitHub Actions runs on a schedule
  detect_layout.py            auto-detects which known PDF table layout a new result uses
  extract_r1r2r3_pdf.py       table extractor: the 16-column Round-1/2/3-side-by-side layout
  extract_stray_pdf.py        table extractor: the 8-column single-round (e.g. Stray) layout
  mcc_cleaning.py             shared institute/specialty/category text-cleaning, used by both builders
  build_r1r2r3_closing_ranks.py / build_stray_closing_ranks.py
                               aggregate extracted rows into opening/closing ranks per college+specialty+category
  validate.py                 the validation rules a dataset must pass before it can go live
  extract_pipeline.py         ties detect -> extract -> build -> validate -> publish/queue together
  dataset_registry.py         reads/writes site/datasets/*.json + site/datasets_manifest.json
  report_review_queue.py      turns anything in data/review_queue/ into a GitHub Issue
  build_site.py                regenerates site/index.html from data.json + predictor_data.json +
                               every dataset in the manifest -- adding a new round never touches this file

fixtures/   real MCC listing content, hand-wrapped in HTML (see fixtures/README.md
            for why -- Claude's own sandbox can't reach mcc.nic.in directly; GitHub
            Actions, where this actually runs on a schedule, has normal internet access)
tests/      16 tests covering the classifier, date inference, parser and monitor
site/       the mobile-first website (index.html, self-contained; data.json; datasets/)
data/       the local SQLite database, raw extraction CSVs, and the human-review queue
.github/workflows/monitor.yml   the scheduled job definition (see SETUP.md to turn it on)
SETUP.md    one-time, click-by-click setup: GitHub + GitHub Actions + GitHub Pages + your domain
```

## What works today

- **Source monitor + change detection**: run the engine twice with the
  same page and nothing new is recorded; add a new document and exactly
  that one shows up as a "new_document" change, with a full audit trail
  (`update_runs`, `data_changes` tables).
- **Document classifier**: 15 document types (final result, vacancy, seat
  addition/deletion, choice-filling notice, NRI notice, etc.), tolerant of
  MCC's typos ("VACANY"), tested against every real title we captured from
  Current Events, News & Events and the Archive.
- **Date inference**: trust order is title date > filename timestamp >
  "first seen by us" — each with an honest confidence label, never
  presented as more certain than it is.
- **The website**: Dashboard (current cycle, rounds seen, "last checked"
  vs "last official update" shown as two separate numbers, never
  conflated), Latest Updates (searchable feed), Archive (searchable +
  filterable by document type), and an About page with the required
  independence disclaimer. Every single item links back to the real MCC
  PDF it came from.
- **26 real documents** are loaded right now, from MCC's actual Current
  Events, News & Events, and Archive listings for PG Counselling 2025.
- **Real seat/allotment data**: three real MCC rounds are extracted and
  live in the Predictor (2025 Round 3, 2025 Stray Vacancy Round, 2024
  Round 3), each computed directly from the official PDF with full
  provenance, never mixed with the third-party estimate dataset.
- **The automated pipeline (Phase 4)**: `engine/run_scheduled.py` +
  `.github/workflows/monitor.yml` -- on a schedule, downloads any newly
  detected result PDF, auto-detects its table layout, extracts it,
  validates it against a real rule set (impossible ranks, duplicate
  allotments, unknown categories/rounds, unexplained large jumps vs. the
  previous version, malformed extraction), and either publishes it
  automatically or opens a GitHub Issue for you to review -- tested
  end-to-end against both known real layouts.
- **Dataset registry**: adding a new round (by hand or automatically)
  never requires editing site-generation code -- it's picked up from
  `site/datasets_manifest.json` automatically.

## What does not work yet

- **Not deployed anywhere permanent yet.** Everything above has been
  tested inside this sandbox against real MCC PDFs and the real fixture
  pages, but this sandbox's own network can't reach mcc.nic.in (verified
  directly), so the *live* fetch (`engine.fetch.fetch_url`) has only run
  against fixtures here. It's written to work unchanged on GitHub
  Actions, which has normal internet access -- **SETUP.md** walks through
  turning that on, and its first live run is the real test.
- **Only MCC is monitored so far** (by design -- the project's own rule
  is not to attempt every state at once). Adding a state authority is a
  contained, repeatable change once one is prioritized.
- **Only two PDF table layouts are known** (the two real documents
  uploaded so far). A genuinely new layout MCC hasn't used before will be
  correctly routed to human review rather than mis-parsed, but does need
  a small new extractor written (same shape as `extract_stray_pdf.py`,
  the simpler of the two) before it can auto-publish.
- **MCC permission**: before this goes fully public, MCC's own copyright
  policy asks for prior permission to reproduce their content and to
  link to their site. Worth a quick email to MCC or a lawyer's sign-off
  before a public launch, even though private/personal use like this is
  fine meanwhile.

## What you need to do

1. **Follow SETUP.md** when you're ready to go live -- one-time,
   click-by-click, no coding, about 20-30 minutes.
2. **Check the Issues tab occasionally** once it's live -- that's where
   anything needing your judgment shows up (GitHub also emails you).
3. **Try the live link** on your phone in the meantime — tap through
   Dashboard, Updates, Archive, Predictor, About. Tell Claude anything
   that looks wrong or confusing.

## What we should build next

Phase 5 from the roadmap: round comparison and historical analytics
(Round 1 vs Round 2 vs Round 3 vs Stray, once more rounds accumulate),
and Phase 6: adding the first state counselling authority alongside MCC.

## Running it yourself (optional — I can also just keep doing this for you)

```
pip install -r requirements.txt
python3 -m engine.run_local        # runs the monitor against the fixtures (offline, dev/testing)
python3 -m engine.export_json      # regenerates site/data.json
python3 -m engine.export_predictor_json   # regenerates site/predictor_data.json
python3 -m engine.build_site       # regenerates site/index.html from everything above
python3 tests/run_all.py           # runs the 16 tests

# The production entry point (needs real internet access to mcc.nic.in,
# so it won't work from inside a Claude sandbox -- this is what GitHub
# Actions runs):
python3 -m engine.run_scheduled
```
