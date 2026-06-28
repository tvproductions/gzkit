# gz obpi complete

Atomically complete an OBPI: validate, write evidence, flip status,
record attestation, and emit a completion receipt in a single
all-or-nothing transaction.

## Usage

```
gz obpi complete OBPI-X.Y.Z-NN --attestor NAME --attestation-text TEXT
    [--implementation-summary TEXT] [--key-proof TEXT] [--json] [--dry-run]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to complete |
| `--attestor NAME` | Identity of the attestor (required) |
| `--attestation-text TEXT` | Substantive attestation text (required) |
| `--implementation-summary TEXT` | Implementation summary (reads from brief if omitted) |
| `--key-proof TEXT` | Key proof text (reads from brief if omitted) |
| `--attestor-present` | Retained for the `--accept-uncovered` REQ-coverage waiver path only. The prior TTY `ATTEST` human-attestation authenticity gate has been removed: Gate-5 attestation is the operator's verbatim text passed via `--attestation-text` (recorded as `attestation_type: operator-verbatim-conversational`) for every lane / kind / sensitivity. |
| `--accept-uncovered REQ_ID` | Explicitly waive an uncovered REQ (repeatable; requires `--accept-uncovered-reason`) |
| `--accept-uncovered-reason REASON` | Rationale for the corresponding `--accept-uncovered` entry (repeatable, 1:1 pairing) |
| `--accept-security-floor REASON` | Override the security-scan canonical-slot fail-closed gate when the auto-detect classified the brief security-sensitive on surface-overlap but the change is structurally defensive/additive (GHI #462). The override is recorded in console output for audit trail. |
| `--accept-stale-reconciliation` | Override a missing, stale, or drifted reconciliation receipt (OBPI-0.0.37-08). Requires `--reason TEXT` (min 10 chars). Emits `brief_reconcile_drift_overridden` to the ledger before the completion receipt. |
| `--reason TEXT` | Rationale for `--accept-stale-reconciliation` (min 10 chars). |
| `--json` | Machine-readable JSON output |
| `--dry-run` | Show plan without writing files |

## Runtime Behavior

1. Validates brief exists and is not already Completed
2. Checks evidence sufficiency (Implementation Summary, Key Proof)
3. For a requires-human brief (heavy-lane OR foundation-kind OR
   `sensitivity: security`), records the operator's verbatim
   `--attestation-text` as the Gate-5 attestation
   (`attestation_type: operator-verbatim-conversational`). A non-empty
   `--attestation-text` is required; there is no separate TTY ceremony.
4. Writes attestation to ADR-local audit ledger
5. Updates brief with evidence, attestation, and Completed status
6. Emits `obpi_receipt_emitted` event to main ledger
7. Surrenders the work lock mechanically (token-block exit edge, GHI #619):
   writes a completion handoff as the register entry under `.gzkit/handoffs/`
   and, if a lock is held for the OBPI, releases it and emits
   `obpi_lock_released` citing that handoff. No manual `gz obpi lock release`
   is required; the manual release path remains for mid-traversal surrender.

Steps 1-6 are the all-or-nothing transaction: if any step fails, all changes are
rolled back (no partial writes). Step 7 runs after the transaction commits and is
best-effort — if the register entry cannot be written the lock is left for TTL
reaping rather than surrendered without one.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | OBPI completed successfully |
| 1 | Validation failure (missing brief, already completed, insufficient evidence, or `--accept-uncovered` without `--accept-uncovered-reason`) |
| 2 | I/O error |
| 3 | REQ-coverage gate: one or more REQs in `## Acceptance Criteria` lack a passing `@covers`-decorated unit test or `@REQ-*` BDD scenario tag (heavy-lane or foundation-kind briefs); or `--accept-uncovered` override refused (no active pipeline marker / headless invocation); or reconciliation-receipt gate: no fresh `brief_reconciled` receipt for the OBPI (use `gz brief reconcile <OBPI-ID>` or `--accept-stale-reconciliation --reason TEXT` to override) |

## Examples

```bash
gz obpi complete OBPI-0.0.14-01 \
  --attestor jeff \
  --attestation-text "Lock commands verified"

gz obpi complete OBPI-0.0.14-01 \
  --attestor jeff \
  --attestation-text "Verified" \
  --implementation-summary "- Files: obpi_complete.py" \
  --key-proof "gz obpi complete exits 0" \
  --json

gz obpi complete OBPI-0.0.14-01 \
  --attestor jeff \
  --attestation-text "Verified" \
  --dry-run

# Accept an uncovered REQ with a recorded rationale (requires active pipeline marker)
gz obpi complete OBPI-0.0.14-01 \
  --attestor jeff \
  --attestation-text "Verified" \
  --accept-uncovered REQ-0.0.14-01-03 \
  --accept-uncovered-reason "REQ validated by manual integration walkthrough; no unit harness exists" \
  --attestor-present
```
