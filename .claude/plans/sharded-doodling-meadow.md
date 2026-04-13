# OBPI-0.25.0-27 — Policy Guards Pattern (Absorb)

## Context

OBPI-0.25.0-27 is a comparison brief inside ADR-0.25.0 (Core Infrastructure
Pattern Absorption). The task: evaluate `airlineops/src/opsdev/lib/guards.py`
(145 lines) against `gzkit/src/gzkit/hooks/guards.py` (125 lines) and record
one of **Absorb / Confirm / Exclude** with concrete rationale, adapted code
when Absorbing, and tests.

The two files are near-siblings. Core scanner logic is byte-equivalent (same
PATTERNS, same SCAN_EXTS, same `conftest.py` detection, same `pyproject.toml`
dependency check). Three differences matter:

1. **gzkit has a superior API.** `forbid_pytest(root: Path)` takes the scan
   root as a parameter. airlineops still derives `root = Path(__file__).resolve().parents[3]`
   — exactly the anti-pattern gzkit already removed in OBPI-0.0.7-04
   ("Hooks module migration") as part of ADR-0.0.7 (config-first resolution
   discipline). Absorbing airlineops wholesale would **regress** gzkit.
2. **airlineops has one robustness feature gzkit lacks:** `_safe_print(s)`
   catches `UnicodeEncodeError` and falls back to `s.encode("ascii", "backslashreplace")`
   for narrow-encoding terminals (Windows cp1252). The helper is ~7 lines.
3. **airlineops carries airline-specific exclusions** (`archive/`, `tmp/`,
   `examples/`, `/opsdev/lib/guards.py`) that do not belong in gzkit.

The `_safe_print` feature is **concretely relevant** to gzkit. The pre-commit
hook at `.pre-commit-config.yaml:40` invokes `uv run -m gzkit.hooks.guards`
directly — this bypasses `gzkit/__main__.py`'s `sys.stdout.reconfigure(encoding="utf-8")`
UTF-8 guard. On a Windows cp1252 terminal, a finding that contains non-ASCII
bytes in a file path or violation line would raise `UnicodeEncodeError` and
crash the hook. The `cross-platform.md` rule explicitly warns about this
scenario. Gzkit's existing file has no test coverage for this path (0% — in
fact, `hooks/guards.py` has no test file at all in `tests/`).

**Decision: Absorb** — narrow absorption of the `_safe_print` pattern into
the existing gzkit module, with full TDD coverage for the previously untested
scanner. Keep gzkit's superior `forbid_pytest(root: Path)` API. Do not touch
the exclusion set (gzkit's list is correct for gzkit's repo layout; airlineops'
extras are airline-specific). No CLI surface change — this is library + test
hardening only, so Gate 4 BDD records `N/A` with rationale.

## Implementation

### 1. Harden `src/gzkit/hooks/guards.py`

- Add module-level `_safe_print(s: str) -> None` helper that tries `print(s)`
  and, on `UnicodeEncodeError`, prints `s.encode("ascii", "backslashreplace").decode("ascii")`.
- In `forbid_pytest`, use `_safe_print` for the dynamic lines that interpolate
  user-controlled data (file paths and violation messages). Keep plain `print`
  for the static header/footer strings (ASCII-safe by construction).
- Keep the `forbid_pytest(root: Path)` signature, `iter_files`, `scan_file`,
  `PATTERNS`, `SCAN_EXTS`, `EXCLUDE_DIRS`, `EXCLUDE_PATH_SNIPPETS`, and
  `main()` exactly as they are.
- Keep the `# noqa: T201` annotations (print is intentional here — this is a
  pre-commit hook whose output goes to operator-visible stderr/stdout).

### 2. Add `tests/test_hooks_guards.py` (new file — currently zero coverage)

Test classes, all using `tempfile.TemporaryDirectory()` context managers and
temp paths (no real repo mutation):

- `TestIterFiles` — exclusion behavior for `.git/`, `.venv/`, `site/`,
  `/docs/`, and suffix filtering. Table-driven.
