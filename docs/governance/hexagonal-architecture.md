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
| **Adapter** | `feature` | `0.y.z` | ADR-0.13.0 (OBPI pipeline runtime surface — adapter implementing ADR-0.0.14's deterministic-OBPI-command port), ADR-0.18.0 (subagent-driven pipeline execution — one execution-strategy adapter), ADR-0.12.0 (OBPI pipeline enforcement parity — one enforcement implementation) |
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

- **ADR-0.13.0 — `gz obpi pipeline` runtime surface.** One specific runtime
  implementation of ADR-0.0.14's deterministic-OBPI-command port: it elevates
  the `gz-obpi-pipeline` workflow into a first-class command contract (launch,
  stage progression, resume, abort, sync). The port is the command contract;
  this adapter is the specific runtime surface behind it.
- **ADR-0.18.0 — subagent-driven pipeline execution.** One execution strategy
  for the pipeline runtime — subagent dispatch — behind the same OBPI-pipeline
  contract. Its `--no-subagents` fallback preserves inline execution, which is
  the adapter tell: it is *one way* of executing, not the invariant.
- **ADR-0.12.0 — OBPI pipeline enforcement parity.** One specific
  AirlineOps-style enforcement implementation behind the pipeline contract.
  Still an adapter; the enforcement invariants are what it conforms to.

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
