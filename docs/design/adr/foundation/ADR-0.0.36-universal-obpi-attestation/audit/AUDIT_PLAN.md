# AUDIT PLAN — ADR-0.0.36

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.36-universal-obpi-attestation |
| ADR Title | Universal OBPI Attestation (Zero-Maxxing) |
| SemVer | 0.0.36 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ |
| Audit Date | 2026-05-18 |
| Auditor(s) | g0 (operator) + agent-relayed audit (pipeline-orchestrator persona) |

## Purpose

Confirm ADR-0.0.36 implementation is complete by validating its five claims with
reproducible CLI evidence. Audit trigger: COMPLETED → VALIDATED transition
post-landing of OBPI-0.0.36-04 historical-self-close waiver list (commit
`e9f166b1`, 2026-05-17).

## Scope & Inputs

**Primary contract surfaces (per ADR § Decision):**

1. **`AGENTS.md` § OBPI Acceptance Protocol** — Lane & Kind Attestation Matrix
   collapsed; universal-attestation rule binding (OBPI-0.0.36-01)
2. **`src/gzkit/commands/adr_audit.py::_requires_human_obpi_attestation`** —
   collapsed to `return True` (OBPI-0.0.36-02)
3. **`gz validate --receipt-shape`** — fail-closed validator scope (OBPI-0.0.36-03)
4. **`data/historical_self_close_waivers.json`** — closed-entry waiver list,
   schema-validated, `added_under` constrained to OBPI-0.0.36-04 (OBPI-0.0.36-04)
5. **Skill & rule prose sweep** — `gz-obpi-pipeline`, `gz-obpi-reconcile`,
   `ghi-close`, `gz-adr-closeout-ceremony` (OBPI-0.0.36-05)

**System health surfaces:**

- `uv run gz adr audit-check ADR-0.0.36`
- `uv run gz adr status ADR-0.0.36`
- `uv run gz adr report ADR-0.0.36`
- `uv run gz validate --receipt-shape`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.36` | All 5 OBPIs PASS, 29/29 REQs covered | ✓ Confirmed |
| Lifecycle state | `uv run gz adr status ADR-0.0.36` | Lifecycle=Completed, Phase=attested, Closeout=READY, QC=READY | ✓ Confirmed |
| Runtime gate collapse | inspect `_requires_human_obpi_attestation` source | Returns `True` unconditionally | Pending proof |
| Runtime gate test universality | `uv run python -m unittest tests.test_adr_audit_predicates` | All lane/kind/sensitivity branches still require attestation | Pending proof |
| Validator fail-closed scope | `uv run gz validate --receipt-shape` | Exit 0; no post-cutoff drift in current ledger | Pending proof |
| Validator semantic tests | `uv run python -m unittest tests.governance.test_validate_receipt_shape` | All post-cutoff fail-closed + pre-cutoff waiver tests pass | Pending proof |
| Waiver list schema/closure | `python -c "load waivers; assert all added_under == OBPI-0.0.36-04"` | All entries closed-set under OBPI-0.0.36-04 | Pending proof |
| AGENTS.md matrix collapse | `grep` for universal-attestation language and absence of `Self-closeable` cell | Universal rule present; deprecated cell absent | Pending proof |
| Skill prose sweep | `rg -in 'self-clos' .gzkit/skills/` | Zero live references (historical references in this ADR's OBPI briefs are allowed) | Pending proof |
| ADR audit-check (final) | `uv run gz adr audit-check ADR-0.0.36` | PASS, 5/5 OBPIs attested_completed | ✓ Confirmed |

## Risk Focus

- **Doctrine-drift residue:** any skill/template/rule still carrying lite-lane
  self-close language constitutes a vibing-leak surface ADR-0.0.36 was
  explicitly authored to close. Treat surviving instances as shortfalls.
- **Receipt-shape backwards compatibility:** the waiver list must remain
  closed to new entries — any post-2026-04-26 entry without OBPI-0.0.36-04
  origin is a doctrine breach.
- **Layer-3 derived-view drift:** `gz status` / `gz adr report` are derived
  Layer 3; the audit trusts Layer 1 (canon) and Layer 2 (ledger), not derived
  views.

## Findings Placeholder

See `audit/AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md`.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- Shortfalls (if any) named with severity + remediation route.
- Operator verbatim ack (`accept audit` / `verify audit`) precedes validated
  receipt emission.

## Attestation Placeholder

Operator completes verbatim in `AUDIT.md` after agent relay.
