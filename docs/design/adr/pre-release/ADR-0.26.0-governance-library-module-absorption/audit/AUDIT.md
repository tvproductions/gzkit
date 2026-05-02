# AUDIT — ADR-0.26.0 Governance Library Module Absorption

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.26.0-governance-library-module-absorption |
| ADR Title | Governance Library Module Absorption |
| ADR Dir | docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption |
| Audit Date | 2026-05-02 |
| Auditor(s) | Claude (agent) on behalf of Jeffry Babb |

## Feature Demonstration (Step 3 — MANDATORY)

ADR-0.26.0 governs the **subtraction-test outcome** for ~6,200 lines of opsdev `lib/` governance primitives. The ADR delivers:

- **A 12-module per-brief comparison record** (1 Absorb / 7 Confirm / 4 Exclude) — the briefs are the deliverable for an absorption ADR.
- **Absorbed `temporal_drift` module** (the only Absorb path, OBPI-06) — `src/gzkit/temporal_drift.py` (348 L) + `tests/test_temporal_drift.py` (531 L) with the full opsdev public contract preserved (`DriftStatus`, `DriftResult`, `ObpiDriftResult`, `classify_drift`, `detect_drift`, `detect_obpi_drift`).
- **Confirmed gzkit-incumbent ownership** of ADR management (OBPI-01), governance policy (OBPI-04), traceability (OBPI-07), validation receipts (OBPI-08), audit ledger (OBPI-09), CLI audit (OBPI-10), and docs validation (OBPI-12) — gzkit's existing surfaces win the side-by-side.
- **Excluded as ops-specific** four modules whose surface is airline-domain (OBPI-02 academic-bibliography, OBPI-03 ops-only ADR reconciliation, OBPI-05 ledger schema duplicate, OBPI-11 artifacts-as-airline-artifacts) — each brief names the failed dimensions of the subtraction test.

### Capability 1: Drift detection (the absorbed module, OBPI-06 Absorb)

```bash
$ uv run gz drift --plain | head -10
unlinked	REQ-0.0.2-01-01
unlinked	REQ-0.0.2-01-02
unlinked	REQ-0.0.2-01-03
unlinked	REQ-0.0.2-02-01
unlinked	REQ-0.0.2-02-02
unlinked	REQ-0.0.2-02-03
unlinked	REQ-0.0.2-03-01
unlinked	REQ-0.0.2-03-02
unlinked	REQ-0.0.2-03-03
unlinked	REQ-0.0.2-04-01
```

```bash
$ uv run -m unittest tests.test_temporal_drift -v 2>&1 | tail -3
----------------------------------------------------------------------
Ran 25 tests in 1.626s
OK
```

**Why it matters:** The `gz drift` CLI is the live operator surface for the absorbed `temporal_drift` module. It detects spec → test → code drift across the entire ADR/REQ catalog by reading `.gzkit/ledger.jsonl` (centralized, per Architectural Boundary 6), normalizing short SHAs, and applying the five-branch pure classifier inherited byte-for-byte from opsdev. 25/25 unit tests are green; the public contract is preserved.

### Capability 2: CLI audit (OBPI-10 Confirm — gzkit incumbent)

```bash
$ uv run gz cli audit
CLI audit passed.
Cross-coverage: 89/89 commands fully covered.
```

**Why it matters:** OBPI-10's Confirm decision rests on gzkit already owning a contract-verification surface that subsumes opsdev's `lib/cli_audit.py`. Live evidence: `gz cli audit` enumerates all 89 registered CLI verbs and confirms every one has documented operator-facing coverage. No absorption needed.

### Capability 3: Document validation (OBPI-04, -08, -12 Confirm — gzkit incumbent)

```bash
$ uv run gz validate --documents
Validated: documents

✓ All validations passed (1 scopes).
```

