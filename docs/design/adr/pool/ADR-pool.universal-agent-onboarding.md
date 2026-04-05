---
id: ADR-pool.universal-agent-onboarding
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.universal-agent-onboarding: Universal Agent Onboarding Protocol

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Create a vendor-neutral `gz onboard` command that orients any new agent session
in under 30 seconds — regardless of whether the agent is Claude Code, Codex,
Copilot, Gemini, or a future vendor. Currently, each vendor surface has its own
onboarding path (CLAUDE.md, copilot-instructions.md, AGENTS.md) and cold-start
sessions waste significant context tokens re-discovering project structure,
conventions, and current work state. A unified onboarding protocol reduces
time-to-productive-work and ensures consistent constraint delivery.

---

## Target Scope

- New CLI command: `gz onboard [--vendor <name>] [--adr <id>]` that outputs a focused onboarding payload:
  - Project identity (name, version, architecture summary)
  - Active governance constraints (lane, gates, prohibited patterns)
  - Current work state (active ADRs, in-progress OBPIs, recent handoffs)
  - Vendor-specific adaptations (tool names, output format preferences)
- Output format: single markdown document optimized for agent context injection.
- Optional `--resume <handoff-id>` flag to combine onboarding with handoff resumption.
- Onboarding payload is deterministic and reproducible (same inputs produce same output).

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md — onboarding is a focused summary, not the full contract.
- No automatic session detection or vendor fingerprinting.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.focused-context-loader (complementary — focused-context is per-ADR, onboarding is per-session), ADR-pool.per-command-persona-context (onboarding could set initial persona)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Onboarding payload format and content scope are accepted.
3. Vendor adaptation strategy (compile-time templates vs. runtime flags) is decided.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 2: Multi-Agent Teams.
The report observes that multi-vendor agent environments are becoming standard,
but cold-start overhead and inconsistent context loading remain friction points.
AirlineOps already operates three agent vendors with divergent onboarding paths —
this ADR unifies them behind a single protocol.

---

## Notes

- AirlineOps `/start` skill is the closest precedent — it surfaces domain constraints at session start.
- The gap: `/start` is Claude Code-specific and reads `.github/instructions/` files directly rather than producing a portable payload.
- Key metric: tokens consumed before first productive action.
- Consider: should `gz onboard` be the default preamble for `gz plan` and `gz specify`?
- Consider: integration with CLAUDE.md `@AGENTS.md` reference pattern for Claude Code.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-13** (session-start orientation protocol). Spec proposes `gz status --orientation` as the delivery mechanism; this pool ADR's `--vendor`/`--resume` flags remain valid extensions.
