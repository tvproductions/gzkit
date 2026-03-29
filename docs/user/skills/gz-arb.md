# /gz-arb

Run the quality evidence workflow using native `gz` lint, typecheck, test, and
check commands.

---

## Purpose

`/gz-arb` is the quality evidence workflow for gzkit. It runs the four canonical
quality checks — lint, typecheck, test, and check — in sequence, producing
deterministic evidence that gates and attestation workflows depend on. Think of
it as the pre-flight checklist you run before any governance action that requires
proof of code quality.

## When to Use

Invoke `/gz-arb` at these workflow decision points:

- **Before git-sync** — run quality checks before
  `gz git-sync --apply --lint --test` to catch issues locally first.
- **Before Gate 2 / Gate 3 verification** — produce the lint, typecheck, and
  test evidence that gates require.
- **Before closeout and attestation** — ensure all quality surfaces are green
  before starting the closeout ceremony.
- **After implementation** — verify that new code passes all quality checks
  before presenting evidence.

This skill sits in the quality verification phase of the
[daily workflow](../concepts/workflow.md). It is the manual equivalent of the
automated checks that `gz git-sync` runs during sync.

## What to Expect

The skill runs four commands sequentially:

1. **`uv run gz lint`** — Ruff linting and formatting checks.
2. **`uv run gz typecheck`** — Static type checking via ty.
3. **`uv run gz test`** — Unit test suite via unittest.
4. **`uv run gz check`** — Composite quality check (runs all of the above plus
   additional governance validations).

Each command's output is displayed as it runs. If any step fails, the remaining
steps still execute so you see the full picture. Typical runtime is 30-90
seconds depending on test suite size.

**Success** looks like: all four commands exit 0 with clean output.

**Failure** looks like: lint violations, type errors, or test failures reported
with specific file and line references. Fix the reported issues and rerun.

## Invocation

```text
/gz-arb
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(none)* | — | Runs the full quality workflow with no arguments |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-arb/SKILL.md` | Agent execution instructions | Read |

This skill has no additional assets. It wraps the `gz` CLI quality commands
directly.

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz lint`](../commands/lint.md) | Individual lint command (run separately by this skill) |
| [`gz typecheck`](../commands/typecheck.md) | Individual typecheck command |
| [`gz test`](../commands/test.md) | Individual test command |
| [`gz check`](../commands/check.md) | Composite quality check command |
| [`/gz-check`](gz-check.md) | Similar skill with additional Claude surface validation |
| [`/git-sync`](git-sync.md) | Typically follows after quality checks pass |
| [`/gz-gates`](gz-gates.md) | Gate verification that depends on quality evidence |
