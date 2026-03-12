---
id: ADR-pool.agent-role-specialization
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.agent-role-specialization: Agent Role Specialization Boundaries

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Define a universal agent role taxonomy in gzkit so that multi-agent coordination
has explicit boundaries, handoff protocols, and conflict resolution rules —
independent of any specific vendor. Currently, AirlineOps defines agent profiles
in AGENTS.md (Copilot, Codex, Claude Code) but these describe vendor capabilities,
not functional roles. When multiple agents work concurrently (Exception mode),
there is no formal model for who does what, how work is partitioned, or how
conflicts between concurrent agents are resolved.

---

## Target Scope

- Define a role taxonomy with clear boundaries: Planner (ADR/OBPI design), Implementer (code + tests), Reviewer (QC + verification), Narrator (docs + evidence presentation).
- Add role metadata to OBPI briefs: `assigned_role` field indicating which role category the brief targets.
- Define handoff protocol between roles: what artifacts a Planner produces that an Implementer consumes, what an Implementer produces that a Reviewer consumes.
- Define conflict resolution: when two agents touch the same file, which role takes precedence.
- Add `gz roles` CLI surface for querying role assignments and detecting unassigned work.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No vendor-specific role bindings (roles are abstract; vendor assignment is a deployment concern).
- No enforcement of one-agent-per-role — a single agent can fill multiple roles sequentially.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.per-command-persona-context (personas are cognitive stances; roles are work boundaries), ADR-pool.obpi-pipeline-runtime-surface (pipeline could route by role)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Role taxonomy is accepted (number of roles, boundary definitions).
3. Conflict resolution strategy is decided.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 2: Multi-Agent Teams.
The report documents the emergence of specialized agent roles (planning, coding,
reviewing, testing) and notes that organizations achieving the best outcomes
define explicit role boundaries rather than letting agents self-organize. GovZero's
Exception mode enables multi-agent parallelism but lacks the role taxonomy to
make it predictable.

---

## Notes

- AirlineOps ADR-0.0.11 (Agent Collaboration Profiles) was the first attempt at this but scoped to VS Code/Copilot only.
- The gap: ADR-0.0.11 describes vendor capabilities, not abstract roles. Adding Codex and Claude Code showed the vendor-specific approach doesn't scale.
- Key principle: roles are project-level abstractions; vendor assignment is a session-level decision.
- Consider: should roles be static per ADR or dynamic per OBPI?
- Consider: how does role specialization interact with the OBPI lock model?
