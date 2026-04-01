# AUDIT PLAN (Gate-5) — ADR-0.0.10

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.10 |
| ADR Title | Storage Tiers and Simplicity Profile |
| SemVer | 0.0.10 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile |
| Audit Date | 2026-03-31 |
| Auditor(s) | jeff |

## Purpose

Confirm ADR-0.0.10 implementation is complete by validating its claims with reproducible CLI evidence.

**Audit Trigger:** Post-attestation Gate-5 validation to advance lifecycle from Completed to Validated.

## Scope & Inputs

**Primary contract surfaces:**

- `src/gzkit/core/models.py` — five identity surface Pydantic models (ADR-*, OBPI-*, REQ-*, TASK-*, EV-*)
- `docs/governance/storage-tiers.md` — three-tier storage model documentation
- `docs/governance/governance_runbook.md` — storage tier governance reference
- Pool ADR archive: `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.10` | 4/4 OBPIs completed | Pending |
| Identity surface models | Grep for Pydantic models in core/models.py | Five ID schemes defined | Pending |
| Three-tier documentation | Check docs/governance/storage-tiers.md exists | Tier A/B/C documented | Pending |
| Pool ADR archived | Check pool ADR has forwarding note | Archived with reference | Pending |
| Git-clone recovery | Verify Tier A+B state is git-tracked | All governance data in repo | Pending |
| Unit tests | `uv run -m unittest -q -k test_storage_tiers` | All storage tier tests pass | Pending |
| Docs build | `uv run mkdocs build -q` | Clean build | Pending |

## Risk Focus

- Identity model definitions missing EV-* or TASK-* (added by this ADR)
- Pool ADR not properly archived
- Tier B items (pipeline markers) not documented

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under ADR dir `audit/proofs/`.
- No edits to accepted ADR prose.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final ✓ summary.
