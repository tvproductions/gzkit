# Daily Workflow

This is the operator habit loop for gzkit-first GovZero parity.

---

## Operating Contract

1. OBPI is the unit of execution and completion.
2. ADR is the roll-up boundary for attestation/audit lifecycle state.
3. Repeat OBPI increments continuously; run ADR closeout only when OBPI evidence is complete.

---

## OBPI Increment Loop (Default)

1. **Orient**
   - `uv run gz status`
   - `uv run gz adr status ADR-<X.Y.Z> --json`
2. **Implement one OBPI increment**
   - scoped code/docs changes for one brief item
3. **Verify increment**
   - `uv run gz implement --adr ADR-<X.Y.Z>`
   - `uv run gz gates --gate 3 --adr ADR-<X.Y.Z>` when docs changed
4. **Document completion evidence**
   - set OBPI brief to `Completed` with substantive implementation summary
5. **Record OBPI-scoped accountability evidence**
   - `uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN>-<slug> --event completed --attestor "<Human Name>" --evidence-json '{"attestation":"observed"}'`
6. **Repeat for next OBPI**

---

## ADR Closeout Loop (When OBPI Batch Is Done)

1. `uv run gz adr audit-check ADR-<X.Y.Z>`
2. `uv run gz closeout ADR-<X.Y.Z>`
3. `uv run gz attest ADR-<X.Y.Z> --status completed`
4. `uv run gz audit ADR-<X.Y.Z>`
5. `uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated ...`

---

## Why This Order

- It prevents hidden work-in-progress at ADR scope.
- It keeps evidence close to each OBPI increment.
- It preserves human attestation as explicit ADR-level authority.
- It keeps audit/validation as post-attestation reconciliation.

---

## Related

- [Closeout](closeout.md)
- [OBPIs](obpis.md)
- [Runbook](../runbook.md)
