# Plan: OBPI-0.0.29-05 — Auto-chain from xenon-as-gate failure

## Context

ADR-0.0.29 (Complexity Advisor) item #5: implement the pre-commit auto-chain
hook that fires `gz complexity advise --auto-chain` when xenon-as-gate exits
non-zero. The hook is opt-in, POSIX-shell-compatible, and wraps the advisor
invocation in OBPI-09's timeout primitive. Parent ADR is Heavy lane,
Foundation kind — brief-level Gate 5 attestation required.

Dependencies confirmed present:
- `gz complexity advise --auto-chain` CLI flag (reserved no-op, OBPI-03)
- `run_with_timeout()` primitive at `src/gzkit/complexity/advisor/timeout.py` (OBPI-09)
- `DiagnosisEngine` at `src/gzkit/complexity/advisor/engine.py` (OBPI-02)
- `ThresholdTable` at `src/gzkit/complexity/thresholds.py` (ADR-0.0.28)

## Key Design Decisions

### D1: Shell-hook delegates to Python for timeout primitive (Path B1)

REQ-4 requires wrapping in OBPI-09's timeout primitive; REQ-10 requires POSIX
shell. Resolution: shell script handles xenon and staged-file collection;
delegates to a Python entrypoint for timeout-wrapped advisor analysis. The
Python entrypoint lives in the allowed path `src/gzkit/hooks/install_complexity_advisor.py`
(dual-purpose: `--install` mode and `--run` mode). The runbook at line 812
already commits to "the auto-chain hook (OBPI-05) consumes this primitive."

### D2: Installer replaces `xenon-complexity` entry in `.pre-commit-config.yaml`

The composite hook runs xenon first, then advisor on failure. Running both
the old `xenon-complexity` entry AND the new hook would run xenon twice. The
brief says "additive on the failure path, not substitutive of xenon" — meaning
the advisor is additive on xenon's failure, not that the config entry is
additive. Installer replaces the entry and prints what changed.

### D3: SKIP handled by pre-commit framework

Pre-commit's `SKIP=<hook-id>` convention handles skipping. No custom env var.
The hook id will be `complexity-advisor-auto-chain`. `SKIP=complexity-advisor-auto-chain`
skips both xenon and the advisor (since both run inside the composite hook),
satisfying REQ-3. Documented in the runbook entry.

### D4: Python wrapper uses engine directly, not CLI command

The hook's output requirements differ from the CLI (stderr vs stdout, exit
code 1 vs 3 for block-band). The Python wrapper imports the engine, threshold
loader, and timeout primitive directly — all public APIs from non-denied
modules. The command module is consumed (imported) but not modified.

## Destination-in-Mind Disclosure (Plan-Before-Exploration)

**Destination:** Composite shell+Python hook where shell handles POSIX/git
concerns and Python wraps the diagnosis engine in the timeout primitive.

**Rejected alternatives:**
- Pure-shell hook using `timeout 30 ...` — violates REQ-4 (must use the
  typed Python primitive, per runbook line 812)
- Second Python file (`complexity_advisor_runtime.py`) — violates brief
  allowlist. The `install_complexity_advisor.py` dual-purpose approach stays
  within allowed paths.
- Subprocess call to `uv run gz complexity advise` from Python — loses
  Python-level timeout control and requires messy SystemExit catching.
  Engine-direct is cleaner.

---

## Steps

### Step 1: Shell hook script (TDD — behave fixtures first)

**File:** `.gzkit/hooks/pre-commit-complexity-advisor`

POSIX shell (`#!/bin/sh`). Logic:
1. Run `uvx xenon --max-absolute C --max-modules C --max-average C src/`
2. If exit 0 → exit 0 silently
3. If non-zero → collect staged Python files via
   `git diff --cached --name-only --diff-filter=d -- '*.py'`
4. If no staged Python files → exit 0
5. Delegate to Python: `uv run python -m gzkit.hooks.install_complexity_advisor --run $STAGED_FILES`
6. Propagate Python exit code

Mark executable (`chmod +x`).

### Step 2: Python installer + runtime module

**File:** `src/gzkit/hooks/install_complexity_advisor.py`

Two modes via argparse:

**Install mode** (`python -m gzkit.hooks.install_complexity_advisor` or `--install`):
- Read `.pre-commit-config.yaml`
- Find `xenon-complexity` entry
- Replace with composite entry:
  ```yaml
  - id: complexity-advisor-auto-chain
    name: complexity advisor (xenon + advisor auto-chain)
    entry: .gzkit/hooks/pre-commit-complexity-advisor
    language: script
    pass_filenames: false
    types: [python]
    stages: [pre-commit]
  ```
- Write updated config
- Print summary of change

**Run mode** (`--run <file1.py> <file2.py> ...`):
- Import `DiagnosisEngine`, `AstContext` from engine module
- Import `load_threshold_table` from thresholds module
- Import `run_with_timeout` from timeout module
- Wrap `_diagnose_files(file_paths)` in `run_with_timeout(timeout_s=30.0, ...)`
- On `TimeoutTimedOut`: print warning to stderr, exit 0 (fail-open per REQ-4/OBPI-09)
- On `TimeoutOk`:
  - If any diagnosis has `crossing_band == "block"` → print diagnosis to stderr, exit 1 (REQ-6)
  - If diagnoses exist (warn-band) → print diagnosis to stderr, exit 0 (REQ-6)
  - No diagnoses → exit 0

`_diagnose_files(file_paths)` function:
- Load threshold table from `.gzkit/rules/complexity-thresholds.md`
- Create `DiagnosisEngine()`
- For each file: parse AST, run radon `cc_visit`, find crossings, run engine
- Return `list[AdvisorDiagnosis]`

