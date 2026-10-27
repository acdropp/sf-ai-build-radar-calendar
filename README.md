# 🔦 SF AI Event Search — Calendar + List

A self-hosted calendar + list view of the **🔦 SF AI Event Search**: a daily-refreshed,
taste-scored feed of hands-on AI builder events in the Bay Area (Luma, Meetup /
Hacker Dojo, AI Tinkerers, and off-platform hacker houses).

**Live:** [https://acdropp.github.io/sf-ai-build-radar-calendar/](https://acdropp.github.io/sf-ai-event-search-calendar/) — opens for anyone, no account.

## Status

**Built and live.** Phases 1–4 are complete and deployed, plus a large slice of the
Phase 5 extras (see `ROADMAP.md`). The site refreshes itself every morning from the
Radar digest with no manual step.

## What's here

| File | What it is |
| --- | --- |
| `index.html` | The whole app — one self-contained page (calendar + list, theming, filters, all behavior). No build step, no framework. |
| `data/events.json` | **The source of truth.** The daily sync writes it from the digest database; the page reads it. |
| `data/events.sample.json` | A hand-written sample in the same shape — the Phase-1 fallback (also embedded in `index.html` for offline/dev). |
| `scripts/build_events.py` | Deterministic transform: a dump of the digest DB → a clean, guarded `events.json`. Run by the daily sync task. |
| `og-image.png` | Social-preview card (1200×630) referenced by the OpenGraph/Twitter tags. |
| `SPEC.md` | The full as-built spec — architecture, data contract, features, pipeline, acceptance. |
| `DESIGN.md` | The design spec — typography, colour themes and rules, header layout, per-view styling. |
| `ROADMAP.md` | Phase-by-phase status (what shipped, what's declined). |
| `HANDOFF.md` | Short operator's guide — how the pipeline runs, how to make changes. |

## The shape of it (one paragraph)

A single `events.json` is the source of truth. A daily Claude scheduled task reads the
existing Radar digest's database (scrape → score 1–5 → dedupe, already running), runs
`scripts/build_events.py` to produce a clean file, and commits it to this repo. GitHub
Pages serves a static `index.html` that reads it and renders two switchable views — a
3-month synchronized calendar and a rich, collapsible scored list. Because the data is
committed into the repo and baked into what the browser downloads, the public URL opens
for **anyone, with no account** — the whole point of going self-hosted.

```
Radar digest (artifact DB) ──▶ daily sync task ──▶ events.json ──▶ GitHub Pages ──▶ Public page
(scrape · score · dedupe,       (dump DB ·          (source of        (static         (Calendar ⇄ List,
 writes the DB ~6:52am PT)       build_events.py ·   truth, committed) hosting)        no account needed)
                                 commit + push ~7:20am)
```

## Features (as built)

- **Calendar view** — adaptive 3-month grid: portrait stacks months (≥2 visible), landscape fills one month; synchronized nav, month/year picker, Today, wheel-nav in landscape; score-based + past-day dimming; a day popover for crowded days; a collapsible "to be confirmed" shelf that drops out when it would squeeze the calendar.
- **List view** — collapsible digest rows (date · name + format emojis · time · location · setting · score); expand for When / Where / Setting / Admission / Format / Source, theme bullets, a "why it fits you" note, **add-to-calendar** (`.ics` + Google Calendar), and the event link. Collapsible sections (What's new, This week, Upcoming, To be confirmed, Past) plus **Coverage gaps** and **Recurring series on watch** panels from the digest.
- **Filter & search** — one collapsible card: keyword search + score ≥4, source, setting, SF-only, and hide-unverified/low-fit, applied to both views. All state lives in the URL for **shareable deep links** (e.g. `?v=list&s=4&dist=sf`).
- **Light / dark theme** toggle, **social-preview** tags, a **stale-data banner** if the sync falls >36h behind, and a **print** stylesheet.

## Make a change

Edit `index.html` and push to `main`; GitHub Pages redeploys in ~1–2 minutes. The daily
sync only ever writes `data/events.json`, so editing the page never collides with it.
See `HANDOFF.md` for the full operator's guide.

## Earlier planning docs

The original build spec and handoff were first drafted as live Claude docs; the
canonical, current versions now live in this repo (`SPEC.md`, `HANDOFF.md`, `ROADMAP.md`).
