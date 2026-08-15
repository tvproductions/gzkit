# /gz-health-audit

Namespace router for the four-axis health and integrity audit. Routes to the concrete axis surfaces in a fixed cheapest-first order, and owns the ordering rationale and the budget rule rather than the analyses themselves.

---

## Purpose

`/gz-health-audit` answers the question "is governance actually holding?" — as distinct from "does the repo pass its checks?", which `/gz-check` already answers. The distinction is the point: gzkit's validator surface audits conformance to declared invariants, and almost nothing audits whether a declared mechanism *ever fires* or whether an invariant is still coherent with its original intent. A system can pass every check it knows how to make and still be misaligned.

## When to Use

Invoke when the operator reports that gzkit feels "wobbly", misaligned, or that governance is not holding; when a capability "exists but doesn't really work"; or before a release, to confirm declared mechanisms still fire.

## What to Expect

A routing decision, not an analysis. The skill names which axis to run and in which order, then hands off:

| Axis | Surface |
|---|---|
| Conformance + validator reachability | `control-surface-validator-reachability` chore |
| Ledger vocabulary inertness | `ledger-vocabulary-inertness` chore |
| Doctrine coherence | `control-surface-rule-conflicts` chore |
| Intent trace | `/gz-intent-trace` skill |

The mechanical axes run first because they emit the risk signals the intent trace samples on. Run the trace first and those signals do not exist yet.

The skill also carries the **budget rule**: budget the audit by net surface reduction, not by findings count. An audit that adds more governance surface than it retires has made the diagnosed problem worse.

## Invocation

```text
/gz-health-audit
```

The canonical execution contract lives at `.gzkit/skills/gz-health-audit/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, `.github/skills/`).

## Related

- [`/gz-intent-trace`](gz-intent-trace.md) — the deep axis this router sequences last
- [`/gz-tech-debt-review`](gz-tech-debt-review.md) — debt across probes; this method is about mechanisms firing