- `TestScanFileSourceLevel` — pytest import / `from pytest import` /
  `pytest.` / `@pytest.` / `py.test` pattern hits; line numbers reported
  correctly; clean files return empty list.
- `TestScanFileSpecialCases` — `conftest.py` short-circuits to
  "contains pytest-specific conftest.py"; `pyproject.toml` with `pytest`
  declaration returns "declares pytest dependency"; `requirements.txt` /
  `requirements-dev.txt` same path.
- `TestScanFileReadError` — unreadable file returns `"unreadable file: ..."`
  (simulate with a directory masquerading via `OSError`, or delete between
  listing and reading using a mocked `read_text`).
- `TestForbidPytest` — integration: clean temp root returns 0; root
  containing `bad.py` with `import pytest` returns 1; findings are printed
  (capture via `contextlib.redirect_stdout`).
- `TestSafePrint` — normal ASCII passes through; non-encodable unicode
  triggers the fallback branch (patch `sys.stdout` with a writer that raises
  `UnicodeEncodeError` on non-ASCII).

All tests are table-driven where possible, deterministic, no network, no
real repo state. Coverage for `hooks/guards.py` should go from ~22% to
>=90%.

### 3. Update the OBPI brief
`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-27-policy-guards-pattern.md`

Author at completion time:

- **Capability Comparison** table with concrete dimensions (API design, root
  resolution, cross-platform print safety, exclusion scope, test coverage,
  lines of code, convention compliance, subtraction test).
- **Decision: Absorb** with 5–7 point rationale naming the three concrete
  deltas and why the narrow absorption is the right outcome.
- **Gate 1–5** checklist marked per actual evidence.
- **Gate 4 (BDD): N/A** subsection explaining no operator-visible behavior
  change (scanner still prints the same header/footer; the only change is a
  fallback branch for unprintable bytes, which by definition changes nothing
  on any terminal that could previously print them).
- **Implementation Summary**, **Key Proof** (three commands + expected
  output), **Closing Argument**, and populated REQ coverage table for the
  Stage 4 ceremony.

## Critical files

| Path | Action | Reason |
|------|--------|--------|
| `src/gzkit/hooks/guards.py` | Edit | Add `_safe_print` helper; route dynamic-content prints through it |
| `tests/test_hooks_guards.py` | **Create** | No existing tests for this module — TDD requires Red first |
| `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-27-policy-guards-pattern.md` | Edit | Record decision, rationale, gate checklist, ceremony content |

## Reuse

- `tempfile.TemporaryDirectory()` context manager — canonical pattern per
  `.claude/rules/tests.md` and `.claude/rules/cross-platform.md`.
- `contextlib.redirect_stdout` — stdlib, for capturing `forbid_pytest` output
  in tests without subprocess.
- Follows the comparison-brief template established by OBPI-0.25.0-26
  (drift-detection-pattern), OBPI-0.25.0-24 (cli-audit-pattern), and siblings.

## Verification

Stage 3 Phase 1 (baseline):

```bash
uv run gz lint
uv run gz typecheck
uv run gz test                              # full suite incl. behave
uv run gz validate --documents              # heavy lane
uv run mkdocs build --strict                # heavy lane
```

Stage 3 Phase 1b (REQ → @covers parity):

```bash
uv run gz covers OBPI-0.25.0-27-policy-guards-pattern --json
# Expected: summary.uncovered_reqs == 0
```

Stage 3 Phase 2 (REQ-level):

```bash
uv run -m unittest tests.test_hooks_guards -v
# Expected: all new tests pass; ≥90% line coverage of hooks/guards.py

rg -n 'Decision: Absorb' \
  docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-27-policy-guards-pattern.md
# Expected: one match

test -f ../airlineops/src/opsdev/lib/guards.py && test -f src/gzkit/hooks/guards.py
# Expected: both exist
```

Out-of-scope: `features/core_infrastructure.feature` — Gate 4 BDD is N/A
because there is no operator-visible behavior change.
