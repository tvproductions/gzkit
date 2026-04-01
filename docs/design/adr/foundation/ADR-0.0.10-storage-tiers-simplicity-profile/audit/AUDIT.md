# AUDIT (Gate-5) — ADR-0.0.10

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.10 |
| ADR Title | Storage Tiers and Simplicity Profile |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile |
| Audit Date | 2026-03-31 |
| Auditor(s) | jeff |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?**

- Three-tier storage model (A: canonical, B: derived/rebuildable, C: external/stateful) with explicit authority boundaries
- Five portable identity surfaces (ADR-*, OBPI-*, REQ-*, TASK-*, EV-*) as frozen Pydantic models
- Tier escalation governance: Tier C requires explicit Heavy-lane ADR authorization
- Git-clone recovery: all Tier A + B state survives a fresh clone
- Pool ADR properly archived with forwarding note

### Capability 1: Three-tier storage model documentation

```bash
$ head -30 docs/governance/storage-tiers.md
# Storage Tiers Reference

**Purpose:** Define the three-tier storage model for gzkit.
**Authority:** ADR-0.0.10 — Storage Tiers and Simplicity Profile

## Three-Tier Model

| Tier | Name | Definition | Authority Boundary |
|------|------|------------|--------------------|
| **A** | Canonical | Authored markdown + append-only JSONL ledger | Human and agent authors via governed workflows |
| **B** | Derived / Rebuildable | Deterministic derived indexes rebuilt from Tier A | Automated tooling; may be deleted and regenerated |
| **C** | External / Stateful | External runtime backends | Only by explicit Heavy-lane ADR authorization |
```

**Why it matters:** Every storage location has an explicit tier classification. No silent escalation from Tier B to Tier C is possible without a Heavy-lane ADR. Operators know exactly what can be deleted (B) vs. what is sacred (A).

### Capability 2: Five portable identity surfaces

```bash
$ grep "class.*Id(BaseModel)" src/gzkit/core/models.py
class AdrId(BaseModel):     # Pattern: ADR-X.Y.Z
class ObpiId(BaseModel):    # Pattern: OBPI-X.Y.Z-NN
class ReqId(BaseModel):     # Pattern: REQ-X.Y.Z-NN-MM
class TaskId(BaseModel):    # Pattern: TASK-X.Y.Z-NN-MM-SS
class EvidenceId(BaseModel): # Pattern: EV-X.Y.Z-NN-SSS
```

All five are frozen Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` and regex-validated `raw` fields. IDs are portable across all tiers — no tier-specific translation required.

**Why it matters:** Any downstream ADR (graph engine, pipeline lifecycle) can reference governance entities by their canonical ID without worrying about which storage tier they live in.

### Capability 3: Pool ADR archived with forwarding

```bash
$ head -5 docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md
---
id: ADR-pool.storage-simplicity-profile
status: archived
superseded_by: ADR-0.0.10
archived_date: 2026-03-29
```

**Why it matters:** The pool-to-foundation promotion lifecycle is complete. The pool ADR is properly archived with a machine-readable `superseded_by` pointer.

### Capability 4: Validation surfaces pass

```bash
$ uv run gz validate --documents --surfaces
Validated: surfaces, documents
✓ All validations passed (2 scopes).
```

**Why it matters:** The storage model integrates cleanly with existing governance validation. No document or surface drift.

### Value Summary

Before ADR-0.0.10, storage locations had no formal tier classification. An innocent-looking cache could silently accumulate irreplaceable state. Now every location is classified, identity surfaces are portable frozen models, and any move to external dependencies requires an explicit governance decision.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.10` | ✓ | 4/4 OBPIs completed with evidence |
| Identity surface models | grep core/models.py | ✓ | All 5 ID models present (AdrId, ObpiId, ReqId, TaskId, EvidenceId) |
| Three-tier documentation | `docs/governance/storage-tiers.md` | ✓ | Comprehensive doc with tier catalog |
| Pool ADR archived | Check frontmatter | ✓ | status: archived, superseded_by: ADR-0.0.10 |
| Unit tests | `uv run -m unittest -q -k test_storage_tiers` | ✓ | 2 tests pass in 10.3s |
| Docs build | `uv run mkdocs build -q` | ✓ | Clean build |
| Document/surface validation | `uv run gz validate --documents --surfaces` | ✓ | All validations passed |

## Evidence Index

- `audit/proofs/audit-check.txt` — Ledger completeness output
- `audit/proofs/unittest.txt` — Storage tier test results
- `audit/proofs/storage-tiers-doc.txt` — Three-tier model doc header
- `audit/proofs/pool-archive.txt` — Pool ADR archive frontmatter
- `audit/proofs/validate.txt` — Document/surface validation output

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 4 OBPIs delivered |
| Data Integrity | ✓ Five identity surfaces with regex-validated frozen models |
| Documentation Alignment | ✓ Storage tiers doc, governance runbook, mkdocs clean |
| Risk Items Resolved | ✓ Pool ADR archived; no Tier C present; escalation governance locked |

## Recommendations

- **Advisory:** REQ coverage is 16.7% (3/18 REQs with `@covers`). OBPI-02 is at 100%; others at 0%. Non-blocking but could improve.
- No blocking issues found.

## Attestation

I/we attest that ADR-0.0.10 is implemented as intended, evidence is reproducible, and no blocking discrepancies remain.

Signed: _jeff, 2026-03-31_
