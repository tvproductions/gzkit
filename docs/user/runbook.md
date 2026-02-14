# Operator Runbook

This runbook is a proof surface and must match executable runtime behavior.

---

## Heavy-Lane Standard Flow

```bash
# 1) Orientation
uv run gz status
uv run gz adr audit-check ADR-<X.Y.Z>

# 2) Tool use + verification
uv run gz gates --adr ADR-<X.Y.Z>
uv run mkdocs build --strict
uv run gz lint

# 3) Closeout presentation (paths/commands only)
uv run gz closeout ADR-<X.Y.Z>

# 4) Human attestation (prerequisites enforced by default)
uv run gz attest ADR-<X.Y.Z> --status completed

# 5) Post-attestation audit (strict)
uv run gz audit ADR-<X.Y.Z>

# 6) Receipt/accounting
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"OBPI-<X.Y.Z-NN>","adr_completion":"not_completed","obpi_completion":"attested_completed","attestation":"I attest I understand the completion of OBPI-<X.Y.Z-NN>.","date":"YYYY-MM-DD"}'
```

---

## Verification Checklist

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

## Notes

- Do not run `gz audit` pre-attestation.
- Do not use receipt emission as a substitute for ADR completion attestation.
- For heavy lane without `features/`, Gate 4 is reported N/A with explicit rationale.
