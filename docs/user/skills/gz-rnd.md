# /gz-rnd

Run a governed R&D session that retains and routes the outcomes of exploratory design work.

---

## Purpose

`/gz-rnd` governs the exploratory session that comes before gzkit's artifacts. The typical
case is pasting external material and asking whether gzkit should take something from it.
The skill keeps the session's findings and reasoning in a durable record. It routes each
finding to exactly one outcome: an ADR or OBPI proposal, a GHI, chore advice, a doc or rule
draft, a one-shot refactoring program, or take-no-action. The design and the operator's
rulings behind it are in [`docs/governance/rnd-discipline.md`](../../governance/rnd-discipline.md).

## When to Use

Invoke it when you say "consider this for gzkit", "is there something here gzkit is missing
or could improve on", or open a design discussion whose outcome is not yet known. It comes
before [`/gz-design`](gz-design.md): an R&D run may *propose* an ADR, and you decide whether
to start one. The active campaign's § Workflow fronts names R&D as a standing front.

The skill is operator-invoked only (`disable-model-invocation: true`); an agent never starts
a run by itself.

## What to Expect

- **A record** at `docs/governance/rnd/<YYYY-MM-DD>-<slug>.md` with five sections:
  Question, Findings, Outcomes, Not pursued, and What this record does not license.
- **Research sources** saved verbatim under a `sources/` directory beside the record.
- **Question rounds** batched by dependency, each question with a recommended answer.
- **An Outcomes table** where the run stops. Nothing is executed until you give a go on a
  row. ADRs and OBPIs are only ever proposed; chores are only ever advised.

A successful run ends with every finding routed or recorded as not pursued, and with no
ADR, OBPI or chore started by the run itself.

## Invocation

```text
/gz-rnd
/gz-rnd <pasted material or question>
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| material or question | no | What to consider; otherwise the run starts by asking |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-rnd/SKILL.md` | Canonical skill contract | Read |
| `.gzkit/skills/gz-rnd/assets/rnd-record-template.md` | Record template | Read |
| `docs/governance/rnd/` | R&D records and their sources | Write |
| `docs/governance/rnd-discipline.md` | Design and operator rulings | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-design`](gz-design.md) | Where an R&D proposal goes once you start an ADR |
| [`/ghi-author`](ghi-author.md) | Files outcome-2 GHIs; its Step 0 searches R&D records as prior art |
| [`/gz-chore-runner`](gz-chore-runner.md) | Runs chores; R&D only advises new ones |
| [`/gz-session-handoff`](gz-session-handoff.md) | Carries an R&D thread across sessions as its own named line |
