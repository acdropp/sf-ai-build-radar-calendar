# 🔦 SF AI Event Search — Operator's Guide

Updated Oct 12, 2026 · @Aaron

The site is built and live. This is how it runs day to day and how to change it.

- **Live site:** https://acdropp.github.io/sf-ai-event-search-calendar/
- **Repo:** `github.com/acdropp/sf-ai-event-search-calendar` (public)
- **Upstream brain:** the Radar digest artifact `https://claude.ai/artifact/HGrcsBLV1hvx2DsP18QZsW` (its database is the source the sync reads).

## How the daily refresh works

Two Claude scheduled tasks run each morning, in order:

1. **~6:52am PT — digest refresh.** Scrapes the sources, scores each event 1–5, dedupes,
   and writes the results into the digest artifact's database (`events` collection +
   `meta/run` document, which holds `summary`, `newIds`, `gaps`, and `tracked`). This is
   the curation step — it is *not* rebuilt here; the calendar reuses it.
2. **~7:20am PT — events.json sync.** Clones this repo, dumps the digest DB with the
   ArtifactData tool, runs `scripts/build_events.py` to produce a clean `data/events.json`,
   and commits + pushes **only if the data changed**. GitHub Pages redeploys in ~1–2 min.

Push access is via the **Claude GitHub App**; commits use the noreply email
`247266112+acdropp@users.noreply.github.com` to avoid GitHub's email-privacy rejection.

**Guardrail:** `build_events.py` refuses to write (exit 2) if the dump has fewer than
`--min-events` events, or fewer than 50% of the previously published count — so a broken
or partial scrape can't wipe the calendar. The sync task skips the commit on exit 2.

If the site looks stale, the page shows a **"data may be stale" banner** once the last
sync is >36h old — a visible signal that the pipeline stopped.

## Making changes to the site

The app is one self-contained file, `index.html` (no build step, no framework).

```
# from a fresh clone or your local copy:
git fetch origin && git reset --hard origin/main   # get the latest (the sync pushes daily)
# edit index.html
git add index.html && git commit -m "…" && git push origin main
```

GitHub Pages redeploys automatically. Because the daily sync only ever writes
`data/events.json`, editing the page never collides with it — but always pull first,
since the sync pushes its own commits.

> **Local repo note:** Aaron's working copy lives at
> `~/Documents/CLAUDE CODE REPO/Projects/sf-ai-build-radar-calendar`. After the daily sync
> (or any cloud edit) it will be behind — resync with
> `git fetch origin && git reset --hard origin/main` before editing.

## Changing what the data looks like

- **Scoring, taste, sources, or event fields** → change the **digest refresh task's**
  prompt (the 6:52am one). That's where scraping and scoring live.
- **The shape of `events.json`** (sorting, flags, the `meta` block) → `scripts/build_events.py`.
  It passes `summary` / `gaps` / `tracked` straight through from the digest's `meta/run`.
- **Past events stay visible (greyed).** The digest only tracks upcoming events, so once a
  date passes it drops from the dump. `build_events.py` carries past-dated events forward
  from the previous `events.json` for `--keep-past-days` (default 45) and marks them
  `status: "seen"`, so the calendar keeps a dimmed history instead of them vanishing. Set
  `--keep-past-days 0` to go back to upcoming-only.
- **How events are displayed** (calendar, list, filters, theming) → `index.html`.

## Gotchas

- **Don't unpublish the digest artifact.** Unpublishing a Claude artifact is permanent —
  you can't republish the same one. Just stop sharing its link if you ever want it private.
- **The page is a daily snapshot, not real-time** — as fresh as the last successful sync.
  That's by design (it's what makes account-less public viewing reliable).
