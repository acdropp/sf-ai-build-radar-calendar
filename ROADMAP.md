# 🔦 SF AI Event Search — Calendar Build Roadmap

Updated Oct 12, 2026 · @Aaron

## Where we are now

**Phases 1–4 are done and live**, plus most of the Phase 5 extras. The site is public at
https://acdropp.github.io/sf-ai-event-search-calendar/ and refreshes itself every morning
from the Radar digest. What remains is genuinely optional (a custom domain) or
deliberately declined (a whole-calendar subscribe feed; retiring the artifact DB).

## Roadmap at a glance

```text
Phase 1 - Calendar on sample data   ✅ ┐
Phase 2 - Real data export          ✅ ├─ Milestone 1: shareable, self-hosted live site ✅
Phase 3 - Public site live          ✅ ┘
Phase 4 - Toggle + polish           ✅
Phase 5 - Optional extras           ◑  (most shipped; a couple declined)
```

## Scope by phase

| Phase | Goal | Status | Notes |
| --- | --- | --- | --- |
| **1 · Calendar on sample data** | See the calendar working | ✅ Done | 3-month adaptive grid (portrait stacks ≥2 months; landscape fills one), synced nav, month/year picker, Today, wheel-nav, score + past dimming, TBC shelf, day popover for crowded days. |
| **2 · Real data export** | Feed it real scraped events | ✅ Done | `scripts/build_events.py` transforms a dump of the digest DB into a clean, guarded `events.json`. No rebuild of the scrape — the existing digest stays the brain. |
| **3 · Public site live** | A shareable URL, no account | ✅ Done | Repo public, GitHub Pages enabled, daily commit+push via a Claude scheduled task (push through the Claude GitHub App; noreply commit email). Zero/too-few-events guardrail in the build script. |
| **4 · Toggle + polish** | The unified dashboard | ✅ Done | List ⇄ Calendar toggle, shared header, "last refreshed" from `meta`, density tuning, past events kept but dimmed. |
| **5 · Optional extras** | Upside | ◑ Mostly shipped | See below. |

### Phase 5 — what shipped

- ✅ **Light / dark theme toggle** (light theme uses the digest's color scheme).
- ✅ **Rich collapsible list** — digest-style expandable rows (When/Where/Setting/Admission/Format/Source, themes, why-it-fits), format emojis, region flags (⚠️ + South Bay / East Bay / Online), NEW / VERIFY badges.
- ✅ **Filter bar + keyword search + hide toggle**, applied to both views (score ≥4, source, setting, SF-only, hide unverified/low-fit), in one collapsible card.
- ✅ **Shareable deep links** — view / month / filters mirrored to the URL.
- ✅ **Add to calendar per event** — `.ics` download (with `America/Los_Angeles` VTIMEZONE) + Google Calendar link.
- ✅ **Social preview** — OpenGraph / Twitter tags + `og-image.png`.
- ✅ **Coverage gaps + Recurring series on watch panels** and a **What's new since last run** section, surfaced from the digest's `meta/run`.
- ✅ **Stale-data banner** when the last sync is >36h old.
- ✅ **Collapsible list sections** (with sensible defaults) and a **collapsible TBC shelf**; calendar drops the TBC shelf in short landscape to stay readable.
- ✅ **Print stylesheet** + mobile list refinements.

### Phase 5 — not done (by choice)

- ⬜ **Custom domain** — optional; needs a domain + DNS. Easy to add later.
- ❌ **Whole-calendar subscribe feed** (a single `events.ics` to subscribe to) — **declined** (Oct 12). Per-event add-to-calendar covers the need for now.
- ❌ **Retire the artifact-DB dependency** — **declined**. The DB hop works fine and keeps the LLM curation in place; not worth the rework.

## Deliberately out of scope

Still true, and worth keeping honest about — this is a static, read-only site fed by a daily job:

- **Live database reads in the browser.** The page ships a committed static snapshot, which is exactly what makes account-less public viewing reliable.
- **Any login, accounts, or auth.** Public and read-only.
- **Event submission by other people.** The scrape + curation is the only input; no forms, no moderation queue.
- **A backend server or API.** Nothing to run at runtime — a static file plus a daily job that commits to Git.
- **Editing events in the UI.** Corrections happen upstream in the digest, not by clicking a cell.
