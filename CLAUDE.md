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
