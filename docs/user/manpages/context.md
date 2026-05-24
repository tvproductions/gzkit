# gz context

Focused-context payload renderer for a single ADR.

## NAME

gz context — render the target ADR body, its OBPI brief bodies, the
test files carrying matching `@covers` decorators, and a governance-
rules section as a single Markdown payload suitable for verbatim piping
to an AI agent harness.

## SYNOPSIS

```text
gz context <ADR-ID>
```

## DESCRIPTION

`gz context` is the focused-context loader introduced by
ADR-0.28.0-focused-context-loader (Move 2 of the get-out-of-jail
recovery plan). It composes one Markdown document combining four
sections in fixed order:

1. The target ADR's full Markdown body, copied verbatim from disk.
2. Every OBPI brief under the ADR's `obpis/` directory, each delimited
   by a heading containing its OBPI ID.
3. The covering-tests section: every test file carrying a
   `@covers(REQ-<ADR-semver>-…)` decorator, grouped by REQ.
4. A governance-rules section naming the ADR's lane, lifecycle, the
   current gate, and the next required action.

The payload contains no ANSI escapes or Rich-terminal frames and is
suitable for piping verbatim to any agent harness (Claude Code, Codex,
Copilot) or for redirecting to a file for archival inspection.

The `--slim` variant omits the governance-rules section (lane,
lifecycle, current gate, next required action) for non-governance
agent harnesses; pass `--slim` to subtract that section from the
payload. The other three sections (ADR body, OBPI briefs, covering
tests) are unaffected.

## OPTIONS

- `<ADR-ID>` — Positional: ADR identifier. Either the bare semver form
  (e.g. `ADR-0.0.3`) or the full slug form
  (e.g. `ADR-0.0.3-hexagonal-architecture-tune-up`). Resolution uses
  the project's configured ADR root.
- `--slim` — Omit the governance-rules section (lane, lifecycle,
  current gate, next required action) from the payload. Use for
  non-governance agent harnesses that do not need governance metadata.
  Subtractive: the other three sections (ADR body, OBPI briefs,
  covering tests) are byte-identical to the default-mode payload.
- `--quiet`, `-q` — Suppress non-error output.
- `--verbose`, `-v` — Enable verbose output.
- `--debug` — Enable debug mode with full tracebacks.
- `-h`, `--help` — Show help and exit.

## EXIT STATUS

- `0` — Payload rendered and written to stdout.
- `1` — User/config error: unresolvable ADR ID. A `BLOCKERS:`-prefixed
  diagnostic line is written to stderr naming the missing ADR.
- `2` — System or I/O error.
- `3` — Policy breach (reserved; not used by this verb in OBPI-01).

## EXAMPLES

```bash
# Render the focused payload for ADR-0.0.3 to stdout
uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up

# Pipe directly to another agent harness (the load-on-demand path)
uv run gz context ADR-0.0.3-hexagonal-architecture-tune-up | wc -c

# Slim payload — governance section omitted (non-governance harness)
uv run gz context --slim ADR-0.0.3-hexagonal-architecture-tune-up

# Error path — unresolvable ADR ID exits non-zero with BLOCKERS:
uv run gz context ADR-9.9.9-does-not-exist; echo "exit=$?"
```

## SEE ALSO

- [`gz adr report`](adr-report.md) — tabular ADR summary
- [`gz adr status`](adr-status.md) — focused OBPI progress for one ADR
- [`gz justify`](justify.md) — pre-execution reasoning scaffold
- ADR-0.28.0-focused-context-loader — parent ADR
