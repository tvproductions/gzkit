# Plan: OBPI-0.0.70-01-stop-hook-turn-end-feedback

**OBPI:** `OBPI-0.0.70-01-stop-hook-turn-end-feedback`
**Parent ADR:** `ADR-0.0.70-turn-end-feedback-and-correction-mining`
**Lane:** Lite
**Date:** 2026-06-12

## Context

ADR-0.0.70 checklist item #1 (verbatim): "Stop-hook turn-end deterministic
feedback — `.claude/hooks/stop-turn-feedback.py` + `Stop` matcher wiring in
`.claude/settings.json`; ruff over session-dirty Python files; sub-2s budget;
`stop_hook_active` loop guard; off-switch; block telemetry line;
agent-actionable block prose; unit tests"

Key discovery reconciled in-flight: `.claude/hooks/**` and `.claude/settings.json`
are GENERATED surfaces owned by `setup_claude_hooks`. The canonical hook template
lives in `src/gzkit/hooks/scripts/quality.py` and the `Stop` phase is gzkit-owned
in `src/gzkit/hooks/claude.py`. REQ-0.0.70-01-09 fences this ownership.

## Files

- **CREATE** `.claude/hooks/stop-turn-feedback.py` — generated stop hook script
- **CREATE** `tests/hooks/test_stop_turn_feedback.py` — unit tests (importlib loading)
- **MODIFY** `src/gzkit/hooks/scripts/quality.py` — canonical hook template
- **MODIFY** `src/gzkit/hooks/claude.py` — Stop phase generation/merge/setup/README
- **MODIFY** `src/gzkit/sync_surfaces.py` — drift-detection Stop phase coverage
- **MODIFY** `tests/test_hooks.py` — generator test coherence (coupled-surface, DO IT RIGHT 1a)
- **MODIFY** `.claude/settings.json` — Stop matcher entry (generated)
- **MODIFY** `.gitignore` — exclude `.gzkit/sensors/`

## Steps

### Step 1: TDD RED — Author tests from REQ semantics
Write `tests/hooks/test_stop_turn_feedback.py` before the hook exists.
- REQ-0.0.70-01-01: dirty Python files with findings → block prose names what/why/next-step
- REQ-0.0.70-01-02: `stop_hook_active` true → exit 0 no-block regardless of lint
- REQ-0.0.70-01-03: `GZ_STOP_FEEDBACK=off` → exit 0 no ruff invocation
- REQ-0.0.70-01-04: internal failure (ruff unavailable, timeout, malformed stdin) → fail open exit 0
- REQ-0.0.70-01-05: block emitted → exactly one telemetry JSON line, cap at 1 MiB (500 lines kept)
- REQ-0.0.70-01-06: `.claude/settings.json` has `Stop` matcher pointing at script; script exists
- REQ-0.0.70-01-08: `--demo` flag → real lint pipeline against synthetic violation, no stdin/block/telemetry

Verification: `uv run -m unittest tests.hooks.test_stop_turn_feedback -q` — expect FAIL (file not found)

### Step 2: Author canonical template in `src/gzkit/hooks/scripts/quality.py`
Add `stop_turn_feedback` function implementing the full stop-hook logic:
- Dirty file detection via `git diff --name-only --diff-filter=ACMR`
- Subprocess `ruff check` with 2s timeout, fail-open on timeout/error
- `stop_hook_active` guard from stdin JSON
- `GZ_STOP_FEEDBACK` env var off-switch
- Three-part block prose: what failed / why forbidden / governed next step
- Telemetry append to `.gzkit/sensors/stop-turn-feedback.jsonl` with 1-MiB/500-line cap
- `--demo` mode against synthetic violation

### Step 3: Wire generation/merge/setup in `src/gzkit/hooks/claude.py`
- `generate_claude_settings`: include `Stop` phase entry pointing at `stop-turn-feedback.py`
- `merge_settings`: preserve `Stop` phase when merging generated into user settings
- `setup_claude_hooks`: copy canonical template to `.claude/hooks/stop-turn-feedback.py`
- README generation: document the new hook

Update `src/gzkit/sync_surfaces.py` to include `Stop` phase in drift detection.
Update `tests/test_hooks.py` for generator test coherence (DO IT RIGHT 1a).

### Step 4: Generate `.claude/hooks/stop-turn-feedback.py`
Run `gz agent sync control-surfaces` or the setup writer to materialize the hook
from the canonical template. Verify script exists and is executable.

### Step 5: Update `.gitignore`
Add `.gzkit/sensors/` exclusion for the local telemetry log directory.

### Step 6: TDD GREEN — Run full test suite
```
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck
```

All tests pass. REQs covered by `@covers` decorators.

## Verification

```
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f .claude/hooks/stop-turn-feedback.py
test -f tests/hooks/test_stop_turn_feedback.py
uv run -m unittest tests.hooks.test_stop_turn_feedback -q
```

## Notes

- Retrospective plan: implementation completed in commit `863250d6`, 2026-06-12
- Generated-surface discovery reconciled in-flight; brief Allowed Paths updated accordingly
- REQ-0.0.70-01-07 is a STRUCTURAL-FENCE REQ verified at ADR closeout via parent ADR Boundary Invariants
- 11 unit tests delivered covering REQs 01-01 through 01-06, 01-08, 01-09
