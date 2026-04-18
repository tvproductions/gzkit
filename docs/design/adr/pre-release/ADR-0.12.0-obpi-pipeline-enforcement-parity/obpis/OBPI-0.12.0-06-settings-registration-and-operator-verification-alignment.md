---
id: OBPI-0.12.0-06-settings-registration-and-operator-verification-alignment
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 6
lane: Heavy
status: in_progress
---

# OBPI-0.12.0-06-settings-registration-and-operator-verification-alignment: Settings registration and operator verification alignment

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #6 - "OBPI-0.12.0-06: Register the hook chain in settings and align tests, docs, and operator verification with the enforced runtime."

**Status:** Completed

## Objective

Activate the previously ported pipeline-enforcement hook chain in generated
Claude settings with deterministic matcher ordering, while updating tests,
runtime docs, and operator guidance so gzkit’s enforced runtime matches the
documented OBPI pipeline contract.

## Lane

**Heavy** -- This unit changes the active hook runtime used by operators and
future Claude sessions by registering blocking and advisory governance hooks in
`.claude/settings.json`.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/hooks/claude.py` -- generated Claude settings and README source of
  truth
- `tests/test_hooks.py` -- settings registration, ordering, and README coverage
- `.claude/hooks/**` and `.claude/settings.json` -- generated Claude hook
  artifacts and active settings surface touched by control-surface sync
- `.gzkit/skills/gz-plan-audit/**`, `.claude/skills/gz-plan-audit/**`,
  `.agents/skills/gz-plan-audit/**`, `.github/skills/gz-plan-audit/**` --
  operator guidance updated through canonical skill edits and mirror sync
- `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`,
  `.github/discovery-index.json`, `.github/copilot-instructions.md`,
  `.copilotignore` -- generated control surfaces changed by sync
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- parity matrix and OBPI evidence package for this tranche

## Denied Paths

- `../airlineops/**`
- Hook behavior changes already owned by `OBPI-0.12.0-02` through
  `OBPI-0.12.0-05`; this tranche registers existing contracts instead of
  redesigning their semantics
- New dependencies, CI files, lockfiles, or unrelated runtime changes

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.claude/settings.json` MUST register `plan-audit-gate.py` on
   `PreToolUse` `ExitPlanMode`.
1. REQUIREMENT: `.claude/settings.json` MUST register `pipeline-router.py` on
   `PostToolUse` `ExitPlanMode`.
1. REQUIREMENT: `.claude/settings.json` MUST register `pipeline-gate.py` before
   `instruction-router.py` in the `PreToolUse` `Write|Edit` chain so blocking
   happens before informational surfacing.
1. REQUIREMENT: `.claude/settings.json` MUST register
   `pipeline-completion-reminder.py` on `PreToolUse` `Bash`.
1. REQUIREMENT: Existing `Edit|Write` post-edit ordering MUST remain
   `post-edit-ruff.py` followed by `ledger-writer.py`.
1. REQUIREMENT: Generated README, parity docs, and `gz-plan-audit` guidance
   MUST describe the hook chain as active and MUST name the enforced matcher
   order truthfully.
1. REQUIREMENT: Tests MUST lock the exact settings matcher layout and order so
   later drift is caught mechanically.
1. NEVER: Change the semantics of the previously ported hook scripts beyond
   what is necessary to register them.
1. ALWAYS: Keep the generated command pattern as `uv run python <hook-path>`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `src/gzkit/hooks/claude.py`
- [x] `tests/test_hooks.py`
- [x] `.claude/settings.json`
- [x] `.claude/hooks/README.md`
- [x] `.gzkit/skills/gz-plan-audit/SKILL.md`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related completed OBPIs in the same ADR, especially
      `OBPI-0.12.0-02`, `OBPI-0.12.0-03`, `OBPI-0.12.0-04`, and
      `OBPI-0.12.0-05`

**Prerequisites (check existence, STOP if missing):**

- [x] Hook generator exists: `src/gzkit/hooks/claude.py`
- [x] Generated hook sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Ported hook artifacts already exist in generator output
- [x] Receipt and marker contracts already exist from earlier OBPIs

**Existing Code (understand current state):**

- [x] Current settings generator and tests in `src/gzkit/hooks/claude.py` and
      `tests/test_hooks.py`
- [x] AirlineOps ordering notes from `../airlineops/.claude/hooks/README.md`
      and planning artifacts that place `pipeline-gate.py` first in the
      `Write|Edit` chain

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

- [x] REQ-0.12.0-06-01: Generated `.claude/settings.json` wires the active
      pipeline hook chain on `ExitPlanMode`, `Write|Edit`, and `Bash` with
      exact matcher and command ordering.
- [x] REQ-0.12.0-06-02: [doc] Generated README and operator-facing `gz-plan-audit`
      guidance describe the hook chain as active and document the actual
      matcher order instead of pending registration.
- [x] REQ-0.12.0-06-03: Tests lock the settings layout and order, and the
      direct hook behavior suites still pass with the registered runtime.

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
- [x] Parity matrix updated to reflect active registration and ordering.
- [x] `gz-plan-audit` guidance updated from pending registration to active
      enforcement.

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_hooks -v
Ran 43 tests in 0.558s

OK

$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .agents/skills/gz-plan-audit/SKILL.md
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/pipeline-completion-reminder.py
  Updated .claude/hooks/pipeline-gate.py
  Updated .claude/hooks/pipeline-router.py
  Updated .claude/hooks/plan-audit-gate.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .claude/skills/gz-plan-audit/SKILL.md
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .github/skills/gz-plan-audit/SKILL.md
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz test
Running tests...
Ran 379 tests in 8.985s

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
INFO    -  Documentation built in 0.73 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.287s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-13: "completed and fix"

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

$ uv run gz obpi emit-receipt OBPI-0.12.0-06-settings-registration-and-operator-verification-alignment --event completed --attestor "human:jeff" --evidence-json '{...}'
OBPI receipt emitted.
  OBPI: OBPI-0.12.0-06-settings-registration-and-operator-verification-alignment
  Parent ADR: ADR-0.12.0-obpi-pipeline-enforcement-parity
  Event: completed
  Attestor: human:jeff
```

### Value Narrative

Before this tranche, gzkit had the full set of pipeline-enforcement hooks on
disk, but the actual Claude runtime still left them unwired, which meant the
OBPI pipeline contract depended on operator memory instead of active settings.
Now the hook chain can be enforced through `.claude/settings.json`, so the
runtime behavior, tests, and operator docs all describe the same active path.

### Key Proof

```text
$ sed -n '1,260p' .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/plan-audit-gate.py"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/pipeline-gate.py"
          },
          {
            "type": "command",
            "command": "uv run python .claude/hooks/instruction-router.py"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/pipeline-completion-reminder.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/pipeline-router.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/post-edit-ruff.py"
          },
          {
            "type": "command",
            "command": "uv run python .claude/hooks/ledger-writer.py"
          }
        ]
      }
    ]
  }
}
```

### Implementation Summary

- Files created/modified: hook generator, hook tests, `gz-plan-audit` skill,
  parity matrix, OBPI brief, and generated Claude/mirror control surfaces
- Tests added: settings matcher/order assertions and active-runtime README
  assertions
- Date completed: 2026-03-13
- Attestation status: human attestation recorded and completion receipt emitted
  after guarded git sync
- Defects noted: `uv run gz adr status ADR-0.12.0-obpi-pipeline-enforcement-parity --json`
  now reports completion-anchor drift on completed `OBPI-0.12.0-01`,
  `OBPI-0.12.0-02`, `OBPI-0.12.0-03`, `OBPI-0.12.0-04`, and `OBPI-0.12.0-07`
  because this tranche touched shared tracked files in the ADR package,
  generated hook surfaces, and `gz-plan-audit` skill guidance

## Human Attestation

- Attestor: human:jeff
- Attestation: completed and fix
- Date: 2026-03-13

---

**Brief Status:** Completed

**Date Completed:** 2026-03-13

**Evidence Hash:** -
