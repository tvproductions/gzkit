---
name: gz-chore-runner
persona: main-session
description: Run a gzkit chore end-to-end (show, plan, advise, execute, validate). Use when executing scheduled maintenance, refactoring, or code quality work items from the chores registry.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.1.1"
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

## Common Rationalizations

These thoughts mean STOP — you are about to ship a chore that broke its own discipline:

| Thought | Reality |
|---------|---------|
| "advise looks fine, I'll skip plan and run directly" | The 5-step sequence (show → plan → advise → execute → audit) exists because chores accumulate scope creep when steps merge. Each step is a fail-closed gate. |
| "I'll add a new dependency — it'll make the fix cleaner" | Acceptance rule: chores do not introduce dependencies. A "cleaner" fix that bloats the dependency surface is a worse fix. |
| "The chore is lite lane but I need to touch heavy-lane gates" | Lane is set in the chore config, not in the moment. If the work is heavier, fix the chore definition first; do not silently escalate. |
| "I'll run the chore without reading CHORE.md" | The remediation procedure lives in CHORE.md. Running blind produces ad-hoc fixes that don't match the chore's contract. |
| "advise passed, no need to run audit" | `gz chores audit` is what records the proof. Skipping it leaves the chore unverified in the registry. |
| "The diff is bigger than the chore says — that's fine, I'm fixing adjacent rot" | Adjacent rot is its own chore. Large diffs in a small chore mean two chores are colliding; split them. |
| "Validation failed but the change is minor — ship it" | Lane validation is the chore's stop-light. Failed lint/typecheck/tests means the chore violated its acceptance rule. Fix or revert. |

## Red Flags

- Skipping any of the 5 steps (show, plan, advise, execute, audit)
- Modifying files outside the chore's declared scope
- Adding dependencies, scripts, or config keys not part of the chore contract
- Running `gz chores run` before validation passes
- No proof file written to `ops/chores/{slug}/proofs/`
- Mixing two chores in one execution (collision)
- Ad-hoc command variants instead of `uv run gz chores ...`
