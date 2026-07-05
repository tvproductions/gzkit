# /gz-flighttest

Drive one flight-test sortie against a target substrate to prove a gzkit
workflow end-to-end and harvest feedback that refines gzkit.

---

## Purpose

`/gz-flighttest` flies **one sortie** of the
[Flight-Test Program](../../flighttest/README.md) — a chained run of test points
that executes a gzkit workflow through its governed path against a live target
repo, with the target's ledger and receipts as the flight-data recorder. The
product of a sortie is **design feedback that refines gzkit**, not a built
target; the target is scaffolding.

The skill **operates inside the target repo**, where gzkit is the
system-under-test. It is authored and versioned in gzkit and ships via
`gz init`, but it runs on the ground in the target.

## When to Use

Invoke this skill to run the flight-test program — when advancing a flight-test
campaign, when the operator says "fly sortie S<N>", "run a flight test", or
"prove gzkit against <target>". One invocation flies exactly one sortie.

## What to Expect

The skill resolves the topmost unflown sortie whose entry gate is met, authors a
flight card (freezing the pre-registered falsifier **before** flying), pauses for
the human **test director's** Go/No-Go, flies the governed-path chain, collects
the black box, dispatches an independent **Chase** (`spec-reviewer` /
`quality-reviewer`) to verdict the pass from evidence alone, debriefs, and routes
every squawk. gzkit-directed feedback files **cross-repo** via `gz issue file`
(never a target-local `/ghi-author`).

The agent flies and advises; the human operator authorizes (Go/No-Go, Gate-5)
and the Chase verdicts — the pilot never grades its own landing.

## Invocation

```text
/gz-flighttest
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Persona

Active driver: `flight-test-engineer` — falsifier-precommitment, black-box
evidence, envelope discipline, governed-path fidelity, chase deference.

## Related

- [Flight-Test Program charter](../../flighttest/README.md)
- [Flight-card template](../../flighttest/flight-card-template.md)
- [Sortie manifest + coverage matrix](../../flighttest/manifest.md)
- [`/gz-issue-file`](gz-issue-file.md) — the cross-repo channel for gzkit-directed squawks
