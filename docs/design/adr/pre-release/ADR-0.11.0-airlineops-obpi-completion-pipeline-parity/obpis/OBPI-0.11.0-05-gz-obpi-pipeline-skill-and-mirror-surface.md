---
id: OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface: Gz obpi pipeline skill and mirror surface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #5 -- "Port the `gz-obpi-pipeline` skill into `.gzkit` and sync mirror control surfaces."

**Status:** Completed

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

- [x] `AGENTS.md`
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [x] `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md`
- [x] `.gzkit/skills/gz-obpi-audit/SKILL.md`
- [x] `.gzkit/skills/gz-obpi-sync/SKILL.md`
- [x] `.gzkit/skills/gz-session-handoff/SKILL.md`
- [x] `docs/governance/GovZero/session-handoff-obligations.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical skill root exists: `.gzkit/skills/`
- [x] Mirror sync surface exists: `uv run gz agent sync control-surfaces`

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

- [x] Human attestation recorded

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

- [x] REQ-0.11.0-05-01: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` exists and defines the staged OBPI execution flow.
- [x] REQ-0.11.0-05-02: Mirror skill surfaces are synchronized and reference the same staged pipeline contract.
- [x] REQ-0.11.0-05-03: The skill preserves evidence presentation, attestation, and sync stages as first-class steps.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests and validation commands pass
- [x] **Code Quality:** Lint and type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .agents/skills/gz-obpi-pipeline/SKILL.md
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .claude/skills/gz-obpi-pipeline/SKILL.md
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .github/skills/gz-obpi-pipeline/SKILL.md
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Running tests...
Ran 349 tests in 7.990s

OK

Tests passed.
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
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.76 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
5 scenarios passed, 0 failed, 0 skipped
27 steps passed, 0 failed, 0 skipped
Took 0min 0.212s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-12: "I'll attest completed"
```

## Value Narrative

Before this tranche, gzkit had a canonical `gz-obpi-pipeline` skill, but the
post-attestation closeout order still allowed completion accounting to be
captured from a dirty or unsynced repository state. Now the pipeline contract
is explicit across canon, mirrors, generated agent surfaces, and operator docs:
guarded `git sync` runs before final completion receipt/accounting and the
later brief/ADR reconciliation steps.

## Key Proof

```text
Canonical gzkit now contains `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, and the
same staged pipeline contract is mirrored into `.agents/skills/`,
`.claude/skills/`, and `.github/skills/` by `uv run gz agent sync control-surfaces`.
The generated operator contract in `AGENTS.md` now states that the pipeline
enforces `verify -> ceremony -> guarded git sync -> completion accounting`, and
the Gate 4 scenario in `features/heavy_lane_gate4.feature` asserts that wording
explicitly. Parity evidence for this tranche is recorded in:

- `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
```

### Implementation Summary

- Files created/modified:
  - `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
  - `.agents/skills/gz-obpi-pipeline/SKILL.md`
  - `.claude/skills/gz-obpi-pipeline/SKILL.md`
  - `.github/skills/gz-obpi-pipeline/SKILL.md`
  - `src/gzkit/templates/agents.md`
  - `src/gzkit/templates/claude.md`
  - `src/gzkit/templates/copilot.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.github/copilot-instructions.md`
  - `docs/governance/GovZero/obpi-transaction-contract.md`
  - `docs/governance/GovZero/obpi-runtime-contract.md`
  - `docs/governance/GovZero/validation-receipts.md`
  - `docs/user/commands/git-sync.md`
  - `docs/user/commands/index.md`
  - `docs/user/commands/obpi-emit-receipt.md`
  - `tests/test_sync.py`
  - `features/heavy_lane_gate4.feature`
  - `features/steps/gz_steps.py`
  - mirrored skill/control-surface files regenerated via `gz agent sync control-surfaces`
- Tests added:
  - `tests/test_sync.py::test_sync_generated_surfaces_include_guarded_git_sync_pipeline_contract`
  - `features/heavy_lane_gate4.feature` scenario asserting generated pipeline guidance
- Date completed: 2026-03-12
- Attestation status: human attestation recorded
- Defects noted:
  - `gz-obpi-lock` parity is still missing; pipeline currently fails closed for concurrent/shared-scope execution instead of claiming support.
  - plan-audit hook parity is still missing; the pipeline can consume a receipt if present but gzkit does not yet generate the AirlineOps receipt surface.
  - lane doctrine may currently classify process/documentation surface changes more broadly than intended by the operator rule "Heavy only when APIs, commands, or other human/system-used runtime surfaces change"; carry this into OBPI-06 governance/template alignment.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** —
