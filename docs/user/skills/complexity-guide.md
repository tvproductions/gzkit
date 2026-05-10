# /complexity-guide

Preview authoring-time complexity hints before committing.

---

## Purpose

`/complexity-guide` wraps the `gz complexity guide` CLI verb from the
four-ADR complexity-doctrine cluster (ADR-0.0.27 through ADR-0.0.30). It
gives operators a first-stop authoring-time preview of functions approaching
the warn threshold — use it while editing to catch growing complexity before
xenon-as-gate would trip at commit time.

## When to Use

Two operator moments trigger this skill:

1. **Ad-hoc authoring-time review** — preview hints for a file or directory
   while actively editing code. The guide surfaces functions in the `advise`
   band (approaching the warn threshold) before they cross into `warn` or
   `block`.
2. **Preflight complexity check** — before committing, check which functions
   are growing toward the warn threshold so refactor decisions land at design
   time rather than gate time.

For functions that have already crossed into `warn` or `block`, use
`/complexity-advisor` instead — that is the trigger-time surface.

See [Runbook: Complexity doctrine surfaces](../runbook.md) for the full
workflow context.

## What to Expect

- **Output:** In-line hint prose with one block per advise-band crossing
  (archetype, band position, doctrinal-frame headline, recommended move).
  Pass `--json` for machine-readable `AuthoringHint` Pydantic serialization.
- **Duration:** Seconds for a single file; may take longer on large directory
  trees.
- **Side effects:** None. The guide never blocks and emits no ledger events.
- **Success:** Exit 0 always — this surface does not use exit 3.

## Invocation

```text
/complexity-guide
/complexity-guide src/gzkit/commands/validate.py
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `path` | yes | File or directory to analyze |
| `--json` | no | Emit machine-readable JSON array |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/complexity-guide/SKILL.md` | Agent execution instructions | Read |
| `.gzkit/rules/complexity-thresholds.json` | Canonical threshold table (ADR-0.0.28) | Read |
| `docs/user/manpages/complexity-guide.md` | CLI verb manpage | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/complexity-advisor`](complexity-advisor.md) | Trigger-time advisor for functions that have already crossed warn/block |
| [`gz complexity guide`](../manpages/complexity-guide.md) | Underlying CLI verb this skill wraps |
