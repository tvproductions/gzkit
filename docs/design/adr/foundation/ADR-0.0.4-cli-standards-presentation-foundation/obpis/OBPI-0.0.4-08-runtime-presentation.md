---
id: OBPI-0.0.4-08
title: Runtime Presentation
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-08: Runtime Presentation

## Objective

Make every command's runtime output professional and consistent: Rich tables everywhere,
status symbols, structured error format, and coherent color conventions.

## Scope

### In Scope

- **Kill ASCII pipe tables**: Replace `box.ASCII` in `status --table` with Rich box
  drawing (consistent with `gz state`, `gz chores list`, `gz roles`)

- **Status symbols**: Standardize across all commands:
  - `✓` (U+2713) — success/pass
  - `❌` (U+274C) — failure/blocker
  - `⚠` (U+26A0) — warning/pending
  - `→` (U+2192) — flow/action indicators

- **Apply to specific commands**:
  - `gz check`: Replace bare `"Lint: PASS"` / `"Format: FAIL"` with `✓ Lint` / `❌ Format`
  - `gz tidy`: Replace bare indented text with structured symbol output
  - `gz validate`: Show what was validated, not just "All validations passed."
  - `gz gates`: Structured gate-by-gate output with pass/fail symbols
  - `gz status --table`: Rich table (not ASCII pipes)

- **BLOCKERS: prefix**: All error output uses `BLOCKERS:` prefix via OutputFormatter

- **Color conventions** (documented, consistent):
  - `[green]` — success, pass, completed
  - `[red]` — failure, error, blocker
  - `[yellow]` — warning, pending, in-progress
  - `[cyan]` — informational, identifiers (ADR IDs, command names)
  - `[dim]` — secondary/hint text
  - `[bold]` — section headers, labels

- **Deprecation messages**: Structured format with migration guidance

### Out of Scope

- New command functionality
- OutputFormatter implementation (OBPI-06)
- Progress bars (OBPI-09)

## Constraints

- All output changes go through OutputFormatter (OBPI-06)
- Color must degrade gracefully when `NO_COLOR` set
- JSON mode must remain clean (no symbols, no color codes)
- Table column widths must handle long ADR names without mid-word breaks

## Acceptance Criteria

### Evidence

- [ ] `gz status --table` uses Rich tables (no ASCII pipes)
- [ ] `gz check` output uses `✓`/`❌` symbols
- [ ] `gz tidy` output uses structured symbols
- [ ] `gz validate` shows what was validated
- [ ] All error output uses `BLOCKERS:` prefix
- [ ] Color conventions documented and consistent
- [ ] `NO_COLOR=1 gz check` produces clean output without ANSI codes
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-06 (OutputFormatter provides rendering methods)
- OBPI-0.0.4-07 (exception hierarchy provides structured errors)

## Test Plan

- Snapshot tests for representative command output
- Verify `NO_COLOR` disables all ANSI codes
- Verify JSON mode produces no symbols or color
- Visual inspection of key commands before/after
