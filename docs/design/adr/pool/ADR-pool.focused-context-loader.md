# ADR-pool.focused-context-loader: Focused Context Loader

## Status

Proposed

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

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — load-on-demand context management
that only loads `project.md` + relevant `tasks.md` + specific specs, reducing token
consumption and preventing context drift.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: ADR-pool.prime-context-hooks (related but independent)

---

## Notes

- This is the agent-efficiency counterpart to prime-context-hooks
- Could replace the current AGENTS.md monolith with composable context fragments
- Key metric: tokens consumed before agent starts productive work
- Consider: integrate with Claude Code's `/context` or CLAUDE.md conventions?
