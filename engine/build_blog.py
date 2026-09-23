"""Builds one real, standalone, indexable HTML page per post in
engine/blog_posts.py (site/blog/<slug>.html), plus a blog index page
(site/blog/index.html) listing all of them. These are genuine separate
pages with their own URL, <title> and <meta name="description"> -- unlike
a card inside the single-page app, search engines can crawl and rank each
one on its own.

Also exposes `list_cards_html()`, which engine/build_site.py uses to
render the same list (as plain <a href> cards, so it's readable even
without JavaScript) into the main site's in-app Blog tab.

Usage: python3 -m engine.build_blog
"""

from __future__ import annotations

import html
from pathlib import Path

from engine.blog_posts import POSTS, BlogPost

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "site" / "blog"

SITE_NAME = "NEET-PG Help"
SITE_URL = "https://neetpghelp.com"

# A trimmed copy of the main site's tokens/fonts, just enough for a clean,
# on-brand reading page -- these pages don't need the app shell (bottom
# nav, view-switching JS, dataset predictor, etc.), just good typography.
_STYLE = """
<style>
  :root {
    --paper: #f5f6fa; --surface: #ffffff; --surface-2: #eef0f7; --line: #dfe3ee;
    --ink: #121a2b; --ink-muted: #5b637a; --ink-faint: #8991a8;
    --brand: #16305a; --brand-fill: #16305a; --on-brand-fill: #fdfdff;
    --accent: #a3742a; --accent-tint: #f6ecd8;
    --font-display: "Newsreader", ui-serif, Georgia, serif;
    --font-body: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", monospace;
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #0a0e18; --surface: #121a2b; --surface-2: #182238; --line: #29334d;
      --ink: #eef1f8; --ink-muted: #9aa3ba; --ink-faint: #6b7386;
      --brand: #8fb3ea; --brand-fill: #24437a; --on-brand-fill: #f4f7fd;
      --accent: #dcae63; --accent-tint: #2c2410;
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --paper: #0a0e18; --surface: #121a2b; --surface-2: #182238; --line: #29334d;
    --ink: #eef1f8; --ink-muted: #9aa3ba; --ink-faint: #6b7386;
    --brand: #8fb3ea; --brand-fill: #24437a; --on-brand-fill: #f4f7fd;
    --accent: #dcae63; --accent-tint: #2c2410;
    color-scheme: dark;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: var(--font-body); background: var(--paper); color: var(--ink); -webkit-font-smoothing: antialiased; }
  a { color: var(--brand); }
  .top-link { display: block; padding: 16px; font-size: 13px; font-weight: 600; text-decoration: none; }
  main { max-width: 640px; margin: 0 auto; padding: 4px 20px 48px; }
  .eyebrow { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); font-weight: 700; }
  h1 { font-family: var(--font-display); font-size: 28px; font-weight: 600; line-height: 1.25; margin: 8px 0 6px; text-wrap: balance; }
  .post-date { font-size: 12.5px; color: var(--ink-faint); font-family: var(--font-mono); margin-bottom: 18px; }
  .hero { background: var(--surface-2); border: 1px solid var(--line); border-radius: 16px; padding: 12px; margin-bottom: 22px; }
  .hero svg { width: 100%; height: auto; display: block; }
  article { font-size: 15.5px; line-height: 1.7; }
  article h2 { font-family: var(--font-display); font-size: 19px; font-weight: 600; margin: 28px 0 8px; }
  article p { margin: 0 0 14px; }
  article ul { margin: 0 0 14px; padding-left: 20px; }
  article li { margin-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; margin: 0 0 18px; font-size: 13.5px; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
  th { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-faint); }
  td:not(:first-child), th:not(:first-child) { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
  .disclosure { background: var(--accent-tint); border-radius: 12px; padding: 12px 14px; font-size: 12.5px; color: var(--ink-muted); margin: 26px 0 0; }
  .site-footer { max-width: 640px; margin: 0 auto; padding: 18px 20px 32px; border-top: 1px solid var(--line); font-size: 11.5px; color: var(--ink-faint); line-height: 1.6; }
  .site-footer a { color: var(--ink-faint); }
  .card-list { list-style: none; padding: 0; margin: 0; }
  .card-list li { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 15px 16px; margin-bottom: 10px; }
  .card-list a { text-decoration: none; color: var(--ink); font-family: var(--font-display); font-size: 17px; font-weight: 600; }
  .card-list .card-date { font-size: 11.5px; color: var(--ink-faint); font-family: var(--font-mono); margin: 2px 0 6px; }
  .card-list .card-summary { font-size: 13.5px; color: var(--ink-muted); line-height: 1.55; }
</style>
"""

