# gz tidy

Report governance maintenance findings and, with `--fix`, regenerate the control surfaces.

## Usage

```bash
gz tidy [OPTIONS]
```

## Description

Prints a read-only maintenance report and deletes nothing. The report has four sections:

- **Validation issues** — the manifest, the ledger, every ADR and OBPI document the manifest lists (checked against its schema, the historical OBPI corpus included), the control surfaces including sync parity, the instruction audit and the persona files. Each line gives the issue type and message but not the file; `gz validate --documents` reports document findings with the file and skips OBPI briefs, which the version-aware `gz validate --briefs` owns (GHI #500).
- **Orphaned OBPIs** — ledger OBPIs whose parent ADR is absent from the ledger graph.
- **Settings vault** — shown when the snapshots of `.claude/settings.local.json` are drifted, absent or recoverable (GHI #1072).
- **ADRs pending attestation** — every ADR in the ledger graph without an attestation event, pool ADRs included.

Findings do not change the exit status.

## Options

| Option | Description |
|--------|-------------|
| `--check` | No effect: the report is read-only with or without it |
| `--fix` | After the report, regenerate the control surfaces on the same guarded path as `gz agent sync control-surfaces`: it refuses, leaving every mirror unchanged, when canonical skills fail the sync preflight (GHI #1100); otherwise it syncs, appends an `agent_sync_completed` ledger event, and runs the post-sync skill audit. It repairs control-surface drift only |
| `--dry-run` | With `--fix`, print that the sync would run instead of running it; for the planned path list use `gz agent sync control-surfaces --dry-run`. Without `--fix` it has no effect |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | The report ran, whatever it found, and any `--fix` sync succeeded |
| 1 | The project is not initialized, or a `--fix` sync was refused by the canonical preflight or failed by the post-sync skill audit |
