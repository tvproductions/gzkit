# Hexagonal Architecture (Ports and Adapters) — Influence on gzkit

> **Influence, not wholesale adoption.** gzkit borrows Cockburn's vocabulary
> (port, adapter) and the topological intuition (invariant boundaries are
> ports; concrete implementations are adapters), then maps it onto gzkit's
> own ADR-kind taxonomy. This document is the canonical reference for that
> mapping.

## Source

Alistair Cockburn, **Hexagonal Architecture** (2005), originally subtitled
*"or, Ports and Adapters"*. Source: <https://alistair.cockburn.us/hexagonal-architecture/>.

The pattern names two roles:

- **Port** — an abstract contract every implementation must honor. Defined by
  the application's invariants, not by any specific implementation.
- **Adapter** — a concrete implementation behind a port. Adapts the port's
  abstract contract to one specific outside world (database, framework, CLI,
  test fixture, etc.).

Cockburn's original framing: ports point inward to invariance; adapters point
outward to concrete dependencies. The hexagon is the application core
surrounded by adapters on every side.

## Mapping to gzkit ADR taxonomy

gzkit's ADR-kind taxonomy maps directly onto Cockburn's pattern:

| Cockburn term | gzkit ADR kind | Semver | Examples |
|---|---|---|---|
| **Port** | `foundation` | `0.0.x` | ADR-0.0.50 (validation pipeline port + redteam-terminal doctrine), ADR-0.0.51 (milestone-maintenance port + `/goal`-first-class doctrine) |
| **Adapter** | `feature` | `0.y.z` | ADR-0.48.0 (plan pipeline — adapter conforming to ADR-0.0.50's port), ADR-0.49.0 (OBPI pipeline retrofit — adapter), ADR-0.50.0 (gz-architecture-review skill — adapter into ADR-0.0.51's sweep manifest port) |
| **Pool** (gzkit-specific) | `pool` | none | Backlog: not yet classified as port or adapter |

Foundation ADRs (ports) define what every implementation MUST honor; feature
ADRs (adapters) plug into existing foundation ports with one specific
implementation.

## Why this mapping holds

The invariance test (*"Without this ADR, would the project still be the
project?"*) is structurally identical to Cockburn's port test (*"Is this an
invariant the application depends on, or one specific way of satisfying an
invariant?"*).

- If the answer is *"the project would still be the project; this is one way
  of doing X"* → adapter (feature kind).
- If the answer is *"the project would not be the project without this
  invariant"* → port (foundation kind).

The hexagonal lens clarifies edge cases the invariance test alone can leave
fuzzy. When considering whether a new ADR is foundation or feature, ask: *"Is
this defining the contract every implementation must honor (port / foundation),
or is this one implementation behind an already-defined contract (adapter /
feature)?"*

## Worked examples

### Ports (foundation)

- **ADR-0.0.50 — validation pipeline + redteam-terminal doctrine.** The port
  specifies the multi-skill orchestrator contract (stage sequence, persona
  dispatch, receipt shape, redteam terminal, fail-closed gating) every
  validation-phase implementation must honor. `gz-adr-validation-pipeline` is
  the canonical adapter.
- **ADR-0.0.51 — milestone-maintenance pipeline + `/goal`-first-class doctrine.**
  The port specifies when the maintenance milestone fires, what must be
  checked, and how convergence is bounded.

### Adapters (feature)

- **ADR-0.48.0 — `gz-adr-plan-pipeline`.** One specific implementation of
  ADR-0.0.50's port for the design phase. The port is the orchestrator
  contract; this adapter is the specific design-phase orchestrator.
- **ADR-0.49.0 — `gz-obpi-pipeline` retrofit.** Retrofits an existing adapter
  to conform to ADR-0.0.50's redteam-terminal doctrine. Still an adapter; the
  port (the redteam-terminal contract) is what it conforms to.
- **ADR-0.50.0 — `gz-architecture-review` skill.** Adapter into ADR-0.0.51's
  sweep manifest port. One specific review skill among many that the port
  allows.

### Pool ADRs are pre-classification

A pool ADR has not yet been classified as port or adapter. Promotion via
`gz adr promote --kind {foundation,feature}` is when the classification is
recorded. Pool ADRs may eventually promote to either kind based on the
invariance test outcome.

## Where this is cited

Operational guidance and the invariance test itself live in
[`docs/user/concepts/foundation-feature-invariance-test.md`](../user/concepts/foundation-feature-invariance-test.md).
That document is the canonical home for the *how do I choose* answer; this
document is the canonical home for the *what's the conceptual origin* answer.

The `gz-design` skill body cites both: the framing question presented to the
operator during ADR design is *"Is this ADR a port (an abstract contract every
implementation must honor) or an adapter (one implementation behind an
existing port)?"*

## Departures from Cockburn

Three deliberate departures from Cockburn's original framing:

1. **gzkit's "pool" kind has no Cockburn analog.** Pool ADRs are pre-port
   pre-adapter — backlog items awaiting classification. Cockburn's pattern
   has no notion of an unclassified node.
2. **Adapters don't always map to external systems.** Cockburn's adapters
   typically wrap external dependencies (DB, framework, UI). gzkit's adapters
   (feature ADRs) frequently implement internal capabilities that don't cross
   process boundaries. The pattern still holds — internal capabilities are
   "outside" the invariant core — but the framing is broader than Cockburn's
   original DB/UI/framework examples.
3. **gzkit makes the port/adapter distinction structural, not architectural.**
   Cockburn used the pattern to organize code; gzkit uses it to organize
   *governance artifacts*. The ADR is the unit, not the module. This is a
   conceptual borrowing, not a code-organization rule.

## Why this codification exists

Before this document, gzkit's ADR scaffold and `gz-design` skill body used
the term *"plug"* in place of Cockburn's canonical *"adapter."* The
terminology drifted from the source and operators picked up the wrong term
through the template scaffold. GHI #489 (filed 2026-05-18) tracks the
mechanical fix; this canon document is the durable answer to *"where did
gzkit's port/adapter framing come from"* — and prevents the next drift by
naming the source explicitly.
