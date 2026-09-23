"""Hand-written, long-form blog content -- separate from the auto-detected
entries in Latest Updates (see engine/export_json.py). Each post here
becomes its own real, indexable static page (site/blog/<slug>.html, built
by engine/build_blog.py) with its own URL, <title> and meta description --
not just a card inside the single-page app, which search engines would
have a much harder time crediting as a distinct, rankable page.

Add new posts here (newest first). Every post must be genuinely useful on
its own, per the project's own SEO rule ("do not generate thin pages
solely for SEO") -- a post that only exists to catch a search query and
says nothing real once someone lands on it does not belong here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BlogPost:
    slug: str
    title: str                # <title> / <h1>
    meta_description: str     # <meta name="description">
    date: str                 # ISO date
    summary: str              # shown on list cards
    hero_svg: str             # inline SVG markup, no wrapping <div>
    body_html: str            # full article body (semantic HTML, no <script>)


# ---------------------------------------------------------------------------
# Hero illustrations. Inline SVG (no external image hosting needed), using
# the site's own CSS custom properties so each renders correctly in both
# light and dark mode without a separate dark-mode asset.
# ---------------------------------------------------------------------------

_FREE_VS_PAID_SVG = """
<svg viewBox="0 0 320 160" role="img" aria-label="A free, unlocked checkmark badge next to a paid, locked price badge">
  <rect x="0" y="0" width="320" height="160" fill="none"/>
  <g transform="translate(28,28)">
    <rect x="0" y="0" width="118" height="104" rx="16" fill="var(--brand-fill)"/>
    <circle cx="59" cy="40" r="22" fill="none" stroke="var(--accent)" stroke-width="3.5"/>
    <path d="M48 40l8 8 16-17" fill="none" stroke="var(--accent)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="59" y="86" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="15" font-weight="700" fill="var(--on-brand-fill)">FREE</text>
  </g>
  <g transform="translate(174,28)">
    <rect x="0" y="0" width="118" height="104" rx="16" fill="var(--surface-2)" stroke="var(--line)" stroke-width="1.5"/>
    <rect x="37" y="18" width="44" height="34" rx="6" fill="none" stroke="var(--ink-faint)" stroke-width="3.5"/>
    <path d="M45 18v-6a14 14 0 0128 0v6" fill="none" stroke="var(--ink-faint)" stroke-width="3.5"/>
    <circle cx="59" cy="35" r="4.5" fill="var(--ink-faint)"/>
    <text x="59" y="86" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="14" font-weight="600" fill="var(--ink-muted)">&#8377;6,000+</text>
  </g>
</svg>
"""

_ROUND_COMPARISON_SVG = """
<svg viewBox="0 0 320 200" role="img" aria-label="Bar chart comparing 1,499 institutes with a Round 3 seat against 743 institutes with a Stray Vacancy Round seat">
  <rect x="0" y="0" width="320" height="200" fill="none"/>
  <line x1="40" y1="164" x2="290" y2="164" stroke="var(--line)" stroke-width="1.5"/>
  <g>
    <rect x="80" y="34" width="56" height="130" rx="6" fill="var(--brand-fill)"/>
    <text x="108" y="24" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="15" font-weight="700" fill="var(--ink)">1,499</text>
    <text x="108" y="182" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11.5" font-weight="600" fill="var(--ink-muted)">Round 3</text>
  </g>
  <g>
    <rect x="196" y="99" width="56" height="65" rx="6" fill="var(--accent)"/>
    <text x="224" y="89" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="15" font-weight="700" fill="var(--ink)">743</text>
    <text x="224" y="182" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11.5" font-weight="600" fill="var(--ink-muted)">Stray Vacancy</text>
  </g>
  <text x="165" y="198" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--ink-faint)">Institutes with at least one seat allotted, PG Counselling 2025</text>
</svg>
"""


POSTS: list[BlogPost] = [
    BlogPost(
        slug="free-zynerd-alternative-neet-pg-counselling",
        title="A Free ZyNerd Alternative for NEET-PG Counselling Data",
        meta_description=(
            "Looking for a free alternative to ZyNerd for NEET-PG counselling data? "
            "See what NEET-PG Help tracks for free -- real MCC seat/allotment data, "
            "a rank predictor, and a live document tracker -- compared honestly."
        ),
        date="2026-09-23",
        summary=(
            "ZyNerd's NEET PG Pro package costs ₹6,000. Here's what you can get for "
            "free instead, and where a paid tool still makes sense."
        ),
        hero_svg=_FREE_VS_PAID_SVG,
        body_html="""
<p><strong>Quick disclosure up front:</strong> NEET-PG Help is an independent
project, not affiliated with, endorsed by, or in any way connected to ZyNerd.
We're mentioning them because a lot of NEET-PG aspirants search for
"ZyNerd alternative," and we think candidates deserve an honest, sourced
comparison rather than another marketing page. Where we cite a price below,
it's sourced from ZyNerd's own <a href="https://apps.apple.com/in/app/zynerd-neet-ug-pg-mds/id6504278658" target="_blank" rel="noopener">App Store listing</a>
(pricing on any app can change -- always check the current price on their site
before deciding).</p>

