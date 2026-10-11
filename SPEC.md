# SF AI Build Radar — Calendar + List Build Spec

Oct 11, 2026 · @Aaron

## Overview & goals

Build a self-hosted web page that shows the SF AI Build Radar's events in two switchable views — a month-grid calendar and the existing scored list — both reading one shared event file, and host it as a plain website anyone can open with no account.

This is an extension, not a rebuild. The Radar already scrapes, scores, and publishes a daily digest; what's missing is a visual calendar and a host that doesn't depend on an Anthropic login. The work is a frontend view plus a hosting/data move, sitting on top of the pipeline that already runs.

Concrete goals this spec commits to:

- **Two views, one data source.** A Calendar ⇄ List toggle, both bound to the same event records. No second copy of the data to keep in sync.
- **Shareable with anyone, no account.** The people Aaron sends it to open a normal URL in any browser — no Claude/Anthropic sign-in, no app.
- **Daily auto-updates.** The existing \~7:00am PT job keeps refreshing events; the published page reflects each day's run with no manual step.
- **Own-your-stack resilience.** The source of truth lives in Aaron's own GitHub (`github.com/acdropp`) as a plain, version-controlled file — portable, diffable, and independent of any one platform.
- **Keep the taste signal.** The 1–5 fit score and the `new` / `needs-verification` flags carry through to the calendar, so quality stays visible at a glance.

## What already exists today

The Radar is a running system, not a blank slate — the spec builds on these parts and leaves them in place:

- **A daily scrape + score job.** It sweeps Luma calendars, Meetup iCal feeds (including Hacker Dojo), AI Tinkerers, and web search for off-platform hacker houses, then scores each event 1–5 against Aaron's taste (hands-on, own-your-AI / local-first, in-person SF, community). South Bay & Peninsula events are flagged for distance but kept. It refreshes around 7:00am PT.
- **A stored event set.** Events currently live in the Radar artifact's shared database (an `events` collection plus a `meta/run` record), written by the job and read by the page.
- **A published digest page.** A list-only view, organized into sections — New, This week, All upcoming, Needs verification, Coverage gaps, Tracked series — each event a tap-to-expand row with its score as a 5-dot meter and a "why it fits you" note.
- **A clean, calendar-ready schema.** Every event already carries the fields a calendar needs (date, times, venue, score, flags). That schema is the contract in the next section.

**What this project changes, precisely:** it adds a calendar view beside the list, and it moves the source of truth and the hosting off the artifact platform into Aaron's GitHub. It does **not** touch the scraping, scoring, or the daily schedule — those stay as-is and simply gain a new output target (a committed file) and a new reader (the self-hosted page).

## Target architecture

A static site reads one committed file; the daily job is the only thing that writes it. Nothing a public viewer loads depends on a database read or a login.

> _Architecture diagram (sources → daily job → GitHub file → public page) lives in the live doc; it renders as text here. The flow is described in the paragraph below and in the README._

The move that matters: the source of truth leaves the artifact platform and becomes a plain `events.json` in Aaron's GitHub. That one change buys account-less public viewing (the data is baked into what the browser downloads), version history as a backup, and portability to any host or future tool — none of which the artifact-database-only setup can promise.

## Event data contract

