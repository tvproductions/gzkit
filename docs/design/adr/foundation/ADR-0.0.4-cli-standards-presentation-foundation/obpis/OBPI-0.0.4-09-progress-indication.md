---
id: OBPI-0.0.4-09-progress-indication
title: Progress Indication
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-09: Progress Indication

## Objective

Add `rich.progress` indicators to long-running operations (>1s) per v3 specification.
Progress writes to stderr, is suppressed in quiet/JSON modes, and degrades gracefully
in non-interactive terminals.

## Scope

### In Scope

- Progress indication on long-running commands:
  - `gz check` — shows progress across lint/format/typecheck/test/audit steps
  - `gz tidy` — shows progress across check categories
  - `gz gates` — shows progress across gate evaluations
  - `gz validate` — shows progress across validation targets
  - `gz git-sync` — shows progress across sync ritual steps
  - `gz closeout` — shows progress across closeout pipeline

- Progress bar integration with OutputFormatter:
  - Suppressed in `QUIET` and `JSON` modes
  - Writes to stderr (not stdout, so piped output is clean)
  - Degrades to periodic status lines in non-interactive terminals

- `OutputFormatter.progress_context(total, description)` context manager

### Out of Scope

- Commands that complete in <1s
- Spinner-style indicators (use progress bars with known step counts)

## Constraints

- Progress must write to stderr only
- Must not appear in JSON output or piped stdout
- Must degrade gracefully when `sys.stderr.isatty()` is False
- Must be suppressible via `--quiet`

## Acceptance Criteria

### Evidence

- [ ] `gz check` shows step-by-step progress in human mode
- [ ] Progress suppressed with `--quiet`
- [ ] Progress suppressed with `--json`
- [ ] Progress writes to stderr, not stdout
- [ ] `gz check 2>/dev/null` produces clean stdout
- [ ] Non-interactive terminals get status lines instead of progress bars
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-06 (OutputFormatter provides progress_context)

## Test Plan

- Test progress suppression in quiet mode
- Test progress suppression in JSON mode
- Test stderr-only output (capture stdout, verify empty)
- Test non-interactive terminal degradation
