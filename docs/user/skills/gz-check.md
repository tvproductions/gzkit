# /gz-check

Run the full quality check suite in one pass, including Claude surface
validation when running in Claude Code.

---

## Purpose

`/gz-check` runs the `gz check` command and then validates Claude-specific
surfaces (hooks, generated mirrors, CLAUDE.md budget) to ensure the full
operator environment is healthy. It is the single command you run when you need
comprehensive quality and configuration assurance before a merge or attestation.

## When to Use

Invoke `/gz-check` at these workflow decision points:

- **Pre-merge** — run the full quality suite before merging a branch to confirm
  lint, typecheck, tests, and governance validations all pass.
- **Pre-attestation** — before starting a closeout ceremony, verify that all
  quality surfaces and Claude configuration surfaces are healthy.
- **After hook or surface changes** — if you modified `.claude/settings.json`,
  skill mirrors, or rules files, run `/gz-check` to confirm nothing broke.

This skill extends `/gz-arb` by adding Claude surface checks. Use `/gz-arb`
when you only need code quality evidence; use `/gz-check` when you also need
configuration health assurance. See [Runbook: Quality Loop](../runbook.md) for
the full verification workflow.

## What to Expect

The skill runs in two phases:

**Phase 1 — Quality checks:**

Runs `uv run gz check`, which executes lint, typecheck, test, and governance
validations in a single composite pass. Output shows each check's result.

**Phase 2 — Claude surface checks** (Claude Code only):

1. Verifies no hook errors appeared at session start.
2. Confirms generated surfaces (`.claude/skills/`, `.claude/rules/`) match their
   canonical sources in `.gzkit/`.
3. Checks that `CLAUDE.md` is under 200 lines for optimal adherence.

If surface issues are found, the skill invokes `@claude-code-guide` to diagnose
against current Anthropic documentation.

Typical runtime is 30-90 seconds for quality checks plus a few seconds for
surface validation.

**Success** looks like: all quality checks pass, no hook errors, surfaces in
sync, CLAUDE.md under budget.

**Failure** looks like: quality check failures (fix code), hook errors (fix
`.claude/settings.json`), or surface drift (run `gz agent sync control-surfaces`).

## Invocation

```text
/gz-check
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(none)* | — | Runs the full check workflow with no arguments |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-check/SKILL.md` | Agent execution instructions | Read |
| `.claude/skills/gz-check/agents/openai.yaml` | OpenAI agent definition for cross-vendor use | Read |
| `.claude/settings.json` | Hook configuration validated during surface checks | Read |
| `CLAUDE.md` | Checked for line budget compliance | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz check`](../commands/check.md) | The CLI command this skill wraps |
| [`/gz-arb`](gz-arb.md) | Quality-only workflow (no Claude surface checks) |
| [`/gz-gates`](gz-gates.md) | Gate verification that depends on check results |
| [`/gz-agent-sync`](gz-agent-sync.md) | Regenerates surfaces when drift is detected |
| [`/git-sync`](git-sync.md) | Typically follows after checks pass |