The source of truth is a single `events.json` file: an array of event objects, each following the shape below. The daily job writes it; both views read it. Lock this contract first — everything else binds to it.

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | string | Stable unique key (e.g. source + slug). Drives dedupe and calendar cell keys. |
| `name` | string | Event title. |
| `date` | string \| null | ISO `YYYY-MM-DD`. `null` when undated → routed to the TBC shelf, not the grid. |
| `dateDisplay` | string | Human label for undated/fuzzy events ("Late Oct", "To be confirmed"). |
| `startTime` | string | e.g. `18:00`. |
| `endTime` | string | e.g. `21:00`. |
| `tz` | string | Timezone label, default `PT`. |
| `venue` | string | Venue name. |
| `address` | string | Street address. |
| `city` | string | City (drives the distance flag). |
| `setting` | string | In-person / hybrid / online. |
| `price` | string | Admission ("Free", "$20"). |
| `membership` | string | Membership note, if any. |
| `source` | string | Where it was found (Luma, Meetup, Hacker Dojo, web). |
| `url` | string | Link to the event page — the calendar's click-through. |
| `tags` | string\[\] | Short topic tags. |
| `themes` | string\[\] | Longer theme phrases for the detail view. |
| `fit` | string | The "why it fits you" sentence. |
| `score` | number | 1–5 taste score. Drives visual ranking on the grid. |
| `status` | string | e.g. `new` — badges the event and left-accents its row. |
| `distanceNote` | string | e.g. "South Bay — \~45 min". Present = distance badge. |
| `needsVerification` | boolean | `true` = unconfirmed fields; dimmed + `verify` badge. |

A top-level `meta` object should travel alongside (`{ "generatedAt": "...", "runId": "...", "sourceCounts": {...} }`) so the page can show "last refreshed" and so each daily commit is self-describing.

Example record:

```json
{
  "id": "luma-ai-tinkerers-2026-10-16",
  "name": "AI Tinkerers SF — Build Night",
  "date": "2026-10-16",
  "startTime": "18:00",
  "endTime": "21:00",
  "tz": "PT",
  "venue": "Shack15",
  "city": "San Francisco",
  "setting": "In-person",
  "price": "Free",
  "source": "Luma",
  "url": "https://lu.ma/...",
  "tags": ["agents", "demos"],
  "fit": "Hands-on build night, local-first crowd, in SF proper.",
  "score": 5,
  "status": "new",
  "needsVerification": false
}
```

## Frontend — calendar + list views

One self-contained page, two views behind a toggle, both fed by `events.json`. The list view is the existing digest, carried over. The calendar view is new and is where most of the build effort goes.

**The toggle.** A persistent List ⇄ Calendar switch in the header. Same data, same filters apply to both. Default to Calendar (Aaron is visual), remember the last choice in `localStorage` as a per-viewer convenience only.

**Calendar view — the 3-month synchronized dashboard.** Reuse the prototype Aaron already designed. Core requirements carried from that spec:

- Three consecutive months shown, defaulting to current month + next two.
- **Synchronized navigation:** the back/forward arrows on *any* month shift all three by one month together — never one calendar independently.
- A clickable month/year heading opens a month+year picker; the chosen month lands in the calendar whose heading was clicked, and the others re-sequence around it. Works across year boundaries.
- **Responsive:** stack vertically in portrait/tall windows; flow side-by-side (3-up, or 2-up with the third wrapping) in wide windows; recompute on resize without changing the selected months.
- **Mouse wheel scrolls the page, never changes months.** No nested scroll region hijacks the wheel.
- A **Today** button resets to the current month and scrolls to top.
- Dark charcoal theme, lighter rounded panels, one accent color, today's date distinguished.

**Binding events onto the grid.** For each day cell, render the events whose `date` matches. Each event chip shows name + time, links out to `url`, and carries its score and flags visually.

**Score-based density (the key decision applied).** Show everything, but rank it:

- Score 4–5: full weight, accent-tinted.
- Score 3: normal.
- Score ≤ 2 and `needsVerification`: dimmed / muted so the grid stays scannable without hiding anything.
- `status: new` gets a small badge; `distanceNote` gets a distance badge.

**The TBC shelf.** Undated events (`date: null`) can't sit in a grid. Render them in a labeled "No date yet" strip above or below the calendar so they never silently vanish — a real failure mode given how many community events are announced before they're scheduled.

**A day with many events.** Cap visible chips per cell (e.g. 3), then a "+N more" affordance that expands the day or opens a day detail. Prevents tall, ragged rows.

**List view.** The existing scored, sectioned digest — unchanged in logic, restyled only as needed to share the page's header and toggle.

## Daily data pipeline

