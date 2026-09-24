"""Builds site/index.html by inlining site/data.json + site/predictor_data.json
+ every real dataset listed in site/datasets_manifest.json into a template.

Design v2: premium "credential / ledger" treatment, full light+dark theme
support (system-detected + manual toggle), per the artifact-design skill's
page contract (this file is CONTENT ONLY -- no <!DOCTYPE>/<html>/<head>/
<body> of its own; the Artifact tool wraps it in that skeleton at publish
time; on the real deployment it's served as-is by GitHub Pages, which
needs the full <!DOCTYPE html><html>... wrapper -- see the bottom of this
file).

Adding a new real MCC round (whether by hand or by the automated
pipeline) never touches this file: engine/dataset_registry.publish_dataset
writes site/datasets/<id>.json and updates site/datasets_manifest.json,
and this script picks up whatever is listed there. Nothing here is
hardcoded to a specific year or round.

Usage: python3 -m engine.build_site
"""
from __future__ import annotations

import json
import os
import pathlib

from engine import build_blog, college_type, dataset_registry

ROOT = pathlib.Path(__file__).resolve().parent.parent

TEMPLATE = r"""<title>NEET-PG Help</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,500&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {
    /* ---- light palette (default) ---- */
    --paper: #f5f6fa;
    --surface: #ffffff;
    --surface-2: #eef0f7;
    --line: #dfe3ee;
    --ink: #121a2b;
    --ink-muted: #5b637a;
    --ink-faint: #8991a8;
    --brand: #16305a;
    --brand-strong: #0c1f3d;
    --brand-tint: #e8edf7;
    --brand-fill: #16305a;
    --brand-fill-strong: #0c1f3d;
    --on-brand-fill: #fdfdff;
    --accent: #a3742a;
    --accent-tint: #f6ecd8;
    --success: #1f7a5c;
    --success-tint: #e3f3ec;
    --warn: #a34e12;
    --warn-tint: #fbe9d9;
    --danger: #b3261e;
    --shadow-color: 220 40% 20%;

    --font-display: "Newsreader", ui-serif, Georgia, serif;
    --font-body: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", monospace;

    padding-top: env(safe-area-inset-top, 0px);
    padding-bottom: env(safe-area-inset-bottom, 0px);
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #0a0e18;
      --surface: #121a2b;
      --surface-2: #182238;
      --line: #29334d;
      --ink: #eef1f8;
      --ink-muted: #9aa3ba;
      --ink-faint: #6b7386;
      --brand: #8fb3ea;
      --brand-strong: #b7cdf3;
      --brand-tint: #182746;
      --brand-fill: #24437a;
      --brand-fill-strong: #152847;
      --on-brand-fill: #f4f7fd;
      --accent: #dcae63;
      --accent-tint: #2c2410;
      --success: #4bb693;
      --success-tint: #112a22;
      --warn: #e2a45c;
      --warn-tint: #2c1f0e;
      --danger: #f0827d;
      --shadow-color: 220 60% 2%;
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --paper: #0a0e18;
    --surface: #121a2b;
    --surface-2: #182238;
    --line: #29334d;
    --ink: #eef1f8;
    --ink-muted: #9aa3ba;
    --ink-faint: #6b7386;
    --brand: #8fb3ea;
    --brand-strong: #b7cdf3;
    --brand-tint: #182746;
    --brand-fill: #24437a;
    --brand-fill-strong: #152847;
    --on-brand-fill: #f4f7fd;
    --accent: #dcae63;
    --accent-tint: #2c2410;
    --success: #4bb693;
    --success-tint: #112a22;
    --warn: #e2a45c;
    --warn-tint: #2c1f0e;
    --danger: #f0827d;
    --shadow-color: 220 60% 2%;
    color-scheme: dark;
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    -webkit-font-smoothing: antialiased;
    padding-bottom: calc(76px + env(safe-area-inset-bottom, 0px));
  }
  ::selection { background: var(--accent-tint); color: var(--brand-strong); }

  /* ---------- header ---------- */
  header.top {
    background:
      radial-gradient(120% 160% at 8% -20%, color-mix(in srgb, var(--accent) 20%, transparent), transparent 55%),
      linear-gradient(135deg, var(--brand-fill) 0%, var(--brand-fill-strong) 100%);
    color: #fdfdff;
    padding: calc(14px + env(safe-area-inset-top, 0px)) 18px 14px;
    position: sticky;
    top: 0;
    z-index: 10;
    border-bottom: 2px solid var(--accent);
  }
  .brand-row { display: flex; align-items: center; gap: 11px; }
  .brand-mark {
    width: 38px; height: 38px; flex: 0 0 auto;
    display: flex; align-items: center; justify-content: center;
    filter: drop-shadow(0 3px 6px hsl(var(--shadow-color) / 0.5));
  }
  .brand-mark svg { width: 38px; height: 38px; display: block; }
  header.top h1 {
    font-family: var(--font-display);
    font-size: 21px;
    font-weight: 600;
    margin: 0;
    letter-spacing: 0.01em;
    flex: 1;
  }
  header.top p {
    margin: 4px 0 0 42px;
    font-size: 12px;
    color: color-mix(in srgb, #fff 78%, transparent);
    font-weight: 500;
  }
  .theme-toggle {
    flex: 0 0 auto;
    width: 34px; height: 34px;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, #fff 30%, transparent);
    background: color-mix(in srgb, #fff 10%, transparent);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
  }
  .theme-toggle svg { width: 16px; height: 16px; }

  .disclaimer-banner {
    background: var(--warn-tint);
    border-bottom: 1px solid var(--line);
    color: var(--warn);
    font-size: 11.5px;
    font-weight: 500;
    padding: 8px 18px;
    line-height: 1.5;
  }

  main { padding: 16px; max-width: 640px; margin: 0 auto; }
  .view { display: none; }
  .view.active { display: block; animation: fadein 0.2s ease; }
  @keyframes fadein { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) { .view.active { animation: none; } }

  /* ---------- inputs ---------- */
  .search-box {
    width: 100%;
    padding: 13px 16px;
    font-size: 15px;
    font-family: var(--font-body);
    border: 1px solid var(--line);
    border-radius: 12px;
    margin-bottom: 12px;
    background: var(--surface);
    color: var(--ink);
  }
  .search-box::placeholder { color: var(--ink-faint); }
  .filter-row { display: flex; gap: 8px; overflow-x: auto; padding: 2px 2px 8px; margin-bottom: 4px; }
  .filter-chip {
    flex: 0 0 auto;
    padding: 7px 14px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: var(--surface);
    font-family: var(--font-body);
    font-size: 12.5px;
    font-weight: 600;
    color: var(--ink-muted);
    cursor: pointer;
    white-space: nowrap;
  }
  .filter-chip.active { background: var(--brand-fill); border-color: var(--brand-fill); color: var(--on-brand-fill); }

  /* ---------- dashboard hero ---------- */
  .hero-card {
    background: linear-gradient(155deg, var(--brand-fill) 0%, var(--brand-fill-strong) 78%);
    color: #fdfdff;
    border-radius: 20px;
    padding: 22px 22px 20px;
    margin-bottom: 14px;
    box-shadow: 0 16px 34px -14px hsl(var(--shadow-color) / 0.55);
    border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
    position: relative;
    overflow: hidden;
  }
  .hero-card::after {
    content: "";
    position: absolute; inset: 0;
    background:
      radial-gradient(120% 90% at 100% 0%, color-mix(in srgb, var(--accent) 26%, transparent), transparent 55%),
      linear-gradient(135deg, color-mix(in srgb, var(--accent) 14%, transparent), transparent 60%);
    pointer-events: none;
  }
  .hero-card::before {
    content: "";
    position: absolute; top: 10px; right: 10px; bottom: 10px; left: 10px;
    border: 1px solid color-mix(in srgb, #fff 14%, transparent);
    border-radius: 13px;
    pointer-events: none;
  }
  .hero-eyebrow { position: relative; font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); font-weight: 700; }
  .hero-cycle { position: relative; font-family: var(--font-display); font-size: 27px; font-weight: 600; margin: 5px 0 12px; text-wrap: balance; }
  .hero-rounds { position: relative; display: flex; gap: 6px; flex-wrap: wrap; }
  .hero-round-pill {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    padding: 4px 11px;
    border-radius: 999px;
    background: color-mix(in srgb, var(--accent) 22%, transparent);
    border: 1px solid color-mix(in srgb, var(--accent) 55%, transparent);
    color: #fdf3e2;
  }

  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
  .stat-card {
    background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 13px 14px;
    box-shadow: 0 6px 16px -12px hsl(var(--shadow-color) / 0.5);
    position: relative; overflow: hidden;
  }
  .stat-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2.5px;
    background: linear-gradient(90deg, var(--accent), transparent 85%);
  }
  .stat-card .label { font-size: 10.5px; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
  .stat-card .value { font-family: var(--font-mono); font-size: 17px; font-weight: 600; margin-top: 5px; font-variant-numeric: tabular-nums; }
  .stat-card.wide { grid-column: 1 / -1; }

  .timestamp-row { display: flex; justify-content: space-between; align-items: baseline; font-size: 12.5px; color: var(--ink-muted); padding: 7px 0; }
  .timestamp-row + .timestamp-row { border-top: 1px solid var(--line); }
  .timestamp-row strong { font-family: var(--font-mono); color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }

  .section-title {
    font-family: var(--font-body);
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--ink-faint);
    margin: 20px 0 9px;
  }

  /* ---------- cards ---------- */
  .card {
    background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--brand-tint);
    border-radius: 13px; padding: 13px 15px 13px 14px; margin-bottom: 9px;
    box-shadow: 0 4px 14px -12px hsl(var(--shadow-color) / 0.5);
  }
  .card .title { font-family: var(--font-display); font-size: 15px; font-weight: 600; line-height: 1.4; margin-bottom: 7px; }
  .card a.title-link { color: var(--ink); text-decoration: none; }
  .card a.title-link:hover, .card a.title-link:active { color: var(--brand); }
  .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 7px; }
  .tag { font-family: var(--font-body); font-size: 10.5px; font-weight: 700; padding: 3px 9px; border-radius: 999px; background: var(--brand-tint); color: var(--brand); letter-spacing: 0.01em; }
  .tag.round { background: var(--accent-tint); color: var(--accent); }
  .tag.low-confidence { background: var(--warn-tint); color: var(--warn); }
  .meta { font-size: 12px; color: var(--ink-muted); display: flex; justify-content: space-between; align-items: center; gap: 10px; }
  .meta .source-link { color: var(--brand); font-weight: 600; text-decoration: none; white-space: nowrap; }
  .meta .source-link:hover { text-decoration: underline; }

  .empty-state { text-align: center; color: var(--ink-faint); font-size: 13px; padding: 34px 14px; }

  /* ---------- bottom nav ---------- */
  nav.bottom {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: var(--surface);
    border-top: 1px solid var(--line);
    padding: 6px 8px calc(6px + env(safe-area-inset-bottom, 0px));
    display: flex;
    gap: 4px;
    z-index: 20;
    box-shadow: 0 -8px 24px -16px hsl(var(--shadow-color) / 0.35);
  }
  nav.bottom button {
    flex: 1; background: none; border: none; padding: 7px 4px;
    border-radius: 12px;
    font-family: var(--font-body); font-size: 10.5px; font-weight: 600;
    color: var(--ink-faint);
    display: flex; flex-direction: column; align-items: center; gap: 3px;
    transition: background-color .15s ease, color .15s ease;
  }
  nav.bottom button svg { width: 20px; height: 20px; }
  nav.bottom button.active { color: var(--brand); background: var(--brand-tint); }
  nav.bottom button.active svg { stroke: var(--brand); }

  /* ---------- about ---------- */
  .about-block { background: var(--surface); border: 1px solid var(--line); border-radius: 15px; padding: 18px; font-size: 13.5px; line-height: 1.65; }
  .about-block h3 { font-family: var(--font-display); font-size: 16px; font-weight: 600; margin: 18px 0 6px; }
  .about-block h3:first-child { margin-top: 0; }
  .about-block a { color: var(--brand); font-weight: 600; text-decoration: none; }
  .about-block a:hover { text-decoration: underline; }
  .about-block hr { border: none; border-top: 1px solid var(--line); margin: 20px 0; }
  .about-block code { font-family: var(--font-mono); font-size: 12px; background: var(--surface-2); padding: 1px 5px; border-radius: 5px; }
  .about-blog-links { margin: 0 0 4px; padding-left: 20px; }
  .about-blog-links li { margin-bottom: 6px; }
  .provenance-line { font-size: 11px; color: var(--ink-faint); margin-top: 4px; font-family: var(--font-mono); }

  .text-link-btn {
    background: none; border: none; padding: 0; margin: 0; cursor: pointer;
    font-family: var(--font-body); font-size: 12.5px; font-weight: 600;
    color: var(--brand); text-decoration: none;
  }
  .text-link-btn:hover { text-decoration: underline; }
  .about-crosslinks { display: flex; gap: 10px; align-items: center; color: var(--ink-faint); margin: 0; }

  /* ---------- site footer ---------- */
  .site-footer {
    max-width: 640px; margin: 4px auto 0; padding: 18px 16px 6px;
    border-top: 1px solid var(--line);
  }
  .footer-links { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px; }
  .footer-links .text-link-btn { font-size: 12px; }
  .footer-meta { font-size: 11px; color: var(--ink-faint); line-height: 1.6; }

  /* ---------- predictor ---------- */
  .predictor-warning {
    background: var(--warn-tint);
    border: 1px solid color-mix(in srgb, var(--warn) 35%, transparent);
    color: var(--warn);
    border-radius: 13px;
    padding: 13px 15px;
    font-size: 12.5px;
    line-height: 1.55;
    margin-bottom: 14px;
  }
  .predictor-warning strong { display: block; font-family: var(--font-display); font-size: 14.5px; font-weight: 600; margin-bottom: 4px; }
  .predictor-form { background: var(--surface); border: 1px solid var(--line); border-radius: 15px; padding: 15px; margin-bottom: 14px; }
  .predictor-form label { display: block; font-size: 11.5px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.04em; margin: 12px 0 5px; }
  .predictor-form label:first-child { margin-top: 0; }
  .predictor-form input, .predictor-form select {
    width: 100%; padding: 11px 13px; font-size: 15px; font-family: var(--font-mono);
    border: 1px solid var(--line); border-radius: 10px; background: var(--paper); color: var(--ink);
  }
  .predictor-form select { font-family: var(--font-body); }
  .predictor-form button {
    width: 100%; margin-top: 14px; padding: 13px; font-family: var(--font-body);
    font-size: 14.5px; font-weight: 700; color: var(--brand-strong);
    background: linear-gradient(135deg,
      color-mix(in srgb, var(--accent) 90%, #fff 10%) 0%,
      var(--accent) 45%,
      color-mix(in srgb, var(--accent) 78%, #000 22%) 100%);
    border: none; border-radius: 11px; cursor: pointer;
    box-shadow: 0 10px 22px -10px hsl(var(--shadow-color) / 0.55);
    transition: transform .12s ease, box-shadow .12s ease;
  }
  .predictor-form button:active { transform: translateY(1px); box-shadow: 0 6px 14px -10px hsl(var(--shadow-color) / 0.5); }
  :root[data-theme="dark"] .predictor-form button { color: #241804; }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .predictor-form button { color: #241804; }
  }
  .predictor-mode-toggle {
    display: flex; gap: 3px; margin-bottom: 12px;
    background: var(--surface-2); border: 1px solid var(--line); border-radius: 13px; padding: 3px;
  }
  .predictor-mode-toggle button {
    flex: 1; padding: 9px; border-radius: 10px; border: none;
    background: transparent; font-family: var(--font-body); font-size: 12.5px; font-weight: 600; color: var(--ink-muted); cursor: pointer;
    transition: background-color .15s ease, color .15s ease, box-shadow .15s ease;
  }
  .predictor-mode-toggle button.active {
    background: var(--surface); color: var(--brand);
    box-shadow: 0 3px 10px -4px hsl(var(--shadow-color) / 0.4);
  }
  .predictor-dataset-label {
    font-size: 11.5px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase;
    letter-spacing: 0.04em; margin-bottom: 6px; display: block;
  }
  #dataset-select {
    width: 100%; padding: 11px 34px 11px 13px; margin-bottom: 12px;
    border-radius: 12px; border: 1px solid var(--line); background: var(--surface);
    font-family: var(--font-body); font-size: 13.5px; font-weight: 600; color: var(--ink);
    appearance: none; -webkit-appearance: none;
    background-image: linear-gradient(45deg, transparent 50%, var(--ink-muted) 50%), linear-gradient(135deg, var(--ink-muted) 50%, transparent 50%);
    background-position: calc(100% - 18px) calc(50% - 3px), calc(100% - 13px) calc(50% - 3px);
    background-size: 5px 5px, 5px 5px; background-repeat: no-repeat;
    cursor: pointer;
  }
  #dataset-select:focus-visible { outline: 2px solid var(--brand); outline-offset: 1px; }
  #seat-type-select {
    width: 100%; padding: 11px 34px 11px 13px; margin-bottom: 6px;
    border-radius: 12px; border: 1px solid var(--line); background: var(--surface);
    font-family: var(--font-body); font-size: 13.5px; font-weight: 600; color: var(--ink);
    appearance: none; -webkit-appearance: none;
    background-image: linear-gradient(45deg, transparent 50%, var(--ink-muted) 50%), linear-gradient(135deg, var(--ink-muted) 50%, transparent 50%);
    background-position: calc(100% - 18px) calc(50% - 3px), calc(100% - 13px) calc(50% - 3px);
    background-size: 5px 5px, 5px 5px; background-repeat: no-repeat;
    cursor: pointer;
  }
  #seat-type-select:focus-visible { outline: 2px solid var(--brand); outline-offset: 1px; }
  .seat-type-note { font-size: 11.5px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 14px; }
  .seat-type-note strong { color: var(--ink); }
  .predictor-result-card {
    background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--accent);
    border-radius: 11px; padding: 11px 13px; margin-bottom: 8px; font-size: 13.5px;
    box-shadow: 0 4px 14px -12px hsl(var(--shadow-color) / 0.5);
  }
  .predictor-result-card .name { font-weight: 600; margin-bottom: 3px; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
  .predictor-result-card .ranks { font-size: 12px; color: var(--ink-muted); font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
  .basis-badge { font-family: var(--font-body); font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; padding: 2px 7px; border-radius: 999px; }
  .basis-badge.reported { background: var(--success-tint); color: var(--success); }
  .basis-badge.calculated { background: var(--warn-tint); color: var(--warn); }
</style>

<header class="top">
  <div class="brand-row">
    <div class="brand-mark">
      <svg viewBox="0 0 40 40" aria-hidden="true">
        <defs>
          <linearGradient id="npShieldFill" x1="6" y1="3" x2="34" y2="37" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="#28497f"/>
            <stop offset="1" stop-color="#0c1f3d"/>
          </linearGradient>
        </defs>
        <!-- Credential shield -- a medical cross (what this tracks) rising
             into a bar chart (rank climbing through rounds toward a seat),
             on a crest instead of a generic seal. -->
        <path d="M20 3.2 L33.5 8 V18.5 C33.5 28 27 34.5 20 37.2 C13 34.5 6.5 28 6.5 18.5 V8 Z" fill="url(#npShieldFill)"/>
        <path d="M20 3.2 L33.5 8 V18.5 C33.5 28 27 34.5 20 37.2 C13 34.5 6.5 28 6.5 18.5 V8 Z" fill="none" stroke="#dcae63" stroke-width="1.3"/>
        <path d="M20 6.6 L30.6 10.3 V18.4 C30.6 26.2 25.3 31.6 20 33.9 C14.7 31.6 9.4 26.2 9.4 18.4 V10.3 Z" fill="none" stroke="#f4dfb0" stroke-opacity="0.3" stroke-width="0.7"/>
        <rect x="18.8" y="9.4" width="2.4" height="9" rx="1.1" fill="#f4dfb0"/>
        <rect x="15.5" y="12.7" width="9" height="2.4" rx="1.1" fill="#f4dfb0"/>
        <rect x="11.8" y="25" width="3.6" height="5.4" rx="1" fill="#dcae63"/>
        <rect x="18.2" y="21" width="3.6" height="9.4" rx="1" fill="#dcae63"/>
        <rect x="24.6" y="17" width="3.6" height="13.4" rx="1" fill="#e8c37e"/>
        <path d="M10.3 30.9h19.4" stroke="#dcae63" stroke-opacity="0.55" stroke-width="0.9" stroke-linecap="round"/>
      </svg>
    </div>
    <h1>NEET-PG Help</h1>
    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode">
      <svg id="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
    </button>
  </div>
  <p>Free NEET PG College Predictor &amp; Branch Predictor &middot; live MCC counselling tracker &middot; independent, not official</p>
</header>
<div class="disclaimer-banner">
  Independent, free information service &mdash; not MCC, NBEMS or any government authority, and not officially affiliated with them. Verify against the official source link on every item.
</div>

<main>

  <!-- DASHBOARD -->
  <section id="view-dashboard" class="view active">
    <div class="hero-card">
      <div class="hero-eyebrow">Current cycle</div>
      <div class="hero-cycle" id="dash-cycle">&mdash;</div>
      <div class="hero-rounds" id="dash-rounds"></div>
    </div>

    <div class="stat-grid">
      <div class="stat-card">
        <div class="label">Documents tracked</div>
        <div class="value" id="dash-doc-count">&mdash;</div>
      </div>
      <div class="stat-card">
        <div class="label">Sources monitored</div>
        <div class="value" id="dash-source-count">&mdash;</div>
      </div>
      <div class="stat-card wide">
        <div class="label">Timestamps &mdash; these are different</div>
        <div class="timestamp-row"><span>Last checked (by us)</span><strong id="dash-last-checked">&mdash;</strong></div>
        <div class="timestamp-row"><span>Last official update (by MCC)</span><strong id="dash-last-official">&mdash;</strong></div>
      </div>
    </div>

    <div class="section-title">Latest release</div>
    <div id="dash-latest-list"></div>
    <button class="text-link-btn" data-view="updates" style="margin-top:4px;">See all updates &rarr;</button>
  </section>

  <!-- LATEST UPDATES -->
  <section id="view-updates" class="view">
    <input class="search-box" id="updates-search" placeholder="Search updates by title&hellip;">
    <div id="updates-list"></div>
  </section>

  <!-- ARCHIVE -->
  <section id="view-archive" class="view">
    <input class="search-box" id="archive-search" placeholder="Search the document archive&hellip;">
    <div class="filter-row" id="archive-filters"></div>
    <div id="archive-list"></div>
  </section>

  <!-- BLOG -->
  <section id="view-blog" class="view">
    <div id="blog-list">__BLOG_LIST_HTML__</div>
  </section>

  <!-- PREDICTOR (DEMO) -->
  <section id="view-predictor" class="view">
    <label class="predictor-dataset-label" for="dataset-select">Data source</label>
    <select id="dataset-select">
__DATASET_OPTIONS__
    </select>

    <div class="predictor-warning" id="real-data-warning">
      <strong id="real-data-warning-title"></strong>
      <span id="real-data-warning-body"></span>
    </div>
    <div class="predictor-warning" id="estimate2025-warning" style="display:none">
      <strong>Estimate only &mdash; not MCC data</strong>
      These 2025 numbers come from third-party exam-prep websites, not MCC's own results. Real counselling can vary significantly. Use this only as a rough starting point, never as a guarantee.
    </div>

    <label class="predictor-dataset-label" for="seat-type-select">Seats to include</label>
    <select id="seat-type-select">
      <option value="government">Government seats only</option>
      <option value="all">All seats (govt + private/deemed + unverified)</option>
    </select>
    <p class="seat-type-note" id="seat-type-note"></p>

    <div class="predictor-mode-toggle">
      <button data-mode="branch" class="active">Branch Predictor</button>
      <button data-mode="college">College Predictor</button>
    </div>

    <div class="predictor-form" id="branch-form">
      <label for="branch-rank">Your NEET-PG rank</label>
      <input type="number" id="branch-rank" placeholder="e.g. 12000" min="1">
      <label for="branch-category">Category</label>
      <select id="branch-category">
        <option value="Open">Open / UR</option>
        <option value="OBC">OBC</option>
        <option value="EWS">EWS</option>
        <option value="SC">SC</option>
        <option value="ST">ST</option>
      </select>
      <div id="branch-round-wrap">
        <label for="branch-round">Round</label>
        <select id="branch-round">
          <option value="R1">Round 1</option>
          <option value="R2">Round 2</option>
        </select>
      </div>
      <button id="branch-predict-btn">See possible branches</button>
    </div>

    <div class="predictor-form" id="college-form" style="display:none">
      <label for="college-specialty">Specialty</label>
      <select id="college-specialty"></select>
      <label for="college-category">Category</label>
      <select id="college-category">
        <option value="Open">Open / UR</option>
        <option value="OBC">OBC</option>
        <option value="EWS">EWS</option>
        <option value="SC">SC</option>
        <option value="ST">ST</option>
      </select>
      <label for="college-rank">Your NEET-PG rank</label>
      <input type="number" id="college-rank" placeholder="e.g. 500" min="1">
      <button id="college-predict-btn">See possible colleges</button>
    </div>
    <div class="predictor-warning" id="college-calculated-warning" style="display:none; margin-bottom: 0;">
      <strong>Calculated, not reported</strong>
      No source publishes college-level ranks for this category. These are <em>calculated</em> by scaling each college's real Open-category rank by the category gap seen at the specialty level &mdash; not a number any source actually reported. Treat it as a rough order of magnitude only.
    </div>

    <div id="predictor-results"></div>
  </section>

  <!-- ABOUT -->
  <section id="view-about" class="view">
    <div class="about-block">
      <h3>What this is</h3>
      <p>NEET-PG Help is a free, independent tracker of official NEET-PG counselling documents published by the Medical Counselling Committee (MCC). It is built and maintained independently and is <strong>not</strong> MCC, NBEMS, or any government body, and has no official affiliation with them.</p>
      <h3>Where the data comes from</h3>
      <p>Every item you see here links back to the exact official PDF or notice it came from, on MCC's own website (mcc.nic.in). We don't retype or reinterpret official numbers &mdash; we track when a document appears and classify what kind of document it is, so you can go straight to the source.</p>
      <h3>What &ldquo;confidence&rdquo; means</h3>
      <p>Document type and date are guessed automatically from the title MCC gives each file. Most guesses are reliable, but some titles are ambiguous &mdash; those are marked <span class="tag low-confidence">uncertain</span> so you know to check the source PDF yourself rather than trusting the label blindly.</p>
      <h3>What this is not (yet)</h3>
      <p>Seat matrices, allotment results and cutoffs that require reading inside each PDF are added as they're validated (see the Predictor tab for what's real so far). No login is required and no personal data is collected.</p>
      <h3>About the Predictor tab</h3>
      <p>The Predictor's dropdown lets you pick between real MCC rounds we've extracted and validated (clearly labeled "Real MCC"), and a third-party estimate dataset which is not official MCC data and exists only to test the idea until enough verified rounds cover every specialty.</p>
      <h3>From the blog</h3>
      __ABOUT_BLOG_LINKS_HTML__
      <p class="provenance-line">Data snapshot generated: <span id="about-generated-at"></span></p>
      <hr>
      <p class="about-crosslinks">
        <button class="text-link-btn" data-view="contact">Contact us</button>
        <span aria-hidden="true">&middot;</span>
        <button class="text-link-btn" data-view="privacy">Privacy policy</button>
      </p>
    </div>
  </section>

  <!-- CONTACT -->
  <section id="view-contact" class="view">
    <div class="about-block">
      <h3>Contact us</h3>
      <p>Spotted an error, a missing document, or have feedback? Write to us at <a href="mailto:helpneetpg@gmail.com">helpneetpg@gmail.com</a>. We read every message &mdash; as a free, independently-run service we may not always be able to reply quickly, but corrections and missed documents are the fastest way to help every other candidate using this site too.</p>
      <p>For press, partnership or data-source enquiries, the same address reaches us: <a href="mailto:helpneetpg@gmail.com">helpneetpg@gmail.com</a>.</p>
      <p class="provenance-line">neetpghelp.com &middot; helpneetpg@gmail.com</p>
      <hr>
      <p class="about-crosslinks">
        <button class="text-link-btn" data-view="about">About</button>
        <span aria-hidden="true">&middot;</span>
        <button class="text-link-btn" data-view="privacy">Privacy policy</button>
      </p>
    </div>
  </section>

  <!-- PRIVACY POLICY -->
  <section id="view-privacy" class="view">
    <div class="about-block">
      <h3>Privacy policy</h3>
      <p><strong>No account, no personal data required.</strong> You can use every feature of NEET-PG Help &mdash; the dashboard, updates, archive and predictor &mdash; without signing up or giving us your name, rank, phone number or email.</p>
      <p><strong>What we store locally.</strong> Your choice of light or dark theme is saved directly in your browser (via <code>localStorage</code>) so it's remembered next time you visit. This stays on your device; it is never sent to us or to anyone else.</p>
      <p><strong>Official source data.</strong> Every document, date, seat and rank figure shown here is already public information published by MCC. We link back to the original MCC source on every item; we don't collect or store any candidate-identifying data beyond what MCC has itself made public.</p>
      <p><strong>Advertising.</strong> To keep this site free, we intend to show ads through Google AdSense. Google and its partners may use cookies to serve ads based on your visits here and other sites; you can control ad personalisation in your Google account settings. We will not place ads on top of official notices or in ways designed to cause accidental clicks.</p>
      <p><strong>Analytics.</strong> We may use basic, privacy-respecting analytics (e.g. aggregate page-view counts) to understand which pages are useful. This does not identify you personally.</p>
      <p><strong>Changes.</strong> If this policy changes meaningfully, we'll update this page and the date below.</p>
      <p>Questions or requests about your privacy: <a href="mailto:helpneetpg@gmail.com">helpneetpg@gmail.com</a>.</p>
      <p class="provenance-line">neetpghelp.com &middot; helpneetpg@gmail.com &middot; Privacy policy last updated 21 Sept 2026</p>
      <hr>
      <p class="about-crosslinks">
        <button class="text-link-btn" data-view="about">About</button>
        <span aria-hidden="true">&middot;</span>
        <button class="text-link-btn" data-view="contact">Contact us</button>
      </p>
    </div>
  </section>

</main>

<footer class="site-footer">
  <div class="footer-links">
    <button class="text-link-btn" data-view="about">About</button>
    <button class="text-link-btn" data-view="blog">Blog</button>
    <button class="text-link-btn" data-view="contact">Contact us</button>
    <button class="text-link-btn" data-view="privacy">Privacy policy</button>
  </div>
  <div class="footer-meta">NEET-PG Help &middot; neetpghelp.com &middot; independent &amp; free &middot; not affiliated with MCC or NBEMS</div>
</footer>

<nav class="bottom">
  <button data-view="dashboard" class="active">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10l9-7 9 7v9a2 2 0 01-2 2H5a2 2 0 01-2-2v-9z"/><path d="M9 21V12h6v9"/></svg>
    Dashboard
  </button>
  <button data-view="updates">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 00-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 01-3.4 0"/></svg>
    Updates
  </button>
  <button data-view="archive">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M3 7l2.5-4h13L21 7"/><path d="M9 12h6"/></svg>
    Archive
  </button>
  <button data-view="predictor">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/></svg>
    Predictor
  </button>
  <button data-view="about">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.5" r="0.6" fill="currentColor"/></svg>
    About
  </button>
</nav>

<script>
// engine/export_json.py regenerates data.json after every monitor run.
const DATA = __DATA_JSON__;
// Third-party estimate data for the Predictor tab ONLY -- see
// engine/predictor_data.py for full provenance notes. Never merged with
// DATA above, which holds only officially-sourced MCC documents.
const PREDICTOR = __PREDICTOR_JSON__;
// Every real MCC dataset listed in site/datasets_manifest.json, keyed by
// id. Each one comes from a build_*_closing_ranks.py script run against
// an actual MCC PDF -- either uploaded by hand or downloaded and
// extracted automatically by engine/extract_pipeline.py once validation
// passes. New rounds appear here automatically; nothing in this script
// needs to change when one is added. See engine/dataset_registry.py.
const REAL_DATASETS_RAW = __REAL_DATASETS_JSON__;
// Government/Private classification for the Predictor's "Government seats
// only" filter -- see engine/college_type.py for how and why this exists
// and how it was built. Keyed by normalized (whitespace-collapsed,
// lowercased) institute name; an institute NOT in this map is treated as
// "unverified" and excluded from the Government view, never assumed to be
// government -- see that file's docstring for the reasoning.
const COLLEGE_TYPE = __COLLEGE_TYPE_JSON__;

const DOC_TYPE_LABELS = {
  final_result: "Final Result", provisional_result: "Provisional Result", revised_result: "Revised Result",
  result: "Result", vacancy: "Vacancy List", seat_matrix: "Seat Matrix", seat_addition_deletion: "Seat Change Notice",
  admitted_candidates: "Admitted Candidates List", counselling_schedule: "Counselling Schedule",
  choice_filling_notice: "Choice Filling Notice", refund_notice: "Refund Notice", nri_notice: "NRI Notice",
  public_notice: "Public Notice", news_event: "News / Guideline", unclassified: "Uncategorized",
};

function fmtDate(iso) {
  if (!iso) return "Unknown date";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}
function fmtDateTime(iso) {
  if (!iso) return "Never";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
function docTypeLabel(t) { return DOC_TYPE_LABELS[t] || t; }
function tagsForDoc(d) {
  let tags = `<span class="tag">${docTypeLabel(d.doc_type)}</span>`;
  if (d.round_label) tags += `<span class="tag round">${d.round_label}</span>`;
  if (d.pub_date_confidence === "low" || d.doc_type_confidence < 0.5) tags += `<span class="tag low-confidence">uncertain</span>`;
  return tags;
}
function docCard(d) {
  return `<div class="card"><div class="tag-row">${tagsForDoc(d)}</div>
    <div class="title"><a class="title-link" href="${d.file_url}" target="_blank" rel="noopener">${d.title}</a></div>
    <div class="meta"><span>${fmtDate(d.pub_date)} &middot; ${d.pub_date_basis === 'first_seen' ? 'date unclear, first seen' : d.pub_date_basis}</span>
    <a class="source-link" href="${d.file_url}" target="_blank" rel="noopener">Source &rarr;</a></div></div>`;
}
function changeCard(c) {
  // Show the document's own MCC publication date (what "latest" should
  // mean), not when our system happened to detect it -- see the comment in
  // engine/export_json.py on why detected_at alone is not a reliable sort
  // or display value here.
  const dateLabel = c.pub_date
    ? `${fmtDate(c.pub_date)} &middot; ${c.pub_date_basis === 'first_seen' ? 'date unclear, first seen' : c.pub_date_basis}`
    : `Detected ${fmtDateTime(c.detected_at)}`;
  return `<div class="card"><div class="tag-row">${tagsForDoc(c)}</div>
    <div class="title"><a class="title-link" href="${c.file_url}" target="_blank" rel="noopener">${c.title}</a></div>
    <div class="meta"><span>${dateLabel}</span>
    <a class="source-link" href="${c.file_url}" target="_blank" rel="noopener">Source &rarr;</a></div></div>`;
}

// Blog post cards are rendered server-side by engine/build_blog.py into the
// blog-list div's placeholder above -- plain <a href> links to real,
// separately-indexable pages under site/blog/, not JS-injected content, so
// they're crawlable without executing JavaScript at all.

function renderDashboard() {
  const db = DATA.dashboard;
  document.getElementById("dash-cycle").textContent = "PG Counselling 2026";
  document.getElementById("dash-rounds").innerHTML = db.rounds_seen.length
    ? db.rounds_seen.map(r => `<span class="hero-round-pill">${r}</span>`).join("")
    : `<span class="hero-round-pill">No rounds yet</span>`;
  document.getElementById("dash-doc-count").textContent = db.total_documents;
  document.getElementById("dash-source-count").textContent = db.sources_monitored;
  document.getElementById("dash-last-checked").textContent = fmtDateTime(db.last_checked);
  document.getElementById("dash-last-official").textContent = fmtDate(db.last_official_update);
  // The dashboard shows only the single most recent MCC release -- the full
  // history lives in the Latest Updates tab. DATA.changes is already sorted
  // newest-official-date-first (see engine/export_json.py), so this is just
  // the first item.
  const latest = DATA.changes.slice(0, 1);
  document.getElementById("dash-latest-list").innerHTML = latest.length ? latest.map(changeCard).join("") : `<div class="empty-state">No updates yet.</div>`;
}
function renderUpdates(filterText) {
  filterText = (filterText || "").toLowerCase();
  const items = DATA.changes.filter(c => c.title.toLowerCase().includes(filterText));
  document.getElementById("updates-list").innerHTML = items.length ? items.map(changeCard).join("") : `<div class="empty-state">No updates match &ldquo;${filterText}&rdquo;.</div>`;
}
let archiveTypeFilter = "all";
function renderArchiveFilters() {
  const types = ["all", ...new Set(DATA.documents.map(d => d.doc_type))];
  const el = document.getElementById("archive-filters");
  el.innerHTML = types.map(t => `<button class="filter-chip ${t === archiveTypeFilter ? 'active' : ''}" data-type="${t}">${t === 'all' ? 'All' : docTypeLabel(t)}</button>`).join("");
  el.querySelectorAll(".filter-chip").forEach(btn => {
    btn.addEventListener("click", () => { archiveTypeFilter = btn.dataset.type; renderArchiveFilters(); renderArchive(document.getElementById("archive-search").value); });
  });
}
function renderArchive(filterText) {
  filterText = (filterText || "").toLowerCase();
  let items = DATA.documents.filter(d => d.title.toLowerCase().includes(filterText));
  if (archiveTypeFilter !== "all") items = items.filter(d => d.doc_type === archiveTypeFilter);
  document.getElementById("archive-list").innerHTML = items.length ? items.map(docCard).join("") : `<div class="empty-state">No documents match.</div>`;
}
function switchView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById("view-" + name).classList.add("active");
  document.querySelectorAll("nav.bottom button").forEach(b => b.classList.toggle("active", b.dataset.view === name));
  window.scrollTo(0, 0);
}
document.querySelectorAll("nav.bottom button").forEach(btn => btn.addEventListener("click", () => switchView(btn.dataset.view)));
document.getElementById("updates-search").addEventListener("input", (e) => renderUpdates(e.target.value));
document.getElementById("archive-search").addEventListener("input", (e) => renderArchive(e.target.value));
document.getElementById("about-generated-at").textContent = fmtDateTime(DATA.generated_at);

// ---- theme toggle (manual override on top of system preference) ----
const SUN = '<circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.2M12 19.8V22M4.9 4.9l1.5 1.5M17.6 17.6l1.5 1.5M2 12h2.2M19.8 12H22M4.9 19.1l1.5-1.5M17.6 6.4l1.5-1.5"/>';
const MOON = '<path d="M20 14.5A8.5 8.5 0 019.5 4a8.5 8.5 0 1010.5 10.5z"/>';
function currentTheme() {
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit) return explicit;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function paintThemeIcon() {
  document.getElementById("theme-icon").innerHTML = currentTheme() === "dark" ? SUN : MOON;
}
function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try { localStorage.setItem("neetpg-theme", theme); } catch (e) {}
  paintThemeIcon();
}
(function initTheme() {
  let saved = null;
  try { saved = localStorage.getItem("neetpg-theme"); } catch (e) {}
  if (saved === "dark" || saved === "light") document.documentElement.setAttribute("data-theme", saved);
  paintThemeIcon();
})();
document.getElementById("theme-toggle").addEventListener("click", () => setTheme(currentTheme() === "dark" ? "light" : "dark"));

// ---- Predictor: every real MCC dataset in the manifest, plus one third-party estimate ----
// "estimate2025" is the only non-official dataset -- third-party-sourced,
// see engine/predictor_data.py. Never merged with the real datasets.
const REAL_DATASETS = {};
Object.keys(REAL_DATASETS_RAW).forEach(id => {
  const d = REAL_DATASETS_RAW[id];
  REAL_DATASETS[id] = {
    label: d.label,
    roundNote: d.roundNote,
    warningTitle: d.warningTitle,
    warningBody: d.warningBody,
    raw: { provenance: d.provenance, methodology: d.methodology },
    specialties: d.specialty_category,
    collegeRows: d.college_specialty_category,
    specialtyNames: [...new Set(d.college_specialty_category.map(r => r.specialty))].sort(),
  };
});
// Default to the newest real round in the manifest (site/datasets_manifest.json order).
let currentDataset = "__DEFAULT_DATASET_ID__";

const ESTIMATE2025_SPECIALTY_NAMES = Object.keys(PREDICTOR.colleges_by_specialty);

// ---- Government-seats-only filter (see engine/college_type.py) ----
// Defaults to "government" so the calculator shows government medical
// college / hospital seats unless the person explicitly asks to see
// everything -- this is what keeps a handful of private/deemed colleges
// and a flood of small private DNB/Diploma hospitals from inflating the
// seat counts and closing ranks shown by default.
let seatTypeFilter = "government";
function normInstitute(name) { return (name || "").replace(/\s+/g, " ").trim().toLowerCase(); }
function collegeType(name) { return COLLEGE_TYPE[normInstitute(name)] || "unverified"; }
function passesSeatTypeFilter(name) { return seatTypeFilter === "all" || collegeType(name) === "government"; }

// Real per-round datasets store one row per institute+specialty+category
// (ds.collegeRows) plus a precomputed specialty-level rollup across EVERY
// institute (ds.specialties) -- that rollup mixes government, private and
// unverified-ownership institutes together, so under the Government filter
// it has to be recomputed from just the filtered rows rather than reused.
function filteredCollegeRows(ds) {
  return ds.collegeRows.filter(r => passesSeatTypeFilter(r.institute));
}
function recomputeSpecialties(rows) {
  const byKey = new Map();
  rows.forEach(r => {
    const key = r.specialty + "\u0000" + r.category;
    let agg = byKey.get(key);
    if (!agg) { agg = { specialty: r.specialty, category: r.category, opening_rank: r.opening_rank, closing_rank: r.closing_rank, seats_counted: 0, institutes: new Set() }; byKey.set(key, agg); }
    agg.opening_rank = Math.min(agg.opening_rank, r.opening_rank);
    agg.closing_rank = Math.max(agg.closing_rank, r.closing_rank);
    agg.seats_counted += r.seats_counted;
    agg.institutes.add(r.institute);
  });
  return Array.from(byKey.values()).map(a => ({
    specialty: a.specialty, category: a.category, opening_rank: a.opening_rank, closing_rank: a.closing_rank,
    seats_counted: a.seats_counted, institutes_counted: a.institutes.size,
  }));
}
function updateSeatTypeNote() {
  const note = document.getElementById("seat-type-note");
  const ds = REAL_DATASETS[currentDataset];
  if (!ds) {
    note.innerHTML = seatTypeFilter === "government"
      ? `This third-party estimate dataset only lists colleges directly (no per-branch ownership breakdown), so the Government filter applies to the College Predictor here, not the Branch Predictor.`
      : ``;
    return;
  }
  const total = ds.collegeRows.length, totalSeats = ds.collegeRows.reduce((s, r) => s + r.seats_counted, 0);
  const kept = filteredCollegeRows(ds);
  const keptSeats = kept.reduce((s, r) => s + r.seats_counted, 0);
  if (seatTypeFilter === "government") {
    const excluded = total - kept.length, excludedSeats = totalSeats - keptSeats;
    note.innerHTML = `Showing <strong>${kept.length.toLocaleString('en-IN')} government-college seat-rows</strong> (${keptSeats.toLocaleString('en-IN')} seats) in ${ds.roundNote}. ${excluded.toLocaleString('en-IN')} rows (${excludedSeats.toLocaleString('en-IN')} seats) at private/deemed colleges or hospitals with unverified ownership are excluded -- switch to "All seats" to include them.`;
  } else {
    note.innerHTML = `Showing all ${total.toLocaleString('en-IN')} seat-rows (${totalSeats.toLocaleString('en-IN')} seats) in ${ds.roundNote}, including private/deemed colleges and DNB/Diploma hospitals of unverified ownership.`;
  }
}

function populateCollegeSpecialtyOptions() {
  const select = document.getElementById("college-specialty");
  const names = REAL_DATASETS[currentDataset] ? REAL_DATASETS[currentDataset].specialtyNames : ESTIMATE2025_SPECIALTY_NAMES;
  select.innerHTML = names.map(n => `<option value="${n}">${n}</option>`).join("");
}

function updateDatasetWarning() {
  const ds = REAL_DATASETS[currentDataset];
  document.getElementById("real-data-warning").style.display = ds ? "block" : "none";
  document.getElementById("estimate2025-warning").style.display = ds ? "none" : "block";
  if (ds) {
    document.getElementById("real-data-warning-title").textContent = ds.warningTitle;
    document.getElementById("real-data-warning-body").innerHTML = ds.warningBody;
  }
  document.getElementById("branch-round-wrap").style.display = ds ? "none" : "block";
}

function initPredictor() {
  populateCollegeSpecialtyOptions();
  updateDatasetWarning();
  updateSeatTypeNote();

  document.getElementById("dataset-select").value = currentDataset;
  document.getElementById("dataset-select").addEventListener("change", (e) => {
    currentDataset = e.target.value;
    updateDatasetWarning();
    populateCollegeSpecialtyOptions();
    updateCalculatedWarning();
    updateSeatTypeNote();
    document.getElementById("predictor-results").innerHTML = "";
  });

  document.getElementById("seat-type-select").value = seatTypeFilter;
  document.getElementById("seat-type-select").addEventListener("change", (e) => {
    seatTypeFilter = e.target.value;
    updateSeatTypeNote();
    document.getElementById("predictor-results").innerHTML = "";
  });

  document.querySelectorAll(".predictor-mode-toggle button").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".predictor-mode-toggle button").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const isBranch = btn.dataset.mode === "branch";
      document.getElementById("branch-form").style.display = isBranch ? "block" : "none";
      document.getElementById("college-form").style.display = isBranch ? "none" : "block";
      document.getElementById("college-calculated-warning").style.display = "none";
      document.getElementById("predictor-results").innerHTML = "";
    });
  });

  document.getElementById("branch-predict-btn").addEventListener("click", () => {
    const rank = parseInt(document.getElementById("branch-rank").value, 10);
    const category = document.getElementById("branch-category").value;
    const resultsEl = document.getElementById("predictor-results");
    if (!rank || rank < 1) { resultsEl.innerHTML = `<div class="empty-state">Enter your rank first.</div>`; return; }

    const ds = REAL_DATASETS[currentDataset];
    if (ds) {
      // Recomputed from the seat-type-filtered institute rows, not the
      // dataset's own precomputed rollup -- see recomputeSpecialties().
      const specialties = recomputeSpecialties(filteredCollegeRows(ds));
      const withData = specialties.filter(s => s.category === category);
      const matches = withData.filter(s => s.closing_rank >= rank).sort((a, b) => a.closing_rank - b.closing_rank);
      if (matches.length === 0) {
        resultsEl.innerHTML = `<div class="empty-state">No specialty's ${ds.roundNote} closing rank for ${category} reached rank ${rank.toLocaleString('en-IN')} in this data${seatTypeFilter === "government" ? " (government seats only)" : ""}.</div>`;
        return;
      }
      resultsEl.innerHTML = matches.map(s => `<div class="predictor-result-card"><div class="name">${s.specialty}<span class="basis-badge reported">Reported</span></div>
        <div class="ranks">${category} closing rank (${ds.roundNote}): <strong>${s.closing_rank.toLocaleString('en-IN')}</strong> &middot; ${s.institutes_counted} institutes, ${s.seats_counted} seats counted</div></div>`).join("");
      return;
    }

    const round = document.getElementById("branch-round").value;
    const roundLabel = round === "R1" ? "Round 1" : "Round 2";
    const withData = PREDICTOR.specialties.filter(s => s.categories[category] && s.categories[category][round] !== null);
    const matches = withData.filter(s => s.categories[category][round] >= rank).sort((a, b) => a.categories[category][round] - b.categories[category][round]);
    const noCategoryData = PREDICTOR.specialties.length - withData.length;
    if (matches.length === 0) {
      resultsEl.innerHTML = `<div class="empty-state">No specialty's ${roundLabel} (2025) closing rank for ${category} reached rank ${rank.toLocaleString('en-IN')} in this dataset.</div>`;
      return;
    }
    resultsEl.innerHTML = matches.map(s => `<div class="predictor-result-card"><div class="name">${s.specialty}<span class="basis-badge reported">Reported</span></div>
      <div class="ranks">${category} closing rank (${roundLabel}, 2025): <strong>${s.categories[category][round].toLocaleString('en-IN')}</strong></div></div>`).join("") +
      (noCategoryData ? `<div class="empty-state">${noCategoryData} more specialties had no ${category} / ${roundLabel} data in these sources.</div>` : "");
  });

  function updateCalculatedWarning() {
    const category = document.getElementById("college-category").value;
    const show = !REAL_DATASETS[currentDataset] && category !== "Open";
    document.getElementById("college-calculated-warning").style.display = show ? "block" : "none";
  }
  document.getElementById("college-category").addEventListener("change", updateCalculatedWarning);
  updateCalculatedWarning();

  document.getElementById("college-predict-btn").addEventListener("click", () => {
    const rank = parseInt(document.getElementById("college-rank").value, 10);
    const specialty = document.getElementById("college-specialty").value;
    const category = document.getElementById("college-category").value;
    const resultsEl = document.getElementById("predictor-results");
    if (!rank || rank < 1) { resultsEl.innerHTML = `<div class="empty-state">Enter your rank first.</div>`; return; }

    const ds = REAL_DATASETS[currentDataset];
    if (ds) {
      const allForCategory = filteredCollegeRows(ds).filter(r => r.specialty === specialty && r.category === category);
      const colleges = allForCategory.filter(c => c.closing_rank >= rank).sort((a, b) => a.closing_rank - b.closing_rank);
      const seatTypeSuffix = seatTypeFilter === "government" ? " (government seats only)" : "";
      if (allForCategory.length === 0) {
        resultsEl.innerHTML = `<div class="empty-state">No ${category} seats recorded for ${specialty} in this ${ds.roundNote} data${seatTypeSuffix}.</div>`;
        return;
      }
      if (colleges.length === 0) {
        resultsEl.innerHTML = `<div class="empty-state">None of the ${allForCategory.length} colleges with ${specialty} (${category}) data${seatTypeSuffix} closed at or beyond rank ${rank.toLocaleString('en-IN')} in ${ds.roundNote}.</div>`;
        return;
      }
      resultsEl.innerHTML = colleges.map(c => `<div class="predictor-result-card"><div class="name">${c.institute}<span class="basis-badge reported">Reported</span></div>
        <div class="ranks">Opening rank: ${c.opening_rank.toLocaleString('en-IN')} &middot; Closing rank: <strong>${c.closing_rank.toLocaleString('en-IN')}</strong> (${category}, ${ds.roundNote}) &middot; ${c.seats_counted} seat(s)</div></div>`).join("");
      return;
    }

    const allForCategoryRaw = (PREDICTOR.colleges_by_specialty[specialty] || {})[category] || [];
    const allForCategory = allForCategoryRaw.filter(c => passesSeatTypeFilter(c.college));
    const colleges = allForCategory.filter(c => c.closing_rank >= rank).sort((a, b) => a.closing_rank - b.closing_rank);
    if (allForCategory.length === 0) {
      resultsEl.innerHTML = `<div class="empty-state">No ${category} data available for ${specialty} &mdash; the specialty-level source has no ${category} figure to calculate from.</div>`;
      return;
    }
    if (colleges.length === 0) {
      resultsEl.innerHTML = `<div class="empty-state">None of the ${allForCategory.length} colleges we have data for in ${specialty} (${category}) closed at or beyond rank ${rank.toLocaleString('en-IN')}. This list is not exhaustive.</div>`;
      return;
    }
    const badge = category === "Open" ? '<span class="basis-badge reported">Reported</span>' : '<span class="basis-badge calculated">Calculated</span>';
    resultsEl.innerHTML = colleges.map(c => `<div class="predictor-result-card"><div class="name">${c.college}${badge}</div>
      <div class="ranks">Opening rank: ${c.opening_rank.toLocaleString('en-IN')} &middot; Closing rank: <strong>${c.closing_rank.toLocaleString('en-IN')}</strong> (${category}, 2025)</div></div>`).join("");
  });
}

renderDashboard();
renderUpdates("");
renderArchiveFilters();
renderArchive("");
initPredictor();
document.querySelectorAll(".text-link-btn[data-view]").forEach(btn => btn.addEventListener("click", () => switchView(btn.dataset.view)));
</script>
"""

