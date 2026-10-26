#!/usr/bin/env python3
"""
Build data/events.json for the SF AI Build Radar calendar from a dump of the
Radar digest's artifact database.

The daily sync task dumps the digest DB with the ArtifactData tool:
  - events collection  -> <events-dir>/*.json   (one file per event; filename = event id)
  - meta/run document  -> <meta-file>            (the run's data object, optional)
then runs this script to produce a clean, contract-shaped events.json.

Deterministic + guarded so an unattended daily run can't publish garbage:
  * event id comes from the document key (filename stem)
  * events listed in meta.newIds are flagged status="new" (the "new" badge)
  * events are sorted by date (undated last), then score desc  -> tidy diffs
  * GUARDRAIL: refuses to write (exit 2) if the dump has fewer than --min-events
    events, or fewer than --min-ratio of the events already in --out, unless
    --force is given. This stops a broken/partial scrape from wiping the calendar.

Usage:
  python3 scripts/build_events.py \
      --events-dir dump/events \
      --meta dump/meta_run.json \
      --out data/events.json \
      [--min-events 10] [--min-ratio 0.5] [--force]

Exit codes: 0 = wrote events.json (changed or unchanged), 2 = guardrail blocked,
1 = error. The sync task should commit+push only on exit 0 with a real change.
"""
import argparse
import datetime
import glob
import json
import os
import sys


def iso_ok(s):
    try:
        datetime.date.fromisoformat(s)
        return True
    except Exception:
        return False


def load_events(events_dir):
    events = []
    for f in sorted(glob.glob(os.path.join(events_dir, "*.json"))):
        doc_id = os.path.splitext(os.path.basename(f))[0]
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"  ! skipping unreadable {f}: {e}", file=sys.stderr)
            continue
        if not isinstance(d, dict):
            continue
        d = dict(d)
        d["id"] = doc_id  # the document key is the stable id
        events.append(d)
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events-dir", required=True)
    ap.add_argument("--meta", default=None, help="meta/run document JSON (optional)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-events", type=int, default=10)
    ap.add_argument("--min-ratio", type=float, default=0.5,
                    help="min fraction of the previously published count; below this, refuse")
    ap.add_argument("--keep-past-days", type=int, default=45,
                    help="carry past-dated events forward from the previous out file for this "
                         "many days after they occur, so the calendar keeps a greyed history. "
                         "0 disables carry-forward (past events drop as before).")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    events = load_events(args.events_dir)
    n = len(events)
    print(f"loaded {n} events from {args.events_dir}")

    # previous out file (used for both the guardrail and carrying past events forward)
    prev_events = []
    if os.path.exists(args.out):
        try:
            prev_events = json.load(open(args.out, encoding="utf-8")).get("events", []) or []
        except Exception:
            prev_events = []

    # --- guardrail ---
    # Compare the dump against the previous *upcoming* count only. The dump is
    # upcoming-only (the digest skips past events); the out file also carries greyed
    # past events, so counting those would make a healthy dump look like a partial one.
    def is_upcoming(e):
        d = e.get("date")
        return (not d) or d >= today
    prev = sum(1 for e in prev_events if is_upcoming(e))
    if not args.force:
        if n < args.min_events:
            print(f"GUARDRAIL: only {n} events (< --min-events {args.min_events}); refusing to write.",
                  file=sys.stderr)
            return 2
        if prev and n < args.min_ratio * prev:
            print(f"GUARDRAIL: {n} events is < {args.min_ratio:.0%} of the previous {prev}; "
                  f"looks like a partial scrape. Refusing to write (use --force to override).",
                  file=sys.stderr)
            return 2

    # --- meta / new flags ---
    new_ids, last_run_label = [], None
    summary, gaps, tracked = None, [], []
    if args.meta and os.path.exists(args.meta):
        try:
            md = json.load(open(args.meta, encoding="utf-8"))
            md = md.get("data", md)  # accept either the raw data object or a {data:...} envelope
            new_ids = md.get("newIds", []) or []
            last_run_label = md.get("lastRunLabel")
            # Narrative / radar fields the site renders (what's-new, coverage gaps,
            # tracked series). Passed straight through so the static site shows them.
            summary = md.get("summary")
            gaps = md.get("gaps", []) or []
            tracked = md.get("tracked", []) or []
        except Exception as e:
            print(f"  ! could not read meta {args.meta}: {e}", file=sys.stderr)

    new_set = set(new_ids)
    for e in events:
        if e["id"] in new_set:
            e["status"] = "new"

    # validate + report
    bad_dates = [e["id"] for e in events if e.get("date") and not iso_ok(e["date"])]
    for bid in bad_dates:
        print(f"  ! non-ISO date on {bid}; treating as undated", file=sys.stderr)
    for e in events:
        if e.get("date") and not iso_ok(e["date"]):
            e["date"] = None

    # --- carry past events forward (greyed history) ---
    # The digest only tracks upcoming events, so once an event's date passes it
    # disappears from the dump. To keep it visible (dimmed, like the frontend's
    # past styling) we re-add past-dated events from the previous out file for a
    # bounded window. They are frozen as last seen and marked "seen" (never "new").
    carried = 0
    if args.keep_past_days > 0 and prev_events:
        window_start = (datetime.date.fromisoformat(today)
                        - datetime.timedelta(days=args.keep_past_days)).isoformat()
        have = {e["id"] for e in events if e.get("id")}
        for pe in prev_events:
            d = pe.get("date")
            if not d or not iso_ok(d):
                continue
            if window_start <= d < today and pe.get("id") not in have:
                pe = dict(pe)
                if pe.get("status") == "new":
                    pe["status"] = "seen"
                pe.setdefault("status", "seen")
                events.append(pe)
                have.add(pe.get("id"))
                carried += 1
        if carried:
            print(f"carried {carried} past event(s) forward (>= {window_start})")

    events.sort(key=lambda e: (e.get("date") or "9999-99-99", -(e.get("score") or 0)))

    generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {
        "meta": {
            "generatedAt": generated_at,
            "lastRunLabel": last_run_label,
            "source": "SF AI Event Search digest (artifact DB)",
            "eventCount": len(events),
            "newCount": sum(1 for e in events if e.get("status") == "new"),
            "datedCount": sum(1 for e in events if e.get("date")),
            "pastCount": sum(1 for e in events if e.get("date") and e["date"] < today),
            "summary": summary,
            "gaps": gaps,
            "tracked": tracked,
        },
        "events": events,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    new_text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    old_text = open(args.out, encoding="utf-8").read() if os.path.exists(args.out) else ""
    # ignore the generatedAt line when deciding "changed" so an unchanged run is a no-op diff
    def strip_gen(t):
        return "\n".join(l for l in t.splitlines() if '"generatedAt"' not in l)
    changed = strip_gen(new_text) != strip_gen(old_text)

    open(args.out, "w", encoding="utf-8").write(new_text)
    print(f"wrote {args.out}: {out['meta']['eventCount']} events, "
          f"{out['meta']['newCount']} new, {out['meta']['datedCount']} dated"
          + ("" if changed else "  (no substantive change)"))
    # emit a machine-readable summary line for the sync task to parse
    print("SUMMARY " + json.dumps({"events": out["meta"]["eventCount"],
                                   "new": out["meta"]["newCount"],
                                   "changed": changed}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
