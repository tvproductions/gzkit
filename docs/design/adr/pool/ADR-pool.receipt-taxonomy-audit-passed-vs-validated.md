---
id: ADR-pool.receipt-taxonomy-audit-passed-vs-validated
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI #354
amendments:
  - date: 2026-05-26
    scope: |
      Absorbing audit-runtime defects surfaced by GHI #517 cross-analyst
      diagnosis (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`).
      Findings F7 (`gz audit` auto-validates with `attestor=get_git_user()`
      at `audit_cmd.py:318-348`), F8 (AUDIT.md template completion not
      checked before `validated` receipt at `audit_cmd.py:138-199`), and
      P3-r5 (`validated` receipt emitted on audit failure — `audit_cmd.py:306`
      comment: "Emit validation receipt (always -- even on failure, to record
      the audit)") all fit the existing event-taxonomy frame proposed by this
      ADR — splitting `validated` into agent-emittable `audit-passed` plus
      operator-typed `validated` mechanically separates the failures: F7's
      auto-validation becomes legal `audit-passed` emission (no TTY gate); F8's
      template incompletion blocks `audit-passed`; P3-r5's audit-failure
      receipt becomes a distinct `audit-failed` event rather than misnamed
      `validated`. Existing five-event taxonomy and `--attestor-present`
      proxy preserved; no new scope claimed beyond surfacing the GHI #517
      evidence trail and renaming the on-failure receipt within the same
      taxonomy. Pattern routing: prose-vs-mechanics + tautological-test-
      surface (GHI #531) per GHI #517 operator tie-break D8 (two parallel
      dominant patterns).

# ADR-pool.receipt-taxonomy-audit-passed-vs-validated: Receipt Taxonomy: agent-emittable audit-passed vs operator-typed validated

## Status

Pool

## Date

2026-04-28

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

The current ADR-level `validated` receipt event conflates two distinct facts:

1. **Audit-pass** — a derived fact the agent can produce by running `gz adr audit-check`,
   tallying tests/BDD/coverage, validating layout, and checking that every brief-level
   Gate-5 receipt the audit consumes is present in the ledger. Agent-attestable.
2. **Gate-5 attestation** — the operator's fresh, in-the-moment attestation that the
   audit pass is correct and the ADR is fit to become canon. Human-only by GHI #290.

Today both collapse into one event name (`validated`), which fires the
`_enforce_human_attestation_authenticity` TTY gate. The skill-prescribed agent path
in `/gz-adr-audit` therefore cannot reach its own final step from a non-TTY shell —
the original Invariant-2 violation surfaced by GHI #354. The agent-relayed
co-presence proxy (audit-begin/audit-end + `--attestor-present`, landed in commit
`bbe24585`) closes the *ceremony-open* gap but leaves the *event-taxonomy* conflation
in place.

This ADR proposes splitting the event vocabulary so each fact has a named home:

- `audit-passed` — agent-emittable derived fact, headless-safe, no TTY gate.
- `validated` — operator-typed Gate-5 receipt, behavior preserved exactly as today.

Lifecycle composes from both: an ADR advances `Pending → Validated` only when a
`validated` receipt exists *and* its evidence references an `audit-passed` receipt
on the same ADR ID. Either alone leaves the ADR at `Completed`.

---

## Design Tensions

These are the key architectural questions to resolve at promotion time:

| Tension | Option A | Option B |
|---------|----------|----------|
| **Event-name placement** | New event `audit-passed` (additive; existing `validated` semantics preserved) | Rename: `validated` becomes operator-only; new `audit-passed` as today's `validated` minus TTY gate (breaks ledger replay) |
| **Lifecycle composition** | Resolver requires both receipts (`audit-passed` + `validated` referencing it) for `Validated` lifecycle | Resolver treats `validated` as sufficient (same as today); `audit-passed` is advisory evidence only |
| **Reference shape** | `validated` evidence carries `audit_passed_receipt_id` field (explicit string ref) | Implicit pairing by ADR ID + chronological proximity (looser, simpler) |
| **Backwards compatibility** | Existing `validated` receipts in the ledger remain valid Gate-5 records; the new gate fires on the next emit only | Re-emit retroactive `audit-passed` receipts during reconciliation to anchor pre-split records |
| **Schema strictness** | `audit-passed` evidence schema requires brief-level Gate-5 receipt-IDs, audit-check JSON snapshot, test/BDD/coverage counts | Free-form evidence dict (matches today's `validated`); rely on agent discipline |
| **Skill split** | `/gz-adr-audit` Step 8 = agent emits `audit-passed`; new Step 8b = operator types `validated` | Single skill step that emits `audit-passed` and prints the operator's `validated` command, mirroring the current 6.7.0 audit-begin/end shape |

---

## Potential OBPI Decomposition (Sketch)

1. **Event registration** — Add `audit-passed` to the receipt event vocabulary; ensure it is **not** in `_HUMAN_ATTESTATION_RECEIPT_EVENTS` and runs headless.
2. **Evidence schema** — Pydantic model for `audit-passed` evidence: brief-level Gate-5 receipt IDs (list), audit-check snapshot, test/BDD/coverage counts, layout-validator status, distribution proofs.
3. **Lifecycle resolver update** — Modify the `Pending → Validated` transition to require both receipts with matching ADR ID and explicit `audit_passed_receipt_id` cross-reference in the `validated` evidence.
4. **CLI surface** — `gz adr emit-receipt <adr-id> --event audit-passed` accepts the new evidence shape; help text + manpage updates; doc-coverage manifest entry.
5. **Skill update** — `/gz-adr-audit` 6.7.0 → 6.8.0: Step 8 emits `audit-passed` agent-side; Step 8b prints the operator's `validated` command (no `--attestor-present` agent-relay needed for the audit-pass half).
6. **Reconciliation** — Decide and implement the backwards-compatibility branch chosen in the Design Tensions table (Option A: new gate fires on next emit only, vs. Option B: re-emit retroactive `audit-passed`).

---

## Dependencies

- GHI #290 — the authenticity gate this redesign respects without weakening.
- GHI #292 — `--attestor-present` co-presence proxy; preserved for OBPI-pipeline-relayed cases.
- Commit `bbe24585` (GHI #354 sub-scope) — `gz adr audit-begin` / `gz adr audit-end` already provide the ceremony-open surface; this ADR is the event-taxonomy follow-up.
- ADR-0.0.21 — first ADR closed via the audit-begin/end relay; reference precedent for `attestation_type=agent-relayed-operator-attestation`.

---

## Consequences (if promoted)

- New receipt event landing in `_RECEIPT_EVENT_VOCABULARY` (or equivalent registry).
- `_HUMAN_ATTESTATION_RECEIPT_EVENTS` membership remains unchanged for `validated`; `audit-passed` is explicitly excluded.
- Lifecycle resolver gains a cross-reference check; ledger queries grow a new evidence-field traversal.
- `/gz-adr-audit` skill step count increases by one (Step 8 + Step 8b).
- Documentation: `docs/user/manpages/adr.md`, runbook entries for the audit ceremony, and `.gzkit/rules/adr-audit.md` § Audit sequence updates.
- Operator typing burden reduced: the agent owns the audit-pass receipt; the operator's `validated` invocation references the receipt ID rather than re-typing the audit-pass evidence.

---

## Origin

Surfaced by GHI #354 during the ADR-0.0.21 audit ceremony (2026-04-28). The
audit-begin/audit-end CLI verbs landed in commit `bbe24585` as a partial sub-scope —
they close the ceremony-open gap so an agent can complete the relay, but they do not
split the event vocabulary. The remaining open scope (the event-taxonomy split) is
foundation-kind (touches receipt taxonomy, an identity-shaping fact about the ledger)
and heavy-lane (changes the CLI emit-receipt surface and the lifecycle resolver), so
it routes here for design rather than direct fix.

GHI #354 closes `superseded` against this pool ADR; this file becomes the
design-conversation home for the receipt-taxonomy split.
