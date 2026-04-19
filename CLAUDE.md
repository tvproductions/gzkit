# CLAUDE.md

@AGENTS.md

<!--
AGENTS.md is the authoritative governance contract. Claude Code resolves the
@import above at load time, so AGENTS.md content (including agents.local.md,
which AGENTS.md already embeds) appears inline without duplication here.

This file contains Claude-Code-specific guidance only. If it and AGENTS.md
diverge, follow AGENTS.md and run `gz agent sync control-surfaces`.
-->

## Claude Code addendum

Build commands (Python project — Python 3.13+ with uv, ruff, ty):

```bash
uv sync                              # Hydrate environment
uv run -m gzkit --help            # CLI entry point
uv run gz lint                       # Lint
uv run gz format                     # Format
uv run gz typecheck                  # Type check
uv run gz test                       # Run tests
```

Coding conventions: Ruff defaults: 4-space indent, 100-char lines, double quotes

Governance rules load contextually from `.claude/rules/` (mirrored from
`.gzkit/rules/` via `gz agent sync control-surfaces`).

Skills are auto-discovered from `.claude/skills/`. See AGENTS.md for the
catalog.

## Compact Instructions

When compacting context (`/compact`), preserve:

- Active pipeline ID and current stage (from `uv run gz obpi pipeline status`)
- Active OBPI ID and brief status (lane, gates passed, attestation state)
- Gate pass/fail state for the current ADR (from `uv run gz gates --adr <ID>`)
- Pending attestation requirements (which Gate 5 awaits human witness)
- Any unresolved defects or blockers (GHIs in scope, insights logged)
- The current TASK ID if one is open (`uv run gz task list --active`)

The ledger (`.gzkit/ledger.jsonl`) is the system-of-record; compaction must
not drop references to live ledger events for the current session's ADR.
