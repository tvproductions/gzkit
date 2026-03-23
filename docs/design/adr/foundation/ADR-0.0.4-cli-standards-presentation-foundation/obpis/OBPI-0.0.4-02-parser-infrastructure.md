---
id: OBPI-0.0.4-02-parser-infrastructure
title: Parser Infrastructure
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-02: Parser Infrastructure

## Objective

Create the foundational parser classes and constants that all commands use: stable error
formatting, hyphen-preserving help text, and standardized exit code documentation.

## Scope

### In Scope

- `src/gzkit/cli/parser.py`:
  - `StableArgumentParser` — overrides `error()` to emit `BLOCKERS: {prog}: error: {message}` on stderr with exit code 2
  - `_NoHyphenBreaksFormatter` — extends `HelpFormatter` with `break_on_hyphens=False` in `_split_lines()` and `_fill_text()`, preserving tokens like `ADR-0.0.4`, `YYYY-MM`, `OBPI-0.0.4-01`
- `src/gzkit/cli/helpers/exit_codes.py`:
  - `EXIT_SUCCESS = 0`
  - `EXIT_USER_ERROR = 1`
  - `EXIT_SYSTEM_ERROR = 2`
  - `EXIT_POLICY_BREACH = 3`
  - `STANDARD_EXIT_CODES_EPILOG` — reusable `textwrap.dedent` block for epilogs
- Wire `StableArgumentParser` as the top-level parser in `cli/main.py`
- Wire combined formatter (NoHyphenBreaks + RawDescription) on all parsers

### Out of Scope

- Command-specific help text content (OBPI-04)
- Common flags (OBPI-03)

## Constraints

- stdlib-only (`argparse`, `textwrap`) — no third-party parser dependencies
- Error format must be machine-parseable for CI/governance tooling
- Must respect existing exit code semantics (0, 1, 2 currently used)

## Acceptance Criteria

### Evidence

- [ ] `StableArgumentParser` exists and is used as top-level parser
- [ ] Invalid arguments produce `BLOCKERS: gz: error: ...` on stderr
- [ ] Exit code 2 on parse errors
- [ ] Help text preserves `ADR-0.0.4` as one token (no line break on hyphen)
- [ ] `STANDARD_EXIT_CODES_EPILOG` constant exists
- [ ] Unit tests for parser error format and formatter behavior
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure exists)

## Test Plan

- Test `StableArgumentParser.error()` output format
- Test `_NoHyphenBreaksFormatter` preserves hyphenated tokens
- Test exit codes on invalid input
