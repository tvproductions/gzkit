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
| `--adversary-verdict {refuted,not-refuted,refuted-with-caveats,degraded-human-only}` | Step-4b independent adversarial validation verdict. **Required on the heavy lane** (GHI #676). Emits an `adversarial_validation` ledger event before the completion receipt. |
| `--adversary IDENTITY` | Adversary identity — vendor/model (e.g. `codex/gpt-5.4`), or `human` in degraded mode. Required whenever `--adversary-verdict` is given. |
| `--adversary-job-id ID` | Adversary run id, when the runtime supplies one (e.g. a Codex `task-*` id). |
| `--refuted-claim TEXT` | The specific claim the adversary broke, verbatim. |
| `--adversary-resolution TEXT` | How a refutation was closed and re-verified. **Required when `--adversary-verdict refuted`** — a known refutation may never be handed to the operator dressed as clean. |
| `--json` | Machine-readable JSON output |
| `--dry-run` | Show plan without writing files |

## Step 4b — Independent adversarial validation (heavy lane)

Stage 4 of the OBPI pipeline is fail-closed: no OBPI reaches attestation without an
independent adversary, prompted to **refute**, re-deriving the completion claim from
the REQs and the repository (GHI #643). Nothing enforced that at the chokepoint, so a
run that skipped Step 4b and a run that was refuted and attested anyway left
indistinguishable durable records — the verdict lived only in an agent transcript or a
vendor cache (GHI #676).

`gz obpi complete` now refuses a heavy-lane completion unless the verdict is recorded,
and writes it to the ledger as an `adversarial_validation` event **before** the
completion receipt, so a receipt can never exist without the finding that gated it.

```bash
# The adversary found nothing.
uv run gz obpi complete OBPI-0.33.0-01-airlock-data-model-and-events \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict not-refuted --adversary codex/gpt-5.4 \
  --adversary-job-id task-mrcrhhaq-dambrd

# The adversary refuted the work; the gap was fixed and re-verified.
uv run gz obpi complete OBPI-0.33.0-01-airlock-data-model-and-events \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict refuted --adversary codex/gpt-5.4 \
  --refuted-claim 'closed enum vocabularies are not fail-closed' \
  --adversary-resolution 'membership assertions added to REQ-03/04; the adversary
   mutation (Authority.MATE + Decision.DEFER + Verdict.REVIEW) now FAILS'

# Neither a different-vendor adversary nor an independent subagent could run.
# The degraded floor is explicit and attested — never silence.
uv run gz obpi complete OBPI-0.0.99-01-example \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict degraded-human-only --adversary human
```

`--adversary-verdict refuted` without `--adversary-resolution` is blocked. The lite
lane is exempt, matching the lane that already carries fail-closed Gate 3 and Gate 4.

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
