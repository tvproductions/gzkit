---
id: OBPI-0.0.4-04-help-text-completeness
title: Help Text Completeness
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-04: Help Text Completeness

## Objective

Ensure every argument, option, and subcommand across all 35 top-level commands and 26
subcommands has a `help=` string and every parser has a `description=`.

## Scope

### In Scope

- Audit all parsers via recursive parser walk
- Add `help=` to all ~123 arguments currently missing help text
- Add `description=` to all commands currently missing descriptions
- Set `formatter_class` to combined NoHyphenBreaks+RawDescription on all parsers
- Help text conventions:
  - Action-oriented (verb-first)
  - Under 80 characters
  - No `TODO`, `FIXME`, `XXX`, or `print(` in help text
  - Positional arguments documented by name and purpose

### Target Commands (known gaps)

- `gz validate`: `--manifest`, `--documents`, `--surfaces`, `--ledger`, `--instructions`, `--json`
- `gz gates`: `--gate`, `--adr`
- `gz implement`: `--adr`
- `gz attest`: positional `adr`, `--reason`, `--force`, `--dry-run`
- `gz status`: `--json`
- `gz plan`: 12 arguments with no help
- `gz specify`, `gz prd`, `gz init`: arguments undocumented
- `gz closeout`, `gz audit`: critical arguments undocumented
- All chores subcommand arguments

### Out of Scope

- Epilog content (OBPI-05)
- Runtime output changes (OBPI-08)

## Constraints

- Help text must be accurate and operator-focused
- No breaking changes to argument names or behavior
- Help lines must not exceed 80 characters

## Acceptance Criteria

### Evidence

- [ ] Recursive parser audit finds zero undocumented arguments
- [ ] Recursive parser audit finds zero commands without descriptions
- [ ] No help text contains `TODO`, `FIXME`, `XXX`
- [ ] All help text under 80 characters
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure)
- OBPI-0.0.4-03 (option factories provide canonical help)

## Test Plan

- Recursive parser walk asserting all `.help` attributes are non-None and non-SUPPRESS
- Recursive parser walk asserting all parsers have `.description`
- Regex scan of help text for forbidden patterns
