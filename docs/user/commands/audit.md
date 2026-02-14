# gz audit

Run ADR audit reconciliation and persist audit artifacts.

---

## Usage

```bash
gz audit <ADR-ID> [--json] [--dry-run]
```

---

## Runtime Behavior

`gz audit` is strict post-attestation.

- If the target ADR has no human attestation event, the command exits non-zero.
- The failure response includes explicit next steps (`gz closeout`, then `gz attest`).
- `--dry-run` is non-mutating but still enforces post-attestation gating.

After attestation is present, the command:

1. Creates `<adr-dir>/audit/` and `<adr-dir>/audit/proofs/`.
2. Runs verification commands from manifest defaults (test/lint/typecheck/docs).
3. Writes proof files under `audit/proofs/`.
4. Writes `AUDIT_PLAN.md` and `AUDIT.md`.

If any verification command fails, `gz audit` exits non-zero.

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable results/blockers |
| `--dry-run` | Show intended actions without writing files |

---

## Example

```bash
uv run gz audit ADR-0.3.0
```
