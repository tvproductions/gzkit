---
id: OBPI-0.13.0-05-runtime-engine-integration
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.13.0-05-runtime-engine-integration: Runtime Engine Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #5 - "Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose"

**Status:** Completed

## Objective

Make `uv run gz obpi pipeline` the single runtime authority for OBPI execution
sequencing, marker state, and next-command guidance, while reducing the skill,
Claude hook surface, templates, and docs to thin adapters over that runtime.

## Lane

**Heavy** - This OBPI changes the runtime contract exposed through hooks,
generated control surfaces, and operator-facing command guidance.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` - shared runtime helpers and canonical command/message contract
- `src/gzkit/cli.py` - canonical pipeline command implementation
- `src/gzkit/hooks/claude.py` - generated hook wrappers over the runtime contract
- `src/gzkit/templates/agents.md` - generated shared root surface wording
- `src/gzkit/templates/claude.md` - generated Claude adapter wording
- `src/gzkit/templates/copilot.md` - generated Copilot adapter wording
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` - thin alias skill contract
- `docs/user/commands/obpi-pipeline.md` - canonical public command contract
- `docs/user/concepts/workflow.md` - workflow guidance
- `docs/user/concepts/lanes.md` - lane/runtime guidance
- `docs/user/runbook.md` - operator loop examples
- `tests/commands/test_obpi_pipeline.py` - runtime command tests
- `tests/test_hooks.py` - Claude hook generation/runtime tests
- `tests/test_sync.py` - generated control-surface sync assertions
- `tests/test_templates.py` - template semantics assertions
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-05-runtime-engine-integration.md` - this brief

## Denied Paths

- `.gzkit/ledger.jsonl` - do not edit directly
- `docs/design/adr/**` outside this brief - no parent ADR rewrites in this OBPI
- `.claude/settings.local.json` - local config is unrelated here
- New dependencies, CI files, or lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `uv run gz obpi pipeline` remains the canonical runtime surface for OBPI execution.
2. REQUIREMENT: Hook scripts, templates, and the `gz-obpi-pipeline` skill MUST delegate to the canonical runtime contract instead of restating stage semantics in detail.
3. REQUIREMENT: Shared command/message helpers MUST produce the canonical next-command and re-entry text used by wrappers.
4. REQUIREMENT: Marker payload semantics, verification command parsing, and closeout sequencing MUST remain unchanged for the CLI runtime.
5. NEVER: Introduce a second primary runtime contract in hooks, skills, or root control surfaces.
6. NEVER: Bypass the guarded `uv run gz git-sync --apply --lint --test` step before final completion accounting guidance.
7. ALWAYS: Update docs and tests in the same patch when operator-facing wording changes.

> STOP-on-BLOCKERS: if shared runtime extraction would change marker payload shape or CLI behavior beyond this OBPI, stop and surface blockers instead of silently widening the contract.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - full runtime-surface context

**Context:**

- [x] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [x] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-01-runtime-command-contract.md`
- [x] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-02-persist-stage-state.md`
- [x] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md`
- [x] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-04-human-gate-boundary.md`
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [x] `src/gzkit/cli.py`
- [x] `src/gzkit/hooks/claude.py`
- [x] `src/gzkit/templates/agents.md`
- [x] `src/gzkit/templates/claude.md`
- [x] `src/gzkit/templates/copilot.md`
- [x] `docs/user/commands/obpi-pipeline.md`
- [x] `docs/user/concepts/workflow.md`
- [x] `docs/user/runbook.md`
- [x] `tests/commands/test_obpi_pipeline.py`
- [x] `tests/test_hooks.py`
- [x] `tests/test_sync.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests updated with implementation
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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.13.0-05-01: Given a PASS plan-audit receipt, when the Claude pipeline router or gate surfaces guidance, then they point to `uv run gz obpi pipeline` as the canonical runtime and treat `/gz-obpi-pipeline` as a thin alias.
- [x] REQ-0.13.0-05-02: Given full, verify, and ceremony pipeline entrypoints, when the runtime emits marker state and next commands, then wrappers and reminders rely on those canonical command strings instead of duplicating stage logic.
- [x] REQ-0.13.0-05-03: Given generated AGENTS, CLAUDE, Copilot, skill, and user-doc surfaces, when they describe post-plan OBPI execution, then they identify the CLI runtime as canonical and keep wrapper guidance shallow.

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

- [x] Intent and scope recorded on 2026-03-14

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_templates tests.test_sync tests.test_hooks tests.commands.test_obpi_pipeline
Ran 110 tests in 3.242s
OK

$ uv run gz test
Running tests...
Ran 397 tests in 38.251s
OK
Tests passed.
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
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Documentation built in 1.18 seconds
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

## Value Narrative

Before this OBPI, the CLI already knew the real pipeline contract but the skill,
hook scripts, and generated control surfaces restated that behavior in their
own prose. That created drift risk and made the runtime surface look less
authoritative than it actually was. After this OBPI, wrappers should delegate
to one shared runtime contract and operator guidance should consistently point
back to the canonical CLI surface.

## Key Proof

Focused proof:

- `uv run gz obpi pipeline OBPI-0.13.0-01-runtime-command-contract`
- generated `pipeline-router.py` output now names `uv run gz obpi pipeline OBPI-0.12.0-03` first and keeps `/gz-obpi-pipeline OBPI-0.12.0-03` as the thin alias
- generated `pipeline-completion-reminder.py` now re-enters through the marker's canonical `next_command` instead of restating a parallel closeout workflow

### Implementation Summary

- Files created/modified: `src/gzkit/pipeline_runtime.py`, `src/gzkit/cli.py`, `src/gzkit/hooks/claude.py`, `src/gzkit/templates/{agents,claude,copilot}.md`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, user docs under `docs/user/**`, regenerated control surfaces and mirrors, `tests/test_hooks.py`, `tests/test_sync.py`, `tests/test_templates.py`, `features/obpi_anchor_drift.feature`, this brief
- Tests added: expanded existing hook/template/sync assertions plus updated BDD expectation for anchor-state semantics
- Date completed: 2026-03-14
- Attestation status: human attestation recorded
- Defects noted: stale BDD expectation still asserted the pre-fix `runtime_state=drift` semantics and was corrected to the current completed-plus-stale-anchor contract

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-14

---

**Brief Status:** Completed

**Date Completed:** 2026-03-14

**Evidence Hash:** pending-sync-anchor