**Why it matters:** Three Confirm decisions (governance policy, validation receipts, docs validation) fold into gzkit's existing `gz validate` family. The audit reproduces the receipt-style structured validation opsdev's `lib/validation_receipt.py` provides — and produces it against the live tree, on demand, with explicit pass/fail accounting.

### Capability 4: Layer-2 ledger truth (the audit's own substrate)

```bash
$ uv run gz adr audit-check ADR-0.26.0
ADR audit-check: ADR-0.26.0-governance-library-module-absorption
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.26.0-01-adr-management
  ... (12 OBPIs, all PASS)
Coverage: 50/60 REQs covered (83.3%)
```

**Why it matters:** Layer 2 audit-check confirms every linked OBPI is `attested_completed` with cited ARB receipts in its Human Attestation block. The 10 advisory uncovered REQs are by-design for Exclude outcomes (OBPI-02, -03) — the brief is the deliverable, no code lands, nothing for `@covers` to decorate. The validator correctly classifies these as advisory (non-blocking) rather than failures.

### Value Summary

Before this ADR, gzkit had partial coverage of governance primitives interleaved through `cli.py`/`ledger.py`/`validate.py`/`sync.py`, and ~6,200 lines of focused opsdev library code sat upstream as candidate primitives — uninspected. After this ADR, every reusable primitive has a documented decision: gzkit either owns the better implementation, absorbed the opsdev one (drift detection), or excluded the module with concrete subtraction-test rationale. The operator can now exercise the absorbed surface (`gz drift`), the confirmed surfaces (`gz cli audit`, `gz validate --documents`, `gz adr audit-check`), and trust that nothing reusable was left stranded in opsdev.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Layer 2 evidence | `uv run gz adr audit-check ADR-0.26.0` | ✓ | All 12 linked OBPIs PASS. 10 advisory uncovered REQs (OBPI-02/-03 Exclude) by-design. `audit/proofs/audit-check.txt` |
| ADR lifecycle report | `uv run gz adr report ADR-0.26.0` | ✓ | 12/12 OBPIs `attested_completed`; Closeout=READY; QC=READY. `audit/proofs/adr-report.txt` |
| ADR status (JSON) | `uv run gz adr status ADR-0.26.0 --json` | ✓ | Machine-readable confirmation. `audit/proofs/adr-status.json` |
| Heavy gates summary | `uv run gz gates --adr ADR-0.26.0` | ⚠ | Gate 1 PASS (after frontmatter reconcile), Gate 2 PASS, Gate 4 PASS, Gate 5 PENDING (manual). Gate 3 fails on orthogonal Skill Audit blocker — see Recommendations. `audit/proofs/gates.txt` |
| Absorbed module tests | `uv run -m unittest tests.test_temporal_drift -v` | ✓ | 25/25 tests pass in 1.626s. `audit/proofs/temporal-drift-tests.txt` |
| Drift CLI demo (Absorb path) | `uv run gz drift --plain` | ✓ | exit 0; emits drift records one-per-line. `audit/proofs/drift-detection.txt` |
| CLI audit (OBPI-10 Confirm) | `uv run gz cli audit` | ✓ | 89/89 commands covered. `audit/proofs/cli-audit.txt` |
| Document validation (OBPI-04/-08/-12 Confirm) | `uv run gz validate --documents` | ✓ | All scopes pass. `audit/proofs/validate-documents.txt` |

## Dataset Spot Examples

### Decision tally read from briefs

```text
OBPI-0.26.0-01-adr-management: Confirm
OBPI-0.26.0-02-references:     Exclude
OBPI-0.26.0-03-adr-recon:      Exclude
OBPI-0.26.0-04-adr-governance: Confirm
OBPI-0.26.0-05-ledger-schema:  Exclude
OBPI-0.26.0-06-drift-detection: Absorb
OBPI-0.26.0-07-adr-traceability: Confirm
OBPI-0.26.0-08-validation-receipt: Confirm
OBPI-0.26.0-09-adr-audit-ledger: Confirm
OBPI-0.26.0-10-cli-audit-lib:  Confirm
OBPI-0.26.0-11-artifacts-lib:  Exclude
OBPI-0.26.0-12-docs-lib:       Confirm
```

