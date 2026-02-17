---
id: ADR-0.3.0
status: Proposed
semver: 0.3.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-02-13
promoted_from: ADR-pool.airlineops-canon-reconciliation
---

# ADR-0.3.0: AirlineOps Canon Reconciliation

## Intent

Promote canon reconciliation from pool to active foundation implementation and freeze a bounded execution scope for 0.3.x.

The objective is to restore governance extraction fidelity from AirlineOps without changing GovZero semantics.

## Decision

Execute reconciliation in five controlled work packages, each mapped 1:1 to an OBPI:

1. Port missing canonical `gz-*` skill surfaces.
2. Reconcile divergent shared skills (`gz-adr-audit`, `gz-adr-create`) to canonical behavior.
3. Introduce canonical `docs/governance/GovZero/` documentation surface and import missing files.
4. Reconcile charter/lifecycle/linkage/closeout semantics so gzkit concept docs are additive overlays.
5. Harden parity scan path resolution for worktree and non-worktree execution contexts.

Scope constraints:

- Canonical source remains `/Users/jeff/Documents/Code/airlineops`.
- Divergence is prohibited unless explicitly authorized by a later ADR.
- This ADR focuses on extraction parity, not product feature expansion.
- Go-runtime migration work is blocked until this ADR materially closes parity gaps.

## Consequences

### Positive

- Governance extraction gains auditable parity targets and explicit execution units.
- Risk of silent doctrine drift is reduced via canonical path restoration.
- Downstream foundation ADRs (including runtime migration) get a stable baseline.

### Negative

- 0.3.x delivery is documentation and governance heavy.
- Promotion creates immediate implementation load across skills, docs, and path-hardening logic.

## OBPIs

1. [`OBPI-0.3.0-01-skills-surface-parity`](obpis/OBPI-0.3.0-01-skills-surface-parity.md) — port missing canonical `gz-*` skills.
2. [`OBPI-0.3.0-02-divergent-skill-reconciliation`](obpis/OBPI-0.3.0-02-divergent-skill-reconciliation.md) — reconcile shared skill behavior.
3. [`OBPI-0.3.0-03-govzero-canonical-doc-surface`](obpis/OBPI-0.3.0-03-govzero-canonical-doc-surface.md) — import canonical GovZero docs.
4. [`OBPI-0.3.0-04-core-semantics-reconciliation`](obpis/OBPI-0.3.0-04-core-semantics-reconciliation.md) — reconcile charter/lifecycle/linkage/closeout semantics.
5. [`OBPI-0.3.0-05-parity-scan-path-hardening`](obpis/OBPI-0.3.0-05-parity-scan-path-hardening.md) — make parity scan repo path resolution robust.

## Evidence

- [x] Parity scan baseline and post-OBPI-0.3.0-01 update: `docs/proposals/REPORT-airlineops-parity-2026-02-13.md`
- [ ] OBPI implementation evidence captured in each brief (OBPI-0.3.0-01..03 completed; OBPI-0.3.0-04..05 pending)
- [x] `gz status` shows Gate 2 pass for ADR-0.3.0
- [ ] Human attestation recorded after heavy-lane gates are satisfied

Current note: OBPI-0.3.0-01..03 are completed; next critical path is OBPI-0.3.0-04/05 for semantic reconciliation and parity-scan hardening.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.3.0 | Pending | | | |
