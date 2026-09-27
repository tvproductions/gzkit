---
name: gz-migrate-semver
description: Record semver identifier migration events. Use when applying canonical ADR or OBPI renaming migrations.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.2.0"
model: haiku
---

# gz migrate-semver

## Overview

Append `artifact_renamed` events so the ledger resolves an old ADR or OBPI id to
its canonical id. The ledger is never rewritten. `gz migrate-semver` proposes a
rename from two sources:

- `SEMVER_ID_RENAMES` in `src/gzkit/commands/register.py`, a fixed table of
  legacy renames (pool and SemVer re-sequencing, early slug corrections);
- on-disk drift (GHI #345): for each ADR or OBPI file whose stem is a slug id,
  the bare id (`ADR-0.35.0`, `OBPI-0.1.0-01`) when ledger events still carry it.

A pair is skipped when its rename event already exists, when the old id never
appears in the ledger, or when the ledger already canonicalizes the old id.
Re-running is safe. Each event has reason `semver_minor_sequence_migration`.

It covers bare→slug renames and the table only. A slug→slug correction to an
OBPI id goes through `uv run python -m gzkit.governance.obpi_slug_rename`, and a
pool ADR promotion records its own rename through `gz adr promote`.

## Workflow

1. Preview: `uv run gz migrate-semver --dry-run` lists each
   `Would append artifact_renamed: <old> -> <new>` and writes nothing.
2. Show the operator the list. The run writes one ledger event per pair in bulk
   and has no confirmation step, and a bulk rename written in error cannot be
   removed from an append-only ledger, only countered (GHI #584).
3. On the operator's approval, run `uv run gz migrate-semver` and report the
   count it prints. `No applicable SemVer ID migrations found.` means nothing
   was pending.

## Example

```bash
uv run gz migrate-semver --dry-run
uv run gz migrate-semver
```
