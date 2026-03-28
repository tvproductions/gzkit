---
id: OBPI-0.12.0-05-completion-reminder-surface
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.12.0-05-completion-reminder-surface: Completion reminder surface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #5 - "OBPI-0.12.0-05: Port the completion reminder surfaces that reinforce unfinished pipeline state before commit and push."

**Status:** Completed

## Objective

Port the AirlineOps `pipeline-completion-reminder.py` hook into gzkit as a
generated Claude `PreToolUse` advisory surface for `Bash` that warns before
`git commit` and `git push` when an OBPI pipeline marker still exists and the
corresponding brief has not yet reached `Completed`, while leaving
`.claude/settings.json` registration to `OBPI-0.12.0-06`.

## Lane

**Heavy** -- This unit ports an operator-facing runtime contract that affects
local commit and push workflows even though it is advisory rather than
blocking.

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
- Active `.claude/settings.json` registration or hook ordering changes --
  reserved for `OBPI-0.12.0-06`
- New dependencies, CI files, lockfiles, or unrelated runtime changes

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The hook MUST be generated into
   `.claude/hooks/pipeline-completion-reminder.py` from
   `src/gzkit/hooks/claude.py`.
1. REQUIREMENT: The reminder MUST inspect only `Bash` payloads whose command
   includes `git commit` or `git push`.
1. REQUIREMENT: The reminder MUST read active pipeline state from
   `.claude/plans/.pipeline-active-*.json` with
   `.claude/plans/.pipeline-active.json` as legacy compatibility input.
1. REQUIREMENT: The reminder MUST stay silent when no active marker exists,
   when marker JSON is corrupt, when the marker lacks `obpi_id`, or when the
   corresponding brief cannot be resolved under `docs/design/adr/`.
1. REQUIREMENT: If the matched brief is already `Completed`, the reminder MUST
   emit only stale-marker cleanup guidance and exit successfully.
1. REQUIREMENT: If the matched brief is not `Completed`, the reminder MUST emit
   advisory stderr output that includes `/gz-obpi-pipeline <OBPI-ID>
   --from=ceremony`.
1. REQUIREMENT: Generated docs and the parity matrix MUST state truthfully that
   `pipeline-completion-reminder.py` is ported but inactive until
   `OBPI-0.12.0-06` wires `.claude/settings.json`.
1. NEVER: Block commit or push in this tranche.
1. ALWAYS: Exit `0`; this surface is an advisory reminder, not an enforcement
   gate.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `../airlineops/.claude/hooks/pipeline-completion-reminder.py`
- [x] `src/gzkit/hooks/claude.py`
- [x] `tests/test_hooks.py`
- [x] `.claude/settings.json`
- [x] `.claude/hooks/README.md`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related OBPIs in the same ADR, especially `OBPI-0.12.0-03`,
      `OBPI-0.12.0-04`, and `OBPI-0.12.0-06`

**Prerequisites (check existence, STOP if missing):**

- [x] Hook generator exists: `src/gzkit/hooks/claude.py`
- [x] Generated hook sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Active marker contract exists:
      `.claude/plans/.pipeline-active-{OBPI-ID}.json` and
      `.claude/plans/.pipeline-active.json`
- [x] Briefs exist under `docs/design/adr/` for lookup by OBPI identifier

**Existing Code (understand current state):**

- [x] Pattern to follow:
      `../airlineops/.claude/hooks/pipeline-completion-reminder.py`
- [x] Test patterns: `tests/test_hooks.py`

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

- [x] REQ-0.12.0-05-01: `.claude/hooks/pipeline-completion-reminder.py`
      exists as a generated hook and stays silent unless an active pipeline
      marker exists for a commit or push attempt.
- [x] REQ-0.12.0-05-02: The reminder emits stale-marker guidance when the brief
      is already `Completed`, and emits a non-blocking completion reminder when
      the brief is found but still incomplete.
- [x] REQ-0.12.0-05-03: [doc] Generated docs and settings remain truthful: the hook
      is ported and documented, but still inactive in `.claude/settings.json`.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md`
> section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded
- [x] Parity matrix updated to reflect the ported but inactive reminder artifact.
- [x] Generated hook docs remain explicit that settings registration is deferred
      to `OBPI-0.12.0-06`.

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_hooks -v
Ran 43 tests in 0.638s

OK

$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/pipeline-completion-reminder.py
  Updated .claude/hooks/pipeline-gate.py
  Updated .claude/hooks/pipeline-router.py
  Updated .claude/hooks/plan-audit-gate.py
  Updated .claude/hooks/post-edit-ruff.py
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
Ran 379 tests in 8.842s

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
INFO    -  Documentation built in 0.74 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.295s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-13: "attest bcompleted"

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

$ uv run gz obpi emit-receipt OBPI-0.12.0-05-completion-reminder-surface --event completed --attestor "human:jeff" --evidence-json '{...}'
OBPI receipt emitted.
  OBPI: OBPI-0.12.0-05-completion-reminder-surface
  Parent ADR: ADR-0.12.0-obpi-pipeline-enforcement-parity
  Event: completed
  Attestor: human:jeff
```

### Value Narrative

Before this tranche, gzkit could create and enforce OBPI pipeline state, but it
still lacked the final operator-facing reminder that catches the easy failure
mode where a commit or push happens before the brief and sync steps are closed
out. Now the generated hook surface can warn on that incomplete state without
reinterpreting the contract into a blocking gate.

### Key Proof

```text
$ printf '{"cwd":"<temp-workspace>","tool_input":{"command":"git push origin main"}}' | uv run python .claude/hooks/pipeline-completion-reminder.py
PIPELINE COMPLETION REMINDER

Active OBPI pipeline: OBPI-0.12.0-05
Brief status: Accepted
Current stage: verify
Receipt state: pass

You are about to commit or push while the governance pipeline still
appears incomplete. Finish the runtime-managed closeout path first:

Next canonical command:
  uv run gz obpi pipeline OBPI-0.12.0-05 --from=ceremony

Do not clear the pipeline marker by hand; the runtime owns it.
```

### Implementation Summary

- Files created/modified: hook generator, hook tests, parity matrix, OBPI brief,
  and generated Claude control surfaces
- Tests added: direct `pipeline-completion-reminder.py` generation and behavior
  coverage
- Date completed: 2026-03-13
- Attestation status: human attestation recorded and completion receipt emitted
  after guarded git sync
- Defects noted: `uv run gz adr status ADR-0.12.0-obpi-pipeline-enforcement-parity --json`
  reports completion-anchor drift on completed `OBPI-0.12.0-01`,
  `OBPI-0.12.0-02`, `OBPI-0.12.0-03`, and `OBPI-0.12.0-07` after this tranche's
  shared-file updates

## Human Attestation

- Attestor: human:jeff
- Attestation: attest bcompleted
- Date: 2026-03-13

---

**Brief Status:** Completed

**Date Completed:** 2026-03-13

**Evidence Hash:** -
