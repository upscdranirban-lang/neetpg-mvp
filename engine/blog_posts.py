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


_PREDICTOR_FUNNEL_SVG = """
<svg viewBox="0 0 320 170" role="img" aria-label="Rank and category going into real MCC allotment data, producing a shortlist of colleges and branches">
  <rect x="0" y="0" width="320" height="170" fill="none"/>
  <g transform="translate(14,20)">
    <rect x="0" y="0" width="86" height="46" rx="10" fill="var(--surface-2)" stroke="var(--line)" stroke-width="1.5"/>
    <text x="43" y="21" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="12" font-weight="700" fill="var(--ink)">Rank</text>
    <text x="43" y="36" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--ink-muted)">+ Category</text>
  </g>
  <path d="M104 43 L138 43" stroke="var(--ink-faint)" stroke-width="2" marker-end="url(#arrow1)"/>
  <g transform="translate(140,14)">
    <rect x="0" y="0" width="100" height="60" rx="10" fill="var(--brand-fill)"/>
    <text x="50" y="24" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11" font-weight="700" fill="var(--on-brand-fill)">Real MCC</text>
    <text x="50" y="39" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11" font-weight="700" fill="var(--on-brand-fill)">allotment</text>
    <text x="50" y="53" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--on-brand-fill)">data</text>
  </g>
  <path d="M242 43 L276 43" stroke="var(--ink-faint)" stroke-width="2" marker-end="url(#arrow2)"/>
  <g transform="translate(222,86)">
    <rect x="0" y="0" width="98" height="60" rx="10" fill="var(--surface-2)" stroke="var(--accent)" stroke-width="2"/>
    <text x="49" y="24" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11" font-weight="700" fill="var(--ink)">Colleges &amp;</text>
    <text x="49" y="39" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="11" font-weight="700" fill="var(--ink)">branches you</text>
    <text x="49" y="53" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--ink-muted)">could reach</text>
  </g>
  <path d="M271 46 L271 86" stroke="var(--ink-faint)" stroke-width="2" marker-end="url(#arrow3)"/>
  <defs>
    <marker id="arrow1" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="var(--ink-faint)"/></marker>
    <marker id="arrow2" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="var(--ink-faint)"/></marker>
    <marker id="arrow3" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="var(--ink-faint)"/></marker>
  </defs>
  <text x="160" y="164" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--ink-faint)">No estimate model in between -- just real opening/closing ranks</text>
</svg>
"""

_BRANCH_TREE_SVG = """
<svg viewBox="0 0 320 170" role="img" aria-label="One rank branching out into several specialty options with different closing ranks">
  <rect x="0" y="0" width="320" height="170" fill="none"/>
  <circle cx="46" cy="85" r="26" fill="var(--brand-fill)"/>
  <text x="46" y="81" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="12" font-weight="700" fill="var(--on-brand-fill)">Your</text>
  <text x="46" y="94" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="12" font-weight="700" fill="var(--on-brand-fill)">rank</text>
  <g stroke="var(--ink-faint)" stroke-width="1.5" fill="none">
    <path d="M70 72 L150 30"/>
    <path d="M70 82 L150 82"/>
    <path d="M70 92 L150 134"/>
  </g>
  <g font-family="Public Sans, sans-serif" font-size="11" font-weight="600" fill="var(--ink)">
    <g transform="translate(150,14)">
      <rect x="0" y="0" width="150" height="32" rx="8" fill="var(--surface-2)" stroke="var(--line)"/>
      <text x="12" y="21">General Medicine</text>
    </g>
    <g transform="translate(150,66)">
      <rect x="0" y="0" width="150" height="32" rx="8" fill="var(--surface-2)" stroke="var(--accent)" stroke-width="1.5"/>
      <text x="12" y="21">Radiodiagnosis</text>
    </g>
    <g transform="translate(150,118)">
      <rect x="0" y="0" width="150" height="32" rx="8" fill="var(--surface-2)" stroke="var(--line)"/>
      <text x="12" y="21">Dermatology</text>
    </g>
  </g>
</svg>
"""

_AIQ_STATE_SVG = """
<svg viewBox="0 0 320 170" role="img" aria-label="All India Quota conducted by MCC compared side by side with State Quota conducted by a state authority">
  <rect x="0" y="0" width="320" height="170" fill="none"/>
  <g transform="translate(24,20)">
    <rect x="0" y="0" width="120" height="130" rx="12" fill="var(--brand-fill)"/>
    <text x="60" y="30" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="12" font-weight="700" fill="var(--on-brand-fill)">AIQ &mdash; 50%</text>
    <text x="60" y="50" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--on-brand-fill)">of govt. seats</text>
    <text x="60" y="88" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" font-weight="700" fill="var(--on-brand-fill)">Run by</text>
    <text x="60" y="103" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" font-weight="700" fill="var(--on-brand-fill)">MCC</text>
  </g>
  <text x="160" y="90" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="13" font-weight="700" fill="var(--ink-faint)">vs</text>
  <g transform="translate(176,20)">
    <rect x="0" y="0" width="120" height="130" rx="12" fill="var(--surface-2)" stroke="var(--accent)" stroke-width="2"/>
    <text x="60" y="30" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="12" font-weight="700" fill="var(--ink)">State Quota</text>
    <text x="60" y="50" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10" fill="var(--ink-muted)">remaining seats</text>
    <text x="60" y="88" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" font-weight="700" fill="var(--ink)">Run by each</text>
    <text x="60" y="103" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" font-weight="700" fill="var(--ink)">state authority</text>
  </g>
</svg>
"""

