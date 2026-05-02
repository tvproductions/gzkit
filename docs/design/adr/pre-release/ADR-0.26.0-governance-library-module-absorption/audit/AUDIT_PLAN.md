# AUDIT PLAN — ADR-0.26.0 Governance Library Module Absorption

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.26.0-governance-library-module-absorption |
| ADR Title | Governance Library Module Absorption |
| SemVer | 0.26.0 |
| ADR Dir | docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption |
| Audit Date | 2026-05-02 |
| Auditor(s) | Claude (agent) on behalf of g0 |

## Purpose

Confirm ADR-0.26.0 implementation is complete by validating its claims against ledger truth and demonstrating the resulting capabilities.

**Audit Trigger:** Post-closeout Gate-5 validation. ADR closeout phase reached `attested` on 2026-05-01; Layer 2 audit-check has been clean since OBPI-0.26.0-12 attestation. All 12 OBPIs are `attested_completed`.

## Scope & Inputs

**Primary contract surfaces (the 12-module subtraction-test outcome):**

- 12 OBPI briefs (`obpis/OBPI-0.26.0-01..12-*.md`) — each records one of three decisions: **Absorb / Confirm / Exclude** — these briefs are the deliverable.
- Absorbed code from the only `Absorb` decision (OBPI-06): `src/gzkit/temporal_drift.py` (348 L) + `tests/test_temporal_drift.py` (531 L), inherited by reference from OBPI-0.25.0-26.
- Confirm-decision incumbents that the audit must show working: `gz drift`, `gz cli audit`, `gz validate --documents`, `gz adr audit-check`, `gz adr report`.

**Decision tally (read from briefs):**

| Outcome | Count | OBPIs |
|---------|-------|-------|
| Absorb  | 1     | 06 (drift-detection) |
| Confirm | 7     | 01, 04, 07, 08, 09, 10, 12 |
| Exclude | 4     | 02, 03, 05, 11 |

**Subtraction-test claim:** `opsdev − gzkit = pure ops domain` — every reusable governance primitive in `../airlineops/src/opsdev/lib/` was either absorbed, confirmed already-owned by gzkit, or excluded as ops-specific with concrete rationale.

## Layer 2 Trust Posture

Per `.claude/skills/gz-adr-audit/SKILL.md` § Layer 2 Trust Model: when `gz adr audit-check` returns PASS for every linked OBPI, the audit consumes proof from the ledger rather than re-running Layer 1 verification. This audit follows that path.

| Layer | Verification | Status |
|-------|--------------|--------|
| L1 (per-OBPI evidence) | OBPI-0.26.0-01..12 — tests, lint, typecheck, ARB receipts cited in each brief's Human Attestation block | Trusted via ledger proof |
| L2 (ledger-of-truth) | `uv run gz adr audit-check ADR-0.26.0` | **PASS** |
| L3 (derived views) | `gz adr report ADR-0.26.0`, `gz adr status ADR-0.26.0 --json` | Confirms Lifecycle=Completed, attested |

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Layer 2 evidence | `uv run gz adr audit-check ADR-0.26.0` | PASS for all 12 linked OBPIs | Pending |
| ADR lifecycle report | `uv run gz adr report ADR-0.26.0` | All 12 OBPIs `attested_completed`, Closeout=READY, QC=READY | Pending |
| ADR status (JSON) | `uv run gz adr status ADR-0.26.0 --json` | machine-readable confirmation | Pending |
| Heavy gates summary | `uv run gz gates --adr ADR-0.26.0` | Gates 1, 2, 4 PASS; Gate 5 PENDING (manual) — Gate 3 has an orthogonal Skill Audit blocker, see Risk Focus | Pending |
| Absorbed module health (OBPI-06) | `uv run -m unittest tests.test_temporal_drift -v` | 25/25 tests pass | Pending |
| Drift CLI demo (Absorb) | `uv run gz drift --plain` | Emits drift records (one per line); exit 0 | Pending |
| CLI audit (Confirm: OBPI-10) | `uv run gz cli audit` | "CLI audit passed. Cross-coverage: 89/89 commands" | Pending |
| Document validation (Confirm: OBPI-08, -04, -12) | `uv run gz validate --documents` | exit 0 (clean validation receipt) | Pending |

## Risk Focus

1. **The 10 advisory uncovered REQs (REQ-0.26.0-02-* and REQ-0.26.0-03-*)** are by-design for Exclude outcomes — the brief itself is the deliverable; there is no gzkit code to decorate with `@covers`. Layer 2 audit-check reports them as advisory (non-blocking) for exactly this reason. Documented in this audit, not flagged as a shortfall.
2. **Gate 3 Skill Audit blocker is orthogonal** — three `[SKA-MIRROR-ASSET-MISSING]` errors on `scripts/__pycache__/triage.cpython-314.pyc` for the unrelated `ghi-triage` skill. Filed as **GHI #379** (`skill-audit: SKA-MIRROR-ASSET-MISSING fires on canonical __pycache__ files`). Not an ADR-0.26.0 evidence defect; not allowed to gate this audit per Layer 2 trust.
3. **Frontmatter drift fixed in flight.** ADR file frontmatter held `status: Pending` while ledger truth said `Completed`. Recovered with `uv run gz frontmatter reconcile` (canonical chore). Single-line edit; emitted reconciliation ledger event.

## Findings Placeholder

Captured in `audit/AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded with ✓/✗/⚠ in `audit/AUDIT.md`.
- Proofs saved under `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/audit/proofs/` and referenced from `AUDIT.md`.
- Feature Demonstration (Step 3) shows the absorbed `gz drift` capability and at least two Confirm-decision incumbents working.
- Validation receipt emitted via `gz adr emit-receipt --event validated` after operator's verbal `attest completed`.
- `gz adr report ADR-0.26.0` shows Lifecycle=Validated.

## Attestation Placeholder

Operator attestation captured in `AUDIT.md` § Attestation after `audit-end` ceremony.
