---
id: ADR-pool.airlineops-direct-governance-migration
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.airlineops-direct-governance-migration: AirlineOps Direct Governance Migration

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Migrate AirlineOps from its current bespoke governance implementation (AGENTS.md,
CLAUDE.md, `.github/instructions/`, `.github/skills/`, `.claude/skills/`) to
gzkit as the primary governance authority. AirlineOps invented GovZero through
100+ work items of iterative learning, but the governance artifacts are now
duplicated — gzkit codifies the protocol while AirlineOps maintains its own
parallel implementation. This ADR plans the consolidation so AirlineOps becomes
a gzkit-governed project rather than a governance framework that happens to also
be an airline scheduling platform.

---

## Target Scope

- **Phase 1 — Authority Inversion**: Replace `AGENTS.md` as the authority root with `.gzkit.json` + gzkit CLI. AGENTS.md becomes a generated summary (read-only view of gzkit state), not a hand-maintained contract.
- **Phase 2 — Skill Migration**: Migrate governance skills from `.github/skills/gz-*` and `.claude/skills/gz-*` into gzkit's skill registry. AirlineOps retains domain-specific skills (warehouse, CLI, etc.) but governance skills live in gzkit.
- **Phase 3 — Gate Unification**: Replace AirlineOps' `opsdev gates` with `gz gates` as the canonical gate runner. `opsdev gates` becomes a thin wrapper or is retired.
- **Phase 4 — Instruction Consolidation**: Merge `.github/instructions/*.instructions.md` domain rules into gzkit's constraint library (ADR-pool.constraint-library). AirlineOps keeps domain-specific constraints; governance constraints move to gzkit.
- **Phase 5 — Hook Migration**: Migrate governance hooks (pipeline-router, instruction-router, OBPI enforcement) from `.claude/hooks/` to gzkit-managed hooks. AirlineOps retains project-specific hooks only.
- Define a compatibility contract: during migration, both old and new paths work. Hard cutover happens per-phase, not all-at-once.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No changes to AirlineOps domain logic (warehouse, CLI, models, etc.).
- No removal of CLAUDE.md or GEMINI.md vendor overlays — these adapt gzkit output to vendor-specific formats.
- No breaking changes to AirlineOps development workflow during migration — each phase must be independently deployable.

---

## Dependencies

- **Blocks on**: ADR-pool.constraint-library (Phase 4 depends on constraint model), ADR-pool.universal-agent-onboarding (Phase 1 depends on onboarding replacing AGENTS.md cold-start)
- **Blocked by**: gzkit reaching sufficient maturity (gate verification, skill mirroring, OBPI pipeline must all be functional)
- **Related**: ADR-0.3.0-airlineops-canon-reconciliation (established AirlineOps as canonical source; this ADR inverts that relationship), ADR-0.9.0-airlineops-surface-breadth-parity (mapped the surface area that needs migrating)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. gzkit reaches feature parity for gates, skills, and OBPI pipeline.
3. Phase ordering and compatibility contract are accepted.
4. AGENTS.md generation strategy (template vs. query) is decided.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 1: SDLC Changes and Trend 2: Multi-Agent Teams.
The report observes that governance frameworks are becoming first-class
infrastructure rather than ad-hoc convention files. AirlineOps proved the
GovZero model works; gzkit extracts it into reusable infrastructure. This ADR
closes the loop by making AirlineOps the first production consumer of gzkit
as an external dependency rather than an embedded framework.

---

## Notes

- This is the capstone ADR: it validates gzkit by proving it can govern the project that created it.
- AirlineOps currently has 40+ foundation ADRs, 70+ skills across 3 mirrors, 20+ instruction files, and 10+ hooks. Migration scope is significant.
- Key risk: the migration must not disrupt active development. Phase-by-phase with rollback capability is essential.
- ADR-0.3.0 established AirlineOps as the canonical source for gzkit reconciliation. This ADR inverts that: gzkit becomes canonical, AirlineOps consumes.
- Consider: should gzkit be a Python dependency of AirlineOps (`uv add gzkit`) or remain a CLI tool invoked via `uvx gz`?
- Consider: what is the minimum viable gzkit version that can govern AirlineOps? This determines when this ADR can be promoted.
- The "generated AGENTS.md" model means the document becomes a build artifact — deterministic, reproducible, always in sync with gzkit state.
