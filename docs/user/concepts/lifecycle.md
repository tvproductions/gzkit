# Lifecycle

ADRs are tracked from ledger events first, with docs as narrative overlay.
Operational delivery still happens at OBPI scope, with ADR lifecycle as roll-up state.

Canonical GovZero source: [`docs/governance/GovZero/adr-lifecycle.md`](../../governance/GovZero/adr-lifecycle.md).

---

## Canonical Lifecycle Outcomes

| Lifecycle | Meaning |
|----------|---------|
| `Pending` | Not yet attested |
| `Completed` | Attested as `completed` or `partial` |
| `Abandoned` | Attested as `dropped` |
| `Validated` | ADR-level receipt emitted with `receipt_event=validated` |

`gz status` and `gz adr status` derive these values from ledger events.
OBPI-scoped receipts that explicitly declare `adr_completion: not_completed` do not promote ADR lifecycle to `Validated`.
OBPI runtime payload fields and state names are defined in the
[OBPI Runtime Contract](../../governance/GovZero/obpi-runtime-contract.md).

---

## Derived Closeout Phase

Runtime also exposes closeout progression:

| Closeout phase | Trigger |
|---------------|---------|
| `pre_closeout` | No closeout initiation yet |
| `closeout_initiated` | `closeout_initiated` event recorded |
| `attested` | `attested` event recorded |
| `validated` | `audit_receipt_emitted` with `validated` |

This phase model is additive and does not replace canonical lifecycle terms.

---

## Attestation Mapping

CLI attestation tokens remain stable, but presentations map to canonical terms:

| Token | Canonical term | Lifecycle effect |
|------|-----------------|------------------|
| `completed` | `Completed` | `Completed` |
| `partial` | `Completed — Partial` | `Completed` |
| `dropped` | `Dropped` | `Abandoned` |

---

## Operational Sequence

1. Run OBPI increments repeatedly (implement, verify, brief evidence update)
2. Record OBPI-scoped receipts using `gz obpi emit-receipt`
   Completed receipts are fail-closed when required value narrative/key proof evidence is missing.
   Heavy/Foundation parent ADRs additionally require explicit human-attestation evidence.
3. Reconcile OBPI completeness at ADR boundary (`gz obpi reconcile`, `gz adr audit-check`)
4. Perform ADR closeout and attestation (`gz closeout`, `gz attest`)
   `gz closeout` remains blocked until linked OBPIs are closeout-ready.
5. Run post-attestation audit (`gz audit`)
6. Emit ADR-level receipt/accounting (`gz adr emit-receipt`)

---

## Related

- [Closeout](closeout.md)
- [Workflow](workflow.md)
- [gz adr status](../commands/adr-status.md)
- [gz status](../commands/status.md)
