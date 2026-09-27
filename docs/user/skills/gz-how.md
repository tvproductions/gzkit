# /gz-how

Answer "how do I …?" and "what can I …?" about gzkit: the flow a question belongs to, the skill to run, the look-alike not to confuse it with, the steps only you may take, and what comes next.

---

## Purpose

`/gz-how` is the map of how gzkit's skills fit together. Every skill belongs to a flow — project setup, idea to ADR, OBPI delivery, ADR closeout, release, defects and GHIs, and a dozen more — each with an order, branches, and steps reserved to the operator. The hub `SKILL.md` holds a question index, the catalog of every active skill grouped by flow, a look-alikes table, and a short guide to phase boundaries; each flow is described in its own file under `references/`.

It answers and never acts, and it reads no project state: "what should I do next here?" is `/gz-status`'s question.

Agents consult it on their own too, whenever they are unsure which skill or flow applies or are choosing between two skills that look alike.

It replaces `gz-skill-router` (GHI #1106). `gz validate --how-coverage` fails when an active skill is missing from its catalog, so it cannot fall behind the skill set the way the router did.

## When to Use

- You want to know how to do something in gzkit, or what is possible.
- You are unsure which skill fits a task.
- Two skills look alike and you need to know which one applies.

## Invocation

```text
/gz-how how do I close out an ADR?
/gz-how
```

With no question it answers "what can I do?": one line per flow, then the catalog.

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| question | No | A "how do I …" or "what can I …" question |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-how/SKILL.md` | Hub: question index, catalog, look-alikes, phase boundaries | Read |
| `.gzkit/skills/gz-how/references/*.md` | One file per flow | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-status`](gz-status.md) | Where things stand and what to do next, read from the ledger |
| [`/gz-skill-review`](gz-skill-review.md) | Reviewing a skill, part of the skill-maintenance flow |
| [skills index](index.md) | The full skill catalog |
