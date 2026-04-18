---
id: ADR-0.8.0-gz-chores-system
status: Validated
semver: 0.8.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-04
promoted_from: ADR-pool.gz-chores-system
---

# ADR-0.8.0-gz-chores-system: gz Chores System

## Intent

Introduce a gzkit-native chore system (registry + runner + logs) so maintenance work is first-class and portable from AirlineOps without copying bespoke opsdev tooling.

## Decision

Implement the Chores System as a config-first subsystem with dedicated lifecycle commands. Decompose delivery into three focused implementation units:

1.  **Registry**: Config-first JSON definition (`OBPI-0.8.0-01`).
2.  **Runner**: Execution engine with evidence capture (`OBPI-0.8.0-02`).
3.  **Lifecycle**: Planning, listing, auditing, and logging commands (`OBPI-0.8.0-03`).

## Consequences

### Positive

- Chore execution becomes deterministic and auditable via the ledger.
- Ops work follows the same governance rigor as feature development.
- Portable chore definitions across project boundaries.

### Negative

- Additional configuration overhead for project maintainers.
- Requires consistent log management to avoid artifact bloat.

## Checklist

- [x] OBPI-0.8.0-01: Chores registry and configuration
- [x] OBPI-0.8.0-02: Chores runner and execution engine
- [x] OBPI-0.8.0-03: Chores lifecycle (plan, list, audit) and logging

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion seeded via `gz adr promote`; interview transcript not captured.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in pool until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.8.0 | Pending | | | |
