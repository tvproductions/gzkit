---
name: gz-tidy
persona: main-session
description: Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
model: haiku
metadata:
  skill-version: "1.1.1"
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

## Common Rationalizations

These thoughts mean STOP — you are about to leave drift in place:

| Thought | Reality |
|---------|---------|
| "Tidy is just cosmetic, skip it" | Tidy catches surface drift before it becomes a Gate 5 blocker. The cost of skipping is paid later in attestation, when the drift is harder to find. |
| "The mirrors look fine — sync isn't needed" | Skill mirrors and canonical state can diverge silently. Tidy is the routine check that surfaces it. "Looks fine" is not a verification protocol. |
| "CLAUDE.md is over budget but it's all useful content" | The 200-line budget exists because adherence drops past it. Useful content that the agent can't load is dead content. Prune or relocate via `@path` imports. |
| "Hook errors at startup are pre-existing — not my problem" | Pre-existing failures are still failures. Tidy is when you self-heal, not when you ignore. |
| "I'll run `--check` instead of `--fix` to be safe" | `--check` is for diagnosis. If you saw drift and didn't fix it, you traded a 30-second sync for a future debugging session. |
| "The Claude surface self-heal is too vague to act on" | Tag the broken files with `@claude-code-guide` and let it diagnose against current Anthropic docs. Vagueness is solved by delegation, not avoidance. |

## Red Flags

- Running tidy with `--check` and ignoring the reported drift
- Skipping the Claude surface validation steps
- CLAUDE.md over 200 lines with no relocation plan
- Hook errors observed but never resolved
- Skill mirrors not regenerated after a skill edit
- Tidy runs that produce no evidence trail (sync output, log, or proof)
