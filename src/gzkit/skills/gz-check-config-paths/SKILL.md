---
name: gz-check-config-paths
description: Validate configured and manifest path coherence. Use when diagnosing control-surface or path drift.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.2.0"
model: haiku
---

# gz check-config-paths

## Overview

Check that the paths `.gzkit.json` configures and the manifest declares exist
and agree. The command reports these checks:

- every configured directory (governance roots, source, tests and docs roots,
  the canonical skills root and each vendor skill mirror) and file (ledger,
  manifest) exists;
- the artifacts and control surfaces the manifest declares exist;
- OBPI briefs live inside their ADR package (the OBPI path contract);
- source code carries no path literal the config does not govern.

It is read-only. It exits 0 with `Config-path audit passed.` and exits 1 when
it lists any issue.

## Workflow

1. Run `uv run gz check-config-paths`, or add `--json` for `{valid, issues}`.
2. On exit 1, fix each named path: correct the value in `.gzkit.json`, create
   the missing directory or file, or regenerate the manifest and control
   surfaces with `uv run gz agent sync control-surfaces`.
3. Re-run until it exits 0, then summarize what changed.

## Example

```bash
uv run gz check-config-paths
uv run gz check-config-paths --json
```