_DISCLOSURE = (
    '<p class="disclosure">NEET-PG Help is a free, independent information service. '
    "It is not MCC, NBEMS, or any government authority, and is not officially "
    "affiliated with them or with any other product or service mentioned above.</p>"
)

_FOOTER = f"""
<footer class="site-footer">
  <a href="../index.html">{SITE_NAME}</a> &middot; neetpghelp.com &middot;
  independent &amp; free &middot; not affiliated with MCC or NBEMS
</footer>
"""


def _post_page_html(post: BlogPost) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(post.title)} | {SITE_NAME}</title>
<meta name="description" content="{html.escape(post.meta_description)}">
<link rel="canonical" href="{SITE_URL}/blog/{post.slug}.html">
<meta property="og:title" content="{html.escape(post.title)}">
<meta property="og:description" content="{html.escape(post.meta_description)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/blog/{post.slug}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,500&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
{_STYLE}
</head>
<body>
<a class="top-link" href="../index.html">&larr; Back to {SITE_NAME}</a>
<main>
  <div class="eyebrow">Blog</div>
  <h1>{html.escape(post.title)}</h1>
  <div class="post-date">{post.date}</div>
  <div class="hero">{post.hero_svg}</div>
  <article>
    {post.body_html}
  </article>
  {_DISCLOSURE}
</main>
{_FOOTER}
</body>
</html>
"""


def _index_page_html() -> str:
    cards = "\n".join(
        f'<li><a href="{p.slug}.html">{html.escape(p.title)}</a>'
        f'<div class="card-date">{p.date}</div>'
        f'<div class="card-summary">{html.escape(p.summary)}</div></li>'
        for p in POSTS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog | {SITE_NAME}</title>
<meta name="description" content="Plain-language explainers and data-driven round-ups on NEET-PG counselling, from {SITE_NAME}.">
<link rel="canonical" href="{SITE_URL}/blog/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,500&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
{_STYLE}
</head>
<body>
<a class="top-link" href="../index.html">&larr; Back to {SITE_NAME}</a>
<main>
  <div class="eyebrow">Blog</div>
  <h1>Latest posts</h1>
  <ul class="card-list">
    {cards if cards else '<li>No posts yet &mdash; check back soon.</li>'}
  </ul>
</main>
{_FOOTER}
</body>
</html>
"""


def list_cards_html() -> str:
    """Server-rendered cards for the main site's in-app Blog tab -- plain
    <a href> links to the real pages above, so they're readable even
    without JavaScript executing (build_site.py substitutes this in)."""
    if not POSTS:
        return (
            '<div class="empty-state">No posts yet &mdash; check back as the counselling '
            'cycle moves, or see <a href="#" class="text-link-btn" data-view="updates">'
            "Latest Updates</a> for the automatic feed in the meantime.</div>"
        )
    cards = []
    for p in POSTS:
        cards.append(
            f'<div class="card"><div class="title"><a class="title-link" href="blog/{p.slug}.html">'
            f'{html.escape(p.title)}</a></div>'
            f'<div class="meta" style="margin-bottom:7px;"><span>{p.date}</span></div>'
            f'<p style="margin:0; font-size:13.5px; line-height:1.6; color:var(--ink-muted);">'
            f'{html.escape(p.summary)}</p></div>'
        )
    return "\n".join(cards)


def main() -> None:
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    for post in POSTS:
        out_path = BLOG_DIR / f"{post.slug}.html"
        out_path.write_text(_post_page_html(post), encoding="utf-8")
        print(f"Wrote {out_path}")
    index_path = BLOG_DIR / "index.html"
    index_path.write_text(_index_page_html(), encoding="utf-8")
    print(f"Wrote {index_path}")


if __name__ == "__main__":
    main()
