---
name: gz-init
description: Initialize gzkit governance scaffolding and project skeleton for a repository. Use when bootstrapping, reinitializing, or repairing project governance surfaces.
category: governance-infrastructure
lifecycle_state: active
skill-version: 6.0.1
owner: gzkit-governance
last_reviewed: 2026-04-15
gz_command: init
---

# gz init

## Overview

Operate the gz init command surface as a reusable governance workflow.
Creates both governance scaffolding and a Python project skeleton
(pyproject.toml, src/<project>/, tests/).

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz init` with the required options.
3. On an already-initialized project, re-running `gz init` enters repair mode:
   detects missing artifacts and creates them without overwriting existing files.
4. Use `--force` only for full reinitialization.
5. Use `--no-skeleton` to skip Python project files (governance-only init).
6. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.
- Verify project skeleton exists: `pyproject.toml`, `src/<project>/__init__.py`, `tests/__init__.py`.

## Example

Use $gz-init to initialize a repository in the requested mode.
