# Plan: OBPI-0.0.29-03 — `gz complexity advise` CLI Verb

**OBPI:** OBPI-0.0.29-03-complexity-advise-cli
**Parent ADR:** ADR-0.0.29-complexity-advisor (foundation, heavy)
**Lane:** Heavy (new CLI subcommand). Foundation-kind brief-level Gate 5
stacks per ADR-0.0.18.

## Context

ADR-0.0.29's third OBPI lands the operator-facing trigger-time response
verb. OBPI-0.0.29-01 (schema) and OBPI-0.0.29-02 (engine) are
**Completed** — the `AdvisorDiagnosis`, `RefactorArchetype`,
`DoctrinalFrame`, `ProofRange` Pydantic models and the `DiagnosisEngine`
are in place at `src/gzkit/complexity/advisor/`. STOP-on-BLOCKERS clears.

The CLI verb wraps the engine for ad-hoc operator invocation:
`gz complexity advise <path>` reads the threshold table at
`.gzkit/rules/complexity-thresholds.md`, measures `<path>` (radon CC),
runs the engine for each per-function crossing, and emits
`AdvisorDiagnosis` results. Exit 3 on `block`-band; exit 0 otherwise
(including warn-band with diagnosis prose, per Acceptance Criterion
03-02 and REQ-2's exit-code map).

The verb registers under the existing `complexity` parser group (next to
`gz complexity distill`) — the parser_artifacts.py comment at line 98
explicitly anticipates `advise` as a sibling subverb. The brief's prose
shorthand "`gz complexity-advise`" is doc/manpage filename convention;
the parser surface is `gz complexity advise <path>`.

## Destination-in-mind disclosure (Step 6a)

**Conclusion already in mind before plan author:** Implement
`gz complexity advise` as a subverb of the existing `complexity` parser
group, dispatching to a thin handler in
`src/gzkit/commands/complexity_advise.py` that uses radon's Python API
(`radon.complexity.cc_visit`) for per-function CC measurement, walks
the AST to bind each measured function to its FunctionDef node, and
calls the engine once per crossing.

**Rejected alternatives considered during exploration:**
1. **Top-level `gz complexity-advise` verb (hyphenated).** Rejected —
   parser_artifacts.py:98 explicitly anchors `advise` as a sibling of
   `distill` under the `complexity` group; introducing a top-level
   hyphenated verb would split the cluster's surface, contradict the
   landed pattern, and force an asymmetric naming convention. The
   brief's hyphenated shorthand is doc/manpage convention only.
2. **Subprocess to `radon` CLI (matching measurement.py pattern).**
   Rejected — measurement.py spawns `radon` for batch corpus
   aggregation that returns flat per-metric lists with no per-function
   line mapping. Ad-hoc per-file analysis needs (function-name,
   line, complexity) tuples to bind back to AST FunctionDef nodes for
   the engine's `target_node` parameter. radon's Python API
   (`cc_visit`) already returns those tuples; subprocess parsing would
   reimplement what the API exposes natively. radon is a declared
   runtime dependency (`pyproject.toml`: `"radon>=6.0,<7.0"`).
3. **Custom AST-based CC calculator (no radon).** Rejected — the
   threshold table cites the metric as `radon_cc`; using a custom
   calculator would produce values incompatible with the table's
   absolute-number boundaries. The metric name carries semantic load.
4. **Compute every metric in the threshold table (radon_mi, lizard,
   cohesion, halstead).** Rejected for OBPI-03 scope — the brief's
   acceptance criteria are framed around per-function crossings;
   `radon_cc` is the canonical per-function metric. Other metrics
   land in subsequent OBPIs (07/09 expand the surface). Limiting to
   radon_cc keeps OBPI-03 a single tractable invariant.

## Files

### Plan creates these files (net-new for this OBPI; GHI #403 suppression)

- `src/gzkit/commands/complexity_advise.py` — handler module
- `tests/commands/test_complexity_advise.py` — REQ-derived tests + Output-Form fixture
- `features/complexity_advise.feature` — behave smoke (3 scenarios, REQ-tagged)
- `docs/user/manpages/gz-complexity-advise.md` — manpage

### Modified

- `src/gzkit/cli/parser_artifacts.py` — register `advise` subverb under
  existing `_register_complexity_parsers`, add lazy handler entry
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-03-complexity-advise-cli.md`
  — evidence sections only (Stage 5 closeout)

## Steps

### Step 1 — TDD red: author REQ-derived tests at `tests/commands/test_complexity_advise.py`

- Two test classes per `.gzkit/rules/tool-skill-runbook-alignment.md`
  Invariant 3 / `tests.md` Output-form-fixture carve-out:
  - `TestComplexityAdviseBehavior` — REQ-derived semantic assertions
    (exit codes, parsing, --json shape, --help content, no crossings,
    warn-band, block-band)
  - `TestComplexityAdviseOutputForm` — Invariant-3 fixture pinning
    default human prose form (string-shape assertions only here)
- Each test decorated with `@covers("REQ-0.0.29-03-NN")`
- Use `TempDBMixin`-style `tempfile.TemporaryDirectory()` for fixture
  Python sources (clean / warn-crossing / block-crossing inputs)
- Capture stdout/stderr via `io.StringIO` + `redirect_stdout`/`redirect_stderr`
- No subprocess spawned (radon Python API is in-process); REQ-10
  satisfied vacuously
- Fixtures inject a small `ThresholdTable` directly via a monkeypatched
  loader path or a module-level constant the handler honors when
  passed `--rule-path` (test-only injection path)
- Assertions:
  - clean file → exit 0, stdout contains "no crossings"
  - warn-band crossing → exit 0, stdout contains archetype name and
    doctrinal-frame authority
  - block-band crossing → exit 3
  - `--json` mode → stdout is JSON parseable into a list of objects
    each validating against `src/gzkit/schemas/advisor_diagnosis.json`
  - `--help` → exit 0, contains "DESCRIPTION", "USAGE", "OPTIONS",
    "EXAMPLE", "Exit codes"
  - `--quiet`/`--verbose`/`--dry-run` accepted by parser without crash
  - bad path → exit 1 with stderr error
- Run: `uv run -m unittest tests.commands.test_complexity_advise -v` —
  expect FAIL (red)

### Step 2 — TDD green: implement `src/gzkit/commands/complexity_advise.py`

- Imports: `argparse`, `ast`, `json`, `sys`, `pathlib.Path`,
  `radon.complexity.cc_visit`, plus
  `gzkit.complexity.advisor.{diagnosis,engine}` and
  `gzkit.complexity.thresholds.load_threshold_table`
- Module constants: `DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.md")`
- Handler signature:
  ```python
  def complexity_advise_cmd(
      *,
      path: str,
      json_output: bool = False,
      quiet: bool = False,
      verbose: bool = False,
      dry_run: bool = False,
      auto_chain: bool = False,
      rule_path: str | None = None,  # test injection
  ) -> int
  ```
  Returns 0 / `raise SystemExit(code)` for non-zero (mirrors
  `complexity_distill_cmd` precedent)
- Helper functions (each <=50 lines, per pythonic.md):
  - `_iter_python_files(target: Path) -> Iterator[Path]` — single
    file or recursive directory walk
  - `_load_table(rule_path: Path | None) -> ThresholdTable`
  - `_analyze_file(path, table, engine) -> list[AdvisorDiagnosis]` —
    parse AST, run radon `cc_visit` on source, for each visited
    function find matching FunctionDef AST node by line number, build
    `AstContext`, call `engine.diagnose("radon_cc", complexity, table)`
  - `_render_prose(diagnoses) -> str` — structured prose form per
    SKILL.md Output Contract (deferred to OBPI-04, but the verb's
    default form is fixed here)
  - `_render_json(diagnoses) -> str` — JSON array via
    `[d.model_dump(mode="json") for d in diagnoses]`
  - `_resolve_exit_code(diagnoses) -> int` — 3 if any
    `crossing_band == "block"`, else 0
- Error handling at boundaries:
  - bad path / parse error / threshold-load error → exit 1
  - missing schema / missing distilled-characteristics → exit 2
  - block-band crossing → exit 3
- Run: `uv run -m unittest tests.commands.test_complexity_advise -v` —
  expect PASS (green)

### Step 3 — Register the parser in `src/gzkit/cli/parser_artifacts.py`

- Add `"complexity_advise_cmd": "gzkit.commands.complexity_advise"` to
  `_LAZY_HANDLERS`
- Extend `_register_complexity_parsers` to add `advise` subparser:
  - help text per `.claude/rules/cli.md` § Help Text Requirements
  - description (1–2 sentences) naming the engine binding
  - epilog with at least one example invocation, plus a `--json`
    example (REQ-5 manpage example parity)
  - positional `path` (required)
  - flags: `--json`, `--quiet`, `--verbose`, `--dry-run`,
    `--auto-chain` (reserved per REQ-3, semantics in OBPI-05)
  - `set_defaults(func=lambda a: _lazy("complexity_advise_cmd")(...))`
- Run: `uv run gz complexity advise --help` — confirm exit 0,
  expected sections render
- Run: `uv run gz cli audit` — confirm new verb covered (manpage
  authored in Step 4 so this lands after Step 4)

### Step 4 — Author manpage `docs/user/manpages/gz-complexity-advise.md`

- Sections per `gz-justify.md` shape: NAME, SYNOPSIS, DESCRIPTION,
  OPTIONS, EXAMPLES, EXIT CODES, SEE ALSO
- Document all flags, the four-code exit map (REQ-2), and at least
  two example invocations: one ad-hoc, one with `--json` (REQ-5)
- Cross-reference the runbook ("Complexity doctrine surfaces")
- Lines <=80 chars (REQ-4)

### Step 5 — Runbook entry at `docs/user/runbook.md`

- Under "Complexity doctrine surfaces" — add line for the operator
  moment "preview advisor diagnosis on a file before commit" (REQ-6)
- Prescribes `uv run gz complexity advise <path>` with one inline
  example and a pointer to the manpage

### Step 6 — Behave smoke at `features/complexity_advise.feature`

- Three scenarios (REQ-7), each tagged `@REQ-0.0.29-03-NN`:
  - clean file → exit 0
  - warn-band crossing → exit 0 + diagnosis prose
  - block-band crossing → exit 3
- Step definitions reuse existing CLI step infrastructure if present;
  otherwise add minimal step file under `features/steps/`
- Heavy-lane requires this; integrates with existing `behave` runner

### Step 7 — Run gates and lint sweep

- `uv run ruff check . --fix && uv run ruff format .`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_complexity_advise -v`
- `uv run gz cli audit` — confirm `complexity advise` covered (manpage,
  command doc, index parity)
- `uv run mkdocs build --strict`
- `uv run -m behave features/complexity_advise.feature`
- `uv run gz arb ruff` / `uv run gz arb typecheck` — capture canonical
  receipts for Stage 4 evidence (Heavy-lane requires receipts)
- `uv run gz covers OBPI-0.0.29-03 --json` — confirm parity
  (`uncovered_reqs == 0`)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict
uv run gz complexity advise --help
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_advise.py -v
uv run -m behave features/complexity_advise.feature
uv run gz covers OBPI-0.0.29-03 --json
```

## Notes

- **No subprocess in unit tests:** radon is invoked via its Python
  API (`cc_visit`); REQ-10 satisfied vacuously. The behave smoke
  scenarios run `gz complexity advise` end-to-end as a subprocess,
  which is the integration tier and is the right place for that.
- **Default rule path injection:** the handler accepts a `rule_path`
  kwarg (None → DEFAULT_RULE_PATH). Tests inject a fixture
  threshold rule body so they don't bind to the live threshold
  table's evolving boundaries.
- **OBPI-04 deferral:** the prose Output Contract format (verbose
  preview vs trigger-time fail-fast) is fully specified in OBPI-04's
  skill SKILL.md. OBPI-03 lands a single readable form (named
  archetype + authority + proof line range + recommended-move
  excerpt). OBPI-04 may iterate the prose form when authoring the
  skill; the verb's `--json` Pydantic serialization is the stable
  surface.
- **Auto-chain flag reservation:** `--auto-chain` is parsed and
  accepted but its semantic effect (different presentation defaults
  per ADR-0.0.29 Mechanical Surfaces description of OBPI-05) is
  reserved here. OBPI-05 wires the hook that fires it.
