# Plan: OBPI-0.28.0-01-context-core

**OBPI:** OBPI-0.28.0-01-context-core
**ADR:** ADR-0.28.0-focused-context-loader
**Lane:** Lite
**Date:** 2026-05-24 (implemented), 2026-05-24 (plan record authored retroactively for pipeline plan-audit coverage)

## Context

ADR-0.28.0 § Decision item #1:
> "OBPI-0.28.0-01: **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent."

Move 2 of the get-out-of-jail recovery plan (`docs/governance/get-out-of-jail-plan-2026-05-23.md`) calls for a focused-context loader so agents do not have to discover the ADR / OBPI / test / governance bundle by repeated reads. The renderer is factored so that OBPI-0.28.0-02's `--slim` flag is a subtractive parameter, not a duplicated code path.

## Files

**Created:**

- `src/gzkit/commands/context_cmd.py` — `build_context_payload`, `context_cmd`, helpers (158 lines)
- `tests/commands/test_context_cmd.py` — eight REQ-derived unittest cases (REQ-0.28.0-01-01..08)
- `docs/user/manpages/context.md` — Synopsis / Description / Options / Exit codes / Examples / See also

**Modified:**

- `src/gzkit/cli/parser_artifacts.py` — `_register_context_parser`; lazy handler registered alongside `_register_justify_parser`
- `docs/user/manpages/index.md` — index row for `gz context`
- `docs/user/runbook.md` — Step 1 (Orientation + parent ADR context) lists `/gz-context ADR-<X.Y.Z>` and the CLI equivalent
- `docs/governance/governance_runbook.md` — Step 5c authored for `gz context`
- `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/obpis/OBPI-0.28.0-01-context-core.md` — Objective rewritten to drop the HTML-comment scaffold that tripped the placeholder detector

## Steps

1. Read ADR-0.28.0 § Decision and § Checklist item #1.
2. Derive eight REQs from the checklist item (help shape, exit 0 on resolvable ADR, ADR body verbatim, OBPI brief inclusion, covers grouping, governance section, unresolvable-ID BLOCKERS path, plain-Markdown / no-ANSI).
3. Author `tests/commands/test_context_cmd.py` — eight REQ-derived tests, RED first.
4. Implement `src/gzkit/commands/context_cmd.py` and wire the parser in `src/gzkit/cli/parser_artifacts.py`.
5. Run `uv run -m unittest tests.commands.test_context_cmd -v` — confirm 8/8 GREEN.
6. Run `uv run ruff check` and `uvx ty check` on the new surfaces — confirm clean.
7. Author the manpage and add the index / operator runbook / governance runbook references.
8. Run `uv run gz cli audit` — confirm cross-coverage 103/103.
9. Run the OBPI pipeline through verify → ceremony → guarded git-sync → completion.

## Verification

```bash
# REQ coverage and tests
uv run -m unittest tests.commands.test_context_cmd -v

# Lint and type
uv run ruff check src/gzkit/commands/context_cmd.py src/gzkit/cli/parser_artifacts.py tests/commands/test_context_cmd.py
uvx ty check src/gzkit/commands/context_cmd.py

# Smoke and error path
uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up | wc -c
uv run gz context ADR-9.9.9-does-not-exist; echo "exit=$?"

# CLI coverage audit
uv run gz cli audit
```

## Destination-in-mind disclosure

The implementation approach was clear before authoring: a single `build_context_payload(adr_file, project_root, *, slim=False)` composes four concatenated Markdown sections, and a thin `context_cmd(adr, *, slim=False)` handler resolves the ADR file, writes payload to stdout, and raises `SystemExit(1)` with a `BLOCKERS:` stderr line on unresolvable IDs. The `slim` parameter is plumbed but the CLI flag is held back for OBPI-0.28.0-02 — landing both flag and renderer in this OBPI would bundle OBPI-02's scope.

## Rejected alternatives

1. **Land `--slim` in OBPI-01** — single-OBPI delivery. Rejected: violates the OBPI-01 / OBPI-02 boundary the recovery plan binds.
2. **Return integer exit code from `context_cmd`** — direct return. Rejected: `gzkit.cli.main` discards handler return values; `SystemExit(1)` after the `BLOCKERS:` stderr write is the only path that propagates the exit code through the entrypoint.
3. **Register as `gz adr context`** — nested under `adr`. Rejected: parity with `gz justify` (also a single positional, top-level command); the verb is a load-on-demand action against a single ADR, not an ADR-mutating operation.
