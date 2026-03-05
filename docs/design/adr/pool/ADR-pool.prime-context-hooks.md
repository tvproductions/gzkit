---
id: ADR-pool.prime-context-hooks
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-pool.execution-memory-graph
---

# ADR-pool.prime-context-hooks: Dynamic Prime Context via CLI + Hooks

## Status

Proposed

## Date

2026-03-01

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Agent context engineering and session reliability

---

## Intent

Add a `gz prime` runtime briefing surface that keeps agent instructions current
through hook-driven context injection, with CLI as the primary integration path.

---

## Target Scope

- Introduce `gz prime` for compact, machine- and human-readable runtime context:
  - active ready work
  - key blockers
  - missing proof targets (`ADR/OBPI/REQ`) that block completion
  - completion protocol
  - current governance constraints
- Integrate prime refresh into supported hook events (session start, pre-compaction).
- Define override/customization behavior for local operator tuning.
- Keep `AGENTS.md` and mirrored control surfaces concise by delegating volatile
  runtime guidance to `gz prime`.

---

## Non-Goals

- No deprecation of canonical instruction/control-surface files.
- No requirement for MCP transport to access runtime context.
- No duplication of full runbook content inside prime output.

---

## Dependencies

- **Blocks on**: ADR-pool.execution-memory-graph
- **Blocked by**: ADR-pool.execution-memory-graph

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Prime output contract and token budget are approved.
2. Hook integration behavior is validated for supported agents.
3. Drift policy between static control surfaces and prime output is defined.

---

## Notes

- This ADR is explicitly CLI + hooks first, matching current `gzkit` operating posture.
- Prime output should be graph-backed and proof-aware, not prose-only summaries.
