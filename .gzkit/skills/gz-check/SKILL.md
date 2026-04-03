---
name: gz-check
description: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-03
model: haiku
---

# gz check

## Overview

Unified quality gate for all code verification. Replaces the individual
`/lint`, `/test`, `/format`, `/gz-typecheck`, and `/gz-arb` skills.

## Individual Commands

| Command | Purpose |
|---------|---------|
| `uv run gz lint` | Ruff linting + PyMarkdown |
| `uv run gz format` | Ruff auto-formatting |
| `uv run gz typecheck` | Static type checks (ty) |
| `uv run gz test` | Unit tests (unittest) |
| `uv run gz check` | All of the above in one pass |

## When to Use

- **Quick fix-up:** Run individual commands (`gz lint`, `gz format`) after small edits
- **Pre-merge / pre-attestation:** Run `gz check` for the full suite
- **Before `gz git-sync --apply --lint --test`:** Run `gz check` first
- **Before Gate 2 / Gate 3 verification:** Full suite required
- **Before closeout and attestation workflows:** Full suite required

## Workflow

1. Run `uv run gz check` with the required options.
2. Summarize results, including evidence and any follow-up gates.
3. **Claude surface check** (Claude Code only): After quality gates pass,
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

## Full Quality Evidence Sequence

When deterministic receipts are needed (e.g., for audit evidence):

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz check
```

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.

## Example

```bash
# Full quality check (preferred)
uv run gz check

# Individual checks when iterating
uv run gz lint
uv run gz format
uv run gz typecheck
uv run gz test

# If Claude surface issues found, diagnose:
@claude-code-guide look at .claude/settings.json — are all hook
references valid? Any deprecated patterns?
```

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/index.md`