<h2>What ZyNerd offers, and what it costs</h2>
<p>ZyNerd is a real, well-used NEET counselling app covering NEET UG, PG and
MDS. It's free to download, but its core counselling tools sit behind paid
packages -- at the time we checked, listed as <strong>NEET PG Pro 2025 at
&#8377;6,000</strong>, with separate paid tiers for NEET UG (&#8377;4,000&ndash;&#8377;5,499)
and NEET MDS 2026 (&#8377;5,500). Its feature set includes allotment data,
cutoffs, fee/stipend/bond information, a round-comparison timeline tool, and
expert guidance -- genuinely useful things, just gated behind a purchase.</p>

<h2>What's actually free on NEET-PG Help</h2>
<p>We don't have ZyNerd's expert-guidance or video-explainer features. What we
do have, for free, with no account or payment required:</p>
<ul>
  <li><strong>A live tracker of MCC's own official documents</strong> --
  results, vacancy lists, seat-addition/deletion notices and more, classified
  automatically and linked straight back to the original PDF on mcc.nic.in.</li>
  <li><strong>A rank predictor built on real MCC allotment data</strong> --
  not estimates. We've directly computed opening/closing ranks from the
  actual Round 3 and Stray Vacancy Round result PDFs for PG Counselling 2025
  (and Round 3, 2024), by institute, specialty and category -- see our
  <a href="round-3-vs-stray-vacancy-round-2025.html">Round 3 vs. Stray Vacancy
  Round comparison</a> for what that data actually shows.</li>
  <li><strong>An automated update pipeline</strong> -- when MCC publishes a
  new result, it's downloaded, validated against a real rule set (no
  impossible ranks, no duplicate seats, nothing published if it fails a
  sanity check), and added automatically.</li>
  <li><strong>Full source transparency</strong> -- every number links back to
  the exact official document and page count it came from. Nothing is
  retyped or reinterpreted from a source we can't show you.</li>
</ul>

<h2>Where a paid tool might still be worth it</h2>
<p>To be fair to readers actually weighing this decision: if you want
one-on-one expert counselling, personalized choice-list building, or
guaranteed human support through a stressful few weeks, that's a real
service with real cost behind it, and a free document tracker like ours
isn't a substitute for that. What we're free for is the data itself --
seeing where ranks actually closed, tracking new documents the moment MCC
posts them, and getting a rank-based estimate without paying for it.</p>

<h2>Try it</h2>
<p>Open the <strong>Predictor</strong> tab on NEET-PG Help, pick a real MCC
round from the dropdown, and enter your rank and category -- no signup, no
payment, and every figure links back to its official source.</p>
""",
    ),
    BlogPost(
        slug="round-3-vs-stray-vacancy-round-2025",
        title="NEET-PG 2025: Round 3 vs. Stray Vacancy Round, By the Numbers",
        meta_description=(
            "A data-driven look at how NEET-PG Counselling 2025's Round 3 and Stray "
            "Vacancy Round actually compared -- institutes, seats and categories, "
            "computed directly from MCC's own official allotment results."
        ),
        date="2026-09-22",
        summary=(
            "We ran the numbers directly from MCC's own Round 3 and Stray Vacancy "
            "Round PDFs. Here's how different the two rounds really were."
        ),
        hero_svg=_ROUND_COMPARISON_SVG,
        body_html="""
<p>Every number in this post is computed directly from MCC's own official
PG Counselling 2025 allotment result PDFs -- Round 3 (1,555 pages) and the
Stray Vacancy Round (130 pages) -- using the same pipeline that powers the
<a href="../index.html">Predictor tab</a> on NEET-PG Help. Nothing here is a
third-party estimate.</p>

<h2>The headline numbers</h2>
<table>
  <thead><tr><th></th><th>Round 3</th><th>Stray Vacancy Round</th></tr></thead>
  <tbody>
    <tr><td>Institutes with at least one seat allotted</td><td>1,499</td><td>743</td></tr>
    <tr><td>Distinct specialties</td><td>97</td><td>85</td></tr>
    <tr><td>Total seats counted</td><td>18,673</td><td>2,798</td></tr>
  </tbody>
</table>

<h2>What that actually means</h2>
<p>The Stray Vacancy Round is, as the name says, a mop-up round -- it only
allots the seats still vacant after Round 3 (and any subsequent state-level
processes) conclude. So a much smaller round is expected. What's more
interesting is <em>which</em> institutes show up: of the 743 institutes with
a seat allotted in the Stray round, all but one also had a seat allotted in
Round 3 -- but 757 institutes that had a Round 3 seat had nothing left to
offer by the Stray round. That's a real signal of which colleges and
specialties fill up early versus which ones still have seats months into the
cycle.</p>

<h2>Category-wise split</h2>
<table>
  <thead><tr><th>Category</th><th>Round 3 seats</th><th>Stray seats</th></tr></thead>
  <tbody>
    <tr><td>Open</td><td>5,987</td><td>1,363</td></tr>
    <tr><td>OBC</td><td>2,209</td><td>446</td></tr>
    <tr><td>SC</td><td>1,422</td><td>383</td></tr>
    <tr><td>EWS</td><td>883</td><td>120</td></tr>
    <tr><td>ST</td><td>777</td><td>171</td></tr>
  </tbody>
</table>
<p>The proportions hold up fairly consistently between the two rounds --
Open seats are roughly 32% of the total in both -- which suggests the Stray
round isn't skewed toward any one category more than Round 3 was, at least
at this aggregate level.</p>

<h2>What this means if you're preparing for PG Counselling 2026</h2>
<p>Don't compare a Stray-round closing rank directly to a Round 3 closing
rank for the same seat and assume they tell you the same thing -- they come
from different, non-overlapping pools of candidates at different points in
the cycle, and our Predictor labels them separately for exactly this reason.
If you want to see where a specific institute or specialty landed in either
round, the <a href="../index.html">Predictor tab</a> lets you pick the round
explicitly and shows you real reported ranks, not a blended estimate.</p>
""",
    ),
]


def get_post(slug: str) -> BlogPost | None:
    for post in POSTS:
        if post.slug == slug:
            return post
    return None
