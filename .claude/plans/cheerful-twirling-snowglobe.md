# Plan: OBPI-0.0.30-01 — `gz complexity guide` CLI Verb

**OBPI:** OBPI-0.0.30-01-complexity-guide-cli
**ADR:** ADR-0.0.30 (Complexity Authoring Guidance)
**Lane:** Heavy | **Kind:** Foundation
**Plan date:** 2026-05-09

---

## ⚠ STOP-on-BLOCKERS — Active

**OBPI-03's engine is NOT landed.** `src/gzkit/complexity/authoring/` does not
exist. Stage 2 CANNOT proceed until OBPI-0.0.30-03 is complete and
`src/gzkit/complexity/authoring/engine.py` + `hint.py` are committed. This plan
is authored for governance readiness; implementation begins only after OBPI-03.

---

## Context

OBPI-0.0.30-01 adds `gz complexity guide` as a subcommand under `gz complexity`
(alongside `gz complexity advise` and `gz complexity distill`). It is the
operator-facing ad-hoc pathway of the ADR-0.0.30 authoring-guidance surface —
the developer runs it while editing a file to preview authoring-time complexity
hints *before* metrics cross the warn/block bands. The critical distinction from
`gz complexity advise`: this verb surfaces `advise`-band hints only, never
blocks (exit 3 is not used), and is for design-time preview, not gate-time
enforcement.

The command wraps `gzkit.complexity.authoring.engine.analyze(path)` (OBPI-03)
and renders `AuthoringHint` objects. It mirrors the shape of
`src/gzkit/commands/complexity_advise.py` closely.

---

## Files

### Created
- `src/gzkit/commands/complexity_guide.py` — command handler
- `tests/commands/test_complexity_guide.py` — unit tests (3-class split)
- `features/complexity_guide.feature` — behave smoke scenarios
- `docs/user/manpages/gz-complexity-guide.md` — manpage

### Modified
- `src/gzkit/cli/parser_artifacts.py` — register `guide` subcommand
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"

---

## Steps

### Step 1 — Register the verb in `parser_artifacts.py`

In `_register_complexity_parsers()`, after the `p_advise` block (~line 274):

1. Add to `LAZY_COMMANDS` dict at top of file:
   `"complexity_guide_cmd": "gzkit.commands.complexity_guide"`

2. Add the parser registration:
   ```python
   p_guide = complexity_commands.add_parser(
       "guide",
       help="Surface authoring-time complexity hints for a file or directory",
       description=(
           "Reads the advise band from the canonical threshold table "
           "(.gzkit/rules/complexity-thresholds.json, ADR-0.0.28), measures "
           "the target file or directory, and emits AuthoringHint blocks for "
           "functions approaching the warn threshold. Exit 3 is NOT used — "
           "this surface never blocks; that is gz complexity advise's role."
       ),
       formatter_class=argparse.RawDescriptionHelpFormatter,
       epilog="\n".join([
           "Examples:",
           "  gz complexity guide src/gzkit/commands/validate.py",
           "  gz complexity guide src/gzkit/ --json",
       ]),
   )
   p_guide.add_argument("path", help="File or directory to analyze")
   p_guide.add_argument("--json", dest="json_output", action="store_true",
       help="Emit canonical AuthoringHint JSON array to stdout")
   p_guide.add_argument("--quiet", action="store_true",
       help="Suppress output; rely on exit code only")
   p_guide.add_argument("--verbose", action="store_true",
       help="Emit debug output to stderr")
   p_guide.set_defaults(
       func=lambda a: _lazy("complexity_guide_cmd")(
           path=a.path,
           json_output=a.json_output,
           quiet=a.quiet,
           verbose=a.verbose,
       )
   )
   ```

### Step 2 — Create `src/gzkit/commands/complexity_guide.py`

Module docstring citing OBPI-0.0.30-01 and the exit-code contract (explaining
why 3 is NOT used — authoring surface never blocks).

