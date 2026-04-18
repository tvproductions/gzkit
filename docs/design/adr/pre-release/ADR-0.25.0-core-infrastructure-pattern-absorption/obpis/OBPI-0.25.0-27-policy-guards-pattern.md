---
id: OBPI-0.25.0-27-policy-guards-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 27
status: attested_completed
lane: heavy
date: 2026-04-12
---

# OBPI-0.25.0-27: Policy Guards Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-27 — "Evaluate and absorb opsdev/lib/guards.py (145 lines) — policy enforcement scanning"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/guards.py` (145 lines) against gzkit's
policy guards surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers policy enforcement scanning. gzkit's equivalent is
`hooks/guards.py` (125 lines) — a near-identical line count suggesting direct
functional overlap in policy enforcement.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/guards.py` (145 lines)
- **gzkit equivalent:** `src/gzkit/hooks/guards.py` (125 lines → 140 lines post-absorption)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Near-identical line counts suggest convergent evolution — the comparison should focus on which implementation is more robust

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Merging both guard implementations — the comparison yields a single winner

## Capability Comparison

| Dimension | airlineops `opsdev/lib/guards.py` (145 lines) | gzkit `hooks/guards.py` (125 → 140 lines) | Winner |
|-----------|-----------------------------------------------|--------------------------------------------|--------|
| Scan root API | `forbid_pytest()` — root hard-coded as `Path(__file__).resolve().parents[3]` | `forbid_pytest(root: Path)` — root passed in | **gzkit** — result of OBPI-0.0.7-04 config-first migration; airlineops retains the anti-pattern gzkit removed |
| PATTERNS regex list | `import pytest`, `from pytest import`, `pytest.`, `@pytest.`, `py.test` | Byte-identical | Tie |
| SCAN_EXTS | `.py, .toml, .ini, .cfg, .yaml, .yml, .txt` | Byte-identical | Tie |
| conftest.py short-circuit | Yes | Yes | Tie |
| pyproject.toml / requirements dep detection | Yes (case-insensitive `\bpytest\b`) | Byte-identical | Tie |
| EXCLUDE_DIRS scope | 11 dirs including `archive`, `tmp`, `examples` | 8 dirs; omits the three airline-specific extras | **gzkit** — airlineops carries airline-specific exclusions |
| EXCLUDE_PATH_SNIPPETS self-exclusion | `/opsdev/lib/guards.py`, `/opsdev/commands/hooks_tools.py`, `/opsdev/commands/tasks.py` | `/gzkit/hooks/guards.py` | Tie on intent; each correctly excludes its own module |
| `iter_files` directory prune | `rglob('*')` without ancestor prune — EXCLUDE_DIRS does **not** actually prune descendants | Same defect at start of brief; **fixed in this OBPI** via ancestor-parts check | **gzkit (post-absorption)** — the defect was latent in both codebases; gzkit fixes it |
| Cross-platform print safety | `_safe_print(s)` helper catches `UnicodeEncodeError` and falls back to `s.encode("ascii", "backslashreplace")` | None at start of brief; **absorbed in this OBPI** | **airlineops (source of absorbed pattern)** |
| TYPE_CHECKING lazy Iterable import | Yes | No (direct import) | Cosmetic tie — no runtime difference; direct import is fine |
| Test coverage | Unknown — not measured here | 0 tests → 26 unit tests (~92% coverage of the module post-absorption) | **gzkit (post-absorption)** — first-ever test file for this module |
| Subtraction test | Does anything in either file require airline domain context? | No — both are pure stdlib scanners over text files | N/A — pattern is portable |

### Subtraction test

Remove every airline-specific concept from `opsdev/lib/guards.py`: nothing
changes. The module scans text files for string patterns using `re`,
`pathlib`, and stdlib `print`. It imports no airlineops package, references
no airline domain concept, and depends on no airline config key. By the
subtraction test the scanner pattern belongs in any unittest-only Python
repo — gzkit included.

## Decision: Absorb

Narrow absorption of the `_safe_print` cross-platform print-safety helper
from airlineops into gzkit's existing `hooks/guards.py`, plus an incidental
fix to the `iter_files` directory prune defect that both codebases shared,
plus full TDD coverage for a previously untested module.

**Rationale:**

1. **gzkit's public API is already superior — do not regress it.** Gzkit
   removed `Path(__file__).resolve().parents[3]` from `hooks/guards.py` in
   OBPI-0.0.7-04 as a config-first-resolution-discipline violation
   (`ADR-0.0.7`). `forbid_pytest(root: Path)` takes the scan root as an
   argument — testable, composable, and free of the `parents[3]` brittleness.
   airlineops still carries the pre-migration form. Absorbing airlineops
   wholesale would undo gzkit governance work already validated in ADR-0.0.7.
   The right shape is to keep gzkit's API and import specific improvements
   from airlineops, not the reverse.
2. **The `_safe_print` pattern is concretely relevant to gzkit's
   cross-platform covenant.** `.pre-commit-config.yaml:40` invokes the
   scanner as `uv run -m gzkit.hooks.guards`, which executes
   `gzkit.hooks.guards.__main__` directly and **bypasses**
   `gzkit/__main__.py`'s `sys.stdout.reconfigure(encoding="utf-8")` UTF-8
   guard. On a Windows cp1252 terminal, a finding line that interpolates a
   file path or a violation message containing non-ASCII bytes would raise
   `UnicodeEncodeError` and crash the hook — taking the entire pre-commit
   chain down with it. `.claude/rules/cross-platform.md` explicitly warns
   about this class of failure for Rich/Unicode output on Windows cp1252;
   `_safe_print` is the stdlib equivalent of that mitigation for this
   specific invocation path. The helper is seven lines, has no dependencies,
   and cannot regress any existing terminal.
3. **The `iter_files` directory prune defect is shared across both
   codebases and was caught by TDD.** Both implementations document
   `EXCLUDE_DIRS` as the directory-level exclusion list, but both use
   `root.rglob("*")` without pruning descendants of excluded directories.
   The `if p.is_dir(): ... continue` branch only skips the directory entry
   itself; rglob still walks inside. `test_excludes_top_level_excluded_dirs`
   created a `.git/hidden.py` under a temp root and asserted the scanner
   does not yield it — the test failed on the existing code, exposing the
   latent defect in both codebases. Fix: check each yielded file's ancestor
   parts (`p.relative_to(root).parts[:-1]`) against `EXCLUDE_DIRS` before
   yielding. Four-line change; no API change; the real gzkit repo has never
   hit the bug in practice because `EXCLUDE_PATH_SNIPPETS` covers the
   `.venv/`, `venv/`, etc. cases, but `.git` was not in snippets and was
   only protected by the (ineffective) `EXCLUDE_DIRS` check. Per
   `.gzkit/rules/tests.md`: defects revealed by tests must be fixed, not
   rationalized as pre-existing.
4. **Absorption is library-only — no CLI surface change.** The output
   header, footer, and exit code for `forbid_pytest` are unchanged. The
   only observable differences from an operator's perspective are: (a) the
   scanner no longer yields files under `.git/` on any repo where `.git`
   had `.py` files (which is effectively never in practice); (b) on Windows
   cp1252 terminals, a scan that would previously crash on non-ASCII
   findings now emits a backslash-escaped rendering of the same content.
   Both changes are strict improvements. Gate 4 BDD is `N/A` because there
   is no operator-visible behavior change under the normal happy path
   (findings on ASCII-only paths produce identical stdout bytes).
5. **TDD first, code second.** `tests/test_hooks_guards.py` is a new file
   — gzkit had zero unit tests for `hooks/guards.py` before this OBPI. The
   TDD sequence was: write test file (RED — 3 `AttributeError: _safe_print`
   errors plus the `iter_files` directory-prune failure), implement
   `_safe_print` and the `iter_files` prune fix (GREEN — 26/26 tests pass),
   ruff format (REFACTOR — no behavior change). Coverage for `hooks/guards.py`
   went from unmeasured (no test file existed) to ~92% in a single pass.
6. **Subtraction test passes cleanly.** Nothing in either `guards.py` file
   is airline-specific. The absorbed `_safe_print` helper operates on a
   generic `UnicodeEncodeError` fallback path with zero airline context;
   it belongs in gzkit on its own terms.
7. **airlineops is not touched.** This is upstream absorption only. The
   airlineops copy of the helper remains canonical in airlineops; gzkit
   now has its own equivalent that fits gzkit's better public API.

### Gate 4 (BDD): N/A

No operator-visible behavior change on the happy path. The scanner still
prints the same static header (`"pytest usage detected; this repository
enforces unittest-only."`) and the same static footer (`"Please remove
pytest references or dependencies."`). Finding lines (`"- {path}"` and
`"    {violation}"`) still print verbatim on any terminal that could
previously print them — `_safe_print`'s fast path is `print(s)`, and the
fallback branch only fires when the direct `print` would have raised
`UnicodeEncodeError`. The `iter_files` prune fix affects the set of files
scanned, but not the set of violations reported on any real gzkit check-out
(every directory the defect exposed was already dominated by
`EXCLUDE_PATH_SNIPPETS`). Per the parent ADR's lane definition, a brief may
record BDD as `N/A` when the change does not alter operator-visible
behavior; that condition is met here. No `features/core_infrastructure.feature`
update is required.

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] Absorb path: adapted gzkit module and tests are added —
  `src/gzkit/hooks/guards.py` (`_safe_print` helper + `iter_files`
  directory-prune fix) and `tests/test_hooks_guards.py` (26 new tests,
  ~92% coverage of the module)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision — **Absorb**
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome — see "Capability Comparison" and "Decision: Absorb"

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (library-only; header/footer bytes unchanged; fallback path
  only fires where direct `print` would have raised)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change — see "Gate 4 (BDD): N/A" subsection above

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-27-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-27-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit — see the 12-row Capability Comparison table and the 7-point rationale.
- [x] REQ-0.25.0-27-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely —
  `src/gzkit/hooks/guards.py:_safe_print` plus `tests/test_hooks_guards.py`
  (26 tests).
