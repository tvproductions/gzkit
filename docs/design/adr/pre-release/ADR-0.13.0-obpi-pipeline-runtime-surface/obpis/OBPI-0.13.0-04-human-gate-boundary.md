---
id: OBPI-0.13.0-04-human-gate-boundary
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.13.0-04-human-gate-boundary: Human Gate Boundary

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #4 - "OBPI-0.13.0-04: Keep Stage 4 human attestation as an explicit authority boundary for Heavy and Foundation work"

**Status:** Completed

## Objective

Keep Stage 4 human attestation as an explicit authority boundary only for
Heavy and Foundation work, while leaving Lite OBPI ceremony flow non-blocking.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli.py` - ceremony-stage runtime behavior and marker payload policy
- `tests/commands/test_obpi_pipeline.py` - command-contract coverage for Heavy, Lite, and Foundation-parent ceremony paths
- `docs/user/commands/obpi-pipeline.md` - operator-facing command contract for Stage 4 behavior
- `docs/governance/GovZero/obpi-runtime-contract.md` - canonical active-marker semantics for `required_human_action`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` - canonical skill ritual text for Stage 4 behavior
- `.agents/skills/gz-obpi-pipeline/SKILL.md` - Codex mirror regenerated from the canonical skill
- `.claude/skills/gz-obpi-pipeline/SKILL.md` - Claude mirror regenerated from the canonical skill
- `.github/skills/gz-obpi-pipeline/SKILL.md` - Copilot mirror regenerated from the canonical skill
- `.claude/hooks/**` - regenerated hook wrappers and README from control-surface sync
- `.claude/settings.json` - regenerated Claude hook registration surface
- `.copilotignore` - regenerated Copilot control-surface ignore file
- `.github/copilot-instructions.md` - regenerated Copilot control surface
- `.github/copilot/hooks/ledger-writer.py` - regenerated Copilot governance hook mirror
- `.github/discovery-index.json` - regenerated discovery surface
- `.gzkit/manifest.json` - regenerated control-surface manifest metadata
- `AGENTS.md` - regenerated control surface synced from canonical skill/manifest state
- `CLAUDE.md` - regenerated control surface synced from canonical skill/manifest state
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-04-human-gate-boundary.md` - this brief and evidence
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md` - parent checklist synchronization during completion accounting

## Denied Paths

- new CLI flags, alternate subcommands, or new marker payload keys
- parent-ADR execution-mode activation (`exception`/SVFR) or self-close semantics
- `src/gzkit/ledger.py`, `src/gzkit/schemas/**`, or receipt-schema changes
- `src/gzkit/hooks/**` - hook/runtime convergence belongs to `OBPI-0.13.0-05`
- new dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Stage 4 policy MUST reuse the existing Heavy/Foundation attestation rule already used by OBPI completion accounting instead of introducing a second policy implementation.
1. REQUIREMENT: Ceremony-stage markers MUST populate `required_human_action` only when the parent ADR requires human attestation for OBPI completion.
1. REQUIREMENT: Ceremony CLI output MUST require explicit human attestation for Heavy and Foundation parents and MUST NOT present it as mandatory for Lite parents.
1. REQUIREMENT: Foundation parents (`ADR-0.0.x`) MUST keep the human-attestation boundary even when the inherited lane resolves to Lite.
1. NEVER: This OBPI MUST NOT add new marker fields, new CLI flags, or enable `exception` execution mode.
1. ALWAYS: Canonical skill text, mirrored skill text, user docs, and runtime behavior MUST describe the same Stage 4 rule.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [x] Related OBPIs in same ADR, especially `OBPI-0.13.0-03` and `OBPI-0.13.0-05`

**Prerequisites (check existence, STOP if missing):**

- [x] Existing `obpi pipeline` runtime helpers exist in `src/gzkit/cli.py`
- [x] Existing attestation policy helper exists in `src/gzkit/cli.py`
- [x] Existing command-contract coverage exists in `tests/commands/test_obpi_pipeline.py`

**Existing Code (understand current state):**

- [x] Pattern to follow: completed receipt attestation rule in `src/gzkit/cli.py`
- [x] Test patterns: `tests/commands/test_obpi_pipeline.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

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
uv run python -m unittest tests.commands.test_obpi_pipeline -v
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.13.0-04-01: `gz obpi pipeline <OBPI> --from=ceremony` under a Heavy parent keeps the explicit attestation requirement in both CLI output and active marker payload.
- [x] REQ-0.13.0-04-02: `gz obpi pipeline <OBPI> --from=ceremony` under a Lite parent leaves `required_human_action=null` and does not claim human attestation is mandatory.
- [x] REQ-0.13.0-04-03: `gz obpi pipeline <OBPI> --from=ceremony` under a Foundation parent (`ADR-0.0.x`) still requires explicit human attestation even when the inherited lane is Lite.
- [x] REQ-0.13.0-04-04: User docs, runtime contract docs, and the canonical/mirrored pipeline skill all describe the same Heavy/Foundation-only Stage 4 authority boundary.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.commands.test_obpi_pipeline -v
Ran 10 tests in 0.299s
OK

$ uv run gz obpi pipeline OBPI-0.13.0-04-human-gate-boundary --from=verify
PASS uv run python -m unittest tests.commands.test_obpi_pipeline -v
PASS uv run gz validate --documents
PASS uv run gz lint
PASS uv run gz typecheck
PASS uv run gz test
PASS uv run mkdocs build --strict
PASS uv run -m behave features/
Verification completed.
```

### Code Quality

```text
$ uv run gz validate --documents
All validations passed.

$ uv run gz lint
Running linters...
All checks passed!
ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!
Type check passed.

$ uv run gz test
Ran 396 tests in 11.214s
OK
Tests passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Documentation built in 0.97 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-14: "attest completed"
```

### Value Narrative

Before this OBPI, Stage 4 always presented human attestation as a mandatory
step. That was correct for Heavy and Foundation work, but it was wrong for Lite
OBPIs and created drift between the pipeline surface and the canonical receipt
rule. After this OBPI, the pipeline runtime and marker payload preserve human
attestation as an explicit authority boundary only where GovZero requires it.

### Key Proof

```text
$ uv run gz obpi pipeline OBPI-0.13.0-04-human-gate-boundary --from=ceremony
Ceremony
- Present a value narrative.
- Present one key proof example.
- Present the verification outputs and files changed.
- Obtain explicit human attestation before completion accounting.
```

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `tests/commands/test_obpi_pipeline.py`, Stage 4 docs/runtime contract text, the canonical pipeline skill, and regenerated control-surface mirrors from `uv run gz agent sync control-surfaces`
- Tests added: Lite-parent and Foundation-parent ceremony coverage in `tests/commands/test_obpi_pipeline.py`
- Date completed: 2026-03-14
- Attestation status: human attestation recorded
- Re-baseline anchor refreshed: 2026-03-15 at `a587714` after completion
  receipt reconciliation cleared stale self/ADR bookkeeping drift.
- Defects noted: the OBPI brief started as an unfilled template and was rewritten into a concrete scope/evidence contract as part of this work

## Tracked Defects

- GHI-13 (closed): Status misclassifies completed OBPIs as drift when anchor freshness degrades

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-14

---

**Brief Status:** Completed

**Date Completed:** 2026-03-14

**Evidence Hash:** a587714
