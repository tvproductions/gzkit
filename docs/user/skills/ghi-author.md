# /ghi-author

Author a GitHub Issue (GHI) for a defect, enhancement, or investigation surfaced in flight.

---

## Purpose

Produces a well-formed GHI when a finding cannot be fixed inside the active
patch — scope expansion would violate the current brief's Allowed Paths, the
fix requires ceremony the active task cannot host, or the finding simply
deserves a trackable home before routing. The skill writes the GHI body in
the governance-doctrine shape (Summary, Non-goals, Proposed resolution,
Verification checklist, Related) so the downstream `/ghi-close` pass has the
evidence it needs.

## When to Use

Reach for `/ghi-author` the moment a defect surfaces that you decide not to
fix in-scope. Common triggers: a brief-boundary conflict, a class-of-failure
wider than the current patch, an investigation needing its own audit trail,
or a post-mortem finding from a ceremony step. Pair with
[`/ghi-close`](ghi-close.md) downstream.

## What to Expect

The skill drafts a GHI body interactively, confirms the title and labels,
and opens the issue via `gh issue create`. Output is the created issue URL.
No repo files are modified. Operator reads the draft before the skill runs
`gh`; nothing lands without that review.

## Invocation

```text
/ghi-author
/ghi-author "short title seed"
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| Title seed | no | Optional short phrase to scaffold the title |

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
