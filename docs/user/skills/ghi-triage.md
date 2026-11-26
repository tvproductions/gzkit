# /ghi-triage

Evaluate and triage all open GitHub Issues (GHIs).

---

## Purpose

Runs the bundled `scripts/triage.py` to fetch every open GHI, score routing
(direct-fix vs OBPI-ceremony vs close-as-duplicate), assign urgency, detect
duplicates, and render a routing table plus copy/paste short list. Replaces
the ad-hoc pattern of orchestrating `gh`, `git`, and Python by hand when the
operator wants to plan the next patch window or sweep the open queue.

## When to Use

Reach for `/ghi-triage` when reviewing the open-issue queue, before a
planning session, or when deciding which GHIs to pull into the next patch
window. The output orders issues by urgency and routing: every issue that is
not a duplicate routes `direct-fix`, because a GHI authorizes direct repair
(`AGENTS.md` § Defect-fix routing), and a duplicate routes `close`. Triage
never routes to an OBPI; it surfaces architectural work as a hint for the
operator.

## What to Expect

The skill runs **exactly one** Bash command — the bundled triage script —
and presents its markdown output verbatim. No repo files are modified. The
script takes optional flags:

```text
/ghi-triage                  # triage all open GHIs
/ghi-triage --label defect   # filter to one label
/ghi-triage --limit 25       # cap the scan
```

## Output

The rendered table has six columns: issue number, label class, routing
decision, urgency, title, and rationale. A copy/paste short list follows,
grouped by urgency, in the form `#NNN — <route> — <title>`.

## Related

- [`/ghi-author`](ghi-author.md) — author a new GHI when a finding deserves
  its own trackable home
- [`/ghi-close`](ghi-close.md) — execute and close a triaged GHI with
  verifiable evidence
- `AGENTS.md` § Defect-fix routing — the routing thresholds the script
  applies
