# /ghi-close

Do the work described in a GHI, then close it with verifiable evidence.

---

## Purpose

Drives an open GHI to its terminal state: read the GHI, execute the
prescribed fix (routed per AGENTS.md § Defect-fix routing), verify the
landed artifacts, and close the issue with a citation comment. The skill
refuses to close on narrative alone — every disposition cites a commit SHA,
ADR ID, OBPI ID, or ARB receipt ID.

## When to Use

Invoke `/ghi-close <id>` when an operator wants a specific GHI resolved end
to end, during triage passes, or at the end of an ADR closeout when the
open-GHI list needs to be driven to zero. This is the downstream complement
to [`/ghi-author`](ghi-author.md).

## What to Expect

Four-phase flow: **read** → **execute** → **verify** → **close**. The
execute phase may route to a direct `fix(...)` commit or to the OBPI
ceremony depending on the routing thresholds. The close comment names the
disposition (`fixed`, `superseded`, `withdrawn`, `duplicate`, `won't-fix`)
and cites the verifiable artifact. `gh issue close` fires with a
`--comment` payload.

## Invocation

```text
/ghi-close <id>
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `<id>` | yes | GHI number (integer; `#` prefix optional) |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/ghi-close/SKILL.md` | Agent execution instructions | Read |
| `AGENTS.md § Defect-fix routing` | Routing thresholds for Phase 2 | Read |
| `.claude/rules/gh-cli.md` | `gh` CLI guardrails | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/ghi-author`](ghi-author.md) | Upstream authoring surface |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Ceremony route when heavy/foundation triggers fire |
| [`/gz-obpi-reconcile`](gz-obpi-reconcile.md) | Propagate closure to brief evidence |
| [`gh issue close`](https://cli.github.com/manual/gh_issue_close) | CLI the skill wraps |
