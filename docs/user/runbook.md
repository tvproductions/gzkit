# Operator Runbook

This runbook is a proof surface and must match executable runtime behavior.

---

## Operating Model (OBPI-First)

- The atomic unit of delivery is the OBPI (One Brief Per Item).
- ADRs are planning and attestation containers that roll up many OBPIs.
- Daily execution should iterate OBPI-by-OBPI, not wait for end-of-ADR batching.

---

## Loop A: OBPI Increment (Primary Daily Loop)

```bash
# 1) Orientation + parent ADR context
uv run gz status
uv run gz adr status ADR-<X.Y.Z> --json

# 2) Implement one OBPI increment (code + docs as needed)
# 3) Verify this increment
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz gates --gate 3 --adr ADR-<X.Y.Z>   # when docs changed
uv run gz lint

# 4) Update the OBPI brief with substantive implementation evidence
#    (status Completed + concrete summary, not placeholders)

# 5) Record OBPI-scoped receipt evidence under the ADR
uv run gz adr emit-receipt ADR-<X.Y.Z> --event completed --attestor "<Human Name>" --evidence-json '{"scope":"OBPI-<X.Y.Z-NN>","adr_completion":"not_completed","obpi_completion":"attested_completed","attestation":"I attest I understand the completion of OBPI-<X.Y.Z-NN>.","date":"YYYY-MM-DD"}'
```

---

## Loop B: ADR Closeout (After OBPI Batch Completion)

Run this only when linked OBPIs are complete and evidenced.

```bash
# 1) Reconcile ADR <-> OBPI completeness
uv run gz adr audit-check ADR-<X.Y.Z>

# 2) Closeout presentation (paths/commands only)
uv run gz closeout ADR-<X.Y.Z>

# 3) Human attestation (prerequisites enforced by default)
uv run gz attest ADR-<X.Y.Z> --status completed

# 4) Post-attestation audit (strict)
uv run gz audit ADR-<X.Y.Z>

# 5) Receipt/accounting at ADR scope
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

---

## Verification Checklist (OBPI + ADR)

- `uv run -m unittest discover tests`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run mkdocs build --strict`
- `uv run gz validate --documents`
- `uv run gz cli audit`
- `uv run gz check-config-paths`
- `uv run gz adr audit-check ADR-<X.Y.Z>`
- `uv run gz adr status ADR-<X.Y.Z> --json`
- `uv run gz status --json`

---

## AirlineOps Parity Scan Canonical-Root Rules

When running parity scans, canonical root resolution is deterministic and fail-closed:

1. explicit override (if provided)
2. sibling path `../airlineops`
3. absolute fallback `/Users/jeff/Documents/Code/airlineops`

If none resolve, stop and report blockers. Do not claim parity completion without canonical-root evidence.

---

## Notes

- Do not run `gz audit` pre-attestation.
- Do not use OBPI-scoped receipt emission as a substitute for ADR completion attestation.
- For heavy lane without `features/`, Gate 4 is reported N/A with explicit rationale.
