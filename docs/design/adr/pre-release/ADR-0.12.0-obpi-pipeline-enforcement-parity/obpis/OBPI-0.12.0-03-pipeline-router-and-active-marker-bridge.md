---
id: OBPI-0.12.0-03-pipeline-router-and-active-marker-bridge
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.12.0-03-pipeline-router-and-active-marker-bridge: Pipeline router and active-marker bridge

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #3 - "OBPI-0.12.0-03: Port the pipeline router and active-marker bridge that hand approved plan work into `gz-obpi-pipeline`."

**Status:** Draft

## Objective

Port the AirlineOps `pipeline-router.py` hook into gzkit as a generated Claude
hook artifact with PASS-only routing behavior, and align the canonical
`gz-obpi-pipeline` Stage 1 marker contract so approved OBPI plans create the
per-OBPI and legacy compatibility markers consumed by later enforcement work.

## Lane

**Heavy** -- This unit ports an operator-facing runtime contract and updates the
canonical pipeline surface that later blocking hooks depend on.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/hooks/claude.py` -- generated Claude hook source of truth
- `tests/test_hooks.py` -- direct hook behavior and hook-generation coverage
- `.gzkit/skills/gz-obpi-pipeline/**` -- canonical Stage 1 / Stage 5 marker
  contract
- `.gzkit/skills/gz-plan-audit/**` -- receipt-consumer documentation that must
  stay honest about current enforcement state
- `.claude/hooks/**` and `.claude/settings.json` -- generated Claude hook
  artifacts and settings surface touched by control-surface sync
- `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- generated
  skill mirrors updated by control-surface sync
- `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`,
  `.github/discovery-index.json`, `.github/copilot-instructions.md`,
  `.copilotignore` -- generated control surfaces changed by sync
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- ADR, parity matrix, and OBPI evidence package for this tranche

## Denied Paths

- `../airlineops/**`
- `.claude/hooks/pipeline-gate.py`,
  `.claude/hooks/pipeline-completion-reminder.py` -- later hook OBPIs
- Active `.claude/settings.json` registration or hook ordering changes --
  reserved for `OBPI-0.12.0-06`
- New dependencies, CI files, lockfiles, or unrelated runtime changes

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The hook MUST be generated into
   `.claude/hooks/pipeline-router.py` from `src/gzkit/hooks/claude.py`.
1. REQUIREMENT: The router MUST emit pipeline instructions only when
   `.claude/plans/.plan-audit-receipt.json` exists, names an OBPI, and has
   verdict `PASS`.
1. REQUIREMENT: The router MUST stay silent for missing, corrupt, mismatched,
   or non-`PASS` receipts.
1. REQUIREMENT: The canonical `gz-obpi-pipeline` skill MUST document Stage 1
   creation of `.claude/plans/.pipeline-active-{OBPI-ID}.json` plus the legacy
   compatibility marker `.claude/plans/.pipeline-active.json`.
1. REQUIREMENT: Stage 5 cleanup in the canonical pipeline skill MUST state that
   the legacy marker is removed only when it still belongs to the same OBPI.
1. REQUIREMENT: Generated hook docs and plan-audit docs MUST state truthfully
   that `plan-audit-gate.py` and `pipeline-router.py` are ported but inactive
   until `OBPI-0.12.0-06` wires them into `.claude/settings.json`.
1. NEVER: Reinterpret the router into a blocking or corrective hook; routing is
   PASS-only and silent otherwise.
1. ALWAYS: Keep `.claude/settings.json` unchanged in this tranche.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `../airlineops/.claude/hooks/pipeline-router.py`
- [x] `src/gzkit/hooks/claude.py`
- [x] `tests/test_hooks.py`
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [x] `.gzkit/skills/gz-plan-audit/SKILL.md`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related OBPIs in the same ADR, especially `OBPI-0.12.0-02`,
      `OBPI-0.12.0-04`, `OBPI-0.12.0-06`, and `OBPI-0.12.0-07`

**Prerequisites (check existence, STOP if missing):**

- [x] Hook generator exists: `src/gzkit/hooks/claude.py`
- [x] Generated hook sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Receipt contract exists: `.gzkit/skills/gz-plan-audit/SKILL.md`
- [x] Pipeline skill surface exists: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`

**Existing Code (understand current state):**

- [x] Pattern to follow: `../airlineops/.claude/hooks/pipeline-router.py`
- [x] Test patterns: `tests/test_hooks.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run python -m unittest tests.test_hooks -v
uv run gz agent sync control-surfaces
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.12.0-03-01: `.claude/hooks/pipeline-router.py` exists as a
      generated hook and emits the `gz-obpi-pipeline` routing instruction only
      for PASS receipts that name an OBPI.
- [x] REQ-0.12.0-03-02: Missing, corrupt, or non-PASS receipts leave the router
      silent and do not mutate `.claude/settings.json`.
- [x] REQ-0.12.0-03-03: The canonical pipeline and plan-audit skill surfaces
      document the per-OBPI plus legacy compatibility marker contract
      truthfully, and generated mirrors/surfaces stay aligned.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded
- [x] Parity matrix updated to reflect the ported but inactive router artifact.
- [x] Pipeline and plan-audit skill surfaces updated to reflect the dual-write
      active-marker contract and inactive registration state.

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_hooks -v
Ran 28 tests in 0.287s

OK

$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .agents/skills/gz-obpi-pipeline/SKILL.md
  Updated .agents/skills/gz-plan-audit/SKILL.md
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/pipeline-router.py
  Updated .claude/hooks/plan-audit-gate.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .claude/skills/gz-obpi-pipeline/SKILL.md
  Updated .claude/skills/gz-plan-audit/SKILL.md
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .github/skills/gz-obpi-pipeline/SKILL.md
  Updated .github/skills/gz-plan-audit/SKILL.md
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz test
Running tests...
Ran 364 tests in 8.630s

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
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.75 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.276s
```

### Gate 5 (Human)

```text
Pending human attestation.
```

## Value Narrative

Before this tranche, gzkit had a plan-audit receipt and a documented pipeline
mandate, but no generated router artifact to carry approved plan work into
`gz-obpi-pipeline`, and the active marker contract still lived only as a loose
note. This OBPI ports the PASS-only router surface and tightens the Stage 1 /
Stage 5 marker contract so later enforcement hooks have a concrete bridge to
consume.

## Key Proof

```text
$ printf '{"cwd":"<temp-workspace>"}' | uv run python .claude/hooks/pipeline-router.py
OBPI plan approved: OBPI-0.12.0-03

REQUIRED: Execute the approved plan via the governance pipeline:
  /gz-obpi-pipeline OBPI-0.12.0-03

Do NOT implement directly; the pipeline preserves the required
verification, acceptance ceremony, and sync stages.

If implementation is already done, use --from=verify or --from=ceremony.
```

### Implementation Summary

- Files created/modified:
  `src/gzkit/hooks/claude.py`, `tests/test_hooks.py`,
  `.gzkit/skills/gz-obpi-pipeline/SKILL.md`,
  `.gzkit/skills/gz-plan-audit/SKILL.md`,
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`,
  and generated hook / skill mirror surfaces via `uv run gz agent sync control-surfaces`
- Tests added:
  PASS-only router coverage plus silent no-op coverage for missing, corrupt,
  missing-OBPI, and `FAIL` receipts
- Date completed:
  Pending human attestation
- Attestation status:
  Pending
- Defects noted:
  `uv run gz adr status ADR-0.12.0-obpi-pipeline-enforcement-parity --json`
  now reports completion-anchor drift on completed `OBPI-0.12.0-01`,
  `OBPI-0.12.0-02`, and `OBPI-0.12.0-07` because this tranche touched
  shared tracked files (`.claude/hooks/README.md` and the parity package).
  Registration remains intentionally deferred to `OBPI-0.12.0-06`.

## Human Attestation

- Attestor: `human:<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
