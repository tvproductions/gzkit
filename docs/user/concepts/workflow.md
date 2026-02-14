# Daily Workflow

This is the operator habit loop for gzkit-first GovZero parity.

---

## Canonical Execution Order

1. **Orientation**
   - `uv run gz status`
   - `uv run gz adr audit-check ADR-<X.Y.Z>`
2. **Tool use and verification**
   - `uv run gz gates --adr ADR-<X.Y.Z>`
   - lane-required quality/docs checks
3. **Closeout presentation**
   - `uv run gz closeout ADR-<X.Y.Z>`
4. **Human attestation**
   - `uv run gz attest ADR-<X.Y.Z> --status completed`
5. **Post-attestation audit**
   - `uv run gz audit ADR-<X.Y.Z>`
6. **Receipts and accounting**
   - `uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated ...`

---

## Why This Order

- Attestation is human authority and must be explicit.
- Audit is reconciliation and is intentionally post-attestation.
- Receipts are accounting artifacts and should not be used to imply premature ADR completion.

---

## OBPI Practice Inside ADR Work

For each OBPI value increment:

1. Execute scoped implementation and verification.
2. Record OBPI brief completion evidence.
3. Optionally emit OBPI-scoped receipt evidence under the parent ADR with `adr_completion: not_completed`.

---

## Related

- [Closeout](closeout.md)
- [OBPIs](obpis.md)
- [Runbook](../runbook.md)
