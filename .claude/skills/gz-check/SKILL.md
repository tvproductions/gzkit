---
name: gz-check
description: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-15
model: haiku
---

# gz check

## Overview

Operate the gz check command surface as a reusable governance workflow.
Includes Claude surface validation via `@claude-code-guide` when running in Claude Code.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz check` with the required options.
3. Summarize results, including evidence and any follow-up gates.
4. **Claude surface check** (Claude Code only): After quality gates pass,
   validate Claude-specific surfaces are healthy. If issues found, invoke
   `@claude-code-guide` to diagnose against current Anthropic documentation.

## Claude Surface Check

When running in Claude Code as a pre-merge or pre-attestation check, verify:

1. **No hook errors at session start** — if any appeared, they must be resolved
   before attestation. Use `@claude-code-guide` to diagnose broken hooks.
2. **Generated surfaces match canonical source** — `.claude/skills/` mirrors
   `.gzkit/skills/`, `.claude/rules/` mirrors `.gzkit/rules/` (when rules-as-content
   is implemented per ADR-0.16.0).
3. **CLAUDE.md is under budget** — under 200 lines for optimal adherence.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.

## Example

```
# Full quality check
uv run gz check

# If Claude surface issues found, diagnose:
@claude-code-guide look at .claude/settings.json — are all hook
references valid? Any deprecated patterns?
```
