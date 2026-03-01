---
applyTo: "docs/design/adr/**"
---

# ADR Audit (gzkit)

Purpose: verify ADR completion claims using reproducible evidence.

## Audit sequence

1. Verify linked OBPI evidence:

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

2. Run quality checks:

```bash
uv run gz lint
uv run gz test
uv run gz typecheck
uv run mkdocs build --strict
```

3. Run closeout/audit lifecycle in order:

```bash
uv run gz closeout ADR-<X.Y.Z> --dry-run
uv run gz attest ADR-<X.Y.Z> --status completed
uv run gz audit ADR-<X.Y.Z>
```

4. Emit audit receipt:

```bash
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

## Rules

- Do not run `gz audit` before attestation.
- If audit-check fails, fix brief evidence first and rerun.
- Keep `docs/user/runbook.md` and `docs/governance/governance_runbook.md` aligned with runtime behavior.