_PWD_INFLATION_SVG = """
<svg viewBox="0 0 320 200" role="img" aria-label="Bar chart showing a closing rank of 229,954 when a PwD allotment is wrongly folded into a category, versus the correct 6,050 when it is excluded">
  <rect x="0" y="0" width="320" height="200" fill="none"/>
  <line x1="40" y1="164" x2="290" y2="164" stroke="var(--line)" stroke-width="1.5"/>
  <g>
    <rect x="70" y="30" width="70" height="134" rx="6" fill="var(--ink-faint)" opacity="0.55"/>
    <text x="105" y="20" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)">229,954</text>
    <text x="105" y="182" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="600" fill="var(--ink-muted)">PwD folded in</text>
    <text x="105" y="195" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="9" fill="var(--ink-faint)">(wrong)</text>
  </g>
  <g>
    <rect x="190" y="160" width="70" height="4" rx="2" fill="var(--brand-fill)"/>
    <text x="225" y="150" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="13" font-weight="700" fill="var(--ink)">6,050</text>
    <text x="225" y="182" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="600" fill="var(--ink-muted)">PwD excluded</text>
    <text x="225" y="195" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="9" fill="var(--accent)">(correct)</text>
  </g>
</svg>
"""

_SERVICE_BOND_SVG = """
<svg viewBox="0 0 320 200" role="img" aria-label="Two seat cards: a government medical college with a normal closing rank of 18,200, and a Command Hospital seat with a lock icon and a closing rank of 205,105">
  <rect x="0" y="0" width="320" height="200" fill="none"/>
  <g transform="translate(18,26)">
    <rect x="0" y="0" width="130" height="140" rx="14" fill="var(--surface-2)" stroke="var(--line)" stroke-width="1.5"/>
    <circle cx="65" cy="42" r="20" fill="none" stroke="var(--brand-fill)" stroke-width="3.5"/>
    <path d="M55 42l7 7 14-15" fill="none" stroke="var(--brand-fill)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="65" y="88" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="700" fill="var(--ink)">Govt. medical</text>
    <text x="65" y="101" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="700" fill="var(--ink)">college</text>
    <text x="65" y="124" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="13" font-weight="700" fill="var(--brand-fill)">18,200</text>
  </g>
  <g transform="translate(172,26)">
    <rect x="0" y="0" width="130" height="140" rx="14" fill="var(--surface-2)" stroke="var(--accent)" stroke-width="2"/>
    <rect x="45" y="26" width="40" height="30" rx="5" fill="none" stroke="var(--accent)" stroke-width="3.5"/>
    <path d="M52 26v-6a13 13 0 0126 0v6" fill="none" stroke="var(--accent)" stroke-width="3.5"/>
    <circle cx="65" cy="41" r="4" fill="var(--accent)"/>
    <text x="65" y="88" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="700" fill="var(--ink)">Command</text>
    <text x="65" y="101" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="10.5" font-weight="700" fill="var(--ink)">Hospital</text>
    <text x="65" y="124" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="13" font-weight="700" fill="var(--accent)">2,05,105</text>
  </g>
  <text x="160" y="192" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="9" fill="var(--ink-faint)">Same category (Open), same round -- one carries a mandatory service bond</text>
</svg>
"""

_SEAT_MATRIX_GRID_SVG = """
<svg viewBox="0 0 320 170" role="img" aria-label="A seat matrix grid with columns for Round 1, Round 2, Round 3 and Stray Vacancy Round, and rows for colleges">
  <rect x="0" y="0" width="320" height="170" fill="none"/>
  <g font-family="Public Sans, sans-serif" font-size="10.5" font-weight="700" fill="var(--ink-muted)">
    <text x="100" y="24" text-anchor="middle">R1</text>
    <text x="160" y="24" text-anchor="middle">R2</text>
    <text x="220" y="24" text-anchor="middle">R3</text>
    <text x="280" y="24" text-anchor="middle">Stray</text>
  </g>
  <g>
    <rect x="20" y="34" width="280" height="26" rx="4" fill="var(--surface-2)"/>
    <rect x="20" y="64" width="280" height="26" rx="4" fill="none"/>
    <rect x="20" y="94" width="280" height="26" rx="4" fill="var(--surface-2)"/>
    <rect x="20" y="124" width="280" height="26" rx="4" fill="none"/>
  </g>
  <g fill="var(--brand-fill)">
    <circle cx="100" cy="47" r="6"/><circle cx="160" cy="47" r="6"/><circle cx="220" cy="47" r="6"/>
    <circle cx="160" cy="77" r="6"/><circle cx="220" cy="77" r="6"/><circle cx="280" cy="77" r="6"/>
    <circle cx="100" cy="107" r="6"/><circle cx="220" cy="107" r="6"/>
    <circle cx="280" cy="137" r="6"/>
  </g>
  <text x="30" y="51" font-family="IBM Plex Mono, monospace" font-size="9" fill="var(--ink-faint)">College A</text>
  <text x="30" y="81" font-family="IBM Plex Mono, monospace" font-size="9" fill="var(--ink-faint)">College B</text>
  <text x="30" y="111" font-family="IBM Plex Mono, monospace" font-size="9" fill="var(--ink-faint)">College C</text>
  <text x="30" y="141" font-family="IBM Plex Mono, monospace" font-size="9" fill="var(--ink-faint)">College D</text>
</svg>
"""