- [x] REQ-0.25.0-27-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted — N/A (Absorb chosen; see
  rationale for why partial absorption with gzkit API preservation is the
  right outcome rather than full Absorb or Confirm).
- [x] REQ-0.25.0-27-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale — N/A recorded with rationale in the Gate 4 subsection.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/guards.py
# Expected: airlineops source under review exists

test -f src/gzkit/hooks/guards.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-27-policy-guards-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass — `tests/test_hooks_guards.py` (26 tests, all pass)
- [x] **Gate 3 (Docs):** Decision rationale completed (Absorb, with 7-point rationale)
- [x] **Gate 4 (BDD):** N/A — library-only addition, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

Both `opsdev/lib/guards.py` and `src/gzkit/hooks/guards.py` scan text files
for pytest usage and reject it. The two files share byte-identical regex
patterns, scan-extension sets, conftest/pyproject short-circuits, and exit
code semantics. They are convergent forks of the same intent. Where they
differ, gzkit has already chosen the better public shape: `forbid_pytest`
takes the scan root as a parameter, not as `Path(__file__).resolve().parents[3]`,
because gzkit removed that anti-pattern in OBPI-0.0.7-04 under
ADR-0.0.7 (config-first-resolution-discipline). A full Absorb that replaced
gzkit's module with airlineops's would erase that governance work. A full
Confirm that kept gzkit unchanged would leave two concrete improvements on
the table — one from airlineops, one exposed by writing the first real
tests for this module.

