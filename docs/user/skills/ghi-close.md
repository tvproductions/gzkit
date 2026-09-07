# /ghi-close

Do the work described in a GHI, then close it with verifiable evidence.

---

## Purpose

Drives an open GHI to its terminal state: read the GHI, execute the
prescribed fix (routed per AGENTS.md § Defect-fix routing), verify the
landed artifacts against a bounded closure contract, and close the issue with a citation comment. The skill
refuses to close on narrative alone — every disposition cites a commit SHA,
ADR ID, OBPI ID, or ARB receipt ID.

## When to Use

Invoke `/ghi-close <id>` when an operator wants a specific GHI resolved end
to end, during triage passes, or at the end of an ADR closeout when the
open-GHI list needs to be driven to zero. This is the downstream complement
to [`/ghi-author`](ghi-author.md).

## What to Expect

Four-phase flow: **read** → **execute** → **verify** → **close**. The
execute phase repairs defects through a direct `fix(...)` commit; it does not
initiate OBPI work. The close comment names the
disposition (`fixed`, `superseded`, `withdrawn`, `duplicate`, `won't-fix`)
and cites the verifiable artifact. `gh issue close` fires with a
`--comment` payload.

Before implementation, the agent records the violated invariant, relevant
input/state population and consumers, semantic acceptance evidence, and exit
condition. Older issues gain this contract during the Read phase. An
investigation uses a question and evidence deliverable instead of promising
a fix before its cause is known.

Review findings must identify a violated criterion, an omitted canonical
obligation, or a concrete evidence gap. An omitted member of the failure
mechanism or a regression caused by the repair expands the contract with
recorded evidence. Independent findings are tracked separately and do not
automatically block closure. Existing quality gates remain required.

Repeated reopening triggers reassessment of the contract, shared validation
authority, and test assumptions before another local patch. Once the contract,
review, and required checks pass, the agent closes, completes guarded sync,
and stops. There is no fixed repair-count limit that permits unresolved defects
to be marked fixed. This is procedural guidance, not a runtime enforcement gate.

## Invocation

```text
/ghi-close <id>
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `<id>` | yes | GHI number (integer; `#` prefix optional) |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/ghi-close/SKILL.md` | Agent execution instructions | Read |
| `AGENTS.md § Defect-fix routing` | Direct repair and operator authority | Read |
| `.claude/rules/gh-cli.md` | `gh` CLI guardrails | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/ghi-author`](ghi-author.md) | Upstream authoring surface |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Separate, operator-initiated planned work; never started to close a defect |
| [`/gz-obpi-sync`](gz-obpi-sync.md) | Separate authorized brief reconciliation when required |
| [`gh issue close`](https://cli.github.com/manual/gh_issue_close) | CLI the skill wraps |
