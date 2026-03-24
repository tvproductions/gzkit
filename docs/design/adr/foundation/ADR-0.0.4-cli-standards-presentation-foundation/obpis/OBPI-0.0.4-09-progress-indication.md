---
id: OBPI-0.0.4-09-progress-indication
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 9
lane: heavy
status: Draft
---

# OBPI-0.0.4-09: Progress Indication

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #9 - "Progress indication -- rich.progress for long-running operations"

**Status:** Draft

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

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (especially OBPI-06 and OBPI-08)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-06 OutputFormatter exists and provides `progress_context` context manager: `src/gzkit/cli/formatters.py`
- [ ] v3 CLI Standards specification: `docs/design/cli-standards-v3.md`

**Existing Code (understand current state):**

- [ ] OutputFormatter implementation: `src/gzkit/cli/formatters.py`
- [ ] Long-running command handlers: `src/gzkit/cli/commands/`
- [ ] Test patterns: `tests/unit/test_output_formatter.py`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] **REQ-0.0.4-09-01:** `gz check` shows step-by-step progress in human mode
- [ ] **REQ-0.0.4-09-02:** Progress suppressed with `--quiet`
- [ ] **REQ-0.0.4-09-03:** Progress suppressed with `--json`
- [ ] **REQ-0.0.4-09-04:** Progress writes to stderr, not stdout
- [ ] **REQ-0.0.4-09-05:** `gz check 2>/dev/null` produces clean stdout with no progress leakage
- [ ] **REQ-0.0.4-09-06:** Non-interactive terminals get status lines instead of progress bars
- [ ] **REQ-0.0.4-09-07:** `uv run gz lint` passes
- [ ] **REQ-0.0.4-09-08:** `uv run gz test` passes

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
