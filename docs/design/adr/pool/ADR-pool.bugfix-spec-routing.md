---
id: ADR-pool.bugfix-spec-routing
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.bugfix-spec-routing: Bugfix Spec Routing

## Status

Pool

## Intent

Give defect work a first-class spec route that is lighter at the front door but
not lighter at the evidence boundary.

Competitor systems are often better at bugfix specs: observed behavior,
expected behavior, reproduction, impact, unchanged behavior, and task wave are
captured before coding begins. gzkit already has GHI and direct-fix routing, but
it lacks a compact bugfix-spec artifact that bridges operator report, GHI,
direct-fix thresholds, and OBPI ceremony.

**Target promotion kind:** feature candidate.

**Comparator signals:** Kiro bugfix specs, Spec Kit tasks, GSD fast command
flows, Superpowers design-before-code discipline.

## Decision

When promoted, define a bugfix spec route:

```bash
gz bugfix spec <ghi-or-slug>
gz bugfix route <spec>
gz bugfix validate <spec>
```

The bugfix spec should include:

- `observed`: exact command/output or user-visible symptom
- `expected`: canonical behavior with cited source
- `unchanged`: behavior explicitly protected from regression
- `route_facts`: diff estimate, surfaces, trigger, coverage viability, recent
  `fix(...)` precedent count
- `routing_decision`: direct fix, OBPI ceremony, pool ADR, or investigation GHI
- `witnesses`: reproduction receipt, failing test, validator output, or explicit
  why a reproduction cannot be generated yet

The route should consume AGENTS.md Defect-fix routing thresholds mechanically.
It must not let agents default every bug to ceremony, and it must not let
agents patch broad behavior under a "small bugfix" narrative.

## Alternatives Considered

- **Rely on GHIs only.** Rejected. GHIs are durable observations, but the route
  decision needs a structured artifact that can feed direct fix, OBPI, or pool
  promotion.
- **Fold into operator-first spec workspace.** Rejected. Bugfixes have their
  own required shape: observed/expected/unchanged behavior and direct-fix
  thresholds.
- **Let agents decide route in prose.** Rejected. gzkit already has routing
  thresholds; the bugfix spec should make those facts visible and checkable.
- **Treat every bugfix as Lite.** Rejected. Runtime/API/schema/security
  changes inherit lane rigor from the surface touched.

## Promotion Triggers

- Defects repeatedly require follow-up clarification for observed/expected
  behavior.
- Direct-fix vs OBPI routing is disputed or inconsistently applied.
- Comparator intake highlights bugfix-spec ergonomics as an adoption gap.

## Related Destinations

- GHI defect routing
- `ADR-pool.operator-first-spec-workspace`
- `ADR-pool.spec-delta-markers`
- `ADR-pool.workflow-specification`
- `ADR-0.43.0-ghi-triage-closeout`

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
