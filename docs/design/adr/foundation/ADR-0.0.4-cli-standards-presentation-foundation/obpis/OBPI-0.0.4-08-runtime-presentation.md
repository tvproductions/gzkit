---
id: OBPI-0.0.4-08-runtime-presentation
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 8
lane: heavy
status: Draft
---

# OBPI-0.0.4-08: Runtime Presentation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #8 - "Runtime presentation with Rich tables everywhere, status symbols, BLOCKERS: prefix"

**Status:** Draft

## Objective

Make every command's runtime output professional and consistent: Rich tables everywhere,
status symbols, structured error format, and coherent color conventions.

## Lane

**heavy** - Changes all CLI runtime output appearance, which is an external operator-facing contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/commands/` - command handlers receiving presentation upgrades
- `src/gzkit/cli/formatters.py` - output formatting utilities
- `tests/` - unit and integration tests for presentation changes

## Denied Paths

- New command functionality (out of scope)
- `src/gzkit/cli/formatters.py` OutputFormatter class implementation (OBPI-06)
- Progress bars and `rich.progress` integration (OBPI-09)

## Requirements (FAIL-CLOSED)

1. All output changes MUST go through OutputFormatter (OBPI-06). NEVER call `console.print()` or bare `print()` directly from command handlers.
2. All table output MUST use Rich box-drawing characters. NEVER use `box.ASCII` pipe tables.
3. Status symbols MUST use the canonical set everywhere:
   - `✓` (U+2713) for success/pass
   - `❌` (U+274C) for failure/blocker
   - `⚠` (U+26A0) for warning/pending
   - `→` (U+2192) for flow/action indicators
4. Color conventions MUST follow the canonical palette:
   - `[green]` for success, pass, completed
   - `[red]` for failure, error, blocker
   - `[yellow]` for warning, pending, in-progress
   - `[cyan]` for informational, identifiers (ADR IDs, command names)
   - `[dim]` for secondary/hint text
   - `[bold]` for section headers, labels
5. Color MUST degrade gracefully when `NO_COLOR` is set. NEVER emit ANSI codes when `NO_COLOR=1`.
6. JSON mode MUST remain clean. NEVER include status symbols or color codes in JSON output.
7. All error output MUST use the `BLOCKERS:` prefix via OutputFormatter.
8. Table column widths MUST handle long ADR names without mid-word breaks.
9. Deprecation messages MUST use a structured format with migration guidance.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (especially OBPI-06, OBPI-07, OBPI-09)
- [ ] CLI Standards v3 specification: `docs/design/cli-standards-v3.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-06 OutputFormatter exists and is implemented: `src/gzkit/cli/formatters.py`
- [ ] OBPI-0.0.4-07 exception hierarchy exists and is implemented: structured error types with typed exit codes

**Existing Code (understand current state):**

- [ ] Current command output patterns: `src/gzkit/cli/commands/`
- [ ] Current table rendering: grep for `box.ASCII`, `console.print`, `Table(` across commands
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
uv run gz status --table          # Verify Rich tables (no ASCII pipes)
uv run gz check                   # Verify status symbols in output
uv run gz tidy --dry-run          # Verify structured symbol output
uv run gz validate                # Verify itemized validation output
NO_COLOR=1 uv run gz check       # Verify clean output without ANSI codes
uv run gz check --json            # Verify no symbols or color in JSON mode
```

## Acceptance Criteria

- [ ] **REQ-0.0.4-08-01:** `gz status --table` uses Rich tables (no ASCII pipes)
- [ ] **REQ-0.0.4-08-02:** `gz check` output uses `✓`/`❌` status symbols
- [ ] **REQ-0.0.4-08-03:** `gz tidy` output uses structured symbols instead of bare indented text
- [ ] **REQ-0.0.4-08-04:** `gz validate` shows what was validated, not just "All validations passed."
- [ ] **REQ-0.0.4-08-05:** `gz gates` produces structured gate-by-gate output with pass/fail symbols
- [ ] **REQ-0.0.4-08-06:** All error output uses `BLOCKERS:` prefix via OutputFormatter
- [ ] **REQ-0.0.4-08-07:** Color conventions documented and applied consistently across all commands
- [ ] **REQ-0.0.4-08-08:** `NO_COLOR=1 gz check` produces clean output without ANSI codes
- [ ] **REQ-0.0.4-08-09:** JSON mode (`--json`) produces no symbols or color codes in output

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
