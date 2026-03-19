---
name: chore-runner
description: Run a gzkit chore end-to-end (show, plan, advise, execute, validate). Use when executing scheduled maintenance, refactoring, or code quality work items from the chores registry.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-19
---

# chore-runner

## Purpose

Execute a repository chore using the canonical `gz chores` workflow.

## Inputs

- `chore_slug`: Chore identifier from `config/gzkit.chores.json`.
- `lane`: The configured lane reported by `gz chores show` (lite, medium, or heavy).

## Outputs

- Updated repository files (as defined by the chore).
- Green validation run for the configured lane.
- Execution log in `ops/chores/{slug}/proofs/CHORE-LOG.md`.

## Procedure

1. Discover chores and choose a slug:

   ```bash
   uv run gz chores list
   ```

2. Inspect the chore details and confirm the lane:

   ```bash
   uv run gz chores show <chore_slug>
   ```

3. Review the acceptance criteria:

   ```bash
   uv run gz chores plan <chore_slug>
   ```

4. Dry-run criteria to assess current state:

   ```bash
   uv run gz chores advise <chore_slug>
   ```

5. If criteria fail, read the CHORE.md workflow and implement fixes:

   - Read `ops/chores/<chore_slug>/CHORE.md` for the remediation procedure
   - Apply fixes surgically — minimal diffs, preserve behavior
   - Iterate: fix, validate, repeat

6. Validate (lane-appropriate):

   ```bash
   # Lite lane (default)
   uv run ruff check . --fix && uv run ruff format .
   uvx ty check . --exclude 'features/**'
   uv run -m unittest -q

   # Heavy lane (adds gates)
   uv run gz gates
   ```

7. Execute the chore to log the result:

   ```bash
   uv run gz chores run <chore_slug>
   ```

8. Audit the logged result:

   ```bash
   uv run gz chores audit --slug <chore_slug>
   ```

## Failure Modes

- **Unknown slug:** `gz chores show <slug>` emits BLOCKERS.
- **Lane mismatch:** Chore expects Heavy actions; do not proceed without meeting gate requirements.
- **Criteria fail:** Fix issues per CHORE.md workflow and rerun `gz chores advise`.
- **Missing acceptance.json:** Registry loader fails closed with BLOCKERS.

## Acceptance Rules

- Uses `uv run gz chores ...` commands (no ad-hoc variants).
- Does not introduce new dependencies.
- Leaves the repo in a validated state for the configured lane.
- Evidence is saved to `ops/chores/{slug}/proofs/`.
