---
id: ADR-0.14.0
status: Draft
semver: 0.14.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-14
---

# ADR-0.14.0: Multi-Agent Instruction Architecture Unification

## Intent

gzkit already provides a multi-agent governance system, but its instruction delivery
surfaces have drifted into a mixed model: shared rules, tool-specific adapters,
path-scoped behavior, recurring workflows, and machine-local settings are not cleanly
separated. That creates context bloat, duplicate guidance, stale instruction files,
and inconsistent behavior between Codex, Claude Code, and Copilot-facing surfaces.

This ADR defines the full instruction-architecture upgrade for gzkit without replacing
the existing governance system. The goal is to make gzkit's current multi-agent model
more native to each agent runtime, lower-drift to maintain, easier to audit, and
better suited to future subproject-specific rules.

## Decision

Adopt a canonical-shared-plus-thin-adapters instruction architecture:

1. `AGENTS.md` becomes the canonical shared source of durable repo instructions.
2. `CLAUDE.md` becomes a thin Claude adapter that points to shared canon and only
   carries Claude-native orientation plus references to Claude-only rule surfaces.
3. Shared path-scoped rules move closer to work through nested `AGENTS.md` support,
   while Claude-only path-scoped rules use native `.claude/rules/`.
4. Root control surfaces are reduced to durable high-signal rules; recurring workflows
   move into skills/playbooks instead of always-loaded root memory.
5. gzkit gains first-class auditing for stale, conflicting, unreachable, and
   foreign-project instruction surfaces.
6. Machine-local agent configuration is explicitly separated from repo-tracked control
   surfaces, and generated surface sync becomes deterministic and self-verifying.
7. gzkit adds an eval/readiness layer for instruction behavior so agent architecture is
   tested by outcomes, not only by file presence.

The target architecture is:

- Canonical shared instruction model rendered into root `AGENTS.md`
- Thin vendor adapters such as `CLAUDE.md` and `.github/copilot-instructions.md`
- Nested `AGENTS.md` files for shared subtree rules
- `.claude/rules/` only for genuinely Claude-only or Claude-path-scoped behavior
- Skills/playbooks for recurring chores such as sync, audits, and migrations
- Repo-tracked config for shared policy, plus explicit local-only config handling
- Readiness and audit commands that validate behavior, reachability, and drift

## Consequences

### Positive

- Shared governance rules live in one canonical source instead of being duplicated
  across vendor root files.
- Codex and Claude each use their native instruction-loading model more directly.
- Root instruction files become smaller, cheaper to load, and easier to audit.
- Stale or airlineops-specific instruction carryover becomes detectable instead of
  silently shaping agent behavior.
- Future subtree-specific rules can be added without bloating repo-root memory.
- gzkit becomes a stronger multi-agent toolkit because it models shared, vendor, path,
  workflow, and local config surfaces as distinct concerns.

### Negative

- gzkit's config, templates, sync flow, validation, and docs will all need coordinated
  changes to preserve current behavior while introducing the new architecture.
- Existing repositories bootstrapped by gzkit may need migration help for older control
  surface layouts.
- Introducing nested/shared rules and Claude-native rules adds more surface types, so
  the product must enforce clear placement rules to avoid replacing one drift pattern
  with another.

## Target Scope

- Refactor control-surface generation so one canonical instruction model feeds
  `AGENTS.md`, `CLAUDE.md`, and Copilot-facing output.
- Add first-class path-scoped rule support for nested `AGENTS.md` and
  `.claude/rules/`.
- Slim root instruction files so durable repo invariants stay loaded while recurring
  workflows move into skills and thin wrappers.
- Add instruction auditing for stale paths, foreign-project carryover, policy
  conflicts, and generated-surface drift.
- Separate machine-local config from repo-tracked policy surfaces and make sync output
  deterministic.
- Add an eval and readiness layer with positive and negative controls across supported
  agent surfaces.

## Non-Goals

- Do not replace gzkit's existing governance model, ledger model, or skill system.
- Do not make `CLAUDE.md` the only source of truth for shared instructions.
- Do not rely on user-local Codex fallback filename configuration as a repository
  contract.
- Do not preserve stale `.github/instructions` or hook-based routing solely for
  backward compatibility when native surfaces exist.
- Do not force dual maintenance of equivalent `AGENTS.md` and `CLAUDE.md` trees.

