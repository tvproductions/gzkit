# Plan: OBPI-0.28.0-02-context-slim

**OBPI:** OBPI-0.28.0-02-context-slim
**Parent ADR:** ADR-0.28.0-focused-context-loader (Decision item 2)
**Lane:** Lite

## Context

The `context_cmd.py` renderer already implements `slim=True` logic
(`build_context_payload` conditionally omits the governance-rules section).
Three surfaces are missing: the parser flag, the REQ-derived tests, and the
manpage update. This plan wires those three surfaces.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py`
- `tests/commands/test_context_cmd.py`
- `docs/user/manpages/context.md`

## Steps

### Step 1: Register `--slim` in `_register_context_parser` (parser_artifacts.py)

- Add `p_context.add_argument("--slim", action="store_true", default=False, help="Omit the governance-rules section (lane, lifecycle, current gate, next required action).")`
- Update the `set_defaults` lambda to `lambda a: _lazy("context_cmd")(adr=a.adr, slim=a.slim)`
- Update the `epilog` to include a `--slim` example

### Step 2: Add OBPI-02 REQ-derived tests (test_context_cmd.py)

New test class `TestContextCmdSlim` with five tests:

- `test_help_documents_slim_flag` → `@covers("REQ-0.28.0-02-01")`: `gz context --help` text contains `--slim`
- `test_slim_omits_governance_section` → `@covers("REQ-0.28.0-02-02")`: payload under `--slim` contains none of "governance rules", "lane:", "lifecycle:", "current gate", "next required action"
- `test_slim_preserves_adr_body_obpi_briefs_and_tests` → `@covers("REQ-0.28.0-02-03")`: payload under `--slim` contains ADR sentinel, OBPI brief sentinel, and (if planted) test-path token
- `test_slim_only_delta_is_governance_section` → `@covers("REQ-0.28.0-02-04")`: default payload minus its governance section equals the `--slim` payload
- `test_obpi_01_tests_unaffected` → `@covers("REQ-0.28.0-02-05")`: re-invoke an OBPI-01 scenario (REQ-0.28.0-01-06: governance section present in default mode) via `_seed_adr` and confirm it still passes — regression-invariant overlay

### Step 3: Update manpage (docs/user/manpages/context.md)

- Remove the placeholder sentence ("The `--slim` variant … is not yet wired in this command.")
- Add `--slim` to the OPTIONS section
- Add a `--slim` example to the EXAMPLES section

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_context_cmd -v
```

## Notes

- `context_cmd.py` is already correct — no changes needed there.
- REQ-0.28.0-02-05 uses `# audit-exempt: regression-invariant-overlay OBPI-01 byte-parity test re-invoked here` because it re-covers REQ-0.28.0-01-06 in the same test file; the decorator is a legitimate overlay, not cosmetic backfill.
