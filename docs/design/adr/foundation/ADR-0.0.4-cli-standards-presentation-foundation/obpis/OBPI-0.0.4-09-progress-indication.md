---
id: OBPI-0.0.4-09-progress-indication
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 9
lane: heavy
status: Completed
---

# OBPI-0.0.4-09: Progress Indication

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #9 - "Progress indication -- rich.progress for long-running operations"

**Status:** Completed

## Objective

Add `rich.progress` indicators to long-running operations (>1s) so operators see step-by-step progress in human mode, with progress suppressed in quiet/JSON modes, written only to stderr, and degraded gracefully in non-interactive terminals.

## Lane

**heavy** - Changes CLI runtime output for long-running commands; modifies the external operator-visible contract for multiple commands (`gz check`, `gz tidy`, `gz gates`, `gz validate`, `gz git-sync`, `gz closeout`).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/formatters.py`
- `src/gzkit/cli/commands/`
- `tests/`

## Denied Paths

- Commands that complete in <1s (no progress indication needed)
- Spinner-style indicators (use progress bars with known step counts only)

## Requirements (FAIL-CLOSED)

1. Progress MUST write to stderr only -- NEVER to stdout.
2. Progress MUST NOT appear in JSON output or piped stdout.
3. Progress MUST degrade gracefully when `sys.stderr.isatty()` is False (periodic status lines instead of progress bars).
4. Progress MUST be suppressed via `--quiet` -- NEVER display progress in quiet mode.
5. Progress MUST be suppressed in JSON output mode -- NEVER display progress alongside `--json`.
6. Progress MUST use `OutputFormatter.progress_context(total, description)` as the single entry point -- NEVER call `rich.progress` directly from command handlers.
7. Long-running commands (>1s) MUST ALWAYS show progress in default human mode.
8. Progress bars MUST ALWAYS use known step counts -- NEVER use indeterminate spinners.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR
- [x] Related OBPIs in same ADR (OBPI-06, OBPI-08)

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-0.0.4-06 OutputFormatter exists: `src/gzkit/cli/formatters.py`
- [x] v3 CLI Standards specification: `docs/design/cli-standards-v3.md`

**Existing Code (understand current state):**

- [x] OutputFormatter implementation: `src/gzkit/cli/formatters.py`
- [x] Progress utilities: `src/gzkit/cli/progress.py`
- [x] Test patterns: `tests/unit/test_progress_indication.py` (created)

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
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m gzkit check 2>/dev/null | head  # stdout clean, no progress leakage
uv run -m gzkit check --quiet 2>&1 | head  # no progress output in quiet mode
uv run -m gzkit check --json 2>&1 | head   # no progress output in JSON mode
```

## Acceptance Criteria

- [x] **REQ-0.0.4-09-01:** `gz check` shows step-by-step progress in human mode
- [x] **REQ-0.0.4-09-02:** Progress suppressed with `--quiet`
- [x] **REQ-0.0.4-09-03:** Progress suppressed with `--json`
- [x] **REQ-0.0.4-09-04:** Progress writes to stderr, not stdout
- [x] **REQ-0.0.4-09-05:** `gz check 2>/dev/null` produces clean stdout with no progress leakage
- [x] **REQ-0.0.4-09-06:** Non-interactive terminals get status lines instead of progress bars
- [x] **REQ-0.0.4-09-07:** `uv run gz lint` passes
- [x] **REQ-0.0.4-09-08:** `uv run gz test` passes

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
Ran 9 tests in 0.001s — OK
Full suite: 1470 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed!
uv run gz typecheck — All checks passed!
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.98 seconds
```

### Gate 4 (BDD)

```text
uv run -m behave features/ — 3 features, 35 scenarios, 164 steps passed
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-25
```

### Value Narrative

Before this OBPI, long-running CLI operations gave no progress feedback — operators waited with no indication of progress. Now `OutputFormatter.progress_context(total, description)` provides step-counted progress bars on TTY stderr, degrades to status lines on non-TTY, and is automatically suppressed in quiet/JSON modes. `gz check` runs 7 quality steps with real-time progress indication.

### Key Proof

```bash
# Non-TTY output (what tests verify):
[1/7] Lint
[2/7] Format
[3/7] Typecheck
[4/7] Test
[5/7] Skill audit
[6/7] Parity check
[7/7] Readiness audit
```

### Implementation Summary

- Files created/modified:
  - Created: `tests/unit/test_progress_indication.py`
  - Modified: `src/gzkit/cli/formatters.py` (added `progress_context()` + `ProgressContext`), `src/gzkit/commands/quality.py` (integrated progress into `check()`), `tests/commands/test_skills.py` (updated mock paths)
- Tests added: 9
- Date completed: 2026-03-25
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeff`
- Attestation: `attest completed`
- Date: `2026-03-25`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-25

**Evidence Hash:** -
