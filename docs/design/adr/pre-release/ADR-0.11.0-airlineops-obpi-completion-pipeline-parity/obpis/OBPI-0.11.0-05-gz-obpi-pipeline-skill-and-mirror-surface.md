---
id: OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface: Gz obpi pipeline skill and mirror surface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #5 -- "Port the `gz-obpi-pipeline` skill into `.gzkit` and sync mirror control surfaces."

**Status:** Draft

## Objective

Port the effective AirlineOps `gz-obpi-pipeline` skill into gzkit as a
canonical `.gzkit/skills/gz-obpi-pipeline/SKILL.md` surface, then mirror it to
the agent control surfaces so OBPI work executes through one staged
implement -> verify -> ceremony -> sync pipeline instead of freeform execution.
AirlineOps is the normative behavioral reference for this skill; gzkit should
adapt command vocabulary, not dilute the staged governance contract.

## Lane

**Heavy** -- This unit creates an operator-facing execution surface that shapes
how OBPI work is carried out across agents.

## Allowed Paths

- `.gzkit/skills/gz-obpi-pipeline/**` -- canonical skill surface
- `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- mirrored skill surfaces
- `docs/governance/GovZero/**` and `docs/user/commands/**` -- pipeline references and operator docs
- `src/gzkit/commands/**` -- help text or compatibility seams if the pipeline references native commands
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any skill port that leaves the canonical version only in a mirror surface
- Any skill text that bypasses heavy-lane human ceremony or sync stages
- New dependencies or unrelated runtime work

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The canonical skill MUST live in `.gzkit/skills/gz-obpi-pipeline/SKILL.md`.
1. REQUIREMENT: Mirror surfaces MUST be synchronized after the canonical skill is added or updated.
1. REQUIREMENT: The staged pipeline MUST preserve the AirlineOps sequencing model, including `--from=verify` and `--from=ceremony`.
1. REQUIREMENT: Skill text MUST map AirlineOps slash-command habits to gzkit-native control surfaces without losing governance rigor.
1. REQUIREMENT: AirlineOps behavior MUST be treated as the reference implementation unless a gzkit-specific compatibility constraint is documented explicitly.
1. NEVER: Leave the pipeline as an undocumented operator habit.
1. ALWAYS: Keep the evidence presentation and sync stages explicit in the skill body.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md`
- [ ] `.gzkit/skills/gz-obpi-audit/SKILL.md`
- [ ] `.gzkit/skills/gz-obpi-sync/SKILL.md`
- [ ] `.gzkit/skills/gz-session-handoff/SKILL.md`
- [ ] `docs/governance/GovZero/session-handoff-obligations.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical skill root exists: `.gzkit/skills/`
- [ ] Mirror sync surface exists: `uv run gz agent sync control-surfaces`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Validation commands pass for updated control surfaces
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [ ] REQ-0.11.0-05-01: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` exists and defines the staged OBPI execution flow.
- [ ] REQ-0.11.0-05-02: Mirror skill surfaces are synchronized and reference the same staged pipeline contract.
- [ ] REQ-0.11.0-05-03: The skill preserves evidence presentation, attestation, and sync stages as first-class steps.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests and validation commands pass
- [ ] **Code Quality:** Lint and type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .agents/skills/gz-obpi-pipeline/SKILL.md
  Updated .claude/skills/gz-obpi-pipeline/SKILL.md
  Updated .github/skills/gz-obpi-pipeline/SKILL.md
  Updated AGENTS.md
  Updated CLAUDE.md
  Updated .github/copilot-instructions.md
Sync complete.

$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Ran 334 tests in 4.504s
OK
```

### Code Quality

```text
$ uv run gz lint
Running linters...
All checks passed!
ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!
Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Documentation built in 0.75 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

## Key Proof

```text
Canonical gzkit now contains `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, and the
same staged pipeline contract is mirrored into `.agents/skills/`,
`.claude/skills/`, and `.github/skills/` by `uv run gz agent sync control-surfaces`.
Parity evidence for this tranche is recorded in:

- `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
```

### Implementation Summary

- Files created/modified:
  - `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
  - `src/gzkit/templates/agents.md`
  - `src/gzkit/templates/claude.md`
  - `src/gzkit/templates/copilot.md`
  - `docs/governance/governance_runbook.md`
  - `docs/user/concepts/workflow.md`
  - `docs/user/runbook.md`
  - `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
  - `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
  - mirrored skill/control-surface files regenerated via `gz agent sync control-surfaces`
- Tests added: none
- Date completed: 2026-03-11
- Attestation status: pending human review for Heavy-lane completion
- Defects noted:
  - `gz-obpi-lock` parity is still missing; pipeline currently fails closed for
    concurrent/shared-scope execution instead of claiming support.
  - plan-audit hook parity is still missing; the pipeline can consume a receipt
    if present but gzkit does not yet generate the AirlineOps receipt surface.

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
