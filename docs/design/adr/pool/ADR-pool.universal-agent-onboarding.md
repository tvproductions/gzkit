---
id: ADR-pool.universal-agent-onboarding
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026, gsd
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

### Bootstrap Chain (`gz bootstrap`)

One-command guided experience for new projects or new contributors that chains the full governance scaffolding sequence:

- `gz bootstrap` runs the complete first-time setup as a guided flow:
  1. **Project identity** — name, description, tech stack, repository conventions (from existing code or user input)
  2. **PRD creation** — `gz prd` with guided interview (what are we building, for whom, why)
  3. **Constitution** — `gz constitute` with project-specific constraints derived from PRD
  4. **First ADR** — `gz plan` with interview for the first feature or foundation work
  5. **OBPI co-creation** — `gz specify` for each ADR checklist item
  6. **Governance scaffolding** — `gz init` for ledger, config, surfaces if not already present
- **Resumable:** If interrupted, `gz bootstrap --resume` detects which steps completed (via ledger events) and picks up where it left off.
- **Opinionated defaults:** For each step, proposes sensible defaults from code analysis (similar to assumptions mode in ADR-pool.pre-planning-interview). Human confirms or corrects.
- **Output:** Fully scaffolded project with PRD, Constitution, first ADR with OBPIs, and governance infrastructure. Ready for `gz next` to route to first implementation.
- **Versus `gz onboard`:** Bootstrap is for first-time project setup (creates artifacts). Onboard is for session-start orientation (reads existing artifacts). Bootstrap runs once; onboard runs every session.

**Inspired by:** [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-new-project` — takes a user from zero to full project scaffold (vision, requirements, roadmap, state) in one guided session.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md — onboarding is a focused summary, not the full contract.
- No automatic session detection or vendor fingerprinting.
- Bootstrap does not replace individual `gz prd`, `gz plan`, `gz specify` commands — it chains them. Each step is independently usable.
- Bootstrap does not auto-approve — every artifact requires human confirmation before proceeding to the next step.

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
4. Bootstrap chain: step sequence and resumability mechanism are validated against at least 2 real project bootstraps.
5. Bootstrap chain: relationship to `gz init` (existing scaffolding) is clearly delineated — no overlapping responsibilities.

---

## Inspired By

- [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 2: Multi-Agent Teams. Multi-vendor agent environments are becoming standard, but cold-start overhead and inconsistent context loading remain friction points.
- [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-new-project` — single-command project scaffold that creates vision, requirements, roadmap, and state documents in one guided session. gzkit's bootstrap chain adapts this for the PRD→Constitution→ADR→OBPI artifact sequence.

---

## Notes

- AirlineOps `/start` skill is the closest precedent — it surfaces domain constraints at session start.
- The gap: `/start` is Claude Code-specific and reads `.github/instructions/` files directly rather than producing a portable payload.
- Key metric: tokens consumed before first productive action.
- Consider: should `gz onboard` be the default preamble for `gz plan` and `gz specify`?
- Consider: integration with CLAUDE.md `@AGENTS.md` reference pattern for Claude Code.
- Bootstrap may be too large for a single pool ADR. Consider: `gz onboard` and `gz bootstrap` as separate promoted ADRs if scope is unwieldy.
- Bootstrap's resumability depends on ledger events marking each step's completion — aligns with ADR-pool.agent-execution-intelligence CAP-22 (`gz next`) which also reads ledger state to infer next action.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-13** (session-start orientation protocol). Spec proposes `gz status --orientation` as the delivery mechanism; this pool ADR's `--vendor`/`--resume` flags remain valid extensions.
