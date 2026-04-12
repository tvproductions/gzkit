---
name: gz-check
persona: main-session
description: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
model: haiku
metadata:
  skill-version: "1.1.1"
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

## Common Rationalizations

These thoughts mean STOP — you are about to skip the gate that catches drift:

| Thought | Reality |
|---------|---------|
| "I only changed one file — `gz lint` is enough" | `gz check` is the unified gate for a reason: lint passes can hide type or test regressions. Pre-merge always runs the full suite. |
| "Tests pass locally, no need to typecheck" | `ty` catches signature drift that unittest can't. The two checks are complementary, not redundant. |
| "Hook errors at session start are cosmetic" | The Claude surface check is part of `gz check` precisely because hook errors mean an agent is operating against stale governance. Resolve before attestation. |
| "The mirrors look fine, skip the surface check" | Canon/derived drift is silent until it isn't. The mirror parity check is cheap; the bug it prevents is expensive. |
| "I'll run the individual commands instead of `gz check`" | Individual commands skip the Claude surface check and the deterministic ordering. Use them for iterative fix-up, not for pre-merge or pre-attestation. |
| "Coverage is close to 40% — round up" | The coverage floor is fail-closed at 40.00%. Rounding rationalizes a regression. |
| "PyMarkdown warnings are noise" | PyMarkdown is part of `gz lint` because docs are first-class deliverables under the Gate 5 Runbook-Code Covenant. Fix or document the exception. |

## Red Flags

- Closing a brief or attestation without running `gz check`
- Running `gz lint` but not `gz typecheck` or `gz test` before merge
- Hook errors in session-start output that were never resolved
- `.claude/skills/` divergent from `.gzkit/skills/` (sync not run)
- CLAUDE.md over 200 lines (budget exceeded, adherence drops)
- Coverage dropped below 40% but the brief was marked complete
- Skipping the full sequence "because nothing meaningful changed"

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/index.md`