The daily job keeps doing what it does — scrape, score, dedupe — and gains one new final step: write `events.json` and commit it to the repo. The published site is static, so no live database read happens when a viewer loads the page; they get whatever the last commit baked in.

The daily sequence:

1. **Scrape** the sources (Luma, Meetup/Hacker Dojo iCal, AI Tinkerers, web) — unchanged.
2. **Score** each event 1–5 against the taste profile — unchanged.
3. **Dedupe** across sources by stable `id`, so the same event from Luma and Meetup collapses to one record.
4. **Serialize** the full set to `events.json` in the contract shape, plus the `meta` block (run time, counts).
5. **Commit & push** the file to `github.com/acdropp/<repo>`. GitHub Pages redeploys automatically on push, so the public page updates within a minute or two.

Practical requirements:

- **Write credentials.** The job needs push rights to the repo — a fine-grained Personal Access Token or a deploy key scoped to that one repo. This is the one new secret to manage; keep it out of the committed files.
- **Idempotency.** Re-running the job the same day should produce the same file (stable ordering, stable ids) so commits only appear when something actually changed — clean git history, no noise.
- **Commit message = a daily marker.** e.g. `radar: 2026-10-11 run (42 events, 3 new)`. The git log becomes a free changelog of what the Radar saw each day.
- **Dual-write option (transitional).** The job can keep writing the artifact database *and* the JSON during changeover, so nothing breaks while the self-hosted page is being stood up. Drop the DB write once the site is the primary surface.
- **Scheduling.** A truly unattended daily run wants a real scheduler (a GitHub Action on a cron, or the existing scheduled task that already drives the 7am refresh) rather than a person pressing go. Decide which owns the schedule — see Open decisions.

## Hosting, sharing & resilience

**Host:** GitHub Pages, served from the `acdropp` repo. The page (`index.html`) and `events.json` live in the repo; every push redeploys. Result: a public URL like `acdropp.github.io/<repo>` that opens in any browser with **no Claude or Anthropic account required** — which is the whole reason for going self-hosted rather than relying on a published artifact.

**Why this meets the "share with anyone" requirement cleanly.** A published Claude artifact *can* be viewed without an account, but the Radar's data loads from the artifact database, and there's no guarantee a logged-out stranger's browser reads that database — they could open a beautiful, empty calendar. A static page with the data committed into the repo has no such failure mode: the events are just there in the file the browser downloads.

**Custom domain (optional).** GitHub Pages supports a custom domain via a `CNAME` file + DNS record — e.g. `radar.<aarondomain>`. Nice-to-have, not required for launch.

**Static.app as an alternative host.** If GitHub Pages setup is friction, Static.app can import an artifact's public link or a copied HTML bundle and serve it as a standalone site with its own URL and optional custom domain. Same end state (account-less public page); different front door.

**Resilience / audit trail, for free.** Because the source of truth is a committed JSON file, git history *is* a daily backup and a visible record of what changed run to run. Nothing depends on a single platform staying up or a single login working.

**Deferred: Google Calendar subscribe.** A one-way nightly push from `events.json` into a public Google Calendar would let people click "add to my calendar" and get events in their own app. Aaron chose view-only for now, so this stays parked — easy to add later, no architectural conflict, just another consumer of the same JSON.

## Build sequence — phased milestones

Ordered so each phase ends in something that works and is worth looking at. A future Claude Code session can pick this up phase by phase.

