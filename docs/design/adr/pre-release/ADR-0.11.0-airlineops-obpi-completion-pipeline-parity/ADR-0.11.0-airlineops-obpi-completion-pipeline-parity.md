---
id: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
status: Proposed
semver: 0.11.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-10
---

# ADR-0.11.0-airlineops-obpi-completion-pipeline-parity: AirlineOps OBPI completion pipeline parity

## Intent

gzkit has partial OBPI-first behavior from `ADR-0.7.0-obpi-first-operations`
and emerging runtime state work from `ADR-0.10.0-obpi-runtime-surface`, but it
still does not implement the full AirlineOps OBPI completion pipeline.

For this ADR, AirlineOps is the working and effective reference for gzkit's
governance design. gzkit should adapt product-coupled details where needed, but
it should not invent alternate OBPI pipeline semantics when AirlineOps already
proves the pattern operationally.

The missing delta is specific, not abstract:

- OBPI execution is not yet treated as a bounded transaction with fail-closed
  scope isolation.
- Completion validation does not yet enforce changed-files auditing and guarded
  git-sync readiness as one pipeline.
- Completion receipts do not yet carry the full anchor-aware evidence envelope
  needed for faithful per-OBPI drift reconciliation.
- Template, operator, and closeout surfaces do not yet express one canonical
  completion ceremony that matches AirlineOps.

This ADR closes that gap by porting the combined governance/runtime model from
AirlineOps `ADR-0.0.29-obpi-completion-anchoring`,
`ADR-0.0.32-govzero-obpi-transaction-protocol`, and the operator-facing
`../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md` control surface into
gzkit-native surfaces.

## Decision

Implement faithful AirlineOps OBPI completion parity as a six-unit heavy-lane
package:

1. **Transaction Contract**: define OBPI as a bounded transaction with explicit
   allowlist law, changed-files audit, serialized spine-touch policy, and
   parallel-safe execution doctrine (`OBPI-0.11.0-01`).
2. **Blocking Validator Pipeline**: enforce completion prerequisites through a
   fail-closed validator that checks evidence completeness, scope compliance,
   git-sync readiness, and heavy-lane attestation prerequisites
   (`OBPI-0.11.0-02`).
3. **Recorder + Anchor Receipts**: record completion transitions with git
   anchor capture and structured receipt evidence while preserving the
   non-blocking post-completion recorder behavior from AirlineOps
   (`OBPI-0.11.0-03`).
4. **Anchor-Aware Drift + Reconcile**: compare recorded OBPI anchors and scope
   evidence against current repository state so reconciliation reports exact
   per-OBPI drift causes instead of only ledger/file disagreement
   (`OBPI-0.11.0-04`).
5. **Pipeline Skill Surface**: port the `gz-obpi-pipeline` skill as a canonical
   `.gzkit` skill with mirrored agent surfaces so post-plan OBPI execution
   follows one staged ritual instead of freeform implementation
   (`OBPI-0.11.0-05`).
6. **Template + Closeout Alignment**: align OBPI brief templates, heavy-lane
   planning guidance, operator docs, and closeout ceremony surfaces to the same
   staged protocol (`OBPI-0.11.0-06`).

This ADR extends existing gzkit work rather than replacing it:

- `ADR-0.7.0` established OBPI-first runtime intent, but at too coarse a
  decomposition to capture the full AirlineOps transaction model.
- `ADR-0.10.0` remains the runtime-state foundation and should be consumed, not
  bypassed.
- `ADR-pool.execution-memory-graph` remains a dependency for broader ready /
  blocked orchestration, but it is not an excuse to omit the faithful OBPI
  completion pipeline.
- AirlineOps remains the normative reference surface for the target pipeline
  behavior until gzkit lands equivalent native control surfaces.

## Consequences

### Positive

- gzkit gets a concrete import plan for the exact AirlineOps OBPI completion
  process instead of another generic parity placeholder.
- Runtime, ledger, and governance surfaces can converge on one operator-facing
  completion ceremony.
- Drift becomes auditable at the commit-anchor and transaction-scope level.

### Negative

- This adds another heavy-lane ADR with cross-cutting runtime, docs, template,
  and hook work.
- Existing `ADR-0.7.0` and `ADR-0.10.0` surfaces will need careful migration so
  user-visible semantics do not fork.

## Decomposition Scorecard

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 6

## Checklist

- [x] OBPI-0.11.0-01: Define the OBPI transaction contract, scope isolation
      rules, and parallel-safe execution doctrine.
- [x] OBPI-0.11.0-02: Deliver the blocking completion validator pipeline with
      changed-files audit and git-sync enforcement.
- [x] OBPI-0.11.0-03: Deliver recorder and receipt semantics for git-anchored
      OBPI completion evidence.
- [x] OBPI-0.11.0-04: Deliver anchor-aware OBPI drift detection and
      reconciliation surfaces.
- [x] OBPI-0.11.0-05: Port the `gz-obpi-pipeline` skill into `.gzkit` and sync
      mirror control surfaces.
- [ ] OBPI-0.11.0-06: Align templates, closeout guidance, and operator docs to
      the faithful AirlineOps completion pipeline.

## Q&A Transcript

Draft seeded from direct parity review of:

- `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.29-obpi-completion-anchoring/`
- `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.32-govzero-obpi-transaction-protocol/`
- `../airlineops/.claude/skills/gz-obpi-pipeline/SKILL.md`
- `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/`
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/`

Key conclusion preserved here: gzkit already imported fragments of the pipeline,
but not the full bounded-transaction completion model or the anchor-aware
reconciliation protocol that makes AirlineOps operationally trustworthy. The
missing orchestration surface is the `gz-obpi-pipeline` skill itself; that must
be ported canonically under `.gzkit/skills/` and mirrored, not left as an
implicit operator habit.

## Evidence

- [ ] Canon parity source ADRs reviewed and cited
- [ ] AirlineOps pipeline skill reviewed and cited
- [ ] Draft package created under `docs/design/adr/pre-release/`
- [ ] Ledger registration recorded through `gz register-adrs`
- [ ] `gz adr status ADR-0.11.0` resolves this package after registration

## Alternatives Considered

- Keep relying on `ADR-0.7.0` plus ad hoc follow-on OBPIs.
- Treat the missing pipeline as fully blocked by
  `ADR-pool.execution-memory-graph`.
- Keep OBPI completion as a receipt/status feature set rather than a bounded
  transaction protocol.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.11.0 | Pending | | | |
