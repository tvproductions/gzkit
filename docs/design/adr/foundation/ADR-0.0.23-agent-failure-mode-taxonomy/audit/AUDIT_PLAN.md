# AUDIT_PLAN — ADR-0.0.23-agent-failure-mode-taxonomy

## Scope

Verify the COMPLETED state of ADR-0.0.23 (foundation, lite-lane,
five-OBPI taxonomy ADR) against ledger proof and demonstrate the
delivered capability before recommending VALIDATED.

## Claims extracted from ADR prose

1. Six-pattern agent failure-mode taxonomy is canonized at
   `.gzkit/rules/agent-failure-modes.md` with per-pattern
   Definition + External citation + gzkit-invariant Backstop
   shape (OBPI-0.0.23-01).
2. The taxonomy cross-links into AGENTS.md DO IT RIGHT 6c/6g/6h
   and the advisory rules audit scorecard
   (`docs/governance/advisory-rules-audit.md`) (OBPI-0.0.23-02).
3. Vendor mirrors at `.claude/rules/agent-failure-modes.md` and
   `.github/instructions/agent_failure_modes.instructions.md` stay
   in lockstep with canon via the control-surface-sync hook
   (OBPI-0.0.23-03).
4. `gz issue file` cross-repo defect filing wrapper enforces the
   gzkit-owned-surface marker check + provenance trailer
   (OBPI-0.0.23-04).
5. `gz adr audit-check` `@covers` same-commit-window backfill
   heuristic detects cosmetic backfill of REQ traceability
   decorators (OBPI-0.0.23-05).

## Checks planned

| Check | Layer | Command | Proof artifact |
|---|---|---|---|
| Layer-2 ledger proof | L2 | `uv run gz adr audit-check ADR-0.0.23` | `proofs/audit-check.txt` |
| Unit tests | L1 | `uv run -m unittest -q` | `proofs/unittest.txt` |
| Docs build | L1 | `uv run mkdocs build -q` | `proofs/mkdocs.txt` |
| Gates | L1 | `uv run gz gates --adr ADR-0.0.23` | `proofs/gates.txt` |

## Risk focus

- OBPI-0.0.23-05 implements the covers-backfill heuristic itself —
  the heuristic that audits the ADR is also the heuristic the ADR
  scopes. Self-referential surface; misalignment between
  implementation and detection would be invisible to the heuristic
  by definition.
- Foundation-kind, lite-lane: brief-level human attestation is
  required by the OBPI Acceptance Protocol (foundation kind triggers
  rigor regardless of lane). Must verify all five briefs carry
  attested completion in the ledger.
- All OBPIs were closed within the past 72 hours (last receipt
  2026-05-02T12:49). Ledger entries are fresh; staleness threshold
  (>7 days) does not apply.
