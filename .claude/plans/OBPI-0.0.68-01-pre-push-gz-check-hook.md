# Plan: OBPI-0.0.68-01-pre-push-gz-check-hook

**OBPI:** OBPI-0.0.68-01-pre-push-gz-check-hook
**ADR:** ADR-0.0.68-green-between-sessions-gate
**Lane:** Lite

## Context

Add a `pre-push` hook stage to `.pre-commit-config.yaml` that runs `gz check`,
document the one-time install step in the runbook, and install it locally.
This delivers the catch-at-push value described in ADR Decision item 1.

## Files

- `.pre-commit-config.yaml` — add pre-push gz-check hook entry
- `docs/user/runbook.md` — add `pre-commit install --hook-type pre-push` to git clone recovery block
- `tests/test_pre_push_hook.py` — new test, parses YAML, asserts pre-push gz check hook declared
- `docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate/obpis/OBPI-0.0.68-01-pre-push-gz-check-hook.md` — update evidence sections

## Steps

### Step 1: TDD RED — Write failing test

Author `tests/test_pre_push_hook.py` with a test class `TestPrePushHookDeclared`
that reads `.pre-commit-config.yaml`, parses it with `yaml.safe_load`, and
asserts a hook with `stages: [pre-push]` running `gz check` (or `uv run gz check`)
is declared in the `local` repo section.

Run `uv run -m unittest tests.test_pre_push_hook -v` — confirm it FAILS (no
pre-push hook declared yet).

### Step 2: GREEN — Add pre-push hook to `.pre-commit-config.yaml`

Add a new local hook entry with:
```yaml
- id: gz-check-pre-push
  name: gz check (pre-push gate)
  entry: uv run gz check
  language: system
  pass_filenames: false
  stages: [pre-push]
```

Run `uv run -m unittest tests.test_pre_push_hook -v` — confirm it PASSES.

### Step 3: Add runbook documentation

In `docs/user/runbook.md`, add `uvx pre-commit install --hook-type pre-push`
to the "Git clone recovery" block (around line 373) so a fresh clone becomes
enforcing after that one-time step.

### Step 4: Install the hook locally

Run `uvx pre-commit install --hook-type pre-push` to install the hook in the
current working tree's `.git/hooks/pre-push`.

### Step 5: Quality checks

Run:
- `uv run gz arb ruff`
- `uv run gz arb typecheck`
- `uv run gz arb step --name unittest -- uv run -m unittest -q`

All must exit 0.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uvx pre-commit run --hook-stage pre-push --all-files
```

## Notes

- `pre-commit` is available via `uvx pre-commit` (v4.6.0 confirmed).
- The existing `manual`-staged unittest hook MUST NOT have its stage changed.
- No `src/gzkit/**` edits — validator scope is OBPI-02's surface.
- REQ-0.0.68-01-01 [behavior]: covered by `tests/test_pre_push_hook.py`
- REQ-0.0.68-01-02 [support]: ledger `artifact_edited` for runbook + `gz validate --documents`
