# /gz-intent-trace

Trace a sampled set of ADRs from declared intent to shipped surface, and route every gap as a correction under its owning ADR.

---

## Purpose

`/gz-intent-trace` answers one question per ADR: **does the shipped surface fulfil its original declared intent?** Every `no` is a *correction* routed under the owning ADR — never a fresh pool ADR, never new-design ceremony, and never an "enhancement". That routing is operator canon: discovering that more is needed to fulfil the intent of a feature is a correction, not an enhancement.

Distinct from `/gz-adr-audit`, which asks whether an ADR's evidence chain supports closeout. This skill asks whether the thing that shipped does what was decided.

## When to Use

Invoke after an inertness audit surfaces candidates, before a release, or when the operator reports that a capability "exists but doesn't really work". It is the deepest axis of `/gz-health-audit` and is sequenced last on purpose.

## What to Expect

A sampled diagnosis with routing, not an exhaustive pass. The skill samples by risk signal — parked/withdrawn/repudiated/uncovered OBPIs, measured-inert mechanisms, heavily-cited foundation ADRs, ADRs already failing their own evaluation binding — and records the sample *before* reading any of it.

Output is a per-claim verdict (fulfilled / correction / enhancement) with the declared claim quoted verbatim and the observed surface pasted, plus a route for each correction.

## Boundaries

- Diagnosis and routing only; never implements the corrections it finds
- Never widens the sample mid-run
- Never authors a new ADR
- Surfaces campaign collisions to the operator rather than resolving them

## Invocation

```text
/gz-intent-trace
```

The canonical execution contract lives at `.gzkit/skills/gz-intent-trace/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, `.github/skills/`).

## Related

- [`/gz-health-audit`](gz-health-audit.md) — the router that sequences this skill last
- [`/gz-adr-audit`](gz-adr-audit.md) — Gate-5 evidence audit; a different question
