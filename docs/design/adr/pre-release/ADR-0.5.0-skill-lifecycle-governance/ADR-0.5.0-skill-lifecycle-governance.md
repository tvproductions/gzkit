---
id: ADR-0.5.0-skill-lifecycle-governance
status: Proposed
semver: 0.5.0
lane: heavy
parent: ADR-0.4.0-skill-capability-mirroring
date: 2026-02-18
---

# ADR-0.5.0: Skill Lifecycle Governance

## Intent

Define the lifecycle contract for skills as first-class governance artifacts so capability parity is maintainable, auditable, and operator-visible over time.

## Decision

Adopt a lifecycle-governance model for canonical skills and mirrors covering taxonomy, parity verification policy, state transitions, and maintenance/deprecation operations.

Execution is decomposed into four OBPIs:

1. Skill taxonomy and capability model (`OBPI-0.5.0-01`).
2. Parity verification policy and runtime checks (`OBPI-0.5.0-02`).
3. Lifecycle transition semantics and evidence (`OBPI-0.5.0-03`).
4. Ongoing maintenance and deprecation operations (`OBPI-0.5.0-04`).

## Consequences

### Positive

- Skill alignment becomes an explicit lifecycle with operational evidence.
- Drift is detected by policy-backed checks instead of ad hoc review.
- Maintenance and deprecation become governed operations rather than one-off edits.

### Negative

- Additional governance overhead for skill authors and maintainers.
- Lifecycle metadata must be kept current to avoid false-positive audit failures.

## OBPIs

1. [`OBPI-0.5.0-01-skill-taxonomy-and-capability-model`](obpis/OBPI-0.5.0-01-skill-taxonomy-and-capability-model.md)
2. [`OBPI-0.5.0-02-parity-verification-policy`](obpis/OBPI-0.5.0-02-parity-verification-policy.md)
3. [`OBPI-0.5.0-03-lifecycle-state-transitions`](obpis/OBPI-0.5.0-03-lifecycle-state-transitions.md)
4. [`OBPI-0.5.0-04-maintenance-and-deprecation-operations`](obpis/OBPI-0.5.0-04-maintenance-and-deprecation-operations.md)

## Evidence

- [ ] Lifecycle metadata contract is defined and enforced for canonical skills.
- [ ] Parity verification policy is executable and integrated with quality checks.
- [ ] Lifecycle transitions are documented with explicit operator evidence requirements.
- [ ] Maintenance and deprecation runbooks are documented and validated.
- [ ] Human attestation recorded after heavy-lane closeout flow.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.5.0 | Pending | | | |
