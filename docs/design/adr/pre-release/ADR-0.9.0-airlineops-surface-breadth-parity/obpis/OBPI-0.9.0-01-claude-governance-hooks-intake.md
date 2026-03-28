---
id: OBPI-0.9.0-01-claude-governance-hooks-intake
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 1
lane: Lite
status: Completed
---

# OBPI-0.9.0-01-claude-governance-hooks-intake: Canonical .claude hooks governance tranche

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #1 — "Execute OBPI-0.9.0-01: import non-blocking `.claude/hooks` tranche with settings wiring and evidence."

**Status:** Completed

## Objective

Import a governance-safe first tranche of canonical `.claude/hooks` (non-blocking)
into gzkit and wire those hooks in `.claude/settings.json` with path-level parity
evidence and explicit deferrals for blocking/product-coupled hooks.

## Lane

**Lite** — Internal governance tooling import with no external contract changes
(no CLI, API, schema, or error message changes). Per GovZero charter, default
lane is Lite; escalate to Heavy only when external contracts change.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.claude/hooks/**` — Hook parity tranche import
- `.claude/settings.json` — Hook wiring
- `src/gzkit/hooks/claude.py` — Generated Claude hook surface
- `tests/test_hooks.py` — Claude hook generation coverage
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` — OBPI and intake evidence

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/adr/pool/**` except parent promotion pointer updates
- `../airlineops/**` (read-only canonical source)
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Import only non-blocking canonical hooks in this tranche.
1. REQUIREMENT: `.claude/settings.json` MUST keep `ledger-writer.py` active.
1. REQUIREMENT: A path-level intake matrix MUST classify all canonical `.claude/hooks` files.
1. NEVER: Do not import product-specific guard logic in this tranche.
1. NEVER: Do not enable blocking hooks until compatibility adaptation is documented.
1. ALWAYS: For every deferred hook, record reason and follow-up target OBPI.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical hooks source exists: `../airlineops/.claude/hooks/`
- [x] Claude settings exists: `.claude/settings.json`

**Existing Code (understand current state):**

- [x] Pattern to follow: `.claude/hooks/ledger-writer.py`
- [x] Pattern to follow: `../airlineops/.claude/hooks/instruction-router.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Coverage maintained: `uv run coverage run -m unittest discover tests && uv run coverage report`

### Code Quality

- [x] Lint clean: `uvx ruff check src tests`
- [x] Format clean: `uvx ruff format --check .`
- [x] Type check clean: `uvx ty check src`

### Gate 3: Docs (Heavy only — not required for Lite)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only — not required for Lite)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only — not required for Lite)

- N/A (Lite lane — self-closeable after evidence presented)

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run gz check-config-paths
uv run gz cli audit
uv run mkdocs build --strict
uv run gz adr status ADR-0.9.0 --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.9.0-01-01: [doc] Given canonical `.claude/hooks` contains non-blocking governance hooks, when OBPI-01 completes, then gzkit contains imported `instruction-router.py` and `post-edit-ruff.py`.
- [x] REQ-0.9.0-01-02: [doc] Given gzkit Claude settings, when hooks are wired, then `instruction-router.py`, `post-edit-ruff.py`, and `ledger-writer.py` are configured in `.claude/settings.json`.
- [x] REQ-0.9.0-01-03: [doc] Given remaining canonical hooks are not imported, when intake evidence is reviewed, then each hook is classified with explicit defer/exclude rationale and follow-up.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below (Lite lane — self-closed)

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run -m unittest discover tests
Ran 305 tests in 10.602s
OK

$ uv run coverage run -m unittest discover tests
Ran 305 tests in 12.531s
OK

$ uv run coverage report
TOTAL                                    8554   1106    87%

$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Code Quality

```text
$ uvx ruff check src tests
All checks passed.

$ uvx ruff format --check .
67 files already formatted

$ uvx ty check src
All checks passed!

$ uv run gz check-config-paths
Config-path audit passed.

$ uv run gz cli audit
CLI audit passed.

$ uv run mkdocs build --strict
Documentation built in 0.85 seconds with informational notices only.
```

### Value Narrative

Before this OBPI reconciliation, gzkit carried the non-blocking Claude hook files
and settings wiring in the working tree, but the canonical generator contract did
not recreate those files and the brief still treated the tranche as unfinished.
After this OBPI, the non-blocking `.claude/hooks` tranche is reproducible from
`src/gzkit/hooks/claude.py`, the intake matrix records explicit defer/exclude
rationale for the remaining canonical hooks, and verification evidence shows the
surface is governance-safe.

### Key Proof

The generated Claude settings now preserve the OBPI-01 hook tranche exactly:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/instruction-router.py"
          }
        ]
      }
    ],
    "PostToolUse": [
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

- Files created/modified:
  - `src/gzkit/hooks/claude.py`
  - `tests/test_hooks.py`
  - `.claude/hooks/instruction-router.py`
  - `.claude/hooks/post-edit-ruff.py`
  - `.claude/hooks/README.md`
  - `.claude/settings.json`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- Tests added:
  - `tests/test_hooks.py` (`generate_claude_settings` and `setup_claude_hooks` coverage)
- Date updated: 2026-03-07

## Closure

- Lane: Lite (internal governance tooling, no external contract changes)
- Closure: Self-closed after evidence presented per GovZero charter Lite lane rules.
- Date: 2026-03-07

---

**Brief Status:** Completed

**Date Completed:** 2026-03-07

**Evidence Hash:** 814baef
