# Daily Workflow

This is the operator habit loop for gzkit-first GovZero parity.

---

## Operating Contract

1. OBPI is the unit of execution and completion.
2. ADR is the roll-up boundary for attestation/audit lifecycle state.
3. After planning an OBPI, execution should flow through `uv run gz obpi pipeline`
   (or the wrapper skill `gz-obpi-pipeline`), not freeform implementation.
   The CLI and generated hook surfaces now share `src/gzkit/pipeline_runtime.py`
   as the canonical runtime engine.
4. Run ADR closeout only when OBPI evidence is complete.

---

## OBPI Increment Loop (Default)

1. **Orient**
   - `uv run gz status`
   - `uv run gz adr status ADR-<X.Y.Z> --json`
2. **Execute through the pipeline**
   - `uv run gz obpi pipeline OBPI-<X.Y.Z-NN>`
   - wrapper skill remains available: `/gz-obpi-pipeline OBPI-<X.Y.Z-NN>`
3. **Verify increment**
   - `uv run gz obpi validate path/to/OBPI-<X.Y.Z-NN>-<slug>.md`
   - `uv run gz implement --adr ADR-<X.Y.Z>`
   - `uv run gz gates --gate 3 --adr ADR-<X.Y.Z>` when docs changed
4. **Present evidence**
   - value narrative, key proof, verification outputs
5. **Run guarded sync**
   - `uv run gz git-sync --apply --lint --test`
6. **Record OBPI completion from the synced state**
   - `uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN>-<slug> --event completed ...`
   - `uv run gz obpi reconcile OBPI-<X.Y.Z-NN>-<slug>`
   - `uv run gz adr status ADR-<X.Y.Z> --json`
7. **Repeat for next OBPI**

---

## ADR Closeout Loop (When OBPI Batch Is Done)

1. `uv run gz obpi reconcile OBPI-<X.Y.Z-NN>-<slug>`
2. `uv run gz adr audit-check ADR-<X.Y.Z>`
3. `uv run gz closeout ADR-<X.Y.Z>`
4. `uv run gz attest ADR-<X.Y.Z> --status completed`
5. `uv run gz audit ADR-<X.Y.Z>`
6. `uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated ...`

---

## Why This Order

- It prevents hidden work-in-progress at ADR scope.
- It keeps evidence close to each OBPI increment.
- It preserves the verify -> ceremony -> guarded git sync -> completion accounting sequence from AirlineOps parity.
- It preserves human attestation as explicit ADR-level authority.
- It keeps audit/validation as post-attestation reconciliation.

---

## Related

- [Closeout](closeout.md)
- [OBPIs](obpis.md)
- [Runbook](../runbook.md)