Tally: **1 Absorb / 7 Confirm / 4 Exclude**, matching the ADR's own decomposition mandate.

### Absorbed module footprint

```text
$ wc -l src/gzkit/temporal_drift.py tests/test_temporal_drift.py
     348 src/gzkit/temporal_drift.py
     531 tests/test_temporal_drift.py
     879 total
```

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ — 12/12 OBPIs `attested_completed`; Absorb path's code shipped under OBPI-0.25.0-26 with public contract preserved. |
| Data Integrity | ✓ — Layer 2 audit-check PASS; ledger reconciled with frontmatter (`gz frontmatter reconcile` applied during this audit). |
| Performance Stability | ✓ — `tests.test_temporal_drift` 25/25 in 1.626s; `gz drift` exit 0 in <1s. |
| Documentation Alignment | ✓ — Each OBPI brief carries Decision / Comparison / Implementation Summary / Key Proof / Closing Argument; ADR Attestation Block records 2026-05-01 closeout. |
| Risk Items Resolved | ⚠ — 10 advisory uncovered REQs (OBPI-02/-03 Exclude — by-design). One orthogonal blocker filed as **GHI #379** (skill-audit pycache exclusion). One in-flight frontmatter drift fixed via canonical chore. |

## Evidence Index

Proofs saved under `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/audit/proofs/`:

- `audit-check.txt` — Layer 2 ledger evidence pass for all 12 OBPIs
- `adr-report.txt` — full ADR lifecycle table
- `adr-status.json` — machine-readable status
- `gates.txt` — `gz gates --adr ADR-0.26.0` full output (includes Gate 3 orthogonal failure)
- `temporal-drift-tests.txt` — 25/25 unit-test pass for absorbed module
- `drift-detection.txt` — `gz drift --plain` representative output (Absorb-path live demo)
- `cli-audit.txt` — `gz cli audit` 89/89 cross-coverage (Confirm OBPI-10)
- `validate-documents.txt` — `gz validate --documents` clean (Confirm OBPI-04/-08/-12)

## Recommendations

- **Issue 1:** Gate 3 Skill Audit fails on `[SKA-MIRROR-ASSET-MISSING]` for `ghi-triage/scripts/__pycache__/triage.cpython-314.pyc`. Orthogonal to ADR-0.26.0; the `_collect_package_files` walker treats gitignored Python bytecode caches as canonical assets.
  - **Remedy:** Filed as **GHI #379** with proposed direct-fix scope (3-line skip in `src/gzkit/skills_mirror.py:140-156`). Per Layer 2 trust model, this audit does not gate on Layer 1 noise unrelated to the audited ADR's evidence chain.
- **Issue 2:** ADR file frontmatter held `status: Pending` while ledger truth said `Completed`. Surfaced by Gate 1 during audit.
  - **Remedy:** Resolved in flight via `uv run gz frontmatter reconcile` (canonical chore). Single-line edit; reconciliation receipt emitted.
- **Issue 3:** 10 advisory REQs without `@covers` traceability (REQ-0.26.0-02-01..05, REQ-0.26.0-03-01..05).
  - **Remedy:** No remediation required. Both OBPIs took the Exclude path; the brief itself is the deliverable, and there is no gzkit code to decorate. The audit-check's own classification ("non-blocking advisory") agrees.

## Attestation

I/we attest that ADR-0.26.0-governance-library-module-absorption is implemented as intended, evidence is reproducible, and no blocking discrepancies remain. All 12 OBPI decisions are recorded with comparison rationale; the only Absorb path's code (drift detection) is live and tested; orthogonal Skill Audit blocker tracked as GHI #379.

Signed: Jeffry Babb (operator) — agent-relayed via `gz adr audit-begin` / `gz adr audit-end` ceremony, 2026-05-02.