_CATEGORY_CUTOFF_SVG = """
<svg viewBox="0 0 320 200" role="img" aria-label="Bar chart of General Medicine closing ranks in 2025 Round 3 across Open, OBC, EWS, SC and ST categories, showing Open far higher than the reserved categories">
  <rect x="0" y="0" width="320" height="200" fill="none"/>
  <line x1="30" y1="164" x2="300" y2="164" stroke="var(--line)" stroke-width="1.5"/>
  <g font-family="IBM Plex Mono, monospace" font-size="10" font-weight="700" fill="var(--ink)">
    <rect x="42" y="28" width="34" height="136" rx="4" fill="var(--brand-fill)"/>
    <text x="59" y="20" text-anchor="middle">228,379</text>
    <rect x="98" y="150" width="34" height="14" rx="4" fill="var(--accent)"/>
    <text x="115" y="144" text-anchor="middle">10,075</text>
    <rect x="154" y="148" width="34" height="16" rx="4" fill="var(--accent)"/>
    <text x="171" y="142" text-anchor="middle">12,928</text>
    <rect x="210" y="141" width="34" height="23" rx="4" fill="var(--accent)"/>
    <text x="227" y="135" text-anchor="middle">27,067</text>
    <rect x="266" y="127" width="34" height="37" rx="4" fill="var(--accent)"/>
    <text x="283" y="121" text-anchor="middle">45,956</text>
  </g>
  <g font-family="Public Sans, sans-serif" font-size="10.5" font-weight="600" fill="var(--ink-muted)">
    <text x="59" y="180" text-anchor="middle">Open</text>
    <text x="115" y="180" text-anchor="middle">OBC</text>
    <text x="171" y="180" text-anchor="middle">EWS</text>
    <text x="227" y="180" text-anchor="middle">SC</text>
    <text x="283" y="180" text-anchor="middle">ST</text>
  </g>
  <text x="165" y="196" text-anchor="middle" font-family="Public Sans, sans-serif" font-size="9" fill="var(--ink-faint)">General Medicine (MD/MS) closing rank, all-India, 2025 Round 3</text>
</svg>
"""


