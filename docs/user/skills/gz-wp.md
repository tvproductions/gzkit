# /gz-wp

Create, attach issues to, move, change, add evidence to or record an issue close on a work package (`WP-<NN>-<slug>`) through `gz wp`.

---

## Purpose

`/gz-wp` exposes the canonical gz-wp workflow for operator invocation. A work package is the record a delivery or a repair runs under (`data/catalog/work_packages.json` and its ledger events), and `gz wp` is the only writer of both.

## When to Use

Invoke this skill when a repair order or a delivery is flown as a work package: writing its record, attaching its GitHub issues, moving it through initiated, frozen, commenced, accepted and closed, recording a change on the change ladder, appending objective quality evidence, or recording an issue's close against it. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-wp/SKILL.md` (mirrored into `.claude/skills/` and `.agents/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol. Closing a package is Gate 5, the operator's own attestation.

## Invocation

```text
/gz-wp
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-wp/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-wp/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-wp/SKILL.md` | Codex mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz wp new`](../manpages/wp-new.md) | The first verb the skill wields; each `gz wp` verb has its own manpage |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
