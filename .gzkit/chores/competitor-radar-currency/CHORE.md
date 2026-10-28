# CHORE: Competitor Radar Currency (Landscape Refresh)

**Lane:** Lite
**Slug:** `competitor-radar-currency`

---

## Overview

Keep gzkit's competitor radar current. The radar covers spec-driven development,
agent skills and agent-workflow tools. It is run by the `gz-competitor-radar`
skill and recorded under `artifacts/reports/competitor-radar/`. The registry and
the monthly scan JSON are the source of truth. The Markdown reports are
generated from them.

**Mode: scan + route.** The chore runs the skill's workflow:

1. refresh every registry competitor from current official sources;
2. actively discover new candidates;
3. write the month's scan;
4. render and validate;
5. open the grill discussion for each suggested move.

It never mutates governance artifacts. Moves route only after the operator rules
them, through the skill's routes: an existing or new pool ADR, an open feature
ADR, a GHI via `ghi-author`, an explicit rejection, or discussion only.

**Why this chore exists:** the radar is meant to run monthly, but nothing
scheduled it. The skill said so itself: *"Monthly is the intended cadence, but
nothing schedules it: the radar runs when the operator invokes it."* The
baseline scan was 2026-05, and no scan ran after it until 2026-10. A landscape
that moves monthly went unread for five months.

## Source

Operator, 2026-10-26, verbatim: *"add this to it: https://github.com/t3dotgg/tstack,
refresh the landscape and get it on a chore rotation (staleness) - yes, chore it."*

## Policy and Guardrails

- **Read-only against governance.** The scan writes only its own report; routed
  moves land through their own governed paths.
- **Network:** Required (official sites, repositories, release notes).
- **Primary sources, never memory.** Every snapshot cites the sources it was
  refreshed from (the skill's workflow step 1).
- **Generated Markdown is never hand-edited.** Change the JSON or the renderer,
  rerender, and revalidate.
- **Absorb mechanisms, never copy brands.** Admission of a new competitor
  answers the skill's admission questions
  (`.gzkit/skills/gz-competitor-radar/references/grill-questions.md`).

## Cadence

**Mechanically gated.** The maximum age of the last scan is this chore's
declared `staleness.periodDays` in `registry.json`. `scripts/check_proof_freshness.py`
reads it, and criterion 1 of `acceptance.json` enforces it. The witness is
`artifacts/reports/competitor-radar/index.md`, which the renderer rewrites
whenever a new month's scan is added. The interval is not restated here: a value
written in a Markdown doc is illustrative, never authoritative (`AGENTS.md`
§ Governance doctrine surfaces).

## Workflow

Follow `.gzkit/skills/gz-competitor-radar/SKILL.md` § Workflow in order.

### 1. Refresh sources — observe

Refresh sources for every competitor in
`artifacts/reports/competitor-radar/registry.json`, and run active discovery.

### 2. Author the month's scan — observe

Create the month's scan with
`uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py new-scan --month YYYY-MM`,
and author its snapshots, discovered candidates and suggested moves from the
evidence.

### 3. Render and validate — observe

`uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py render`, then
`uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py validate`.

### 4. Grill discussion — propose

Open the grill discussion, one question at a time. Record the answers into the
scan JSON, rerender and revalidate.

### 5. Route moves — propose

Route approved moves through their own governed paths. Record rejections.

## Acceptance Criteria

See `acceptance.json`:

1. the last scan is within the declared period (`check_proof_freshness.py`);
2. the registry, scans and generated Markdown validate (`radar.py validate`).