POSTS: list[BlogPost] = [
    BlogPost(
        slug="neet-pg-armed-forces-bond-seats-closing-rank",
        title="Why Some NEET-PG \"Government Seat\" Closing Ranks Look Impossible -- Armed Forces Bond Seats, Explained",
        meta_description=(
            "Some NEET-PG Open-category government seats show a closing rank past "
            "2,00,000 -- and it's not a data error. It's a Command Hospital, AFMC "
            "or Naval Medicine seat with a mandatory service bond. Real MCC numbers "
            "inside, and how we now handle them."
        ),
        date="2026-09-24",
        summary=(
            "A General Surgery Open seat with a closing rank of 2,10,638 isn't a "
            "typo -- it's a military service-bond seat almost no civilian candidate "
            "competes for. Here's the real data, and why we removed these from our "
            "\"Government seats only\" view."
        ),
        hero_svg=_SERVICE_BOND_SVG,
        body_html="""
<p>If you've ever filtered a NEET-PG seat matrix or closing-rank list down to
"Government seats only" and spotted an Open-category closing rank in the
lakhs -- for a normal specialty like General Surgery, Ophthalmology or
Anaesthesiology, at what looks like a real government institute -- you
probably assumed it was a data error, or that the specialty was somehow
brutally undersubscribed everywhere. It's neither. In almost every case
we've checked, that one outlier row belongs to a <strong>Command Hospital,
Armed Forces Medical College (AFMC), Institute of Naval Medicine, Air Force
or Base Hospital seat</strong> -- and it carries a mandatory Armed Forces
service bond that most civilian NEET-PG candidates are not eligible for, or
simply won't take on.</p>

<h2>What these institutes actually are</h2>
<p>The Armed Forces Medical Services (AFMS) run their own PG training seats
inside MCC's central counselling -- these aren't a separate exam, they show
up in the ordinary MCC allotment list, under ordinary category labels like
"Open," "OBC" or "SC," exactly like any civilian government college seat.
The institutes involved include:</p>
<ul>
  <li>Armed Forces Medical College (AFMC), Pune</li>
  <li>Command Hospitals (Eastern, Western, Central, Southern, Air Force, etc.)</li>
  <li>Institute of Naval Medicine</li>
  <li>Army, Air Force and Base Hospitals (e.g. 7 Air Force Hospital, Army
  Hospital Research &amp; Referral)</li>
</ul>
<p>A seat at any of these comes with a fixed period of compulsory Armed
Forces service after the PG course -- not a small print detail, but a real
commitment most candidates either don't qualify for or don't want. That
single fact is enough to push very few candidates to apply, which is exactly
what produces the strange-looking numbers below.</p>

<h2>Real numbers from the 2025 MCC allotment data</h2>
<p>Closing rank is defined as the <em>worst (highest)</em> rank actually
allotted a seat. With only a handful of candidates willing to take the
service bond, that worst rank can land far higher than any ordinary
government college seat in the same specialty and category. Here's what we
found directly in MCC's own Round 3, 2025 allotment result, Open category:</p>
<table>
  <thead><tr><th>Institute</th><th>Specialty</th><th>Category</th><th>Closing rank</th></tr></thead>
  <tbody>
    <tr><td>Base Hospital</td><td>General Surgery (DNB)</td><td>Open</td><td>2,10,638</td></tr>
    <tr><td>Command Hospital (Central Command)</td><td>Pathology (MD/MS)</td><td>Open</td><td>2,05,105</td></tr>
    <tr><td>Institute of Naval Medicine</td><td>General Surgery (MD/MS)</td><td>Open</td><td>2,04,184</td></tr>
    <tr><td>Command Hospital (Eastern Command)</td><td>General Surgery (MD/MS)</td><td>Open</td><td>2,00,328</td></tr>
    <tr><td>7 Air Force Hospital</td><td>Anaesthesiology (DNB)</td><td>Open</td><td>1,90,254</td></tr>
  </tbody>
</table>
<p>For context, an ordinary Open-category government medical college seat in
these same specialties typically closes tens of thousands of ranks earlier.
A candidate scanning a raw MCC PDF (or a predictor that doesn't separate
these out) could easily read one of these rows and draw exactly the wrong
conclusion -- either "this specialty is impossibly hard everywhere" (if they
don't realise it's a bond seat) or, worse, miss a seat they'd have been
genuinely eligible for at a much better rank because a bond-seat row was
sitting in the same list, unlabelled.</p>

<h2>This isn't a one-off -- it's a recurring pattern across every round</h2>
<p>We checked all three real MCC datasets we track. Armed Forces/bond-seat
rows showed up in every one of them, always with closing ranks well past
what a civilian government seat shows in the same specialty and category:</p>
<table>
  <thead><tr><th>Dataset</th><th>Bond-seat rows found</th></tr></thead>
  <tbody>
    <tr><td>2025 Round 3</td><td>79</td></tr>
    <tr><td>2025 Stray Vacancy Round</td><td>13</td></tr>
    <tr><td>2024 Round 3</td><td>16</td></tr>
  </tbody>
</table>

<h2>How NEET-PG Help handles this now</h2>
<p>Our Predictor's <strong>"Government seats only"</strong> filter now
excludes Armed Forces/Command Hospital/service-bond seats entirely from
opening/closing-rank calculations, rather than showing them mixed in with
ordinary civilian government colleges. This isn't about hiding real seats --
every one of these allotments genuinely happened, and a candidate willing to
take the bond should absolutely still look for AFMS-specific counselling
information. It's about not letting a fundamentally different kind of seat,
with a fundamentally different eligibility bar, distort what "a government
college closing rank" means for the civilian candidates this site is
actually built for. This sits alongside a similar fix we made to how
<a href="pwd-reservation-neet-pg-closing-ranks.html">PwD-reserved allotments
affect closing ranks</a> -- both are cases where folding a seat with a
different, more relaxed eligibility bar into an ordinary category's numbers
makes the numbers actively misleading rather than just imprecise.</p>

<h2>What this means if you're reading any NEET-PG rank list</h2>
<p>Whenever a closing rank in a "government seat" list looks wildly out of
line with everything around it, check the institute name before assuming
the data is wrong. Command Hospital, AFMC, Institute of Naval Medicine, and
Army/Air Force/Base Hospital seats all carry a service bond -- treat their
numbers as a separate track, not a data point about ordinary government
medical college competitiveness. If you're actually interested in an AFMS
seat, the bond terms and eligibility are published separately by the Armed
Forces Medical Services and are worth reading in full before you rely on
any closing-rank number for one of these seats.</p>

<h2>Try it yourself</h2>
<p>Open the <a href="../index.html">Predictor tab</a> on NEET-PG Help, switch
"Seats to include" to <strong>Government seats only</strong>, and check any
high-demand specialty at Open category -- you'll no longer see a bond-seat
outlier sitting in the results. Every figure still links back to the exact
official MCC document it came from.</p>
""",
    ),
    BlogPost(
        slug="neet-pg-college-predictor-how-it-works",
        title="NEET PG College Predictor: How It Works (and Why It Uses Real MCC Data)",
        meta_description=(
            "How the free NEET-PG Help college predictor turns your rank and category "
            "into a realistic shortlist -- using real MCC allotment data, not a "
            "third-party estimate model."
        ),
        date="2026-09-23",
        summary=(
            "No black-box estimate model -- here's exactly how the free college "
            "predictor turns a rank and category into a shortlist, and what its "
            "limits are."
        ),
        hero_svg=_PREDICTOR_FUNNEL_SVG,
        body_html="""
<p>Most "NEET PG college predictor" tools work the same way: they take a rank
and category, run it against a model built from previous years' cutoffs, and
give you a probability or a list. The NEET-PG Help predictor does something
narrower and, we think, more honest -- it looks up your rank and category
against <strong>real opening and closing ranks computed directly from MCC's
own allotment result PDFs</strong>, and shows you exactly which
institute+specialty+category cells your rank actually reached in that round.</p>

<h2>What "real data" means here, concretely</h2>
<p>For every round we cover (2025 Round 3, 2025 Stray Vacancy Round, 2024
Round 3), we start from the official MCC result PDF -- not a scraped
third-party table -- and compute, for every institute + specialty + allotted
category combination:</p>
<ul>
  <li><strong>Opening rank</strong> -- the best (lowest) rank actually allotted that seat</li>
  <li><strong>Closing rank</strong> -- the worst (highest) rank actually allotted that seat</li>
  <li><strong>Seats counted</strong> -- how many candidates were actually allotted, so you can tell a cutoff based on 1 seat from one based on 40</li>
</ul>
<p>The category used is always the <strong>allotted</strong> category (the
seat's own category), not the candidate's category -- because an OBC
candidate can and does get allotted an Open seat, and that seat's closing
rank belongs to Open, not OBC. We also exclude PwD-reserved allotments from
their base category's closing rank, since folding them in badly inflates
what a non-PwD candidate could actually get -- see our
<a href="pwd-reservation-neet-pg-closing-ranks.html">separate post on the PwD closing-rank issue</a>
for the real numbers behind that decision.</p>

<h2>How to read a result</h2>
<p>Open the <strong>Predictor</strong> tab, pick a real MCC dataset from the
"Data source" dropdown (not the "Estimate" option, unless you specifically
want a rough third-party figure), choose Branch Predictor or College
Predictor, and enter your rank and category. What you get back is a list of
institute+specialty cells where your rank falls at or better than the
closing rank actually recorded for that category in that round --
each one with the exact opening/closing rank and seat count it's based on,
and a link back to the source document.</p>

<h2>What it can't do</h2>
<p>It cannot predict PG Counselling 2026 with certainty -- no tool can. Seat
counts change, new colleges get added or lose recognition, and candidate
behavior shifts year to year. What real historical data gives you is a
grounded starting point: where did this rank+category combination actually
land last time, with how many seats behind it. Treat it as a shortlist to
verify against the current year's own seat matrix and cutoffs as they're
published, not a guarantee.</p>

<h2>Try it</h2>
<p>The <a href="../index.html">Predictor</a> is free, needs no signup, and
every number links back to its official MCC source document.</p>
""",
    ),
    BlogPost(
        slug="neet-pg-branch-predictor-guide",
        title="NEET PG Branch Predictor: How to Shortlist a Specialty Using Real Closing Ranks",
        meta_description=(
            "A practical guide to using a NEET PG branch predictor -- what closing "
            "rank by specialty actually tells you, and how to shortlist realistic "
            "branch options using real MCC data, free."
        ),
        date="2026-09-23",
        summary=(
            "Closing rank by specialty is the single most useful number for "
            "shortlisting a branch -- here's how to actually use it."
        ),
        hero_svg=_BRANCH_TREE_SVG,
        body_html="""
<p>A branch predictor answers a narrower question than a college predictor:
not "which colleges can I get," but "which specialties are realistically
within reach at my rank and category, across all institutes combined." That
distinction matters if you're more attached to a specialty (say,
Radiodiagnosis or Dermatology) than to any particular college.</p>

<h2>The number that actually matters: specialty-wise closing rank</h2>
<p>On NEET-PG Help's <a href="../index.html">Branch Predictor</a>, each
specialty is shown with its all-India closing rank for your category and
round, plus how many institutes and seats that figure is based on. A
specialty with a closing rank of 45,000 based on 55 seats across 55
institutes is a very different bet from one based on 3 seats at a single
institute -- the predictor shows you both numbers so you're not reading a
cutoff in isolation.</p>

<h2>A real example</h2>
<p>In 2025 Round 3, General Medicine (MD/MS) closed at rank <strong>228,379</strong>
for Open category, across 585 seats and 229 institutes -- versus
<strong>10,075</strong> for OBC (171 seats). That's not a typo or an error in
the data; Open category pulls from the largest and most competitive pool, so
its closing rank naturally runs far higher than reserved categories at the
same specialty. See our <a href="neet-pg-category-wise-cutoff-explained.html">category-wise
cutoff breakdown</a> for the full picture across five specialties.</p>

<h2>How to use this practically</h2>
<ol>
  <li>Pick your round and category correctly first -- Round 1/2 use provisional
  allotment; Round 3 and Stray use different, non-comparable candidate pools.</li>
  <li>Look at the specialty's closing rank <em>and</em> its seat count together
  -- a favorable rank on very few seats is a long shot, not a safe bet.</li>
  <li>Cross-check against the <a href="how-to-read-neet-pg-seat-matrix.html">seat
  matrix</a> for the current year, since seat counts do change year to year.</li>
  <li>Use the College Predictor next to see which specific institutes are
  behind that specialty-level number.</li>
</ol>

<p>The Branch Predictor is free on the <a href="../index.html">Predictor tab</a>
of NEET-PG Help -- pick a real MCC round, not the estimate dataset, for
figures sourced directly from official allotment PDFs.</p>
""",
    ),
    BlogPost(
        slug="aiq-vs-state-quota-neet-pg",
        title="AIQ vs State Quota in NEET PG Counselling: What Actually Differs",
        meta_description=(
            "AIQ vs state quota in NEET PG counselling explained plainly -- who runs "
            "each, what share of seats they cover, and why closing ranks aren't "
            "comparable between them."
        ),
        date="2026-09-23",
        summary=(
            "Two different counselling processes, two different authorities, and "
            "ranks that don't translate directly between them -- here's the plain "
            "version."
        ),
        hero_svg=_AIQ_STATE_SVG,
        body_html="""
<p>NEET-PG seats in government medical colleges are split between two
separate counselling processes, run by two different authorities, with two
separate merit lists in practice. Confusing the two is one of the most
common mistakes candidates make when reading cutoff data.</p>

<h2>All India Quota (AIQ)</h2>
<ul>
  <li>Covers <strong>50% of seats in government medical/dental colleges</strong>
  (state government colleges) plus <strong>100% of seats in central
  institutions</strong> such as AIIMS-run programs, and deemed/central
  universities that participate in AIQ.</li>
  <li>Counselling is conducted entirely by the <strong>Medical Counselling
  Committee (MCC)</strong>, under the Directorate General of Health Services.</li>
  <li>Open to candidates from anywhere in India, regardless of home state --
  domicile doesn't restrict eligibility for AIQ seats.</li>
  <li>This is the data NEET-PG Help tracks and the Predictor is built on --
  every closing rank on this site is from AIQ rounds published by MCC.</li>
</ul>

<h2>State Quota</h2>
<ul>
  <li>Covers the <strong>remaining 50% of state government college seats</strong>,
  plus most seats in state-run private and deemed colleges.</li>
  <li>Counselling is run independently by <strong>each state's own
  counselling authority</strong> (for example, a state directorate of medical
  education), not by MCC.</li>
  <li>Almost always restricted by <strong>domicile</strong> -- you generally
  need to meet that state's residency/domicile criteria to be eligible.</li>
  <li>Rules, reservation categories, seat matrices, and even the number of
  rounds vary state to state -- there is no single "State Quota closing
  rank" the way there's an all-India AIQ figure.</li>
</ul>

<h2>Why closing ranks don't transfer between the two</h2>
<p>An AIQ closing rank of, say, 10,000 for a specialty tells you nothing
directly about what rank clears that same specialty under a specific state's
quota -- the candidate pool, seat count, reservation structure and number of
applicants are all different. Never use an AIQ number as a stand-in for a
state counselling estimate, and vice versa.</p>

<h2>What NEET-PG Help covers today</h2>
<p>Right now, every dataset on this site -- the <a href="../index.html">College
and Branch Predictor</a>, the seat matrix and the closing-rank tables -- is
built from <strong>AIQ (MCC) data only</strong>. We plan to add individual
state counselling authorities over time, each with its own dedicated source
configuration and validation rules, exactly as laid out in our project's own
roadmap. If your target seat is a state-quota seat, treat the numbers here as
AIQ-only context, not a state-specific prediction.</p>
""",
    ),
    BlogPost(
        slug="how-to-read-neet-pg-seat-matrix",
        title="How to Read a NEET PG Seat Matrix (Round 1, 2, 3 and Stray Explained)",
        meta_description=(
            "What a NEET PG seat matrix actually shows, how it changes across "
            "Round 1, Round 2, Round 3 and the Stray Vacancy Round, and how to read "
            "seat additions, deletions and category changes between versions."
        ),
        date="2026-09-23",
        summary=(
            "A seat matrix isn't static -- it changes every round. Here's how to "
            "actually read one, and what changes between versions mean."
        ),
        hero_svg=_SEAT_MATRIX_GRID_SVG,
        body_html="""
<p>A "seat matrix" is simply the list of every seat on offer -- by institute,
course, specialty, category and quota -- for a given counselling round. If
you've only ever seen one round's seat matrix, it's easy to assume it's a
fixed number that just gets filled up. It isn't. The seat matrix itself
changes from round to round, and reading those changes correctly matters
almost as much as reading the matrix itself.</p>

<h2>Why the seat matrix changes between rounds</h2>
<ul>
  <li><strong>New seats get added</strong> mid-cycle when a college receives
  fresh recognition or a specialty's intake is increased after Round 1 has
  already started.</li>
  <li><strong>Seats get removed</strong> when a college loses recognition for
  a course, or when a previously-listed seat turns out to be ineligible.</li>
  <li><strong>Category composition can shift</strong> -- a seat allotted as
  Open in Round 1 doesn't necessarily stay Open if it's vacated and comes
  back into the pool.</li>
  <li><strong>The pool of unfilled seats shrinks</strong> each round, by
  definition -- Round 2 only offers what wasn't filled (or was vacated) after
  Round 1, and so on through Round 3 and the Stray Vacancy Round.</li>
</ul>

<h2>What each round actually represents</h2>
<table>
  <thead><tr><th>Round</th><th>What it offers</th></tr></thead>
  <tbody>
    <tr><td>Round 1</td><td>The full initial seat matrix, first allotment</td></tr>
    <tr><td>Round 2</td><td>Seats vacated or unfilled after Round 1, plus any newly added seats</td></tr>
    <tr><td>Round 3</td><td>Seats vacated or unfilled after Round 2 -- this is usually the last all-India mop-up round with fresh registration</td></tr>
    <tr><td>Stray Vacancy Round</td><td>A final mop-up of whatever remains after Round 3 (and any state-level processes) -- a much smaller round, filled from a different, later candidate pool</td></tr>
  </tbody>
</table>
<p>That last point matters for comparisons: in 2025, Round 3 had allotments
across <strong>1,499 institutes</strong> versus <strong>743</strong> in the
Stray Vacancy Round -- see our <a href="round-3-vs-stray-vacancy-round-2025.html">full
Round 3 vs. Stray comparison</a> for the category-wise breakdown. A rank that
clears a seat in the Stray round isn't directly comparable to the same rank
in Round 3, because it's a different, later pool of candidates.</p>

<h2>Where to check the current seat matrix</h2>
<p>NEET-PG Help's Seat Matrix data comes directly from MCC's own published
seat matrix and allotment result documents for each round, with every entry
linked back to its source PDF. Use the <a href="../index.html">Predictor
tab</a> to see seat counts alongside opening/closing ranks by institute and
specialty, rather than reading a rank in isolation from how many seats it was
actually based on.</p>
""",
    ),
    BlogPost(
        slug="neet-pg-category-wise-cutoff-explained",
        title="NEET PG Category-Wise Cutoff Explained (Open, OBC, EWS, SC, ST)",
        meta_description=(
            "Why NEET PG closing ranks differ so much across Open, OBC, EWS, SC and "
            "ST categories -- explained with real 2025 Round 3 MCC data for General "
            "Medicine."
        ),
        date="2026-09-23",
        summary=(
            "Why does the same specialty show wildly different closing ranks by "
            "category? Real 2025 MCC data for General Medicine makes it concrete."
        ),
        hero_svg=_CATEGORY_CUTOFF_SVG,
        body_html="""
<p>One of the most common points of confusion for first-time NEET-PG
candidates is seeing the same specialty at the same institute show very
different closing ranks depending on category. This isn't inconsistent data
-- it's how reservation-based seat allocation is designed to work. Here's
what's actually happening, with real numbers.</p>

<h2>A real example: General Medicine, 2025 Round 3 (all-India)</h2>
<table>
  <thead><tr><th>Category</th><th>Opening rank</th><th>Closing rank</th><th>Seats</th></tr></thead>
  <tbody>
    <tr><td>Open / UR</td><td>26</td><td>228,379</td><td>585</td></tr>
    <tr><td>OBC</td><td>174</td><td>10,075</td><td>171</td></tr>
    <tr><td>EWS</td><td>239</td><td>12,928</td><td>55</td></tr>
    <tr><td>SC</td><td>1,385</td><td>27,067</td><td>98</td></tr>
    <tr><td>ST</td><td>10,609</td><td>45,956</td><td>55</td></tr>
  </tbody>
</table>
<p>These figures are computed directly from MCC's own 2025 Round 3 allotment
result PDF, aggregated by institute + specialty + allotted category, and are
also what powers the <a href="../index.html">College and Branch Predictor</a>
on this site.</p>

<h2>Why Open's closing rank is so much higher</h2>
<p>This is the part that trips people up: a <em>higher</em> closing rank for
Open here doesn't mean Open is "easier." It's the opposite of what it looks
like at first glance -- Open seats draw from every candidate regardless of
category, which is a far larger and more competitive pool, and Open seats
also make up the largest single share of total seats (585 of the roughly 984
General Medicine seats in this table). With more seats spread across a wider
competitive pool, the seat that goes to the last (highest-ranked) Open
candidate ends up much further down the merit list in absolute rank terms
than the last SC or ST candidate in their much smaller, separately-ranked
category pool.</p>

<h2>The allotted category, not your own category, decides the cutoff</h2>
<p>A closing rank always belongs to the <strong>category of the seat that
was allotted</strong>, not the category the candidate registered under. An
OBC candidate who is allotted an Open seat (because their rank was good
enough to compete on the open list) counts toward the Open closing rank for
that seat, not OBC's. This is exactly why NEET-PG Help's predictor always
groups by allotted category -- mixing the two would produce a cutoff that
doesn't match how MCC's own merit lists actually work.</p>

<h2>One more layer: horizontal reservations like PwD</h2>
<p>Categories like Open, OBC, EWS, SC and ST are <em>vertical</em>
reservations. PwD is a separate, <em>horizontal</em> reservation that cuts
across all of them with its own, much more relaxed rank cutoff -- and
folding a PwD allotment into its base category's figures can badly distort
that category's closing rank. We found and fixed exactly this issue in our
own data; see <a href="pwd-reservation-neet-pg-closing-ranks.html">how PwD
allotments affect NEET PG closing ranks</a> for the real before/after
numbers.</p>

<h2>Use this when reading any predictor's output</h2>
<p>Whenever you check a cutoff -- here or anywhere else -- confirm which
category it's labelled under and how many seats it's based on. A closing
rank on 585 seats is a far more stable number than one based on a handful
of seats, category-per-category.</p>
""",
    ),
    BlogPost(
        slug="pwd-reservation-neet-pg-closing-ranks",
        title="PwD Reservation and NEET PG Closing Ranks: What the Data Actually Shows",
        meta_description=(
            "How PwD (Persons with Disability) reservation works in NEET PG "
            "counselling, and a real example of how wrongly folding PwD allotments "
            "into a base category inflated a closing rank from 6,050 to 229,954."
        ),
        date="2026-09-23",
        summary=(
            "A real, quantified example of how PwD allotments -- if handled wrong "
            "-- can make a closing rank look 38x higher than it should."
        ),
        hero_svg=_PWD_INFLATION_SVG,
        body_html="""
<p>PwD (Persons with Disability) reservation in NEET-PG counselling is a
<strong>horizontal reservation</strong>: unlike Open, OBC, EWS, SC and ST
(which are vertical categories that seats are allotted directly against),
PwD cuts <em>across</em> every vertical category. A candidate can be, for
example, "OBC PwD" or "Open PwD" -- meaning they hold a PwD-reserved seat
within the OBC or Open pool, under relaxed eligibility criteria that MCC
applies for candidates with benchmark disabilities.</p>

<h2>Why this matters for closing-rank data</h2>
<p>Closing rank is conventionally defined as the <strong>worst (highest)
rank actually allotted</strong> for a given institute + specialty +
category. Because PwD eligibility is relaxed, a PwD candidate can be
allotted a seat at a rank far higher (worse) than any non-PwD candidate in
that same base category could achieve. If a PwD-tagged row simply gets
folded into its base category by stripping the "PwD" label -- which is a
completely reasonable-looking simplification -- that one row can badly
distort the closing rank shown for everyone else in that category.</p>

<h2>A real example from our own data</h2>
<p>We found this exact problem while building our Predictor. At Pandit
Bhagwat Dayal Sharma Post Graduate Institute of Medical Sciences, for
Orthopaedics (MD/MS), OBC category, 2025 Round 3:</p>
<table>
  <thead><tr><th>Method</th><th>Closing rank shown</th></tr></thead>
  <tbody>
    <tr><td>PwD allotment folded into OBC (wrong)</td><td>229,954</td></tr>
    <tr><td>PwD allotment excluded from OBC (correct)</td><td>6,050</td></tr>
  </tbody>
</table>
<p>That's a <strong>38x difference</strong> -- an OBC candidate with a rank
around 200,000 reading the wrong figure would have believed they had a real
shot at that seat, when in fact only a PwD-eligible candidate could actually
get it at that rank. This wasn't an isolated case: across the full 2025
Round 3 dataset, this issue affected 114 out of 11,278 college+specialty+category
cells, and 89 out of 9,330 cells in the 2024 dataset we checked.</p>

<h2>How NEET-PG Help handles it now</h2>
<p>Every closing-rank figure on this site -- across the Predictor, Cutoff
Explorer and Seat Matrix -- now <strong>excludes PwD-reserved allotments from
their base category's closing rank</strong> rather than folding them in. This
doesn't delete any underlying PwD data; it simply stops a PwD row's much
easier rank from being counted toward the base category's own cutoff, which
is the statistically correct way to treat a horizontal reservation. A
dedicated, standalone PwD-category view (showing PwD candidates their own
actual closing ranks) is a planned addition, not yet live.</p>

<h2>What this means if you're PwD-eligible</h2>
<p>The base-category figures on this site (Open, OBC, EWS, SC, ST) do
<strong>not</strong> currently show you a PwD-specific closing rank -- they
show what a non-PwD candidate in that category could reach. If you hold PwD
certification, treat these figures as a baseline for the general category
pool, not your own eligibility window, until a dedicated PwD view is added.</p>
""",
    ),
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
