# gzkit

Keep humans in the loop when AI writes code.

---

## Operational Contract

gzkit enforces a ledger-first GovZero workflow:

1. Record intent (`gz specify`, `gz plan`)
2. Execute and verify (`gz gates`, tests/docs checks)
3. Present closeout evidence (`gz closeout`)
4. Record human attestation (`gz attest`)
5. Reconcile post-attestation (`gz audit`)
6. Record receipts/accounting (`gz adr emit-receipt`)

---

## Start Here

- [Quickstart](quickstart.md)
- [Runbook](runbook.md)
- [Commands](commands/index.md)
- [Canonical GovZero docs](../governance/GovZero/charter.md)

---

## Flow

```text
gz init -> gz specify -> gz plan -> implement/verify -> gz closeout -> gz attest -> gz audit -> gz adr emit-receipt
```
