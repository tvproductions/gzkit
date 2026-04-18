---
id: OBPI-0.13.0-03-structured-stage-outputs
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 3
lane: Heavy
status: in_progress
---

# OBPI-0.13.0-03-structured-stage-outputs: Structured Stage Outputs

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #3 - "OBPI-0.13.0-03: Expose structured stage outputs for current stage, blockers, required human action, and next command or resume point"

**Status:** Completed

## Objective

Expose structured stage outputs for the active pipeline stage without adding a
new CLI flag or a second state file.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli.py` - pipeline runtime marker payload and stage-output helpers
- `tests/commands/test_obpi_pipeline.py` - runtime contract coverage for stage-output fields
- `tests/test_hooks.py` - compatibility coverage for richer marker payloads
- `docs/user/commands/obpi-pipeline.md` - operator-facing runtime contract
- `docs/governance/GovZero/obpi-runtime-contract.md` - canonical machine-readable marker contract
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` - canonical skill text for the marker payload contract
- `.agents/skills/gz-obpi-pipeline/SKILL.md` - Codex skill mirror
- `.claude/skills/gz-obpi-pipeline/SKILL.md` - Claude skill mirror
- `.github/skills/gz-obpi-pipeline/SKILL.md` - Copilot skill mirror
- `.claude/hooks/**` - regenerated hook wrappers and README from control-surface sync
- `.claude/settings.json` - regenerated Claude hook registration surface
- `.copilotignore` - regenerated Copilot control-surface ignore surface
- `.github/copilot-instructions.md` - regenerated Copilot control surface
- `.github/copilot/hooks/ledger-writer.py` - regenerated Copilot governance hook mirror
- `.github/discovery-index.json` - regenerated discovery surface
- `.gzkit/manifest.json` - regenerated control-surface manifest metadata
- `AGENTS.md` - generated control surface synced from canonical skills/manifest
- `CLAUDE.md` - generated control surface synced from canonical skills/manifest
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md` - this brief and completion evidence
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md` - parent ADR checklist synchronization during completion accounting

## Denied Paths

- new CLI flags, JSON stdout modes, or alternate runtime subcommands
- new repository-local state files beyond `.claude/plans/.pipeline-active*.json`
- structured blocker-envelope schemas beyond simple `list[str]` blocker output
- Heavy/Foundation gate-enforcement policy changes owned by `OBPI-0.13.0-04`
- new dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The existing active pipeline marker files MUST remain the only machine-readable runtime store for this OBPI.
1. REQUIREMENT: Marker payloads MUST expose `blockers`, `required_human_action`, `next_command`, and `resume_point` in addition to the stage-state fields from `OBPI-0.13.0-02`.
1. REQUIREMENT: Full launch MUST expose `next_command=uv run gz obpi pipeline <OBPI> --from=verify` and `resume_point=verify`.
1. REQUIREMENT: Verify success MUST expose `next_command=uv run gz obpi pipeline <OBPI> --from=ceremony` and `resume_point=ceremony`.
1. REQUIREMENT: Verify failure MUST leave markers in place and rewrite them with populated `blockers`, `next_command=null`, and `resume_point=verify`.
1. REQUIREMENT: Ceremony launch MUST expose the required human action and the guarded-sync next command.
1. NEVER: This OBPI MUST NOT add a second durable state file, a new CLI flag, or the future structured blocker-envelope schema.
1. ALWAYS: Existing marker consumers that only depend on `obpi_id` or earlier stage-state fields MUST remain compatible.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [x] Related OBPIs in same ADR, especially `OBPI-0.13.0-02`, `OBPI-0.13.0-04`, and `OBPI-0.13.0-05`

**Prerequisites (check existence, STOP if missing):**

- [x] Existing `obpi pipeline` runtime and marker helpers exist in `src/gzkit/cli.py`
- [x] Existing marker consumer compatibility tests exist in `tests/test_hooks.py`

**Existing Code (understand current state):**

- [x] Pattern to follow: `OBPI-0.13.0-02` marker payload contract and `OBPI-0.13.0-01` pipeline runtime output
- [x] Test patterns: `tests/commands/test_obpi_pipeline.py`, `tests/test_hooks.py`

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
uv run python -m unittest tests.test_hooks -v
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.13.0-03-01: Full launch writes marker payloads that expose `blockers=[]`, `required_human_action=null`, `next_command=uv run gz obpi pipeline <OBPI> --from=verify`, and `resume_point=verify`.
- [x] REQ-0.13.0-03-02: Verify success writes marker payloads that expose the follow-up `--from=ceremony` command and `resume_point=ceremony` before cleanup.
- [x] REQ-0.13.0-03-03: Verify failure leaves markers in place with structured blocker strings, `next_command=null`, and `resume_point=verify`.
- [x] REQ-0.13.0-03-04: Ceremony launch writes marker payloads that expose the required human action and guarded-sync next command.
- [x] REQ-0.13.0-03-05: [doc] Existing hook consumers remain compatible when markers include the new stage-output fields.

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
Ran 8 tests in 0.292s
OK

$ uv run python -m unittest tests.test_hooks -v
Ran 45 tests in 0.727s
OK

$ uv run gz obpi pipeline OBPI-0.13.0-03-structured-stage-outputs --from=verify
PASS uv run python -m unittest tests.commands.test_obpi_pipeline -v
PASS uv run python -m unittest tests.test_hooks -v
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
Ran 392 tests in 10.331s
OK
Tests passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Documentation built in 0.98 seconds
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
Human attestation received on 2026-03-14: "attest completed and git sync"
```

### Value Narrative

Before this OBPI, the active marker payload only exposed stage-state metadata.
Agents and operators could infer the next step from prose output, but they
could not read a stable machine-readable contract for blockers, required human
action, or resume guidance. After this OBPI, the existing marker files expose
those stage outputs directly while keeping the same file locations and
preserving backward compatibility for current consumers.

### Key Proof

```text
$ uv run gz obpi pipeline OBPI-0.13.0-03-structured-stage-outputs --from=verify
...
Marker payload now includes:
- blockers
- required_human_action
- next_command
- resume_point
```

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `tests/commands/test_obpi_pipeline.py`,
  `tests/test_hooks.py`, runtime/operator docs, canonical and mirrored
  `gz-obpi-pipeline` skills, and generated control surfaces from
  `uv run gz agent sync control-surfaces`.
- Tests added: structured stage-output assertions for full launch, verify
  success/failure, ceremony launch, and hook compatibility with richer marker
  payloads.
- Date completed: 2026-03-14
- Attestation status: human attestation recorded
- Re-baseline anchor refreshed: 2026-03-15 at `a587714` after completion
  receipt reconciliation cleared stale shared-scope ADR drift.
- Defects noted: repaired this brief's placeholder scope/requirements defect
  before implementation; the runtime still warns when the plan-audit receipt is
  missing; mixed-tree Stage 5 sync was explicitly approved by the human
  attestor for this closeout.

## Tracked Defects

- GHI-12 (closed): Recurring false OBPI anchor drift in shared-scope ADRs
- GHI-13 (closed): Status misclassifies completed OBPIs as drift when anchor freshness degrades

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed and git sync
- Date: 2026-03-14

---

**Brief Status:** Completed

**Date Completed:** 2026-03-14

**Evidence Hash:** a587714