`_render_to_stderr(diagnoses)` function:
- Same structured prose as the CLI but written to stderr (REQ-6)

### Step 3: Unit tests (TDD red-green-refactor)

**File:** `tests/hooks/test_complexity_advisor_auto_chain.py`

Test the Python boundary (`run_auto_chain`, `_diagnose_files`, install logic).
All tests mock subprocess/engine boundaries per REQ-11.

| Test | REQ | `@covers` |
|------|-----|-----------|
| `test_xenon_pass_skips_advisor` | REQ-01 | `@covers(REQ-0.0.29-05-01)` |
| `test_xenon_fail_triggers_advisor` | REQ-02 | `@covers(REQ-0.0.29-05-02)` |
| `test_skip_env_bypasses_both` | REQ-03 | `@covers(REQ-0.0.29-05-03)` |
| `test_timeout_wraps_advisor` | REQ-04 | `@covers(REQ-0.0.29-05-04)` |
| `test_staged_files_only` | REQ-05 | `@covers(REQ-0.0.29-05-05)` |
| `test_block_band_exits_1` | REQ-06 | `@covers(REQ-0.0.29-05-06)` |
| `test_warn_band_exits_0_with_stderr` | REQ-06 | `@covers(REQ-0.0.29-05-06)` |
| `test_timeout_exits_0_fail_open` | REQ-04 | `@covers(REQ-0.0.29-05-04)` |
| `test_installer_replaces_xenon_entry` | REQ-01 | `@covers(REQ-0.0.29-05-01)` |
| `test_hook_is_posix_shell` | REQ-10 | `@covers(REQ-0.0.29-05-10)` |
| `test_no_operator_email_in_artifacts` | REQ-12 | `@covers(REQ-0.0.29-05-12)` |

Test infrastructure: `tempfile.TemporaryDirectory` for git repo fixtures.
Mock `DiagnosisEngine.diagnose()`, `load_threshold_table()`, `run_with_timeout()`.

### Step 4: Behave scenarios

**File:** `features/complexity_advisor_auto_chain.feature`

Four canonical paths per REQ-8, tested via subprocess against fixture repos:

| Scenario | Tag | Path |
|----------|-----|------|
| Clean commit (xenon passes) | `@REQ-0.0.29-05-01` | xenon exit 0 → hook exit 0, advisor not invoked |
| Warn-band commit | `@REQ-0.0.29-05-02` | xenon fail → advisor → warn diagnosis to stderr, exit 0 |
| Block-band commit | `@REQ-0.0.29-05-04` | xenon fail → advisor → block diagnosis to stderr, exit 1 |
| SKIP-bypassed commit | `@REQ-0.0.29-05-03` | SKIP set → hook exit 0, neither xenon nor advisor runs |

Step implementations: create temp git repo, stage files, run hook script via
subprocess. Behave steps file at `features/steps/complexity_advisor_auto_chain_steps.py`.

### Step 5: Runbook entry + docs

**File:** `docs/user/runbook.md` — add entry under "Governance Doctrine Surfaces"
(near line 812, after the existing advisor timeout primitive entry):

Content:
- Install command: `python -m gzkit.hooks.install_complexity_advisor`
- What it does: replaces `xenon-complexity` with composite hook
- SKIP semantics: `SKIP=complexity-advisor-auto-chain git commit`
- Uninstall: revert `.pre-commit-config.yaml` to original `xenon-complexity` entry

---

## REQ → Test Coverage Map

| REQ | Unit test | Behave scenario |
|-----|-----------|-----------------|
| REQ-0.0.29-05-01 (opt-in install) | `test_installer_replaces_xenon_entry` | — |
| REQ-0.0.29-05-02 (xenon→advisor chain) | `test_xenon_fail_triggers_advisor` | warn-band, block-band |
| REQ-0.0.29-05-03 (SKIP bypass) | `test_skip_env_bypasses_both` | SKIP-bypassed |
| REQ-0.0.29-05-04 (timeout wrap) | `test_timeout_wraps_advisor`, `test_timeout_exits_0_fail_open` | — |
| REQ-0.0.29-05-05 (staged files only) | `test_staged_files_only` | all scenarios use staged files |
| REQ-0.0.29-05-06 (exit codes) | `test_block_band_exits_1`, `test_warn_band_exits_0_with_stderr` | block-band, warn-band |
| REQ-0.0.29-05-07 (unit tests) | all unit tests | — |
| REQ-0.0.29-05-08 (behave scenarios) | — | all four scenarios |
| REQ-0.0.29-05-09 (runbook entry) | — | — (manual) |
| REQ-0.0.29-05-10 (POSIX shell) | `test_hook_is_posix_shell` | subprocess invocation |
| REQ-0.0.29-05-11 (TDD discipline) | all via RGR cycle | all via subprocess |
| REQ-0.0.29-05-12 (no PII) | `test_no_operator_email_in_artifacts` | — |

## Verification

```bash
uv run -m unittest tests/hooks/test_complexity_advisor_auto_chain.py -v
uv run gz arb ruff
uv run gz arb typecheck
uv run -m behave features/complexity_advisor_auto_chain.feature
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.29-05-auto-chain-hook --json
```

## Files Created/Modified

| File | Action |
|------|--------|
| `.gzkit/hooks/pre-commit-complexity-advisor` | Create (shell script) |
| `src/gzkit/hooks/install_complexity_advisor.py` | Create (installer + runtime) |
| `tests/hooks/test_complexity_advisor_auto_chain.py` | Create (unit tests) |
| `tests/hooks/__init__.py` | Create (package init) |
| `features/complexity_advisor_auto_chain.feature` | Create (BDD scenarios) |
| `features/steps/complexity_advisor_auto_chain_steps.py` | Create (step implementations) |
| `docs/user/runbook.md` | Modify (add hook entry) |