def main() -> None:
    """Reads the current data.json / predictor_data.json / dataset manifest
    fresh from disk every call (so calling this from run_scheduled.py right
    after export_json.main() picks up the just-updated data), builds both
    outputs, and writes them. Returns nothing; prints a one-line summary."""
    build_blog.main()  # regenerate site/blog/*.html before embedding its card list below

    data = json.loads((ROOT / "site" / "data.json").read_text())
    data_json_str = json.dumps(data)
    predictor_data = json.loads((ROOT / "site" / "predictor_data.json").read_text())
    predictor_json_str = json.dumps(predictor_data)

    dataset_ids = dataset_registry.load_manifest()
    real_datasets = {i: dataset_registry.load_dataset(i) for i in dataset_ids}
    real_datasets_json_str = json.dumps(real_datasets)
    default_dataset_id = dataset_ids[0] if dataset_ids else "estimate2025"

    # Government/Private classification for the Predictor's "Government
    # seats only" filter -- see engine/college_type.py for how and why.
    # Built once here (institute name -> "government"/"private") from every
    # institute name that appears anywhere in the real datasets or the
    # third-party estimate dataset; a name that doesn't appear in this map
    # is treated by the site as "unverified" (never assumed government).
    all_institute_names = set()
    for ds in real_datasets.values():
        for row in ds.get("college_specialty_category", []):
            all_institute_names.add(row["institute"])
    for rows in predictor_data.get("colleges_by_specialty", {}).values():
        for cat_rows in rows.values():
            for row in cat_rows:
                all_institute_names.add(row["college"])
    college_type_map = {
        college_type._norm(name): t
        for name in all_institute_names
        if (t := college_type.classify(name)) != "unverified"
    }
    college_type_json_str = json.dumps(college_type_map)

    dataset_options_html = "\n".join(
        f'      <option value="{i}">{real_datasets[i]["label"]}</option>' for i in dataset_ids
    )
    if dataset_options_html:
        dataset_options_html += "\n"
    dataset_options_html += '      <option value="estimate2025">2025 Estimate (Third-party)</option>'

    body_html = (
        TEMPLATE.replace("__DATASET_OPTIONS__", dataset_options_html)
        .replace("__BLOG_LIST_HTML__", build_blog.list_cards_html())
        .replace("__ABOUT_BLOG_LINKS_HTML__", build_blog.about_links_html())
        .replace("__DATA_JSON__", data_json_str)
        .replace("__PREDICTOR_JSON__", predictor_json_str)
        .replace("__REAL_DATASETS_JSON__", real_datasets_json_str)
        .replace("__COLLEGE_TYPE_JSON__", college_type_json_str)
        .replace("__DEFAULT_DATASET_ID__", default_dataset_id)
    )

    # The Artifact tool (Claude's preview host) wraps CONTENT-only HTML in
    # its own <!DOCTYPE>/<html>/<head>/<body> automatically. The real
    # deployment (GitHub Pages) has no such wrapper -- it serves whatever
    # file you give it -- so this writes the full standalone document there.
    seo_title = "NEET PG College Predictor & Branch Predictor 2026 — Free, Real MCC Data | NEET-PG Help"
    seo_description = (
        "Free NEET PG college predictor and branch predictor built on real MCC "
        "counselling data — seat matrix, allotment results and category-wise "
        "cutoffs across every round. No signup, no paid plan. Independent, not "
        "affiliated with MCC or NBEMS."
    )
    json_ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebApplication",
      "name": "NEET-PG Help College & Branch Predictor",
      "url": "https://neetpghelp.com/",
      "applicationCategory": "EducationApplication",
      "operatingSystem": "Any (web-based)",
      "description": "Free NEET PG college predictor and branch predictor that uses real MCC counselling allotment data (Round 1, 2, 3 and Stray Vacancy) to estimate which colleges and specialties a rank/category combination could realistically reach.",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "INR"
      },
      "provider": {
        "@type": "Organization",
        "name": "NEET-PG Help",
        "url": "https://neetpghelp.com/",
        "description": "Independent, free NEET-PG counselling information service. Not affiliated with MCC, NBEMS or any government authority."
      }
    },
    {
      "@type": "WebSite",
      "name": "NEET-PG Help",
      "url": "https://neetpghelp.com/",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://neetpghelp.com/?s={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Is the NEET-PG Help college predictor free?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. The college predictor, branch predictor, cutoff explorer and seat matrix explorer are all free to use, with no signup and no paid tier."
          }
        },
        {
          "@type": "Question",
          "name": "Where does the NEET-PG closing rank and cutoff data come from?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Directly from official Medical Counselling Committee (MCC) allotment result PDFs for Round 1, Round 2, Round 3 and the Stray Vacancy Round. Every dataset links back to its official source document."
          }
        },
        {
          "@type": "Question",
          "name": "Is NEET-PG Help affiliated with MCC or NBEMS?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "No. NEET-PG Help is an independent, free information service and is not MCC, NBEMS or any government authority."
          }
        }
      ]
    }
  ]
}
</script>"""
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{seo_title}</title>
<meta name="description" content="{seo_description}">
<link rel="canonical" href="https://neetpghelp.com/">
<link rel="alternate" type="application/rss+xml" title="NEET-PG Help Blog" href="https://neetpghelp.com/blog/rss.xml">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NEET-PG Help">
<meta property="og:title" content="{seo_title}">
<meta property="og:description" content="{seo_description}">
<meta property="og:url" content="https://neetpghelp.com/">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{seo_title}">
<meta name="twitter:description" content="{seo_description}">
<meta name="theme-color" content="#0b1220">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="/android-chrome-192x192.png">
<link rel="manifest" href="/site.webmanifest">
{json_ld}
</head>
<body>
{body_html}
</body>
</html>
"""

    # site/index.html is the real, standalone deployable page -- this is
    # what GitHub Pages serves at neetpghelp.com. It is NOT what gets
    # passed to Claude's Artifact tool (which wraps CONTENT-only HTML in
    # its own <!DOCTYPE>/<html>/<head>/<body> and would double-wrap this).
    out_path = ROOT / "site" / "index.html"
    out_path.write_text(full_html, encoding="utf-8")
    print(f"Wrote {out_path} ({len(full_html)} bytes, {len(dataset_ids)} real dataset(s): {dataset_ids})")

    # For previewing inside this Claude session only: the content-only
    # fragment, written wherever CLAUDE_ARTIFACT_FRAGMENT_PATH points. Not
    # part of the repo/deployment -- silently skipped (e.g. in CI, where
    # that path doesn't exist and no one is previewing an artifact).
    fragment_path = os.environ.get("CLAUDE_ARTIFACT_FRAGMENT_PATH")
    if fragment_path:
        try:
            pathlib.Path(fragment_path).write_text(body_html, encoding="utf-8")
            print(f"Wrote {fragment_path} ({len(body_html)} bytes) for Claude Artifact preview")
        except OSError as exc:
            print(f"(skipped writing artifact fragment: {exc})")


if __name__ == "__main__":
    main()
