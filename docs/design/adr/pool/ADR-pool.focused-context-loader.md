---
id: ADR-pool.focused-context-loader
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: openspec
---

# ADR-pool.focused-context-loader: Focused Context Loader

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add `gz context <adr-id>` to output a focused context payload containing only the
relevant ADR, its tasks, related test files, and applicable governance rules. Currently
gzkit loads AGENTS.md + CLAUDE.md + all skill files, consuming significant tokens
before the agent starts working. A focused loader reduces context noise and improves
agent accuracy on specific tasks.

---

## Target Scope

- New CLI command: `gz context <adr-id>` that outputs:
  - The target ADR file content
  - Associated task/OBPI brief contents
  - Related test file paths (discovered via @covers decorators or naming convention)
  - Applicable governance rules (lane, current gate, next required action)
- Output format: single markdown document suitable for piping to an AI agent
- Optional: `--slim` flag to omit governance rules (for non-governance agents)

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md — this is a complementary focused view.
- No automatic context injection into agent sessions (manual piping only).

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.prime-context-hooks (complementary, not dependent)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Context payload format is accepted.
3. ADR-to-test discovery mechanism is agreed upon.

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — load-on-demand context management
that only loads `project.md` + relevant `tasks.md` + specific specs, reducing token
consumption and preventing context drift.

---

## Notes

- This is the agent-efficiency counterpart to prime-context-hooks.
- Could replace the current AGENTS.md monolith with composable context fragments.
- Key metric: tokens consumed before agent starts productive work.
- Consider: integrate with Claude Code's `/context` or CLAUDE.md conventions?

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Complements CAP-13** (session-start orientation protocol). Spec proposes orientation as the delivery moment; this ADR defines the composable context fragments that feed it.
