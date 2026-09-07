# /ghi-author

Author a GitHub Issue (GHI) for a defect, enhancement, or investigation surfaced in flight.

---

## Purpose

Produces a GHI with observed evidence, canonical intent, a failure mechanism,
and a bounded closure contract. The contract names the relevant states and
consumers, required outcomes, verification, and exit condition so the downstream
[`/ghi-close`](ghi-close.md) pass can finish without repeatedly rediscovering
its scope. Proposed implementations remain hypotheses, not acceptance criteria.

## When to Use

Reach for `/ghi-author` the moment a defect surfaces that you decide not to
fix in-scope. Common triggers: a brief-boundary conflict, a class-of-failure
wider than the current patch, an investigation needing its own audit trail,
or a post-mortem finding from a ceremony step. Pair with
[`/ghi-close`](ghi-close.md) downstream.

## What to Expect

The skill checks prior issues and brief ownership, gathers evidence, drafts
the closure contract, and creates the issue through `gh`. Output includes the
issue URL and routing disposition. Existing operator authorization governs;
uncertain policy or live-brief conflicts require a ruling. An investigation
names a bounded question and evidence deliverable without inventing its cause.

Independent discoveries are tracked without automatically becoming additional
implementation work. Evidence that invalidates the active repair's contract
must be addressed under that contract; optional neighboring improvements do
not prevent a valid close.

When invoked for authoring only or to capture an independent discovery, the
skill records the issue's eligibility and next-work disposition, then returns.
It does not execute the finding or create planned artifacts as a side effect.
An eligible but unselected issue needs no invented technical blocker.

## Invocation

```text
/ghi-author
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| None | — | Supply the finding and its evidence in the conversation |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/ghi-author/SKILL.md` | Agent execution instructions | Read |
| `.claude/rules/gh-cli.md` | `gh` CLI guardrails | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/ghi-close`](ghi-close.md) | Downstream resolution + close pass |
| [`gh issue create`](https://cli.github.com/manual/gh_issue_create) | CLI the skill wraps |
