---
id: ADR-pool.skill-behavioral-hardening
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: https://github.com/obra/superpowers
---

# ADR-pool.skill-behavioral-hardening: Skill Behavioral Hardening

## Status

Proposed

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance skill robustness

---

## Intent

Enrich existing gzkit governance skills with behavioral defense patterns harvested from the superpowers project. gzkit skills today are procedural ("run this command, validate this output") but do not defend against agent rationalization — the primary failure mode where agents convince themselves to skip governance steps. Superpowers has proven that explicit anti-rationalization tables, circuit breakers, and stricter RED-GREEN-REFACTOR enforcement dramatically reduce this failure mode.

This ADR does not create new governance infrastructure. It strengthens the skill layer that already exists by adding behavioral defense at the OBPI execution level.

---

## Target Scope

### Enrich existing skills with anti-rationalization defense

Add rationalization tables and circuit breaker patterns to governance skills where agents most commonly take shortcuts:

- **`test`** — Rewrite from skeleton stub to enforce strict RED-GREEN-REFACTOR with anti-rationalization table. TDD is already a gzkit feature (Gate 2); this makes enforcement stricter at the skill level.
- **`gz-obpi-pipeline`** — Add rationalization defense for skipping verification, claiming completion without evidence, and bypassing ceremony. Add explicit circuit breakers.
- **`gz-plan`** — Add defense against rushing decomposition, skipping discovery questions, and premature ADR generation. Add dialogue discipline (one question at a time, YAGNI enforcement).
- **`git-sync`** — Add defense against bypassing lint/test gates and direct push.

### Create new methodology skills

Fill genuine gaps where gzkit has no coverage:

- **`gz-debug`** — Systematic 4-phase debugging methodology (root cause investigation, pattern analysis, hypothesis testing, implementation) with 3-fix circuit breaker.
- **`gz-verify`** — Verification-before-completion evidence gate. Prevents premature completion claims across all pipeline stages.
- **`gz-review-response`** — Technical evaluation of code review feedback, not performative agreement.

### Cross-skill integration

Wire new and enriched skills into the existing skill ecosystem with correct cross-references and control surface sync.

---

## Non-Goals

- No new CLI commands, ledger event types, or pipeline stage changes.
- No duplication of superpowers skills available at runtime via the installed plugin (brainstorming, plan writing, subagent orchestration, git worktrees, skill authoring TDD).
- No changes to the gate covenant or lane model.
- No new governance infrastructure — all changes are SKILL.md markdown files.

---

## Dependencies

- **Blocks on**: None. This work is independent and can proceed immediately.
- **Related**: ADR-pool.task-level-governance (the TASK tier will consume these behavioral patterns once formalized).

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Anti-rationalization table format is agreed (consistent structure across all enriched skills).
2. Circuit breaker pattern is agreed (failure count, escalation action, human gate).
3. New skill scope is confirmed (gz-debug, gz-verify, gz-review-response are the right set).
4. Acceptance criteria can be defined for each enriched/new skill independently.

---

## Notes

- Superpowers (github.com/obra/superpowers) demonstrates that treating agent rationalization as the primary failure mode and defending against it explicitly with tables of excuses and rebuttals is highly effective.
- gzkit's hooks already enforce governance mechanically (pipeline-gate blocks writes, plan-audit-gate blocks plan exit). This ADR adds rhetorical defense at the skill layer to catch drift BEFORE hooks need to block.
- TDD is already Gate 2 in gzkit. The `test` skill rewrite makes RED-GREEN-REFACTOR enforcement stricter, not adding a new capability.
- The three new skills (gz-debug, gz-verify, gz-review-response) have no superpowers equivalent that integrates with gzkit's governance model (ledger, pipeline, OBPI scope).

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-15, CAP-16, CAP-17, CAP-19** (native TDD, debugging, code review, anti-rationalization). Spec adds competitive source attribution and design rationale from superpowers, spec-kit, GSD, and BMAD patterns.
