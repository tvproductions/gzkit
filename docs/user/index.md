# gzkit

Keep humans in the loop when AI writes code.

---

## Operational Contract

gzkit enforces a ledger-first GovZero workflow:

1. Record intent (`gz specify`, `gz plan`)
2. Execute and verify (`gz gates`, tests/docs checks)
3. Reconcile OBPI closeout readiness (`gz obpi reconcile`, `gz adr audit-check`)
4. Present closeout evidence (`gz closeout`)
5. Record human attestation (`gz attest`)
6. Reconcile post-attestation (`gz audit`)
7. Record receipts/accounting (`gz obpi emit-receipt` for OBPI scope, `gz adr emit-receipt` for ADR scope)

---

## Start Here

- [Quickstart](quickstart.md)
- [Runbook](runbook.md)
- [Commands](commands/index.md)
- [Canonical GovZero docs](../governance/GovZero/charter.md)

---

## Flow

```text
gz init -> gz specify -> gz plan -> implement/verify -> gz obpi emit-receipt -> gz obpi reconcile -> gz adr audit-check -> gz closeout -> gz attest -> gz audit -> gz adr emit-receipt
```