## Dependencies

- **Related runtime surfaces**: `src/gzkit/sync.py`, `src/gzkit/hooks/claude.py`,
  `src/gzkit/quality.py`, `src/gzkit/validate.py`
- **Related control surfaces**: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
  `.github/instructions/`, `.claude/hooks/`, `.claude/settings.json`
- **Related commands**: `uv run gz agent sync control-surfaces`,
  `uv run gz validate --documents`, `uv run gz readiness audit`

## Migration Principles

1. Preserve gzkit's current governance semantics while changing how instruction
   surfaces are modeled and delivered.
2. Prefer one shared source of truth plus thin adapters over duplicated vendor trees.
3. Move shared rules closer to the code they govern; move recurring chores out of
   always-loaded root files.
4. Keep hook-based automation for enforcement where useful, but do not depend on hooks
   as the primary memory-delivery mechanism when native agent surfaces exist.
5. Treat stale, unreachable, or foreign-project instructions as product defects, not
   benign leftovers.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.14.0-01: Establish the canonical instruction data model with `AGENTS.md`
      as shared source and thin vendor adapter renders.
- [ ] OBPI-0.14.0-02: Add native path-scoped instruction support with nested
      `AGENTS.md` for shared subtree rules and `.claude/rules/` for Claude-only rules.
- [ ] OBPI-0.14.0-03: Slim generated root control surfaces and move recurring workflows
      out of always-loaded root files into skills/playbooks.
- [ ] OBPI-0.14.0-04: Add instruction auditing that detects stale, conflicting,
      unreachable, or foreign-project rules and load-surface drift.
- [ ] OBPI-0.14.0-05: Separate machine-local from repo-local agent config and enforce
      deterministic generated-surface sync across adapters and mirrors.
- [ ] OBPI-0.14.0-06: Add an instruction-architecture eval suite and readiness checks
      with positive and negative controls across supported agent surfaces.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Seeded from repository audit findings on 2026-03-14:

- Root `AGENTS.md` and `CLAUDE.md` duplicate substantial shared guidance.
- Claude-only path behavior currently depends on `.claude/hooks/instruction-router.py`
  reading `.github/instructions/*.instructions.md` instead of native `.claude/rules/`.
- Several instruction files in `.github/instructions/` reference airlineops/opsdev
  paths or policies that do not match gzkit's current codebase.
- `.claude/settings.local.json` is tracked despite being machine-local configuration.
- Checked-in Claude settings drift from the current generator/tests, weakening trust in
  generated control surfaces.
- Root `AGENTS.md` currently carries a large generated skill inventory and deep workflow
  prose that should be loaded on demand instead of in every session.
- Codex natively consumes `AGENTS.md`, while Claude natively consumes `CLAUDE.md` and
  `.claude/rules/`; the current repo treats those surfaces too much like peers.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Audit basis: repository instruction-system analysis dated 2026-03-14
- [ ] Tests: `tests/`
- [ ] Docs: `docs/`
- [ ] Control surfaces: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`
- [ ] Canonical skills: `.gzkit/skills/`
- [ ] Claude hook router basis: `.claude/hooks/instruction-router.py`
- [ ] Foreign/stale instruction basis: `.github/instructions/`
- [ ] Config drift basis: `.claude/settings.json`, `.claude/settings.local.json`

## Alternatives Considered

- Keep dual-maintained `AGENTS.md` and `CLAUDE.md` trees as peers.
- Make `CLAUDE.md` the canonical source and rely on Codex fallback filenames.
- Continue the current mixed model and only patch individual drift defects.

These alternatives were rejected because they either increase drift risk, depend on
user-local tool configuration, or fail to give gzkit a clean multi-agent architecture.

Specific rejection rationale:

- **Dual-maintained trees**: duplicates already drifted in this repo and would keep
  auditing expensive.
- **Claude-canonical**: Codex fallback discovery is not a portable repo contract.
- **Patch-only maintenance**: leaves the load model unclear and keeps giant root files,
  unreachable rules, and local-config leakage in place.

## Notes

- This ADR upgrades how gzkit behaves; it does not replace the existing gzkit system.
- The expected end state is a cleaner multi-agent toolkit with clearer separation
  between shared policy, vendor adapters, path-scoped rules, recurring workflows, and
  machine-local configuration.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.14.0 | Pending | | | |

