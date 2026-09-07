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
- anchor state
- completion anchor commit and current HEAD
- anchor-specific issues and recorded drift files when applicable
- tracked GitHub defect refs parsed from the brief's `## Tracked Defects`
  section, each resolved against live GitHub state through `gh` — `state` is
  `open`, `closed`, or `unresolved` (never read from the brief's own
  `(open)`/`(closed)` token, which is kept separately as `authored_state`;
  GHI #966)
- `issue_details`, which preserve the raw fail-closed issue text and append
  linked `GHI-*` refs with their resolved state for operator-facing output —
  `GHI-737 (closed)`, `GHI-11 (closed; brief says open)` when the brief's
  token is stale, `GHI-737 (unresolved)` when `gh` could not answer
- issue list derived fail-closed from ledger/brief evidence

This command is informational. It exits `0` when the OBPI resolves, even when
issues or drift are present.
Anchor-related issues remain visible in `anchor_state`, `anchor_issues`,
`anchor_drift_files`, and `issues`, but they do not demote a completed OBPI's
`runtime_state` by themselves.

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
  Anchor State: not_applicable
  Anchor Commit: (none)
  Current HEAD: (unknown)
  Completion: PENDING
  Issues:
    - ledger proof of completion is missing
    - brief file status is not Completed
```

```bash
uv run gz obpi status OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
```

Anchor-tracked completed receipts add:

- `anchor_state`
- `anchor_commit`
- `current_head`
- `anchor_issues`
- `anchor_drift_files`
- `tracked_defects`
- `issue_details`