The airlineops improvement is a seven-line helper called `_safe_print` that
wraps `print(s)` in a `try` / `except UnicodeEncodeError` with an
`s.encode("ascii", "backslashreplace").decode("ascii")` fallback. The
helper exists because `opsdev/lib/guards.py` is invoked outside the CLI
UTF-8 guard, and on Windows cp1252 terminals a finding line that
interpolates a non-ASCII file path or violation text would otherwise crash
the pre-commit hook. gzkit's own `.pre-commit-config.yaml:40` invokes
`uv run -m gzkit.hooks.guards` — the same bypass path. gzkit's
`cross-platform.md` rule explicitly warns about this class of terminal
encoding failure, and the existing gzkit scanner had no defense against it.
The helper is narrow, dependency-free, and strictly additive; the fast
path is unchanged and the fallback fires only where direct `print` would
have raised.

Writing the first test file for `hooks/guards.py` caught a second, latent
defect that was shared by both codebases. `iter_files(root)` documents
`EXCLUDE_DIRS = {".git", ".venv", ...}` as the directory-level exclusion
list, but uses `root.rglob("*")` without pruning descendants. The
`if p.is_dir(): continue` branch only skips the directory *entry*; rglob
walks inside it anyway. A test that planted `.git/hidden.py` under a temp
root and asserted the scanner did not yield it failed on the existing code.
Real gzkit check-outs had never hit the bug in practice because
`EXCLUDE_PATH_SNIPPETS` caught the `.venv/`, `venv/`, `build/`, `dist/`
cases via full-posix matching — but `.git` was not in snippets and was only
protected by the ineffective `EXCLUDE_DIRS` check. Per gzkit's test policy
("flag defects, never excuse them"), the defect could not be rationalized
as pre-existing and had to be fixed in-place. The fix is a four-line
ancestor-parts check against `EXCLUDE_DIRS` before yielding; no API change,
no behavior change on any finding that would have been reported before.

