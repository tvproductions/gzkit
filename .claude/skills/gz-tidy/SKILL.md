---
name: gz-tidy
description: Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-15
model: haiku
---

# gz tidy

## Overview

Operate the gz tidy command surface as a reusable governance workflow.
Includes Claude surface self-heal via `@claude-code-guide` when running in Claude Code.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz tidy` with the required options.
3. Summarize results, including evidence and any follow-up gates.
4. **Claude surface self-heal** (Claude Code only): If any surface issues are
   detected (hook errors, stale settings, CLAUDE.md drift), invoke the
   `@claude-code-guide` subagent to diagnose and fix. Tag the broken files
   directly (e.g., `@claude-code-guide look at .claude/settings.json and
   .claude/hooks/` — the guide reads current Anthropic documentation and can
   self-heal configuration without stale knowledge.

## Claude Surface Validation

When running in Claude Code, after the core `gz tidy` checks, perform these
additional surface health checks:

1. **Hook health**: Verify all hooks in `.claude/hooks/` are syntactically valid
   and referenced in `.claude/settings.json`. If any hook errors appeared at
   session start, tag the broken hook files with `@claude-code-guide` for
   diagnosis against current Anthropic docs.
2. **Settings coherence**: Verify `.claude/settings.json` permissions and hook
   references match actual files on disk. Tag with `@claude-code-guide` if
   settings reference missing hooks or stale paths.
3. **CLAUDE.md budget**: Check CLAUDE.md line count. If over 200 lines, flag
   for pruning. The guide subagent can recommend `@path` imports and section
   relocation.
4. **Skill mirror parity**: Verify `.claude/skills/` mirrors match
   `.gzkit/skills/` canonical source. `gz agent sync control-surfaces` fixes
   this, but the guide can diagnose why mirrors drifted.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.

## Example

```
# Core tidy
uv run gz tidy --check

# With fix (syncs control surfaces)
uv run gz tidy --fix

# Claude surface self-heal (invoke in conversation)
@claude-code-guide look at .claude/settings.json and .claude/hooks/ —
diagnose any broken hooks or stale references against current docs
```
