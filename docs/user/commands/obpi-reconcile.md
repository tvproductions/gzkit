# gz obpi reconcile

Fail-closed reconciliation for one OBPI.

---

## Usage

```bash
gz obpi reconcile <OBPI-ID> [--json]
```

`<OBPI-ID>` accepts the full canonical identifier or the same identifier without
the `OBPI-` prefix. Resolution remains ledger-first and follows rename chains.

---

## Runtime Behavior

`gz obpi reconcile` uses the same OBPI runtime payload as `gz obpi status`, then
fails closed when proof or brief state is missing or drifted.

It reports blockers for conditions including:

- missing OBPI brief file
- missing ledger proof of completion
- missing or placeholder implementation summary
- missing or placeholder key proof
- ledger/file completion drift
- missing required human-attestation proof

Text mode prints `PASS` when no blockers are present. Otherwise it prints
`BLOCKERS:` followed by one blocker per line and exits `1`.

`--json` adds:

- `passed`
- `blockers`
- the same OBPI runtime fields returned by `gz obpi status`, including `attestation_requirement`

---

## Example

```bash
uv run gz obpi reconcile OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
```

```text
OBPI reconcile: OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
  Parent ADR: ADR-0.10.0-obpi-runtime-surface
  File: docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md
  Runtime State: PENDING
  Proof State: missing
  Attestation State: not_required
BLOCKERS:
- ledger proof of completion is missing
- brief file status is not Completed
```

```bash
uv run gz obpi reconcile OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
```
