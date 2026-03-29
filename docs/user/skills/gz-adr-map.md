# /gz-adr-map

Build ADR-to-artifact traceability by combining governance state queries with repository search.

---

## Purpose

When you need to understand how an ADR connects to its implementation — which
tests cover it, which briefs are linked, and whether evidence is complete —
`/gz-adr-map` orchestrates the queries that produce that picture. It is a
workflow skill, not a single command: it chains `gz state`, repository grep, and
`gz adr audit-check` into a traceability map that shows where an ADR's evidence
lives in the codebase.

## When to Use

Invoke `/gz-adr-map` when you need to audit the connection between an ADR and
its implementation artifacts. Common situations:

- **Before closeout** — verify all OBPIs have linked tests and evidence before
  starting the closeout ceremony.
- **During review** — understand which test files cover a specific ADR when
  reviewing a pull request.
- **After implementation** — confirm that `@covers` decorators in tests correctly
  reference the ADR.

This skill fits into the governance workflow between implementation and closeout.
See [Runbook: Closeout Protocol](../runbook.md) for the full sequence.

## What to Expect

The skill runs three steps sequentially:

1. **ADR/OBPI graph** — queries the governance ledger via `gz state --json` and
   displays the ADR's OBPI decomposition and status.
2. **Test coverage scan** — greps the `tests/` directory for `@covers("ADR-...")`
   decorators that reference the target ADR.
3. **Audit check** — runs `gz adr audit-check` to validate linked brief evidence.

Output is a narrative summary of findings: which OBPIs are complete, which tests
reference the ADR, and any gaps flagged by the audit check. Typical runtime is
under 10 seconds. No files are modified — this is a read-only workflow.

**Success** looks like: all OBPIs linked, tests found for each brief, audit
check passes.

**Failure** looks like: missing `@covers` decorators, OBPIs without evidence, or
audit-check errors identifying unlinked briefs.

## Invocation

```text
/gz-adr-map ADR-0.3.0
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `ADR-X.Y.Z` | yes | The ADR identifier to map |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-adr-map/SKILL.md` | Agent execution instructions | Read |

This skill has no additional assets. It relies entirely on `gz` CLI commands
and repository search.

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz state`](../commands/state.md) | Provides the ADR/OBPI graph data |
| [`gz adr audit-check`](../commands/adr-audit-check.md) | Validates brief evidence linkage |
| [`/gz-adr-verification`](gz-adr-verification.md) | Deeper ADR evidence and linkage verification |
| [`/gz-adr-autolink`](gz-adr-autolink.md) | Maintains `@covers` decorator links in tests |
| [`/gz-closeout`](gz-closeout.md) | Typically follows after traceability is confirmed |
