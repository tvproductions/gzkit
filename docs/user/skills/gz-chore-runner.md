# /gz-chore-runner

Run a repository chore end-to-end: discover, plan, advise, execute, and
validate.

---

## Purpose

`/gz-chore-runner` is the operator interface for executing scheduled maintenance,
refactoring, and code quality work items from the chores registry. Chores are
small, repeatable maintenance tasks defined in `config/gzkit.chores.json` — things
like cleaning up deprecated patterns, enforcing naming conventions, or running
coverage sweeps. This skill orchestrates the full chore lifecycle so you don't
have to remember the command sequence.

## When to Use

Invoke `/gz-chore-runner` in these situations:

- **Scheduled maintenance** — when a chore is due on the maintenance calendar,
  run it through the full lifecycle.
- **Code quality sweeps** — when a chore targets lint violations, type errors,
  or test coverage gaps.
- **Refactoring tasks** — when a chore defines a controlled refactoring scope
  with acceptance criteria.
- **After a release** — run due chores to clean up technical debt before the
  next development cycle.

This skill operates in the maintenance phase of the
[daily workflow](../concepts/workflow.md). Each chore has its own acceptance
criteria and lane (lite, medium, or heavy) that determines the validation
depth required.

## What to Expect

The skill runs through 6 steps:

1. **Discover** — `gz chores list` shows all registered chores and their status.
2. **Inspect** — `gz chores show <slug>` displays the chore details, lane, and
   acceptance criteria.
3. **Plan** — `gz chores plan <slug>` generates or refreshes the chore execution
   plan.
4. **Advise** — `gz chores advise <slug>` dry-runs the acceptance criteria to
   assess current state and identify what needs fixing.
5. **Execute** — implements the fixes surgically (minimal diffs, preserve
   behavior), validates locally with lint/typecheck/tests, then runs
   `gz chores run <slug>` to log the result.
6. **Audit** — `gz chores audit --slug <slug>` verifies the logged result.

Evidence is saved to `ops/chores/{slug}/proofs/`. Typical runtime varies by
chore complexity — simple lint chores take minutes, larger refactoring chores
may take longer.

**Success** looks like: all acceptance criteria pass, chore run logged, audit
clean.

**Failure** looks like: acceptance criteria fail after fixes (re-read
`CHORE.md` for the remediation procedure), or lane mismatch (chore expects
Heavy actions but you're running Lite validation).

## Invocation

```text
/gz-chore-runner <chore_slug>
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `<chore_slug>` | yes | Chore identifier from `config/gzkit.chores.json` |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-chore-runner/SKILL.md` | Agent execution instructions | Read |
| `config/gzkit.chores.json` | Chore registry with slugs, lanes, and criteria | Read |
| `ops/chores/{slug}/CHORE.md` | Per-chore workflow and remediation procedure | Read |
| `ops/chores/{slug}/proofs/CHORE-LOG.md` | Execution log and evidence | Read/Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz chores list`](../commands/chores.md) | Lists available chores |
| [`gz chores show`](../commands/chores.md) | Displays chore details |
| [`gz chores advise`](../commands/chores.md) | Dry-runs acceptance criteria |
| [`gz chores run`](../commands/chores.md) | Logs the chore execution result |
| [`/gz-arb`](gz-arb.md) | Quality checks run during chore validation |
| [`/gz-check`](gz-check.md) | Full quality check for Heavy lane chores |
