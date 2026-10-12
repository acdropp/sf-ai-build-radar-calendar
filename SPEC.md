# SF AI Build Radar — Calendar + List Spec (as built)

Updated Oct 12, 2026 · @Aaron

> **Status: built and live** at https://acdropp.github.io/sf-ai-build-radar-calendar/.
> This document now describes the system as it actually works. The original plan was
> written forward-looking; this version reflects what shipped (Phases 1–4 plus most of
> Phase 5 — see `ROADMAP.md`).

## Overview & goals

A self-hosted web page that shows the SF AI Build Radar's events in two switchable
views — a month-grid calendar and a rich scored list — both reading one shared event
file, hosted as a plain website anyone can open with no account.

This is an extension, not a rebuild. The Radar already scrapes, scores, and publishes a
daily digest; this added a visual calendar and a host that doesn't depend on an
Anthropic login. The goals, all met:

- **Two views, one data source.** A Calendar ⇄ List toggle, both bound to the same event records and the same filters. No second copy of the data.
- **Shareable with anyone, no account.** A normal URL in any browser — no Claude/Anthropic sign-in, no app.
- **Daily auto-updates.** The existing morning job keeps refreshing events; the published page reflects each day's run with no manual step.
- **Own-your-stack resilience.** The source of truth lives in Aaron's own GitHub (`github.com/acdropp`) as a plain, version-controlled file — portable, diffable, platform-independent.
- **Keep the taste signal.** The 1–5 fit score and the `new` / `needsVerification` flags carry through to both views, so quality stays visible at a glance.

## What the Radar already did (and still does)

The spec builds on these parts and leaves them in place:

- **A daily scrape + score job** — sweeps Luma calendars, Meetup iCal feeds (including Hacker Dojo), AI Tinkerers, and web search for off-platform hacker houses, then scores each event 1–5 against Aaron's taste (hands-on, own-your-AI / local-first, in-person SF, community). South Bay / Peninsula / East Bay events are flagged for distance but kept.
- **A stored event set** — events live in the Radar digest artifact's shared database (an `events` collection plus a `meta/run` record), written by the job.
- **A published digest page** — the list-only view this calendar's list view is modeled on.
- **A clean, calendar-ready schema** — every event already carries the fields a calendar needs. That schema is the contract below.

**What this project changed:** it added the calendar + list site and moved the *source
of truth and hosting* off the artifact platform into GitHub. It did **not** touch the
scraping or scoring — those stay in the digest and simply gained a new consumer (a daily
sync that commits a file).

## Architecture

A static site reads one committed file; a daily sync is the only thing that writes it.
Nothing a public viewer loads depends on a database read or a login.

```
Radar digest (artifact DB)  ──▶  daily sync task  ──▶  data/events.json  ──▶  GitHub Pages  ──▶  Public page
scrape · score · dedupe,         dump DB ·              source of truth,       static            Calendar ⇄ List,
writes DB ~6:52am PT             build_events.py ·      committed to repo      hosting           no account needed
                                 commit + push ~7:20am
```

The move that matters: the source of truth is a plain `events.json` in GitHub. That buys
account-less public viewing (the data is baked into what the browser downloads), version
history as a backup, and portability to any host — none of which an artifact-database-only
setup can promise. The digest artifact remains **upstream** as the curation brain; the
calendar never writes to it (read-only).

## Event data contract

The source of truth is `data/events.json`: a `meta` object plus an `events` array of
objects in the shape below. `scripts/build_events.py` writes it; both views read it.

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | string | Stable unique key (document slug). Drives dedupe, calendar cell keys, and `.ics` UIDs. |
| `name` | string | Event title. |
| `date` | string \| null | ISO `YYYY-MM-DD`. `null` when undated → routed to the TBC shelf, not the grid. |
| `dateDisplay` | string | Human label for undated/fuzzy events ("Late Oct", "To be confirmed"). |
| `startTime` / `endTime` | string | e.g. `9:00 AM` / `2:00 PM` (12-hour; parsed for calendar export). |
| `tz` | string | Timezone label, default `PT`. |
| `venue` / `address` / `city` | string | Location. `city` drives the region flag (⚠️ + South Bay / East Bay / Online). |
| `setting` | string | `in-person` / `hybrid` / `online`. |
| `price` | string | Admission ("Free", "$20", "Not shown"). |
| `membership` | string | Membership note (always shown in the list detail). |
| `source` | string | Where it was found (Luma / Meetup / Hacker Dojo / …). Drives the source filter. |
| `url` | string | Link to the event page — the click-through and calendar-export URL. |
| `tags` | string[] | Format tags as `"emoji label"` (e.g. `"🦾 hackathon"`, `"🛠️ build"`). The list renders the emojis, normalized to a legend (🦾 hackathon, 🛠 build, 🎤 demo, 🗣 discussion, 🍻 social, 👩🏽‍🏫 lecture, 📚 book club). |
| `themes` | string[] | 2–5 theme phrases for the expanded detail. |
| `fit` | string | The "why it fits you" sentence. |
| `score` | number | 1–5 taste score. Drives ranking, dimming, and the score filter. |
| `status` | string | `new` badges the event and left-accents its row; otherwise `seen`. |
| `distanceNote` | string | e.g. "South Bay — ~45 min". Used for the region flag/badge. |
| `needsVerification` | boolean | `true` = unconfirmed fields; `verify` badge. |

