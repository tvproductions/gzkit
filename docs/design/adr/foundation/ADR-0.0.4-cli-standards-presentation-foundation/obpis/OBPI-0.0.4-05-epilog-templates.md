---
id: OBPI-0.0.4-05-epilog-templates
title: Epilog Templates
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-05: Epilog Templates

## Objective

Add epilogs with `Examples` and `Exit codes` sections to every command and subcommand,
following the airlineops/opsdev pattern.

## Scope

### In Scope

- `src/gzkit/cli/helpers/epilog.py`:
  - `build_epilog(examples: list[str], *, exit_codes: str | None = None) -> str`
  - Uses `STANDARD_EXIT_CODES_EPILOG` from OBPI-02 as default
  - Accepts command-specific examples
  - Returns `textwrap.dedent`-formatted string

- Add epilogs to all 35 top-level commands with at least one example each
- Add epilogs to all 26 subcommands with at least one example each
- All epilogs contain:
  - `Examples` section with executable command examples
  - `Exit codes` section (standard or command-specific)

### Example Pattern (target output)

```
Examples
    gz status --table
    gz status --json
    gz status --show-gates

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
```

### Out of Scope

- Help text content (OBPI-04)
- Runtime output formatting (OBPI-08)

## Constraints

- Examples must be real, executable commands
- Epilogs must use `RawDescriptionHelpFormatter` to preserve formatting
- Examples should demonstrate the most common usage patterns
- No placeholder or aspirational examples

## Acceptance Criteria

### Evidence

- [ ] `build_epilog()` helper exists
- [ ] All 35 top-level commands have non-empty epilogs
- [ ] All 26 subcommands have non-empty epilogs
- [ ] Every epilog contains "Examples" and "Exit codes" sections
- [ ] All example commands are syntactically valid
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure)
- OBPI-0.0.4-02 (STANDARD_EXIT_CODES_EPILOG constant)
- OBPI-0.0.4-04 (help text in place first)

## Test Plan

- Automated: every parser has non-empty `.epilog`
- Automated: every epilog contains "Examples" substring
- Automated: every epilog contains "Exit codes" substring
- Verify epilog rendering via `--help` on representative commands
