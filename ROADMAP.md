# SF AI Build Radar — Calendar Build Roadmap

Oct 11, 2026 · @Aaron

## Where we are now

**Phase 0 is done.** The build spec is written, there's a sample `events.json` to build against, and the project is committed to a private GitHub repo (`acdropp/sf-ai-build-radar-calendar`, pushed and in sync). Everything below is forward-looking. **Phase 1 is the next step** — and it needs none of the hosting or GitHub-token setup to start, because it runs against the sample data locally.

## Roadmap at a glance

```text
Phase 1 - Calendar on sample data   ┐
Phase 2 - Real data export          ├─ Milestone 1: shareable, self-hosted live site
Phase 3 - Public site live          ┘
Phase 4 - Toggle + polish
Phase 5 - Optional extras
```

> Rendered roadmap diagram (live, editable): https://claude.ai/code/artifact/7bd026ea-256f-44ec-83ef-435922829c99

Each phase ends in something you can actually use; Phases 1–3 together get you to a shareable, self-hosted live site.

## Scope by phase

| Phase | Goal | In scope | Out of scope / deferred | Ships when |
| --- | --- | --- | --- | --- |
| **1 · Calendar on sample data** | See the calendar working, locally | 3-month synced calendar reading the sample `events.json`; event chips (name + time, score ranking, new/distance/verify badges); TBC shelf; "+N more" per day; dark theme; responsive layout; wheel-vs-nav separation; Today button | Real scraped data; list view; any hosting or GitHub automation | It opens as a local file and shows the sample events correctly placed and ranked |
| **2 · Real data export** | Feed it real scraped events | A serialize-and-write step in the daily job that emits the real `events.json` in the contract shape + `meta` block; dedupe by stable `id` | Hosting; commit/push; list view | A job run produces a valid `events.json` the Phase 1 page renders with no code changes |
| **3 · Public site live** | A shareable URL, no account | Add `index.html` + `events.json` to the repo; make repo public; enable GitHub Pages; wire the job's commit + push with a scoped token; zero-events guardrail | List view; custom domain; Google Calendar | The public URL opens in a logged-out incognito window and shows today's events |
| **4 · Toggle + polish** | The unified dashboard | Fold the existing list view in behind a List ⇄ Calendar toggle; shared header + filters; "last refreshed" from `meta`; density tuning | Custom domain; Google Calendar subscribe | Both views are switchable on the live site and read the same file |
| **5 · Optional extras** | Upside, if wanted | Custom domain; one-way Google Calendar subscribe mirror; retire the dual-write to the artifact DB | — | Whichever extras you pick are live |

Phases **1–3** are the real milestone: a shareable, self-hosted live calendar. **4** turns it into the unified dashboard. **5** is pure upside.

## Deliberately out of scope (for now)

Naming these keeps each phase tight and the build honest about what it is — a static, read-only site fed by a daily job:

- **Live database reads in the browser.** The page ships a committed static snapshot, not a live DB call. That's the simpler design and it's exactly what makes account-less public viewing reliable.
- **Google Calendar sync / "add to my calendar."** Deferred by choice (view-only for now). It reads the same JSON and can be bolted on later without disturbing anything.
- **Any login, accounts, or auth.** The site is public and read-only; there's no sign-in anywhere in it.
- **Event submission by other people.** No one else adds events — the scrape plus your curation is the only input. No forms, no moderation queue.
- **A backend server or API.** Nothing to run or pay for at runtime; it's a static file plus a daily job that commits to Git.
- **Editing events in the UI.** The calendar displays; corrections happen upstream in the data or the job, not by clicking a cell.

None of these are rejected forever — they're just not in the path to a working, shareable calendar, so they wait.