The top-level `meta` object (written each run):

```json
{
  "generatedAt": "2026-10-12T14:00:02Z",
  "lastRunLabel": "Oct 12, 2026 · 7:00am PT",
  "source": "SF AI Build Radar digest (artifact DB)",
  "eventCount": 51, "newCount": 6, "datedCount": 45,
  "summary": "6 new today: …",
  "gaps": ["…coverage gaps this run…"],
  "tracked": [{ "name": "…", "url": "…", "why": "…" }]
}
```

`generatedAt` drives the "data as of" line and the stale-data banner; `summary` is the
intro of the "What's new" section; `gaps` and `tracked` power the two bottom panels.

## Frontend — one self-contained `index.html`

One page, no framework, no build step; two views behind a toggle, both fed by the same
filtered event set. Default view is Calendar (remembered per viewer); the whole thing
themes light/dark (dark default; light uses the digest's color scheme).

### Calendar view

- **Adaptive layout:** landscape shows one month grown to fill the tile; portrait stacks months with at least two visible. Reference month defaults to the current month.
- **Synchronized nav:** arrows and the month/year picker move the reference month; in the stacked view every visible month shifts together. The picker lands the chosen month in the calendar whose heading was clicked; works across year boundaries.
- **Context-aware wheel:** scrolls the page in the stacked view; navigates months in the single-month landscape fill view.
- **Today** resets to the current month. A clickable month/year heading opens the picker.
- **Event chips** show name-first (with a "new" dot) and carry score tier + verify styling. **Score + past dimming:** score ≤2 / `needsVerification` / past days are dimmed but never hidden.
- **Clicking any day — a chip or empty space, one event or many — opens the anchored day popover** (fit-to-content, capped scroll, keyboard nav, edge-flipping) listing that day's events. Each popover row is the same expandable row as the list view: click it to reveal the full detail (When/Where/Setting/Admission/Format/Source, themes, why-it-fits, Open event / Add to calendar / Google Calendar). Crowded cells cap chips and show a "+N ▲" triangle.
- **TBC shelf** ("No date yet · to be confirmed") sits below the calendar, is **collapsible** (default collapsed), and is **dropped automatically in short landscape** so it never squeezes the grid below a legible height.

### List view

- **Collapsible digest rows.** Collapsed: `mm/dd · name (+ ⚠️ if outside SF) · format emojis · time · location · setting · score meter`. Expand for a `When / Where / Setting / Admission (price + membership) / Format / Source` block, 2–5 theme bullets, a "Why it fits you" box, **Add to calendar** (`.ics` + Google Calendar), and the event link.
- **Collapsible sections**, each remembering its state, with defaults: This week (open), Upcoming (open), What's new since last run (collapsed), To be confirmed (collapsed), Past (collapsed). Order: This week → Upcoming → What's new → To be confirmed → Past.
- **Coverage gaps this run** and **Recurring series on watch** panels (collapsed by default) render `meta.gaps` and `meta.tracked`.
- **Region flags:** ⚠️ in the title when outside SF, plus a South Bay / East Bay / Online badge; NEW and VERIFY badges throughout.

### Filter, search & sharing

- **One collapsible "Filter & search" card** (bordered like the TBC shelf, collapsed by default; auto-opens only when a deep link arrives with filters). Applies to **both views**:
  keyword search (name / venue / city / themes / tags / fit), score ≥4, source (Luma / Meetup / Hacker Dojo), setting (in-person / online), SF-only distance, and hide unverified/low-fit. Live match count + Clear.
- **Shareable deep links:** view, month, and every filter are mirrored to the URL — e.g. `?v=list&s=4&dist=sf`, `?v=calendar&m=2026-11`.

### Add to calendar (per event)

Each dated event's detail offers an **`.ics` download** (data-URI, with an
`America/Los_Angeles` `VTIMEZONE` so times import correctly across Apple/Google/Outlook,
and `VALUE=DATE` all-day when no start time) and a **Google Calendar** template link.

### Other

