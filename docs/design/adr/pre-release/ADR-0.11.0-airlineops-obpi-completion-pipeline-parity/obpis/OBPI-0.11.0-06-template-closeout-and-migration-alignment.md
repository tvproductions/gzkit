---
id: OBPI-0.11.0-06-template-closeout-and-migration-alignment
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 6
lane: Lite
status: Completed
---

# OBPI-0.11.0-06-template-closeout-and-migration-alignment: Template, closeout, and migration alignment

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #6 -- "Align templates, closeout guidance, and operator docs to the faithful AirlineOps completion pipeline."

**Status:** Completed

## Objective

Align gzkit templates, operator docs, and closeout surfaces so the faithful
OBPI completion pipeline is visible and executable across drafting,
implementation, attestation, and audit without drifting between runtime logic
and written guidance.

## Lane

**Lite** -- This unit aligns documentation, templates, and generated guidance
without changing a command/API/schema/runtime surface. The parent ADR remains
Heavy, so human attestation still applies at closeout by inheritance.

## Allowed Paths

- `.gzkit/skills/**`, `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- template and mirrored skill surfaces
- `docs/governance/GovZero/**` -- canonical ceremony and transaction docs
- `docs/user/commands/**`, `docs/user/concepts/**`, `docs/user/runbook.md` -- operator-facing guidance
- `src/gzkit/commands/**` -- closeout/help text alignment if required
- `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/**` and `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- migration notes or cross-links if required
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any template change that weakens fail-closed scope or evidence rules
- Any closeout guidance that implies Gate 5 can be automated
- New dependencies or unrelated runtime feature work

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Templates MUST reflect the same transaction and evidence rules enforced by runtime surfaces.
1. REQUIREMENT: Operator docs MUST describe the faithful OBPI completion flow from draft through attestation and reconciliation.
1. REQUIREMENT: If mirrored skill/control surfaces change, `gz agent sync control-surfaces` MUST be run and captured in evidence.
1. NEVER: Leave 0.7.0 / 0.10.0 and 0.11.0 guidance in contradictory states.
1. ALWAYS: Preserve human closeout authority explicitly in docs and examples.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.32-govzero-obpi-transaction-protocol/ADR-0.0.32-govzero-obpi-transaction-protocol.md`
- [ ] `docs/governance/GovZero/validation-receipts.md`
- [ ] `docs/user/commands/obpi-status.md`
- [ ] `docs/user/commands/obpi-reconcile.md`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/`
- [ ] `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/`

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical skill/template directories exist
- [ ] Closeout and attestation command docs exist

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Validation commands pass for updated docs/surfaces
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs and templates updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Parent Heavy inheritance)

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

- [x] REQ-0.11.0-06-01: [doc] Templates express the faithful transaction and evidence rules consistently with runtime surfaces.
- [x] REQ-0.11.0-06-02: [doc] Operator docs describe one coherent OBPI completion and closeout flow.
- [x] REQ-0.11.0-06-03: [doc] Migration notes eliminate contradictory guidance across 0.7.0, 0.10.0, and 0.11.0 surfaces.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests and validation commands pass
- [x] **Code Quality:** Lint and type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Human attestation recorded and completion ready

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Running tests...
Ran 350 tests in 8.242s

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
INFO    -  Documentation built in 0.70 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.252s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-12: "attest completed"
```

### Value Narrative

Before this tranche, gzkit still carried contradictory habits across doctrine,
templates, generated control surfaces, and operator docs: Heavy-lane guidance
was broader than the intended runtime-contract trigger, the OBPI template still
advertised legacy verification commands, and workflow docs still implied older
post-ceremony habits. Now the canon, the brief templates, the generated agent
surfaces, and the operator runbooks all describe one coherent OBPI-first flow:
verify, attest when required, run guarded `git sync`, then record final OBPI
completion accounting and reconcile status from the synced state.

### Key Proof

```text
The regenerated operator contract in `AGENTS.md` now states both sides of the
doctrine and workflow fix:

- Heavy is reserved for command/API/schema/runtime-contract changes used by
  humans or external systems.
- Documentation/process/template-only changes stay Lite unless they change one
  of those external surfaces.
- The pipeline enforces `verify -> ceremony -> guarded git sync -> completion accounting`.
- Generated command examples now use `uv run gz test` and gz-native verification
  defaults from `.gzkit/manifest.json`.

The Gate 4 scenario in `features/heavy_lane_gate4.feature` now asserts that
generated surface directly.
```

### Implementation Summary

- Files created/modified: `docs/governance/GovZero/charter.md`, `docs/user/concepts/lanes.md`, `docs/user/concepts/workflow.md`, `docs/user/concepts/lifecycle.md`, `docs/user/concepts/closeout.md`, `docs/user/runbook.md`, `docs/user/commands/index.md`, `src/gzkit/templates/obpi.md`, `src/gzkit/templates/agents.md`, `src/gzkit/templates/claude.md`, `src/gzkit/sync.py`, `src/gzkit/cli.py`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.gzkit/manifest.json`, `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`, `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`, and regenerated mirror/control-surface files under `.agents/`, `.claude/`, and `.github/`
- Tests added: updated `tests/test_sync.py`, updated `tests/test_validate.py`, updated `features/heavy_lane_gate4.feature`
- Date completed: 2026-03-12
- Attestation status: human attestation recorded
- Defects noted: none

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-12

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** 808cd95
