---
id: ADR-0.19.0-closeout-audit-processes
status: Proposed
semver: 0.19.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-18
promoted_from: ADR-pool.audit-system
---

# ADR-0.19.0-closeout-audit-processes: Closeout & Audit Processes

## Intent

Make **closeout** and **audit** each a single end-to-end orchestrated command that runs its full pipeline without manual subcommand chaining. Both commands must behave identically in gzkit and airlineops.

---

## Decision

Two orchestrated processes, same name and behavior in both projects:

### `closeout`

Single command that:

1. Checks OBPI completion (all briefs done)
2. Runs quality gates (lint, typecheck, test, docs, BDD per lane)
3. Records gate results
4. Prompts for human attestation
5. Records attestation
6. Marks ADR as Completed

### `audit`

Single command that:

1. Verifies ledger completeness (Layer 2 trust)
2. Runs Gate 5 verification checks
3. Demonstrates ADR value (capability walkthrough)
4. Creates audit artifacts (plan, proofs, report)
5. Emits validation receipt
6. Marks ADR as Validated

### Cross-project parity

- Same command names: `closeout`, `audit`
- Same pipeline stages in same order
- Same exit codes and error messages
- Shared contract: if it works in gzkit, it works in airlineops

---

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 9
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 9

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.19.0-01: `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline
- [ ] OBPI-0.19.0-02: `gz audit ADR-X.Y.Z` — end-to-end audit pipeline
- [ ] OBPI-0.19.0-03: Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)
- [ ] OBPI-0.19.0-04: Audit includes attestation record, gate results, evidence links
- [ ] OBPI-0.19.0-05: `audit_generated` event appended to ledger
- [ ] OBPI-0.19.0-06: Audit templates and evidence aggregation from ledger
- [ ] OBPI-0.19.0-07: ADR status transition: Completed → Validated (after audit)
- [ ] OBPI-0.19.0-08: Deprecate `gz gates` as a standalone command (subsumed by closeout)
- [ ] OBPI-0.19.0-09: Deprecate manual `gz attest` during closeout (subsumed by closeout) ---

## Target Scope

- `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline
- `gz audit ADR-X.Y.Z` — end-to-end audit pipeline
- Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)
- Audit includes attestation record, gate results, evidence links
- `audit_generated` event appended to ledger
- Audit templates and evidence aggregation from ledger
- ADR status transition: Completed → Validated (after audit)
- Deprecate `gz gates` as a standalone command (subsumed by closeout)
- Deprecate manual `gz attest` during closeout (subsumed by closeout)

---

## Dependencies

- **Related:** ADR-pool.airlineops-direct-governance-migration (cross-project command parity)

---

## Notes

- Audit runs AFTER attestation (reconciliation, not proof)
- Audit directory: `docs/design/adr/{foundation|pre-release|<major>.0}/ADR-X.Y.Z-{slug}/audit/`
- Anchor drift and dirty worktree issues that block closeout today should be resolvable within the closeout pipeline itself (re-emit + commit cycle)
- The closeout command should handle the emit-sync-emit pattern internally rather than requiring the operator to manually chain git-sync between receipt emissions
- Audit's value demonstration step (currently manual) could be partially automated by running ADR-specific CLI commands from the ADR's evidence section

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.audit-system` on 2026-03-18; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.19.0 | Pending | | | |