1. **Calendar bound to sample data (local).** Take the 3-month prototype, define `events.json`, hand-write \~15 sample records across the current and next two months (include a few score-2s, a `needsVerification`, and a `date: null`). Bind events onto the grid, add score-based dimming and the TBC shelf. *Done when:* the prototype shows real-looking events, correctly placed and ranked, opened as a local file.
2. **Real export from the job.** Add the serialize-and-write step to the daily job so it emits the real `events.json` from live scraped data. *Done when:* a run produces a valid file the Phase 1 page renders with no code changes.
3. **Stand up the public site.** Create/choose the `acdropp` repo, add `index.html` + `events.json`, enable GitHub Pages, wire the job's commit+push with a scoped token. *Done when:* the public URL opens in a logged-out incognito window and shows today's events.
4. **List/calendar toggle + polish.** Fold the existing list view into the page behind the toggle, share the header and filters, tune density, the "+N more" day overflow, and the "last refreshed" stamp from `meta`. *Done when:* both views are switchable on the live site and read the same data.
5. **Optional extras.** Custom domain; the one-way Google Calendar subscribe mirror; retiring the dual-write to the artifact DB once the site is primary. *Done when:* whichever of these Aaron decides he wants is live.

Phases 1–3 are the real milestone (a shareable live calendar). 4 makes it the unified dashboard. 5 is upside.

## Open decisions, risks & future options

Still Aaron's calls — none block starting Phase 1, but they shape later phases:

- **Who owns the schedule?** Keep the current scheduled task as the daily driver, or move the cron into a GitHub Action? The Action keeps everything in one repo and runs even if other tooling changes; the existing task already works. *Lean: whichever is less fragile to Aaron day-to-day — likely the GitHub Action once the repo exists.*
- **Token handling for the commit step.** A fine-grained PAT or deploy key scoped to the one repo, stored as a secret (GitHub Actions secret, or wherever the job runs). Don't let it touch a committed file. Low effort, but it's the one real security surface.
- **Fate of the original artifact.** Keep it as a staging/preview surface while iterating, or retire it once the site is live? Note the one-way door: **unpublishing a Claude artifact is permanent — you can't republish the same one.** So don't unpublish casually; just stop sharing its link.
- **Scrape fragility.** Luma/Meetup markup and feeds change; a silent scrape break would freeze the calendar at the last good run. Worth a cheap guardrail: if a run finds zero events or far fewer than yesterday, skip the commit and flag it rather than publishing an empty calendar.
- **Snapshot vs live.** This spec commits to the static-snapshot model (data baked into each commit). That's the right call for account-less viewing and simplicity; the tradeoff is the page is as fresh as the last run, not real-time — fine for a daily radar.
- **Deferred, not dropped — Google Calendar subscribe.** Revisit if people start asking "can I get these in my own calendar?" It's additive, reads the same JSON, and doesn't disturb anything built here.

## Acceptance criteria

Call it done when all of these hold:

**Sharing & data**

- [ ] The public URL opens in a logged-out incognito window, on a device with no Claude account, and shows today's events.
- [ ] The page reads a single `events.json`; both views use it; there's no second data copy.
- [ ] A daily job run updates the live page within a few minutes, with no manual step.
- [ ] The git history shows one commit per changed run, each with a descriptive message.

**Calendar behavior** (from the prototype spec)

- [ ] Three consecutive months show on load — current + next two.
- [ ] Clicking either arrow on any month shifts all three by exactly one month.
- [ ] Clicking any month heading opens the month/year picker; the chosen month lands in that calendar and the others re-sequence.
- [ ] Navigation across a December→January boundary works correctly.
- [ ] Tall windows stack the months; wide windows lay them out horizontally; resizing re-lays-out without changing the selected months.
- [ ] Mouse-wheel scrolling moves the page and never changes the displayed months.
- [ ] Today returns to the current month and scrolls to top.

**Views & density**

- [ ] A List ⇄ Calendar toggle switches views; the last choice is remembered.
- [ ] Score ≤ 2 and `needsVerification` events appear but are visually dimmed, not hidden.
- [ ] `new` and distance events carry their badges on the grid.
- [ ] Undated (`date: null`) events appear in the TBC shelf, reachable, never dropped.
- [ ] A day with many events caps its chips and offers "+N more".
- [ ] Every event chip links out to its source `url`.

**Robustness**

- [ ] A run that finds zero / far fewer events than usual does not publish an empty calendar.
- [ ] All dates render without clipping or overlap on both desktop and mobile widths.
