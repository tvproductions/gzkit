# /gz-competitor-radar

Run the monthly competitor radar for spec-driven development and adjacent agent-workflow tools.

---

## Purpose

`/gz-competitor-radar` keeps a governed report artifact under
`artifacts/reports/competitor-radar/`. The report tracks competitor status,
trajectory, strength patterns, and suggested gzkit opportunities without
mutating ADRs, GHIs, or pool entries before a grill/design discussion.

## When to Use

Invoke this skill for the monthly competitor scan, for an ad-hoc scan when a
new comparator appears, or before deciding whether competitor pressure warrants
a new pool ADR, an existing pool update, an open ADR amendment, a GHI, or an
explicit rejection.

## What to Expect

The skill reads current official sources, updates JSON source artifacts, renders
Markdown projections, validates that Markdown against JSON byte-for-byte, and
opens a grill queue for suggested moves. The operator answers forcing-function
questions; the agent authors the JSON and generated Markdown.

## Invocation

```text
/gz-competitor-radar
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-competitor-radar/SKILL.md` | Canonical skill contract | Read |
| `.gzkit/skills/gz-competitor-radar/scripts/radar.py` | Portable renderer and validator | Execute |
| `artifacts/reports/competitor-radar/registry.json` | Competitor registry source | Read/Write |
| `artifacts/reports/competitor-radar/scans/YYYY-MM.json` | Monthly scan source | Read/Write |
| `artifacts/reports/competitor-radar/index.md` | Generated report index | Generated |
| `artifacts/reports/competitor-radar/YYYY-MM.md` | Generated monthly report | Generated |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-design`](gz-design.md) | Routes accepted recommendations into design discussion |
| [`/ghi-author`](ghi-author.md) | Files trackable issues when accepted opportunities need GHI routing |
| [`/gz-agent-sync`](gz-agent-sync.md) | Synchronizes this skill into agent mirrors after edits |
| [skills index](index.md) | Browse the full skill catalog |
