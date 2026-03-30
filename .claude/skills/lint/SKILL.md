---
name: lint
description: Run code linting with Ruff and PyMarkdown. Use when code changes need quality validation, after implementation, or before commit/sync. Produces a pass/fail result with categorized violation counts.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-30
model: haiku
---

# Lint

Run Ruff linting and PyMarkdown checks against the project, report violations, and auto-fix where safe.

## When to Use

- After making code changes (pre-commit quality gate)
- As part of Stage 3 verification in the OBPI pipeline
- When `gz check` or `gz gates` reports lint failures
- Before `gz git-sync` to prevent sync rejection

## When NOT to Use

- For formatting only — use `/format` instead (ruff format without lint)
- For type checking — use `/gz-typecheck` instead

## Procedure

1. Run `uv run gz lint` which executes:
   - `ruff check .` — Python linting (style, imports, complexity, security)
   - `pymarkdown scan` — Markdown linting (docs quality)

2. If violations are found:
   - Run `uv run ruff check . --fix` for auto-fixable violations (unused imports, formatting, simple transforms)
   - Run `uv run ruff format .` to apply formatting after fixes
   - Re-run `uv run gz lint` to confirm remaining violations

3. Report results as pass (exit 0) or fail (exit 1) with violation categories.

## Reasoning

- **Auto-fix first, then manual:** Ruff's `--fix` handles ~60% of violations safely. Always try auto-fix before manual remediation.
- **Lint before format:** `ruff check --fix` may change imports/structure; `ruff format` normalizes whitespace after. Order matters.
- **Don't suppress warnings:** If a rule triggers, either fix it or configure the exclusion in `pyproject.toml` — never `# noqa` without justification.

## Edge Cases

- **Partial failure:** Ruff may pass but PyMarkdown may fail (or vice versa). Both must pass for a green lint.
- **New rule violations after ruff upgrade:** Pin ruff version in `pyproject.toml`; upgrade is a deliberate choice, not an accident.
- **Files outside src/:** Ruff config in `pyproject.toml` scopes to `src/` and `tests/`. Docs markdown is scoped separately via PyMarkdown config.

## Output Contract

- **Exit 0:** All checks pass — no violations found
- **Exit 1:** Violations remain after auto-fix — agent must address manually or escalate
- **Stdout:** Human-readable violation list with file:line:column references
- **Machine:** `uv run ruff check . --output-format json` for structured output

## Related Skills

- `/format` — formatting only (subset of lint)
- `/gz-check` — full quality suite (lint + typecheck + test)
- `/gz-arb` — lint with receipt artifacts for audit trails
