---
id: OBPI-0.12.0-04-write-time-pipeline-gate
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.12.0-04-write-time-pipeline-gate: Write-time pipeline gate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #4 - "OBPI-0.12.0-04: Port the write-time pipeline gate for `src/` and `tests/`."

**Status:** Completed

## Objective

Port the AirlineOps `pipeline-gate.py` hook into gzkit as a generated Claude
`PreToolUse` surface that blocks `Write|Edit` operations under `src/` and
`tests/` until the active pipeline marker for the PASS-audited OBPI exists,
while leaving `.claude/settings.json` registration to `OBPI-0.12.0-06`.

## Lane

**Heavy** -- This unit ports a blocking runtime contract used by operators and
future Claude hook orchestration.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/hooks/claude.py` -- generated Claude hook source of truth
- `tests/test_hooks.py` -- direct hook behavior and hook-generation coverage
- `.claude/hooks/**` and `.claude/settings.json` -- generated Claude hook
  artifacts and settings surface touched by control-surface sync
- `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`,
  `.github/discovery-index.json`, `.github/copilot-instructions.md`,
  `.copilotignore` -- generated control surfaces changed by sync
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- ADR, parity matrix, and OBPI evidence package for this tranche

## Denied Paths

- `../airlineops/**`
- `.gzkit/skills/gz-obpi-pipeline/**` and `.gzkit/skills/gz-plan-audit/**` --
  marker and receipt contracts already owned by earlier tranches
- `.claude/hooks/pipeline-completion-reminder.py` -- later hook OBPI
- Active `.claude/settings.json` registration or hook ordering changes --
  reserved for `OBPI-0.12.0-06`
- New dependencies, CI files, lockfiles, or unrelated runtime changes

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The hook MUST be generated into
   `.claude/hooks/pipeline-gate.py` from `src/gzkit/hooks/claude.py`.
1. REQUIREMENT: The gate MUST inspect only `Write|Edit` operations that resolve
   to repo-relative paths under `src/` or `tests/`.
1. REQUIREMENT: The gate MUST allow silently when the plan-audit receipt is
   missing, corrupt, lacks an OBPI, or has verdict other than `PASS`.
1. REQUIREMENT: The gate MUST allow when the per-OBPI marker
   `.claude/plans/.pipeline-active-{OBPI-ID}.json` exists and matches the PASS
   receipt OBPI.
1. REQUIREMENT: The gate MUST fall back to `.claude/plans/.pipeline-active.json`
   and allow only when that legacy marker matches the same OBPI.
1. REQUIREMENT: Corrupt or mismatched markers MUST be treated as missing and
   therefore block when a PASS receipt exists.
1. REQUIREMENT: Generated docs and the parity matrix MUST state truthfully that
   `pipeline-gate.py` is ported but inactive until `OBPI-0.12.0-06` wires
   `.claude/settings.json`.
1. NEVER: Reinterpret this surface into a reminder-only hook or wire it into
   active settings in this tranche.
1. ALWAYS: The block message must direct operators to `/gz-obpi-pipeline
   <OBPI-ID>` and `--from=verify`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `../airlineops/.claude/hooks/pipeline-gate.py`
- [x] `src/gzkit/hooks/claude.py`
- [x] `tests/test_hooks.py`
- [x] `.claude/settings.json`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related OBPIs in the same ADR, especially `OBPI-0.12.0-03`,
      `OBPI-0.12.0-05`, and `OBPI-0.12.0-06`

**Prerequisites (check existence, STOP if missing):**

- [x] Hook generator exists: `src/gzkit/hooks/claude.py`
- [x] Generated hook sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Active marker contract exists:
      `.claude/plans/.pipeline-active-{OBPI-ID}.json` and
      `.claude/plans/.pipeline-active.json`
- [x] Receipt contract exists: `.claude/plans/.plan-audit-receipt.json`

**Existing Code (understand current state):**

- [x] Pattern to follow: `../airlineops/.claude/hooks/pipeline-gate.py`
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

- [x] Human attestation recorded

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

- [x] REQ-0.12.0-04-01: `.claude/hooks/pipeline-gate.py` exists as a generated
      hook and blocks `src/` / `tests/` writes only when a PASS receipt exists
      without a valid matching active marker.
- [x] REQ-0.12.0-04-02: The gate allows when the per-OBPI marker or the legacy
      marker matches the PASS receipt OBPI, and treats corrupt or mismatched
      markers as missing.
- [x] REQ-0.12.0-04-03: Generated docs and settings remain truthful: the hook
      is ported and documented, but still inactive in `.claude/settings.json`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded
- [x] Parity matrix updated to reflect the ported but inactive gate artifact.
- [x] Generated hook docs remain explicit that settings registration is deferred
      to `OBPI-0.12.0-06`.

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_hooks -v
Ran 36 tests in 0.408s

OK

$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/pipeline-gate.py
  Updated .claude/hooks/pipeline-router.py
  Updated .claude/hooks/plan-audit-gate.py
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

$ uv run gz test
Running tests...
Ran 372 tests in 8.354s

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
Took 0min 0.270s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-13: "Accepted"

$ uv run gz git-sync --apply --lint --test
Git sync execution
  Branch: main
  Remote: origin
  ahead=0 behind=0 diverged=False dirty=True
  Actions:
    - git add -A
    - git fetch --prune origin
  Executed:
    - git add -A
    - gz lint (pre-sync)
    - gz test (pre-sync)
    - git commit
    - git push origin main
    - gz lint (post-sync)
Git sync completed.

$ uv run gz obpi emit-receipt OBPI-0.12.0-04-write-time-pipeline-gate --event completed --attestor "human:jeff" --evidence-json '{...}'
OBPI receipt emitted.
  OBPI: OBPI-0.12.0-04-write-time-pipeline-gate
  Parent ADR: ADR-0.12.0-obpi-pipeline-enforcement-parity
  Event: completed
  Attestor: human:jeff
```

### Value Narrative

Before this tranche, gzkit had the plan-exit router and the active-marker
contract, but nothing stopped agents from writing to `src/` or `tests/` before
actually entering the OBPI pipeline. This OBPI ports the missing write-time
gate so PASS-audited implementation work must pass through the pipeline marker
bridge instead of proceeding as freeform edits.

### Key Proof

```text
$ printf '{"cwd":"<temp-workspace>","tool_input":{"file_path":"src/demo.py"}}' | python3 .claude/hooks/pipeline-gate.py
BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.

A plan-audit receipt exists but the governance pipeline has not
been started. Implementation writes to src/ and tests/ are gated
until the pipeline is invoked.

REQUIRED: Invoke the pipeline:
  /gz-obpi-pipeline OBPI-0.12.0-04

If implementation is already complete, use:
  /gz-obpi-pipeline OBPI-0.12.0-04 --from=verify
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:
  `src/gzkit/hooks/claude.py`, `tests/test_hooks.py`,
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`,
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/obpis/OBPI-0.12.0-04-write-time-pipeline-gate.md`,
  and generated hook/control-surface files via `uv run gz agent sync control-surfaces`
- Tests added:
  direct gate coverage for non-implementation paths, missing/non-PASS receipts,
  matching per-OBPI marker, matching legacy marker, corrupt marker, mismatched
  marker, and PASS-without-marker block behavior
- Date completed:
  2026-03-13
- Attestation status:
  human attestation recorded and completion receipt emitted after guarded git sync
- Defects noted:
  `uv run gz adr status ADR-0.12.0-obpi-pipeline-enforcement-parity --json`
  continues to report completion-anchor drift on completed
  `OBPI-0.12.0-01`, `OBPI-0.12.0-02`, and `OBPI-0.12.0-07` because this tranche
  touched shared tracked files (`.claude/hooks/README.md`, the parity package,
  `src/gzkit/hooks/claude.py`, and `tests/test_hooks.py`).

## Human Attestation

- Attestor: human:jeff
- Attestation: Accepted
- Date: 2026-03-13

---

**Brief Status:** Completed

**Date Completed:** 2026-03-13

**Evidence Hash:** -
