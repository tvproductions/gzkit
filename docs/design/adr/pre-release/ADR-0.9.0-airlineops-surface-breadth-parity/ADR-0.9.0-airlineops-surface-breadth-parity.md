---
id: ADR-0.9.0-airlineops-surface-breadth-parity
status: Proposed
semver: 0.9.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-06
promoted_from: ADR-pool.airlineops-surface-breadth-parity
---

# ADR-0.9.0-airlineops-surface-breadth-parity: AirlineOps Control-Surface Breadth Parity

## Intent

Parity scans consistently report partial breadth parity for canonical `.claude/**` and
`.gzkit/**` surfaces. Tracking alone has not reduced the gap quickly enough. This ADR
turns parity findings into execution tranches so each cycle closes concrete deltas.

## Decision

Adopt a tranche-based breadth parity execution protocol:

1. Promote breadth parity into active SemVer execution (`ADR-0.9.0`).
2. Require each parity cycle to produce action artifacts, not only findings:
   - either merged import tranche changes, or
   - a promoted ADR + active OBPI with explicit next command-level steps.
3. Execute OBPI-0.9.0-01 as the first governance-safe `.claude/hooks` tranche
   (non-blocking hooks only).
4. Keep blocking or product-coupled canonical hooks out of the first tranche until
   compatibility adaptation is documented and tested.

## Consequences

### Positive

- Parity scans now drive immediate implementation work, not passive backlog growth.
- Canonical governance behavior can be imported in safe increments.
- Remaining gaps become explicit compatibility work instead of open-ended drift.

### Negative

- More ADR/OBPI operational overhead per parity cycle.
- Incorrect tranche selection can introduce behavior regressions if compatibility is
  not validated first.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.9.0-01: Import non-blocking `.claude/hooks` tranche with
      `.claude/settings.json` wiring and intake matrix evidence.
- [ ] OBPI-0.9.0-02: Adapt blocking/deferred canonical `.claude/hooks` for gzkit
      compatibility and record decisions with verification evidence.
- [ ] OBPI-0.9.0-03: Produce `.gzkit/**` parity intake matrix and tranche sequence
      with explicit import/defer/exclude rationale.
- [ ] OBPI-0.9.0-04: Execute approved `.gzkit/**` import tranche and synchronize
      generated mirror/control surfaces.
- [ ] OBPI-0.9.0-05: Produce parity QC and closeout evidence package for heavy-lane
      gate readiness and attestation review.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion seeded via `gz adr promote` after parity evidence showed recurring partial
breadth parity without execution closure.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`
- [ ] Parity intake matrix:
      `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`

## Alternatives Considered

- Keep this work in pool until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.9.0 | Pending | | | |
