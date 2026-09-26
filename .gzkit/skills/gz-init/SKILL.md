---
name: gz-init
description: Initialize gzkit governance scaffolding and project skeleton for a repository. Use when bootstrapping, reinitializing, or repairing project governance surfaces.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
gz_command: init
metadata:
  skill-version: "6.1.0"
model: sonnet
---

# gz init

## Overview

Operate the gz init command surface as a reusable governance workflow.
Creates both governance scaffolding and a Python project skeleton
(pyproject.toml, src/<project>/, tests/).

## Workflow

1. Confirm the target repository and its governance lane (`--mode lite|heavy`;
   the default is `lite`).
2. Run `uv run gz init` with the required options.
3. On an already-initialized project, re-running `gz init` enters repair mode:
   it creates missing artifacts without overwriting existing canon, re-syncs the
   control-surface mirrors, and lists every file it writes. `--dry-run` lists the
   same writes and makes none. Repair refuses to sync, exiting 1 after reporting
   what it repaired, when canonical skills fail the sync preflight.
4. Use `--update` to refresh canonical surfaces from the installed wheel after
   an upgrade; it preserves operator-edited files.
5. Use `--force` only for full reinitialization. It re-copies the wheel's
   canonical skills, rules, templates and chores over the project's copies,
   losing operator edits to them, and rewrites `.gzkit.json`. It deletes
   nothing and never overwrites personas.
6. Use `--no-skeleton` to skip Python project files (governance-only init).
7. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.
- Verify project skeleton exists: `pyproject.toml`, `README.md`, `src/<project>/__init__.py`, `tests/__init__.py`.

## Example

```bash
uv run gz init --mode heavy     # first init, heavy lane
uv run gz init --dry-run        # on an initialized project: list the repair writes
uv run gz init                  # repair
uv run gz init --update         # refresh canon after a gzkit upgrade
```
