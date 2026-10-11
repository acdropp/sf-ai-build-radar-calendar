# SF AI Build Radar — Calendar + List

A self-hosted calendar + list view of the **SF AI Build Radar**: a daily-refreshed,
taste-scored feed of hands-on AI builder events in the Bay Area (Luma, Meetup /
Hacker Dojo, AI Tinkerers, and off-platform hacker houses).

This folder is the **project workspace** — spec, handoff notes, and a sample data
file. No application code has been built yet; this is the plan to build from.

## What's here

| File | What it is |
| --- | --- |
| `SPEC.md` | The full build spec — architecture, data contract, phased milestones, acceptance criteria. Start here. |
| `HANDOFF.md` | Short handoff: what to confirm before building, and the next move. |
| `data/events.sample.json` | A hand-written sample `events.json` matching the data contract — the Phase-1 starter for binding the calendar to data. |
| `.gitignore` | Standard ignores for when this becomes a git repo. |

## Live (editable) versions of the docs

These are the source documents; the `.md` files here are exported snapshots.

- **Build spec:** https://claude.ai/code/artifact/255de9cb-7fb1-470a-82a1-f7e189eab37c
- **Handoff & next steps:** https://claude.ai/code/artifact/a7090df4-acae-47c4-8d2d-43b7ffab6e60

## The shape of it (one paragraph)

A single `events.json` is the source of truth. The existing daily job (scrape →
score 1–5 → dedupe) writes and commits that file to a GitHub repo (`acdropp`);
GitHub Pages serves a static `index.html` that reads it and renders two switchable
views — a 3-month synchronized calendar and the existing scored list. Because the
data is committed into the repo and baked into what the browser downloads, the
public URL opens for **anyone, with no account** — which is the whole point of
going self-hosted instead of relying on a published artifact.

```
Event sources ──▶ Daily job ──▶ events.json ──▶ GitHub Pages ──▶ Public page
(Luma, Meetup,    (scrape ·     (source of       (static         (Calendar ⇄ List,
 Hacker Dojo,      score ·       truth, in         hosting)        no account needed)
 AI Tinkerers,     dedupe)       acdropp)
 web)
```

## Build order (summary — see SPEC.md for detail)

1. Calendar bound to this sample `events.json`, locally.
2. Real `events.json` export wired into the daily job.
3. Public site stood up on GitHub Pages + commit/push from the job.
4. List/calendar toggle + density polish.
5. Optional: custom domain, Google Calendar subscribe mirror.

Phases 1–3 get a shareable live calendar. 4 makes it the unified dashboard. 5 is upside.

## Status

**Planning complete, build not started.** Phase 1 can begin against
`data/events.sample.json` without any of the GitHub/hosting setup in place.
