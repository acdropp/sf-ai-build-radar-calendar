# Radar Calendar Spec — Handoff & Next Steps

Oct 11, 2026 · @Aaron

The build spec is in SPEC.md (in this folder). The live, editable version is linked in README.md. Two things to confirm before acting on it, then the natural next move.

**Before you execute:**

- The spec assumes the daily job can be pointed at a new output — writing `events.json` — without disturbing the scrape/score logic. True as far as I can tell, but confirm it when you open the job.
- The one real prerequisite is a GitHub repo plus a scoped push token. Everything in Phase 1 can start before that exists, against sample data.

**Next move:** Phase 1 — build the 3-month calendar bound to a sample `events.json`, so you can see and feel it, either here or in a Claude Code session against your `acdropp` repo. Or pressure-test any part of the plan first.
