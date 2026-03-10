# gz obpi status

Show focused runtime status for one OBPI.

---

## Usage

```bash
gz obpi status <OBPI-ID> [--json]
```

`<OBPI-ID>` accepts the full canonical identifier or the same identifier without
the `OBPI-` prefix. Resolution remains ledger-first and follows rename chains.

---

## Runtime Behavior

`gz obpi status` reports one OBPI's runtime state directly from ledger evidence
plus the on-disk brief when present.

The payload includes:

- parent ADR linkage
- resolved brief file path or an explicit missing-file state
- runtime state (`pending`, `in_progress`, `completed`, `attested_completed`, `validated`, `drift`)
- proof state
- attestation requirement
- attestation state
- issue list derived fail-closed from ledger/brief evidence

This command is informational. It exits `0` when the OBPI resolves, even when
issues or drift are present.

---

## Example

```bash
uv run gz obpi status OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
```

```text
OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
  Parent ADR: ADR-0.10.0-obpi-runtime-surface
  File: docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md
  Runtime State: PENDING
  Proof State: missing
  Attestation State: not_required
  Completion: PENDING
  Issues:
    - ledger proof of completion is missing
    - brief file status is not Completed
```

```bash
uv run gz obpi status OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
```
