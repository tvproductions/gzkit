# AUDIT TEMPLATE (Gate-5) — Live Annotation

| Field | Value |
|-------|-------|
| ADR ID | {{ADR_ID}} |
| ADR Title | {{ADR_TITLE}} |
| ADR Dir | {{ADR_DIR}} |
| Audit Date | {{AUDIT_DATE}} |
| Auditor(s) | {{AUDITORS}} |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?** Summarize the capabilities in 3-5 bullets, then demonstrate each.

### Capability 1: (name)

```bash
$ (command that demonstrates this capability)
(actual output)
```

**Why it matters:** (1-2 sentences on the value delivered)

### Capability 2: (name)

```bash
$ (command)
(output)
```

**Why it matters:** (explanation)

### Value Summary

(2-3 sentences: what the operator can do now that they couldn't before)

---

## Execution Log

Annotate each planned check with result symbols:

- ✓ Passed
- ✗ Failed (include command output snippet + remediation note)
- ⚠ Warning (non-blocking discrepancy; capture rationale)

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| (Copy from AUDIT_PLAN) | (exact command run) | __PENDING__ | (results/proof path) |
| (ADR-specific check 2) | (exact command run) | __PENDING__ | (results/proof path) |
| (Add rows for all planned checks) | | | |

## Dataset Spot Examples

Paste short console snippets or attach artifact hashes when relevant.

```text
(Example output from key commands)
(Or reference: "See {{ADR_DIR}}/audit/proofs/output.txt")
```

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | __PENDING__ |
| Data Integrity | __PENDING__ |
| Performance Stability | __PENDING__ |
| Documentation Alignment | __PENDING__ |
| Risk Items Resolved | __PENDING__ |

## Evidence Index

List all proof logs saved under `{{ADR_DIR}}/audit/proofs/`.

- {{ADR_DIR}}/audit/proofs/file1.json
- {{ADR_DIR}}/audit/proofs/file2.txt
- {{ADR_DIR}}/audit/proofs/chores/

## Recommendations

Document any shortcomings or misimplementations found:

- **Issue 1:** (Description of gap/problem)
  - **Remedy:** (Recommended fix)
- **Issue 2:** (If none, state "No blocking issues found")

## Attestation

I/we attest that ADR {{ADR_ID}} is implemented as intended, evidence is reproducible, and no blocking discrepancies remain.

Signed: _<human names & date>_
