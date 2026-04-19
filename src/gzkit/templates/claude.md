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

Build commands (Python project — {tech_stack}):

```bash
{build_commands}
```

Coding conventions: {coding_conventions}

Governance rules load contextually from `.claude/rules/` (mirrored from
`.gzkit/rules/` via `gz agent sync control-surfaces`).

Skills are auto-discovered from `.claude/skills/`. See AGENTS.md for the
catalog.