- **Social preview** — OpenGraph / Twitter tags + `og-image.png` (titled card in Slack / iMessage / Discord).
- **Stale-data banner** — shown when `generatedAt` is >36h old, so a silently-broken sync is visible.
- **Print stylesheet** — a clean, expanded list handout; **mobile** list refinements.

## Daily data pipeline

Two Claude scheduled tasks run each morning:

1. **~6:52am PT — digest refresh.** Scrapes, scores, dedupes, and writes the results into the digest artifact's database (`events` + `meta/run`, including `summary` / `newIds` / `gaps` / `tracked`). Unchanged from the pre-existing Radar; the calendar reuses it.
2. **~7:20am PT — events.json sync.** Clones this repo, dumps the digest DB with the ArtifactData tool, runs `scripts/build_events.py`, and commits + pushes **only if the data changed**. GitHub Pages redeploys in ~1–2 min.

`build_events.py` is deterministic (stable id from the doc key, sort by date then score,
`newIds` → `status:"new"`, pass `summary`/`gaps`/`tracked` through) so unchanged runs are
no-op diffs. Its **guardrail** refuses to write (exit 2) when the dump has fewer than
`--min-events` events or fewer than 50% of the previously published count — a broken or
partial scrape can't wipe the calendar. Commit messages double as a changelog, e.g.
`radar: 2026-10-12 PT sync (51 events, 6 new)`.

**Push access** is via the **Claude GitHub App**; commits use the noreply email
`247266112+acdropp@users.noreply.github.com` to avoid GitHub's email-privacy rejection.

## Hosting, sharing & resilience

- **Host:** GitHub Pages, served from the public `acdropp/sf-ai-build-radar-calendar` repo. Every push redeploys. Public URL opens in any browser with **no Claude/Anthropic account**.
- **Why it meets "share with anyone":** the data is committed into the repo and baked into what the browser downloads, so there's no "beautiful empty calendar" failure mode a live-DB page could have.
- **Audit trail, for free:** git history *is* a daily backup and a record of what changed run to run.
- **Custom domain (optional, not done):** supported via a `CNAME` + DNS record if wanted later.

## Decisions (resolved)

- **Schedule owner:** the existing Claude scheduled tasks drive it (not a GitHub Action). Two tasks: digest refresh, then events.json sync.
- **Push credentials:** the Claude GitHub App (no PAT to manage); noreply commit email.
- **Fate of the artifact:** **kept** as the upstream curation brain and preview surface. (Note the one-way door: unpublishing a Claude artifact is permanent — don't unpublish; just stop sharing the link.)
- **Scrape fragility:** handled by the build-script guardrail (skip the commit on too-few events) + the stale-data banner on the page.
- **Snapshot vs live:** static-snapshot by design — as fresh as the last successful sync, which is what makes account-less viewing reliable.
- **Google Calendar subscribe feed:** **declined** (Oct 12). Per-event add-to-calendar covers the need; a whole-calendar `.ics` feed can still be added later as another consumer of the same JSON.
- **Retire the artifact-DB dependency:** **declined** — the DB hop works and keeps the LLM curation in place.

## Acceptance criteria — all met

**Sharing & data**

- [x] The public URL opens logged-out, no Claude account, and shows today's events.
- [x] The page reads a single `events.json`; both views use it; no second data copy.
- [x] A daily run updates the live page within a few minutes, no manual step.
- [x] Git history shows one commit per changed run with a descriptive message.

**Calendar behavior**

- [x] Portrait stacks ≥2 months; landscape fills one month.
- [x] Any arrow shifts every visible month together by one.
- [x] The month/year picker lands the chosen month in that calendar; others re-sequence.
- [x] December→January navigation works.
- [x] Resize/rotate re-lays-out (stacked ↔ single-month fill) without losing the reference month.
- [x] Wheel scrolls in stacked view; navigates months in single-month landscape.
- [x] Today returns to the current month and scrolls to top.

**Views & density**

- [x] A List ⇄ Calendar toggle switches views; last choice remembered.
- [x] Score ≤2 / `needsVerification` events appear but are dimmed, not hidden.
- [x] `new` and distance/region events carry badges.
- [x] Undated events appear in the (collapsible) TBC shelf, never dropped.
- [x] Clicking any day (chip or empty space) opens the day popover; each row expands to full detail and links out from there.
- [x] Crowded days cap chips and offer a "+N" day popover.

**Robustness**

- [x] A run with zero / far-fewer events does not publish an empty calendar (build-script guardrail).
- [x] Dates render without clipping on desktop and mobile widths.

**Beyond the original bar (Phase 5):** theme toggle, rich collapsible list, filters +
search + hide, shareable deep links, per-event calendar export, social preview, coverage
gaps / tracked panels, stale-data banner, collapsible sections, print styles.
