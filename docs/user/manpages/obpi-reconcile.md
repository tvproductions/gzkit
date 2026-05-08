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
fails closed when canonical ledger proof is missing or drifted.

It reports blockers for conditions including:

- missing OBPI brief file
- missing ledger proof of completion
- missing receipt value narrative
- missing receipt key proof
- completion-anchor drift in recorded OBPI scope
- missing completion-anchor evidence for anchor-tracked receipts
- degraded git-sync evidence recorded at receipt time
- missing required human-attestation proof

Markdown brief mismatches are returned separately as `reflection_issues`. They
do not block reconcile when the ledger receipt and canonical evidence are valid.

Text mode prints `PASS` when no blockers are present. Otherwise it prints
`BLOCKERS:` followed by one blocker per line and exits `1`.

`--json` adds:

- `passed`
- `blockers`
- the same OBPI runtime fields returned by `gz obpi status`, including `attestation_requirement`
- anchor-specific fields: `anchor_state`, `anchor_commit`, `current_head`, `anchor_issues`, `anchor_drift_files`

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
```

```bash
uv run gz obpi reconcile OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
```

Anchor-aware blockers are emitted verbatim, for example:

- `completion anchor evidence is missing`
- `completion anchor drifted in recorded OBPI scope`
- `completion git-sync evidence recorded blockers: ...`