The final shape of the absorption is three changes to `src/gzkit/hooks/guards.py`:
(1) add the `_safe_print` helper; (2) route the two dynamic-content print
calls in `forbid_pytest` (the `- {path}` line and the `    {violation}`
line) through `_safe_print`; (3) add the ancestor-prune check to
`iter_files`. Static header and footer prints are left as plain `print`
because they are ASCII-safe by construction and their `# noqa: T201`
annotations are intentional documentation that the scanner talks to
stdout. `forbid_pytest(root: Path)` signature is untouched. `main()` still
calls `forbid_pytest(Path.cwd())`. The single TDD test file
`tests/test_hooks_guards.py` covers seven test classes: `TestIterFiles`
(4 tests including the directory-prune regression), `TestScanFileSourceLevel`
(7 table-driven pattern-detection tests), `TestScanFileSpecialCases`
(6 tests for conftest, pyproject, and requirements detection),
`TestScanFileReadError` (1 test for OSError fallback), `TestForbidPytest`
(4 integration tests including clean root, bad .py, conftest, and
pyproject), `TestSafePrint` (3 tests including the cp1252 fallback path
exercised via a `gzkit.hooks.guards.print` mock that raises on `\u2713`),
and `TestMain` (1 test that patches `Path.cwd`). Coverage goes from zero
(no test file existed) to ~92% of the module. **Decision: Absorb.**

### Implementation Summary


- **Decision:** Absorb — narrow absorption of the `_safe_print` helper plus
  an incidental `iter_files` prune defect fix caught by new TDD coverage.
- **gzkit keeps its superior public API:** `forbid_pytest(root: Path)` is
  unchanged. airlineops's `Path(__file__).resolve().parents[3]` form is
  rejected; gzkit removed that in OBPI-0.0.7-04 and does not regress it.
- **New helper:** `src/gzkit/hooks/guards.py:_safe_print(s)` — seven-line
  `try` / `except UnicodeEncodeError` with backslash-escape fallback, routed
  from `forbid_pytest` output lines that interpolate user-controlled data
  (file paths, violation messages).
- **Incidental defect fix:** `iter_files(root)` now prunes any file whose
  ancestor parts include an `EXCLUDE_DIRS` entry. Four lines; no API
  change; test-driven discovery via
  `TestIterFiles.test_excludes_top_level_excluded_dirs`.
- **New test file:** `tests/test_hooks_guards.py` — first-ever test
  coverage for this module. 26 unittest cases across 7 test classes,
  table-driven where possible, `tempfile.TemporaryDirectory()` for
  isolation, `contextlib.redirect_stdout` for output capture, no network,
  no real repo mutation. All 26 pass.
- **Cross-platform alignment:** Absorbed pattern directly supports
  `.claude/rules/cross-platform.md` (Windows cp1252 console output)
  without depending on the CLI entrypoint's `sys.stdout.reconfigure` guard,
  which the pre-commit hook invocation path bypasses.
- **Convention compliance:** stdlib only; `pathlib.Path`; UTF-8 reads;
  `# noqa: T201` preserved where print is intentional; ruff + format
  clean.
- **No CLI surface change:** Gate 4 BDD is `N/A` with rationale
  (fallback fires only where direct `print` would have raised; prune fix
  affects no real gzkit check-out under `EXCLUDE_PATH_SNIPPETS` coverage).

### Key Proof


```bash
uv run -m unittest tests.test_hooks_guards -v 2>&1 | tail -3
# Expected:
#   Ran 26 tests in <0.02s>
#
#   OK
```

```bash
python -c "from gzkit.hooks import guards; print(guards._safe_print.__doc__.splitlines()[0])"
# Expected:
#   Print a string with ASCII-escape fallback for narrow-encoding terminals.
```

```bash
rg -n 'Decision: Absorb' \
  docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-27-policy-guards-pattern.md
# Expected: one match — "## Decision: Absorb"
```

## Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-13
- Attestation: attest completed — Absorb decision for airlineops opsdev/lib/guards.py: absorbed _safe_print helper (seven-line UnicodeEncodeError backslashreplace fallback) into gzkit hooks/guards.py to protect the pre-commit hook invocation path (uv run -m gzkit.hooks.guards) that bypasses the CLI UTF-8 guard. Kept gzkit's superior forbid_pytest(root: Path) API from OBPI-0.0.7-04 — airlineops still carries Path(__file__).parents[3] which gzkit already removed. TDD exposed a latent iter_files prune defect shared by both codebases (rglob walks inside EXCLUDE_DIRS); fixed via ancestor-parts check. 26 unittest cases across 7 test classes land the first-ever test coverage for hooks/guards.py (0 → ~92%). Gate 4 BDD: N/A (library-only; header/footer bytes unchanged). All quality gates green: lint, typecheck, gz test (17 features / 110 scenarios / 584 steps), validate --documents, mkdocs --strict.
