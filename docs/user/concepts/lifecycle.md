# Lifecycle

ADRs are tracked from ledger events first, with docs as narrative overlay.

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

1. Orientation and scope (`gz status`, `gz adr audit-check`)
2. Verification/tool use
3. Closeout presentation (`gz closeout`)
4. Human attestation (`gz attest`)
5. Post-attestation audit (`gz audit`)
6. Receipts/accounting (`gz adr emit-receipt`)

---

## Related

- [Closeout](closeout.md)
- [Workflow](workflow.md)
- [gz adr status](../commands/adr-status.md)
- [gz status](../commands/status.md)
