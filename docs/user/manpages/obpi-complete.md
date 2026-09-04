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
| `--accept-uncovered REQ_ID` | **Cannot waive a BEHAVIOR REQ** (GHI #537). Retained so an existing invocation receives a named refusal and its recovery path, rather than an argparse error. See § The waiver refuses every REQ it can reach. |
| `--accept-uncovered-reason REASON` | Rationale for the corresponding `--accept-uncovered` entry (repeatable, 1:1 pairing). A rationale cannot substitute for a test that never ran. |
| `--accept-security-floor REASON` | Override the security-scan canonical-slot fail-closed gate when the auto-detect classified the brief security-sensitive on surface-overlap but the change is structurally defensive/additive (GHI #462). The override is recorded in console output for audit trail. |
| `--accept-stale-reconciliation` | Override a missing, stale, or drifted reconciliation receipt (OBPI-0.0.37-08). Requires `--reason TEXT` (min 10 chars). Emits `brief_reconcile_drift_overridden` to the ledger before the completion receipt. |
| `--reason TEXT` | Rationale for `--accept-stale-reconciliation` (min 10 chars). |
| `--adversary-verdict {refuted,not-refuted,refuted-with-caveats,degraded-human-only}` | Step-4b independent adversarial validation verdict. **Required on the heavy lane** (GHI #676). Emits an `adversarial_validation` ledger event before the completion receipt. |
| `--adversary IDENTITY` | Adversary identity — vendor/model (e.g. `codex/gpt-5.4`), or `human` in degraded mode. Required whenever `--adversary-verdict` is given. |
| `--adversary-job-id ID` | Adversary run id, when the runtime supplies one (e.g. a Codex `task-*` id). Recorded as provenance only — **nothing resolves it**, so it is never proof of the tier (GHI #765). |
| `--adversary-receipt RUN_ID` | ARB step receipt `run_id` proving the tier from the argv that actually ran (GHI #765). **Required for any cross-vendor (tier-1) claim** (GHI #780) — a tier-1 completion citing no receipt is blocked. Unlike `--adversary-job-id`, the gate **resolves** this: the receipt must exist, record `exit_status: 0`, and its `step.command[0]` must be a recognized different-vendor binary. Precedence is **proven > declared > inferred**, and only the `proven` rung admits tier 1 — a receipt contradicting `--adversary-tier 1` fails closed. Produce one with `gz arb step --name codexadversary -- codex exec '<refute prompt>'`. |
| `--refuted-claim TEXT` | The specific claim the adversary broke, verbatim. |
| `--adversary-resolution TEXT` | How a refutation was closed and re-verified. **Required when `--adversary-verdict` is `refuted` OR `refuted-with-caveats`** — a known refutation may never be handed to the operator dressed as clean, and a caveat is a refutation the adversary named and did not withdraw (GHI #959). |
| `--adversary-fallback-reason TEXT` | Why Codex (tier 1, cross-vendor) was unavailable, when a Claude-family (tier-2) adversary ran. **Required for a non-cross-vendor adversary** (GHI #678) — Codex is required first because a Claude validating Claude shares this agent's blind spots; "it was convenient" is not a reason. |
| `--adversary-tier {1,2,3}` | Declared Step-4b tier: 1 cross-vendor, 2 independent same-vendor, 3 degraded. **The declaration governs but does not authorize**: tier 1 named against an adversary that is not a recognized different-vendor model fails closed, tier 1 with no `--adversary-receipt` fails closed (GHI #780), and tier 2/3 still requires `--adversary-fallback-reason` even when the adversary is named after a tier-1 vendor. Omitting it no longer falls back to name-based inference for a tier-1 claim — an unproven cross-vendor name is refused whether or not a tier is declared (GHI #678, #780). |
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
# The adversary found nothing. A cross-vendor claim carries its receipt (GHI #780);
# --adversary-job-id is provenance only and never substitutes for one.
uv run gz obpi complete OBPI-0.33.0-01-airlock-data-model-and-events \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict not-refuted --adversary codex/gpt-5.4 \
  --adversary-tier 1 \
  --adversary-receipt arb-step-codexadversary-c2f59259604a42d68ba594842a624794 \
  --adversary-job-id task-mrcrhhaq-dambrd

# The adversary refuted the work; the gap was fixed and re-verified.
uv run gz obpi complete OBPI-0.33.0-01-airlock-data-model-and-events \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict refuted --adversary codex/gpt-5.4 \
  --adversary-tier 1 \
  --adversary-receipt arb-step-codexadversary-c2f59259604a42d68ba594842a624794 \
  --refuted-claim 'closed enum vocabularies are not fail-closed' \
  --adversary-resolution 'membership assertions added to REQ-03/04; the adversary
   mutation (Authority.MATE + Decision.DEFER + Verdict.REVIEW) now FAILS'

# Codex was genuinely unavailable, so an independent same-vendor subagent ran.
# The tier-2 path needs no receipt — it claims no cross-vendor property.
uv run gz obpi complete OBPI-0.0.99-01-example \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict not-refuted --adversary claude/general-purpose \
  --adversary-tier 2 \
  --adversary-fallback-reason 'codex setup reported ready=false (not authenticated)'

# Neither a different-vendor adversary nor an independent subagent could run.
# The degraded floor is explicit and attested — never silence.
uv run gz obpi complete OBPI-0.0.99-01-example \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict degraded-human-only --adversary human
```

`--adversary-verdict refuted` or `refuted-with-caveats` without `--adversary-resolution`
is blocked. The lite
lane is exempt, matching the lane that already carries fail-closed Gate 3 and Gate 4.

### Proving the tier rather than asserting it (GHI #765, #780)

Run the adversary **under ARB**, then cite the receipt it prints. ARB records the
argv at invocation time, so the cross-vendor property is read from what ran rather
than from the identity string you typed:

```console
$ uv run gz arb step --name codexadversary -- codex --version
codex-cli 0.147.0
arb step name=codexadversary exit_status=0 receipt=artifacts/receipts/arb-step-codexadversary-c2f59259604a42d68ba594842a624794.json
```

```bash
uv run gz obpi complete OBPI-0.0.99-01-example \
  --attestor 'g0' --attestation-text 'attest completed' \
  --adversary-verdict not-refuted --adversary 'independent Codex subagent' \
  --adversary-tier 1 \
  --adversary-receipt arb-step-codexadversary-c2f59259604a42d68ba594842a624794
```

Note the adversary name above does **not** begin with a vendor token, so name-based
inference alone would have refused it as tier 1. The receipt admits it, because
`step.command[0]` is `codex`. The converse also holds: a receipt whose argv ran a
same-family tool blocks a `--adversary-tier 1` declaration, since the declaration
would contradict the caller's own evidence.

The name channel is deliberately left conservative rather than "fixed". It cannot
distinguish mention from use — two adversary identities already in the ledger read
`codex-unavailable`, and any scan admitting a *mentioned* vendor would classify
those degraded Claude-family runs as tier 1, failing open on the exact substitution
Step 4b exists to catch.

#### The receipt is required, not merely available (GHI #780)

GHI #765 made the receipt channel authoritative when cited and optional when
absent, which closed nothing: the gate cannot tell *"no receipt because the
adversary could not be wrapped"* from *"no receipt because none was run"*, so the
honest and the hollow completion arrived as the same input. Every rung of the
precedence ladder below `proven` is a string the claiming agent typed, and their
agreement is self-agreement rather than corroboration.

A **resolved** cross-vendor claim now requires the receipt — not merely a declared
`--adversary-tier 1`. Gating the declaration alone would have fenced a path no
completion has ever used: of the 17 `adversarial_validation` events on the ledger,
**zero** declare a tier and **14** resolved cross-vendor through the name scan, so
the inference path was not a legacy tail but the whole of the surface.

This raises the bar on future completions; it invalidates no record. The gate is a
completion-time check over the invocation in hand and never re-reads history. The
tier-2 path stays reachable with no receipt, deliberately: an unavailable Codex must
remain **recordable**, because a gate whose only admissible shape demanded a receipt
would push an honest degraded run into claiming a false tier 1.

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
| 3 | REQ-coverage gate: one or more REQs in `## Acceptance Criteria` lack a passing `@covers`-decorated unit test or `@REQ-*` BDD scenario tag (heavy-lane or foundation-kind briefs); or `--accept-uncovered` named a BEHAVIOR REQ, which cannot be waived on any lane (GHI #537); or reconciliation-receipt gate: no fresh `brief_reconciled` receipt for the OBPI (use `gz obpi brief-drift <OBPI-ID>` or `--accept-stale-reconciliation --reason TEXT` to override) |

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