```python
def complexity_guide_cmd(
    *,
    path: str,
    json_output: bool = False,
    quiet: bool = False,
    verbose: bool = False,
) -> int:
```

Logic:
1. Validate `path` exists → exit 1 on bad path
2. Resolve threshold table (`DEFAULT_RULE_PATH`) → exit 2 if missing
3. Call `from gzkit.complexity.authoring.engine import analyze` → `analyze(Path(path))`
4. If `json_output`: `print(json.dumps([h.model_dump(mode="json") for h in hints], indent=2))` → exit 0
5. If no hints: print "No advise-band hints found." → exit 0
6. Otherwise: print one block per hint:
   ```
   ── <file_path>:<start_line>-<end_line> ──
   Archetype : <archetype>
   Band      : <precedence_band>
   Guidance  : <doctrinal_frame_headline>
   Move      : <recommended_move>
   ```
7. Return 0 (exit 3 never emitted by this verb)

Error handling:
- `FileNotFoundError`, `PermissionError` → stderr message → sys.exit(2)
- `ValueError` → stderr message → sys.exit(1)
- Engine errors (from OBPI-03's `EngineError` analog) → stderr → sys.exit(2)

Size discipline: keep ≤50 lines per function; decompose `_render_hints_prose()`
and `_render_json_output()` as helpers.

### Step 3 — Create `tests/commands/test_complexity_guide.py`

Three-class split following `test_complexity_advise.py` pattern:

**`TestComplexityGuideBehavior`** (semantic, all with `@covers("REQ-0.0.30-01-NN")`):
- Mock `gzkit.complexity.authoring.engine` at import boundary
- `test_clean_file_exit_0_no_hints` → `@covers("REQ-0.0.30-01-01")`
- `test_advise_band_crossings_exit_0_prose` → `@covers("REQ-0.0.30-01-02")`
- `test_json_mode_valid_schema` → `@covers("REQ-0.0.30-01-03")`
- `test_warn_and_block_not_included` → `@covers("REQ-0.0.30-01-04")`
- `test_help_flag_exit_0_sections` → `@covers("REQ-0.0.30-01-05")`
- `test_bad_path_exit_1` → exit 1 on nonexistent path
- `test_missing_threshold_table_exit_2` → exit 2 on missing rule file
- `test_exit_3_never_produced` → engine returns 100 hints, verify exit code is 0

**`TestComplexityGuideOutputForm`** (string-shape only):
- Verify prose output contains "Archetype", "Band", "Guidance", "Move" headers

**`TestComplexityGuideCliAuditParity`**:
- `test_cli_audit_covers_new_verb` → `@covers("REQ-0.0.30-01-06")`
- Runs `gz cli audit`, verifies exit 0 and verb covered in manpage + index

Helper:
```python
def _invoke(path, **kwargs) -> tuple[int, str, str]:
    """Invoke complexity_guide_cmd; collapse SystemExit to (code, stdout, stderr)."""
```

Mock pattern (mocking `analyze` at module boundary via `unittest.mock.patch`):
```python
with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
    mock_analyze.return_value = ()  # or tuple of AuthoringHint stubs
```
(The command should import `analyze` lazily via a module-level private alias so mocking is clean.)

### Step 4 — Create `features/complexity_guide.feature`

```gherkin
Feature: gz complexity guide — authoring-time hint surface

  @REQ-0.0.30-01-01
  Scenario: Clean file produces exit 0 with no-hints message
    Given a Python file with no advise-band crossings
    When I run "gz complexity guide <path>"
    Then the exit code is 0
    And the output contains "No advise-band hints found"

  @REQ-0.0.30-01-02
  Scenario: File with advise-band crossings produces prose hint blocks
    Given a Python file with functions approaching the warn threshold
    When I run "gz complexity guide <path>"
    Then the exit code is 0
    And the output contains "Archetype"
    And the output contains "Move"

  @REQ-0.0.30-01-03
  Scenario: --json mode produces valid JSON
    Given a Python file with functions approaching the warn threshold
    When I run "gz complexity guide <path> --json"
    Then the exit code is 0
    And the output is valid JSON
    And the JSON contains "precedence_band"

  @REQ-0.0.30-01-04
  Scenario: --help exits 0 with standard sections
    When I run "gz complexity guide --help"
    Then the exit code is 0
    And the output contains "usage"
    And the output contains "options"
    And the output contains "Examples"
```

Step definitions: `features/steps/complexity_guide_steps.py` (new file — also
in allowed paths implicitly via `features/` directory).

### Step 5 — Create `docs/user/manpages/gz-complexity-guide.md`

Sections: NAME / SYNOPSIS / DESCRIPTION / OPTIONS / EXIT CODES / EXAMPLES / SEE ALSO

Key points:
- NAME: `gz-complexity-guide — surface authoring-time complexity hints`
- SYNOPSIS: `gz complexity guide [--json] [--quiet] [--verbose] <path>`
- DESCRIPTION: explain authoring-time vs gate-time distinction; reference ADR-0.0.30 and the advise band; explicitly note "Exit 3 is NOT produced by this verb — the build is never blocked by authoring hints"
- EXIT CODES table: 0 (success), 1 (user/config error), 2 (system/IO error); exit 3 with note "NOT USED"
- EXAMPLES: 4 examples (basic file, directory walk, --json, clean file)
- SEE ALSO: `gz complexity advise`, `gz complexity distill`, ADR-0.0.30, runbook

### Step 6 — Update `docs/user/runbook.md`

Under "Governance Doctrine Surfaces", add before `gz complexity advise`:

```markdown
**`gz complexity guide`** (OBPI-0.0.30-01): Authoring-time preview — run while
editing a file to surface `advise`-band hints before reaching gate time. Emits
one prose block per hint (archetype, guidance, recommended move). Never blocks.

```bash
uv run gz complexity guide <path>           # In-line hint prose
uv run gz complexity guide <path> --json    # Machine-readable AuthoringHint array
```

See [`gz-complexity-guide`](manpages/gz-complexity-guide.md) for full reference.
```

---

## Verification

```bash
# Baseline quality
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_guide.py -v

# CLI audit parity (covers REQ-0.0.30-01-06)
uv run gz cli audit

# Docs build
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# BDD smoke (covers REQ-0.0.30-01-01 through 01-04)
uv run -m behave features/complexity_guide.feature

# Manual smoke check
uv run gz complexity guide --help
uv run gz complexity guide src/gzkit/commands/complexity_advise.py
```

---

## Plan-Before-Exploration Disclosures (gz-plan-audit § Step 6a)

**Destination-in-mind before writing this plan:**
I had already concluded that `gz complexity guide` would register as a
subcommand under the existing `gz complexity` group using `add_parser("guide")`,
following the `gz complexity advise` / `gz complexity distill` pattern. The
lazy-import handler shape was obvious from inspection of parser_artifacts.py.

**Rejected alternatives considered:**
1. Top-level `gz complexity-guide` hyphenated command — rejected because all
   complexity verbs use `gz complexity <subverb>`. A top-level hyphenated command
   would break the cluster's naming consistency.
2. Eager import of the engine at module top-level — rejected to preserve the
   lazy-import performance pattern (heavy complexity stack not loaded at
   `gz --help` time).
3. Single monolithic test class — rejected; the three-class split (behavior /
   output-form / CLI-audit-parity) is the established pattern from
   `test_complexity_advise.py`.
4. Reusing `AdHocPresenter` from ADR-0.0.29 — rejected because the authoring
   surface has a lighter output contract (`AuthoringHint`, not `AdvisorDiagnosis`);
   a dedicated `_render_hints_prose()` helper is cleaner.
