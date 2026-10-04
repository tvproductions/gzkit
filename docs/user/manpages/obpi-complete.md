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
| `--attestor NAME` | Identity of the attestor. Defaults to `authorship.attestor_handle` in `.gzkit.json` when set (GHI #1036); required otherwise |
| `--attestation-text TEXT` | Substantive attestation text (required) |
| `--implementation-summary TEXT` | Implementation summary (reads from brief if omitted) |
| `--key-proof TEXT` | Key proof text (reads from brief if omitted) |
| `--attestor-present` | Retained for the `--accept-uncovered` REQ-coverage waiver path only. The prior TTY `ATTEST` human-attestation authenticity gate has been removed: Gate-5 attestation is the operator's verbatim text passed via `--attestation-text` (recorded as `attestation_type: operator-verbatim-conversational`) for every lane / kind / sensitivity. |
| `--accept-uncovered REQ_ID` | **Cannot waive a BEHAVIOR REQ** (GHI #537). Retained so an existing invocation receives a named refusal and its recovery path, rather than an argparse error. See § The waiver refuses every REQ it can reach. |
| `--accept-uncovered-reason REASON` | Rationale for the corresponding `--accept-uncovered` entry (repeatable, 1:1 pairing). A rationale cannot substitute for a test that never ran. |
| `--accept-security-floor REASON` | Override the security-scan canonical-slot fail-closed gate when the auto-detect classified the brief security-sensitive on surface-overlap but the change is structurally defensive/additive (GHI #462). The override is recorded in console output for audit trail. |
| `--accept-stale-reconciliation` | Override a missing, stale, or drifted reconciliation receipt (OBPI-0.0.37-08). Requires `--reason TEXT` (min 10 chars). Emits `brief_reconcile_drift_overridden` to the ledger before the completion receipt. |
| `--reason TEXT` | Rationale for `--accept-stale-reconciliation` (min 10 chars). |
| `--adversary-job-id ID` | Adversary run id, when the runtime supplies one (e.g. a Codex `task-*` id). Recorded on the `adversarial_validation` event as provenance only; nothing resolves it. |
| `--refuted-claim TEXT` | A claim an earlier round broke, verbatim. Recorded on the event. |
| `--adversary-resolution TEXT` | The record of what earlier rounds found and how each was discharged. Recorded on the event; it clears nothing (GHI #960). |
| `--json` | Machine-readable JSON output |
| `--dry-run` | Show plan without writing files |

## Step 4b — Independent adversarial validation

`gz obpi complete` takes no verdict, reviewer, tier or receipt from its caller. It
reads the current accepted review from the OBPI's acceptance record and refuses,
exit 3, while a required proof or independent review is missing or a finding is
open. The refusal applies on every lane. Recording proofs and reviews, the tier
rules and the degraded human floor are documented in
[`obpi-acceptance.md`](obpi-acceptance.md).

When the record is ready, completion writes an `adversarial_validation` event
**before** the completion receipt, so a receipt never exists without the review
that gated it. The event's fields come from the accepted review:

| Field | Source |
|-------|--------|
| `verdict` | `not-refuted`, or `degraded-human-only` when the accepted review is the operator's own (tier 3) |
| `adversary` | the review's reviewer id |
| `adversary_tier` | derived from the command the review's ARB receipt ran: 1 for a different-vendor binary, 2 otherwise, 3 for a human review |
| `adversary_receipt` | the ARB receipt the review was imported from |

`--adversary-job-id`, `--refuted-claim` and `--adversary-resolution` add detail to
that event and change nothing about whether completion proceeds.

`--adversary-verdict`, `--adversary`, `--adversary-receipt`,
`--adversary-fallback-reason` and `--adversary-tier` were removed (GHI #1163). The
command had accepted and ignored them since the refusal moved to the acceptance
record (GHI #985); an invocation that still passes one now exits 2.

## The waiver refuses every REQ it can reach (GHI #537)

ADR-0.0.59 makes the proof-channel mapping closed. A **BEHAVIOR** REQ's only proof is a
`@covers`-decorated test; a prose rationale cannot stand in for a test that never ran.
`gz obpi complete` now refuses to accept-uncovered any BEHAVIOR REQ, on **every lane** —
it is a proof-channel rule, not a lane policy. An untagged REQ defaults to BEHAVIOR, so
omitting the `[kind]` tag is not a bypass.

Because `_enforce_req_coverage_gate` filters SUPPORT and STRUCTURAL-FENCE REQs out
*before* collecting gaps, those kinds never reach the waiver path. The practical
consequence is that `--accept-uncovered` has no REQ kind it may waive:

```bash
uv run gz obpi complete OBPI-1.2.3-01 \
  --accept-uncovered REQ-1.2.3-01-01 \
  --accept-uncovered-reason "documentation-only; no test surface"

# Error: Completion blocked: REQ-1.2.3-01-01 tagged [BEHAVIOR] and cannot be
# accepted-uncovered. BEHAVIOR's only proof channel is a `@covers`-decorated
# test ... Recovery: author the covering test and confirm with
# `uv run gz covers <OBPI-ID>`, or retag the REQ if its claim is not a code behavior.
# exit 3
```

The flag stays registered so that an existing invocation receives this named refusal and
its recovery path, rather than an `unrecognized arguments` error.

**This is not the TTY refusal.** The kind gate fires *before* the `--attestor-present`
confirmation gate is consulted. No transport mechanism gates it — the canon-owner
directive that a headless operator-verbatim override may never be refused on transport
grounds (GHI #587) stands unchanged.

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
   writes a completion exchange record as the register entry under
   `.gzkit/locks/exchange/` and, if a lock is held for the OBPI, releases it and
   emits `obpi_lock_released` citing that record. No manual `gz obpi lock release`
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
| 3 | REQ-coverage gate: one or more REQs in `## Acceptance Criteria` lack a passing `@covers`-decorated unit test or `@REQ-*` BDD scenario tag (heavy-lane or foundation-kind briefs); or `--accept-uncovered` named a BEHAVIOR REQ, which cannot be waived on any lane (GHI #537); or reconciliation-receipt gate: no fresh `brief_reconciled` receipt for the OBPI (use `gz obpi brief-drift <OBPI-ID>` or `--accept-stale-reconciliation --reason TEXT` to override); or acceptance blocked: a required proof or independent review is missing, or a finding is open (`gz obpi acceptance <OBPI-ID> status`) |

## Examples

```bash
gz obpi complete OBPI-0.0.14-01 \
  --attestor g0 \
  --attestation-text "Lock commands verified"

gz obpi complete OBPI-0.0.14-01 \
  --attestor g0 \
  --attestation-text "Verified" \
  --implementation-summary "- Files: obpi_complete.py" \
  --key-proof "gz obpi complete exits 0" \
  --json

gz obpi complete OBPI-0.0.14-01 \
  --attestor g0 \
  --attestation-text "Verified" \
  --dry-run

# Accept an uncovered REQ with a recorded rationale (requires active pipeline marker)
gz obpi complete OBPI-0.0.14-01 \
  --attestor g0 \
  --attestation-text "Verified" \
  --accept-uncovered REQ-0.0.14-01-03 \
  --accept-uncovered-reason "REQ validated by manual integration walkthrough; no unit harness exists" \
  --attestor-present
```
