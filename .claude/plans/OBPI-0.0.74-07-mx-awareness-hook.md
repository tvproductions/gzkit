# Plan: OBPI-0.0.74-07-mx-awareness-hook

**OBPI:** OBPI-0.0.74-07-mx-awareness-hook
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar
**Lane:** Heavy
**TASKs:** TASK-0.0.74-07-01-01, TASK-0.0.74-07-02-01, TASK-0.0.74-07-03-01

## Pre-Exploration Disclosure (Step 6a)

**Destination-in-mind before planning:** Three core files to create (awareness.py, hook adapter, tests) plus a fold into session_orientation.py. The hook reads the MX marker via stdlib-only path traversal, injects the banner to stdout on UserPromptSubmit, and the liveness check verifies the hook file exists and is registered in settings.json.

**Rejected alternatives:**
- Importing gzkit.mx.marker in the hook adapter directly — rejected because if gzkit itself is broken (the MX premise), the import may fail. Fallback inline stdlib read in the hook adapter is the safer design.
- Making banner injection go to stderr — rejected because UserPromptSubmit hook stdout is injected as agent context; stderr is for blocking feedback (exit-code 2 contract).
- Registering the hook via direct settings.json edit — requires `.claude/settings.json` which is NOT in the allowed paths. The allowed paths require amending, or we generate via `src/gzkit/hooks/claude.py` (also not in allowed paths). Surface as gap below.

## Context

ADR-0.0.74 Decision item #7 (verbatim): "The awareness hook. While the marker is present, a per-vendor hook injects 'MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind' every turn (a guarantee, not agent memory). It adapts per vendor surface (.claude / .agents / .github) the way control surfaces already sync. A tool-output banner is secondary backup."

The MX marker (`src/gzkit/mx/marker.py`) is stdlib+pydantic only and already ships `is_active()`. The existing hook pattern (stop-turn-feedback.py, etc.) reads stdin JSON and exits 0 (non-blocking) or 2 (blocking). The UserPromptSubmit hook type is not yet registered in `.claude/settings.json`.

## Files

### Created
- `src/gzkit/mx/awareness.py` — shared banner constant, `get_banner()`, `LivenessResult`, `check_hook_liveness()`
- `.claude/hooks/mx-awareness.py` — Claude vendor adapter; UserPromptSubmit hook; stdout banner injection; fail-open
- `tests/hooks/test_mx_awareness.py` — unit tests for banner/no-op/liveness behaviors

### Modified
- `scripts/session_orientation.py` — fold MX banner into SessionStart digest (secondary backup)

### Gap — not in allowed paths
- `.claude/settings.json` — needs UserPromptSubmit hook entry to register mx-awareness.py
- `src/gzkit/hooks/claude.py` — needs `generate_claude_settings()` update to add UserPromptSubmit awareness hook

**Brief amendment needed:** Add `.claude/settings.json` to allowed paths (to register the hook) OR add `src/gzkit/hooks/claude.py` to allowed paths (preferred — lets `gz agent sync control-surfaces` own the settings regeneration going forward). Recommend: add `src/gzkit/hooks/claude.py` to allowed paths and modify `generate_claude_settings()` to include the UserPromptSubmit hook, then run sync to regenerate settings.json.

## Steps

### Step 1: Create `src/gzkit/mx/awareness.py` (TASK-0.0.74-07-01-01, TASK-0.0.74-07-02-01)

RED-GREEN-REFACTOR per behavior:

**Behavior A (REQ-07-01 shared logic):** `get_banner()` returns the exact banner string when marker present, empty string when absent.
- Test: `TestGetBanner.test_returns_banner_when_marker_present` (tempdir with marker file)
- Test: `TestGetBanner.test_returns_empty_when_marker_absent` (tempdir without marker file)
- Implementation: stdlib path walk + `.is_file()` check on marker path

**Behavior B (REQ-07-02):** `check_hook_liveness()` returns `LivenessResult(ok=False, defect=...)` when hook file missing.
- Test: `TestLiveness.test_missing_hook_file_reports_defect`
- Implementation: check `.claude/hooks/mx-awareness.py` exists

**Behavior C (REQ-07-02):** `check_hook_liveness()` returns `LivenessResult(ok=False, defect=...)` when hook not in settings.json.
- Test: `TestLiveness.test_hook_not_in_settings_reports_defect`
- Implementation: parse settings.json, look for UserPromptSubmit with mx-awareness.py

**Behavior D (REQ-07-02):** `check_hook_liveness()` returns `LivenessResult(ok=True)` when hook file exists and is registered.
- Test: `TestLiveness.test_wired_hook_reports_ok`
- Implementation: happy path through both checks

Module constraints:
- stdlib-only marker read (pathlib + json) — no gzkit.mx.marker import (awareness.py must survive when gzkit is the patient)
- `LivenessResult` is a simple class (no pydantic — don't add a dep for a result carrier)

### Step 2: Create `.claude/hooks/mx-awareness.py` (TASK-0.0.74-07-01-01)

RED-GREEN-REFACTOR per behavior:

**Behavior A (REQ-07-01):** With marker present, hook outputs exact banner to stdout.
- Test: `TestHookAdapter.test_banner_injected_when_marker_present`
- Load hook via importlib (same pattern as test_stop_turn_feedback.py)
- Simulate: pipe JSON stdin, check stdout

**Behavior B (REQ-07-01 no-op):** Without marker, hook produces no stdout output.
- Test: `TestHookAdapter.test_no_output_when_marker_absent`

**Behavior C (fail-open):** Malformed stdin does not raise; still exits 0.
- Test: `TestHookAdapter.test_fail_open_on_bad_stdin`

Hook design:
- Try `from gzkit.mx.awareness import get_banner`; on ImportError fall back to inline stdlib marker read
- Write banner to stdout (not stderr) — UserPromptSubmit hook contract
- Always exit 0 (fail-open: a turn must always begin)

### Step 3: Edit `scripts/session_orientation.py` (TASK-0.0.74-07-03-01)

Fold MX banner into session_orientation digest:
- Import `gzkit.mx.awareness.get_banner` (try/except for robustness)
- If `get_banner()` non-empty, prepend banner line to the digest output
- Secondary backup only — session_orientation fires on SessionStart/PreCompact, not per-turn

### Step 4: Brief amendment for settings.json / hooks/claude.py

Surface the gap to the operator:
- Preferred: add `src/gzkit/hooks/claude.py` to allowed paths
- Modify `generate_claude_settings()` to include UserPromptSubmit hook
- Run `uv run gz agent sync control-surfaces` to regenerate settings.json
- The liveness check will then report `ok=True` after sync

If operator declines brief amendment, the liveness check will correctly report the hook as unwired, and settings.json wiring is deferred to a follow-up OBPI.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
test -f src/gzkit/mx/awareness.py
test -f .claude/hooks/mx-awareness.py
test -f tests/hooks/test_mx_awareness.py
```

## Notes

- REQ-07-03 SUPPORT proof requires `artifact_edited` ledger events (auto-emitted by hook on file edits) + `gz validate --surfaces` exit 0 (already passes). The vendor mirror rendering via sync is aspirational; the sync code modification is a gap in allowed paths.
- The `req_atomic:` exemptions in the brief frontmatter declare each REQ as a single indivisible TDD unit — no TASK subdivision needed.
- The hook must be a `UserPromptSubmit` type (fires every turn on user prompt), NOT `PreToolUse` (which fires only on tool use — misses the "every turn" guarantee).
