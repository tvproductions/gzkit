# Rule validity review, batch A (2026-11-08, read-only)

Rules: pythonic, models, cross-platform, cli, guardrail-feedback-prose, hexagonal-architecture (restored 0.3.1, glob `**/*.py`), mode-contract.
Validity: T = TRUE, S = STALE, U = UNVERIFIABLE. Usefulness: N = NEEDED, R = REDUNDANT, X = NO-OP.

## Facts I checked that several rules depend on

- `gz check` per-change scope (`src/gzkit/check_step_scopes.json` "change") **skips `Test`** and runs only `Test (changed)`. So a check that exists only as a whole-tree unit test fires late (in `gz check --full` / CI), not while the agent is editing. That covers class-size, pydantic-models, type-ignores, as_posix, errors="replace", the executable AST fence and core import purity. Ruff checks fire right away (`gz lint`, plus the stop hook).
- `gz validate --class-size/--pydantic-models/--type-ignores/--utf8-prefix/--cli-alignment` are tier `"explicit"` (`validate_cmd.py:213-237`). A bare `gz validate` does not run them (`_run_scope_checks`: explicit runners only `if explicit_scopes.get(scope)`). They are reached only through `tests/governance/test_promoted_advisory_audits.py` and `test_type_ignore_syntax.py` (real-tree tests). Every one passed when I ran it with its flag ("All validations passed (1 scopes)").
- Ruff `select = ["ALL"]`, `preview = true` (pyproject). It fires PLW1514 (probe: "unspecified-encoding: `open` in text mode without explicit `encoding` argument"), UP045 for `Optional` (probe: "UP045 [*] Use `X | None`"), BLE001 (`ruff check src/gzkit --select BLE001` -> "All checks passed!"), PLC0415, TID251, PTH (package only), S602 and S607.

## pythonic.md (8,913 B) — KEEP-PARTIAL

| # | Clause | V | Evidence | U | Why |
|---|---|---|---|---|---|
| P1 | Clarity over cleverness | U | — | X | default |
| P2 | Separation of concerns | U | — | X | default |
| P3 | Typed interfaces, `uv run ty check .` | T | `gz typecheck --help`: "Run static type analysis with ty"; Typecheck step in gz check roster (`commands/quality.py`) | R | AGENTS.md Project Identity "uv, ruff, ty"; gz check |
| P4 | EAFP for IO, LBYL for contracts | U | — | X | default |
| P5 | Context managers | U | — | R | ruff SIM115 under ALL |
| P6 | No mutable defaults | T | ruff B006 under ALL | R | ruff |
| P7 | Pydantic BaseModel for data | T | census: 435 direct BaseModel subclasses, 0 `from dataclasses` imports in src/gzkit | R | models.md M1 (loads on src/**) + AGENTS.md STDLIB-FIRST |
| P8 | No bare except, BLE001 on src/gzkit | T | ruff BLE001 clean; per-file-ignores BLE for tests/features/scripts/hooks | R | ruff fires at gz lint |
| P9a | Classes <=300 | T | `code_quality.py:148 limit = 300` | N | the class-size check is late (explicit scope + full-suite test) |
| P9b | Functions <=50, Modules <=600 | S | contradicted by the rule's own admonition and by `.gzkit/rules/complexity-thresholds.json` (lizard_nloc block 37.0; lizard_file_nloc block 3130.24) | R | the table is the authority |
| S2 | Admonition: table values 37.0 / 3130.24 / warn 716.5 / 700 = advise | T | json bands: file_nloc p75 307.25 advise, p90 716.5 warn, p99 3130.24 block; nloc p95 37.0 block | R | only needed while P9b exists |
| S3 | Table: Classes <=300 is a live gate via `gz validate --class-size` | T (partial) | the scope exists and passes, but it is explicit-tier; the real gate is `test_class_size_rule_21` (full suite) | R | dup of P9a |
| S4 | Functions <=50: enforced by nothing | T | `lizard_nloc` is read only by measurement.py, distillation.py and a diagnosis.py description; no gate reads it | R | |
| S5 | **Modules <=600: enforced by "nothing / authoring-time guidance only"** | **S** | gz check step `("Module size", run_module_size_audit)`; `quality.py:2324` runs `.gzkit/chores/module-sloc-cap-radon/check_module_size.py`, docstring lines 4-5: "Reads the ``lizard_file_nloc`` ``block`` band from the ONE canonical threshold table ... and enforces it over ``src/``" | R | |
| S6 | Cyclomatic row: C901 + `--complexity-ceiling` at max-complexity 20; cognitive 15 + baseline; lizard_ccn block 11.0 | T | `complexity_ceiling.py:94` reads `max-complexity`; `.gzkit.json` `{'cognitive_ceiling': 15}`; baseline file exists; ccn p95 11.0 block | R | the ruff/ceiling messages carry it |
| S7 | **"The table's function/module bands have no consumer: complexity_advise.py is reads lizard_ccn alone"** | **S** (module half) | check_module_size.py consumes the `lizard_file_nloc` block band (see S5). Function half TRUE (`complexity_advise.py:132 metrics_checked = 1  # currently only lizard_ccn`). Sentence is also garbled ("is reads") | R | |
| S8 | xenon miscoding note | T | history | X | belongs in rule-version-history / scorecard row 19 |
| S9 | Until resolved: <=300 binding, <=50/<=600 guidance, cite the table not this rule | U (routing claim) | "Pass A conflict-matrix row 11; routed for operator decision" not traced | N | "cite the table" is the one instruction that saves an agent from a false threshold |
| I1 | Top-level imports; stdlib, third-party, local order | T | ruff `I` under ALL | R | |
| I2 | No lazy imports except carve-outs; PLC0415 baseline; a legitimate one carries `# noqa: PLC0415` naming its carve-out | T | 361 PLC0415 rows in `data/ruff_baseline.json`; 608 `noqa: PLC0415` sites in src/gzkit | N (noqa convention only) | ruff refuses the import but does not say to name the carve-out |
| I3a | No `from __future__ import annotations`; unquoted annotations | T | pyproject:175-176 banned-api, msg names the fix; `--astral-discipline` passes | R | TID251 message |
| I3b | Annotation-only imports under `if TYPE_CHECKING:` at top level | T | ruff TC00x under ALL (TC003: 309 baseline rows) | R | |
| I3c | Pydantic field types stay runtime imports | T | `[tool.ruff.lint.flake8-type-checking] runtime-evaluated-base-classes` + `tests/policy/test_ruff_runtime_annotations.py` (pyproject comment) | R | |
| I3d | `annotationlib.get_annotations`, RUF063 | T | under ALL | R | |
| I3e | `lazy import` (PEP 810) is 3.15 | T | requires-python >=3.14 | R | a syntax error stops it at once |
| E1 | **Catch specific exceptions, translate to `core.errors`** | **S** | no `core.errors` module: `ls src/gzkit/core/` -> `exceptions.py` (GzkitError hierarchy with the exit_code map); 15 modules import `gzkit.core.exceptions` | N (once corrected) | an agent cannot find the hierarchy from a wrong name |
| E2 | No bare except outside CLI boundaries | T | as P8 | R | dup |
| E3 | "Mechanized 2026-08-08 ..." narrative | T | history | X | scorecard row 18 + pyproject comment carry it |
| E4 | Boundary catch carries `# noqa: BLE001` with a cited reason | T | 27 `noqa: BLE001` sites | N | ruff does not ask for the reason |
| T1 | Toolchain table (uv / gz lint / ty / gz test) | T | verbs exist | R | AGENTS.md Project Identity + Gate Covenant |
| Y1 | Bracketed `# type: ignore[...]` must name a `ty:` code; table of four forms | T | `--type-ignores` passes; `test_real_tree_has_no_inert_type_ignores` | N | the witness is late, and ty-specific syntax is not a model default |
| Y2 | `no-untyped-def`/`import-untyped`/`no-any-return` have no ty equivalent: delete | U | ty docs not fetched | N | |

Counts (32): T 21 / S 4 / U 7. N 7 / R 20 / X 5.
Surviving ~1.9 KB: P9a line, S9 "cite the table", I2 noqa convention, E1 corrected to `gzkit.core.exceptions`, E4, Y1+Y2 (~1.1 KB).

## models.md (1,679 B) — KEEP-PARTIAL (or fold into pythonic.md)

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| M1 | BaseModel; no stdlib dataclasses | T | 0 dataclass imports; `--pydantic-models` passes (but late: explicit scope, full suite) | N |
| M2 | `ConfigDict(frozen=True, extra="forbid")` for immutable models | T | 427/435 forbid, 417/435 frozen; the audit checks only that `model_config` is present (`models.py:_has_model_config`) | N |
| M3 | `Field(...)` with description for required fields; `Field(None, ...)` for optional | T (mostly) | 945/1005 required Fields have `description=`; no witness (scorecard row 27a Promotable) | N |
| M4 | `str \| None`, `list[str]`, not Optional/List | T | 0 typing Optional/List imports | R (UP045/UP006) |
| M5 | Why table | U | — | X |
| M6 | Pattern example | T | — | R (restates M2/M3) |
| M7-M9 | Do Not list | T | — | R (dups) |
| M10 | Verify: all models extend BaseModel | T | — | R |
| M11 | **Verify: all models have model_config with at least `extra="forbid"`** | **S** | 8 direct BaseModel subclasses use `extra="allow"`: `core/models.py:350,375,400,411,427,459`, `event_evidence.py:133`; `knowledge/concept_frontmatter.py:13` "``extra="allow"`` — a DELIBERATE, ADR-mandated" | R |
| M12 | Verify: immutable snapshots frozen | T | — | R |

Counts (12): T 10 / S 1 / U 1. N 3 / R 8 / X 1. Surviving ~350 B: M1-M3, plus a carve-out for open-schema (frontmatter) models using `extra="allow"`.

## cross-platform.md (6,814 B) — KEEP-PARTIAL

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| X0 | Platforms co-equal | T | — | X |
| Q1 | Path joins, not string separators | T | PTH under ALL, package only (tests/features/scripts ignore PTH) | R (src) |
| Q2 | `.relative_to(root).as_posix()` | T | — | R (dup of A1) |
| Q3 | `encoding="utf-8"` | T | PLW1514 probe fired | R |
| Q4 | Temp files via context managers / no raw rmtree | U | Judgment (row 43); 7 rmtree sites in src | X |
| Q5 | Subprocess list form, `resolve_argv`, no `shell=True` / bare python | T | S602, S607 | R (dup of EX) |
| Q6 | `newline=""` for CSV | T | the only csv use reads a StringIO (`measurement.py:360`) | X |
| Q7 | Console UTF-8 in entrypoint | T | `cli/main.py:154 stream.reconfigure(encoding="utf-8", errors="backslashreplace")` | R (dup of U1) |
| A1 | Render relative paths via `.as_posix()` for JSON/ledger/ids | T | `tests/governance/test_path_separator_portability.py` exists | N (late witness) |
| U1 | Don't prefix `uv run gz` with PYTHONUTF8=1 | T | `cross_platform.py:79` | R (AGENTS.md Execution Rules, word for word) |
| U2 | Fresh `python -c` / helper scripts need explicit reconfigure | T | the guard lives only in cli/main.py | N |
| W1 | Wheel-shipped .md names no authoring-env path; the fail-closed and portable sets | T | `--wheel-path-literals` passes and sits in the gz check roster; its message carries `_REMEDIATION` | R |
| W2 | Remove the prose with the path; say the step is skipped/provisional | U | no observation can check it | N |
| W3 | "canonical rule home; validator is enforcement artifact" | T | — | X |
| EX | Spawn through `gzkit.executables` (`resolve_executable`/`resolve_argv`/`find_executable`, `standalone_source`) | T | `executables.py:28,48,70,87`; `tests/policy/test_executable_resolution.py`; `quality.py` run_command uses `resolve_argv` | N (S607 does not name gzkit.executables; the AST fence is late) |
| SR | Text-mode captures pass `errors="replace"`; never on bytes-mode | T | `quality.py` run_command Popen `text=True, encoding="utf-8", errors="replace"`; test exists | N (late) |
| CL | Code Review Checklist (8 items) | T | — | R (dups) |
| RP | Pointer to rationale doc | T | file exists | X |

Counts (18): T 16 / S 0 / U 2. N 5 / R 8 / X 5. Surviving ~2.4 KB: A1, U2, W2 (~250), EX (~1.2 KB, could be trimmed), SR (~800).

## cli.md (6,840 B) — KEEP-PARTIAL, and its glob is wrong

**Glob defect:** `paths: src/gzkit/commands/**`. But 598 of 607 `add_argument(` calls live in `src/gzkit/cli/parser_*.py`, where subcommands and flags are registered. So the shape rules do not load where shapes are made. `src/gzkit/cli/AGENTS.md` carries tool-skill-runbook-alignment, not cli.md.

Live tree walk (`cli/main.py:_build_parser`): 180 leaves, 34 groups, 34 depth-1 leaves, max depth 3; leaf+group `['mx']`; 15 verb collisions; singular/plural `['flag']`; 6 hyphenated roots; 73 leaves without `--json`; 91 leaves with help lines over 80 characters (COLUMNS=80); 0 leaves without Examples.

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| H0a | Spec pointer; read § Document status | T | `cli-standards-v3.md:14` | N |
| H0b | Heavy lane trigger | T | — | R (AGENTS.md Gate Covenant) |
| CS1 | Depth-1 leaf count may not increase | T | 34 now, 35 at the 2026-08-16 measurement; no witness (row 76; no `--cli-shape` scope) | N |
| CS2 | No subcommand shares a bare root verb | T (canon) | **code non-conformant: 15 collisions now vs 13 measured**; unwitnessed | N |
| CS3 | No singular+plural noun | T | 1 (`flag`/`flags`), unchanged | N |
| CS4 | No hyphenated noun-verb root | T | 6, unchanged | N |
| CS5 | Every leaf has `--json` or a waiver | T (canon) | 73/180 lack it; no waiver registry exists | N |
| CS6 | Node is a leaf or a group, never both | T | `mx` still both, unwaived | N |
| CS7 | Parser tree imports no handler-only deps | T | `tests/cli/test_help_path_imports.py` exists (late) | N |
| CS8 | Seven obligations in the authoring patch | T | — | R (dup of NS) |
| CS9 | Output via the formatter, never console.print | T (canon, UNMET) | spec: 1,230 sites | N |
| CP1 | Human-first | T | — | X |
| CP2 | `gz cli audit` exits 0; usage line agrees | T | "CLI audit" step in the gz check roster | R |
| CP3 | Help with examples | T | 0 leaves without Examples; `tests/test_epilog.py::test_epilogs_contain_examples_section` | R |
| CP4 | Validate early; fail fast; progress | U | — | X |
| EX1 | Exit code table 0/1/2/3 | T | `core/exceptions.py` docstring; the epilog every `--help` prints | R |
| EX2 | **"Use `sys.exit(code)`"** | **S** | spec § CLI Boundary Pattern: handler `-> int` ... `return _exit_code_for(e)`; `core/exceptions.py`: typed errors carry `exit_code`; commands census: 157 `sys.exit(`, 181 `raise SystemExit(`, 181 typed-error raises | R (once corrected; spec carries it) |
| EX2b | Document codes 2/3 in help text | T | the shared epilog adds them automatically (`gz cli audit --help` "Exit codes 0..3"); `test_epilogs_contain_exit_codes_section` | R |
| EX3 | Code 2 = usage or system/IO; every parse error exits 2 | T | `cli/parser.py:49-52` writes `BLOCKERS:` and raises `SystemExit(2)`; NC `cli-usage-error-exit-two` | R |
| EX4 | Never key a retry on exit 2 without the `BLOCKERS:` prefix | T | — | N (binds callers; only the spec also says it) |
| FL1 | Flag table | T | common flags in every leaf's help | R |
| FL2 | Verbosity mapping | T | NC `cli-log-levels-follow-spec` (`log_level_claims.py:21`) | R |
| HT1a | Help has description, usage, options, example | T | epilog tests | R |
| HT1b | Help lines <= 80 chars | T (canon) | **code non-conformant: 91/180 leaves**; no witness | N |
| AD1 | New flag/subcommand = Heavy; planned work = OBPI | T | — | R (AGENTS.md Gate Covenant + OBPI Acceptance) |
| AD2 | Lane is not route: a GHI repair goes direct even when it adds CLI surface | T | consistent with AGENTS.md Defect-fix routing | N (AGENTS.md's "changes a CLI ... is OBPI work" reads ambiguously without it) |
| AD3 | `gz cli audit` says nothing about lane | T | — | X |
| NF | New Flag steps 1-3 | T | manpage row checked by cli audit (GHI #350) | R |
| NS | Seven obligations list | T | `scanner.py:17-23 _SURFACE_NAMES`; `config/doc-coverage.json`; `_NO_SKILL_VERBS` | R (cli audit messages name the missing surface: "Missing {slug}.md", "'{search_str}' not found in {path.name}", "has no docstring") |
| NS8 | Purpose in ADR/brief or GHI; behave smoke; no ADR to discharge a GHI | T | — | R (AGENTS.md Defect-fix routing "Do not create an ADR or OBPI to discharge one"; Gate 4) |
| NS9 | Release notes never hand-written | T | — | R (changelog-release-notes.md) |
| NS10 | Deprecated verb inverts 4/5/7 | T | `scanner.py:426-430` | R |
| NS11 | Format change has consumers the list cannot enumerate | T | — | R (AGENTS.md DO IT RIGHT 1a) |

Counts (33): T 31 / S 1 / U 1. N 12 / R 18 / X 3. Surviving ~1.9 KB: H0a, CS1-CS7 + CS9, EX4, HT1b, AD2. Glob must add `src/gzkit/cli/**`.

## guardrail-feedback-prose.md (4,593 B) — KEEP-PARTIAL

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| G1 | Three-part recovery prose invariant | T | `.claude/hooks/stop-turn-feedback.py:175` "deterministic tier is red (ADR-0.0.70 turn-end feedback; " | N (AGENTS.md only describes validator messages; it does not instruct authors) |
| G2 | Buetow quote | U | — | X |
| G3 | Parts table with examples | T | — | N |
| SC1 | Scope: blocking hooks (exit 2), validate scopes (exit 3), ceremony gates, pre-commit/push; advisory SHOULD | T | `validate_cmd.py:713 raise SystemExit(3)` | N |
| F1 | First consumer stop-turn-feedback; REQ-0.0.70-03-02 | T | `tests/hooks/test_stop_turn_feedback.py:91 @covers("REQ-0.0.70-03-02")` | X (record) |
| F2 | New fail-closed surfaces add an equivalent assertion in their covering tests | T | precedent `CorePurityIsAnAllowlist` (scorecard 61a) | N |
| D1-D3 | Do Not: no bare non-zero, no why-less findings, no unrunnable next step | T | — | R (negations of G1/G3) |
| D4 | Do not inline sub-tool stderr past ~20 lines; precedent ADR-0.0.69 | U | "~20" appears nowhere else; ADR-0.0.69 says "(no stderr inlining)" (lines 246, 261) — the cited precedent allows less than the rule | N |
| PO1 | Advisory by design; no global scope planned; ADR-0.0.70 declined it | T | ADR-0.0.70:267 "REJECTED for now: a validator that grades prose quality is inferential, not computational; promoting the rule to a mechanical scope is a named future candidate once catch evidence exists." The rule's reclassify bar (caught-late evidence) matches | R (scorecard rows 61/61a) |
| PO2 | The per-surface channel is the real enforcement | T | — | R (dup F2) |
| PO3 | Reclassify only on named evidence; 2026-06-08 freeze | T | `advisory-rules-audit.md:718` FROZEN block | R |

Counts (13): T 11 / S 0 / U 2. N 5 / R 6 / X 2. Surviving ~1.5 KB.
Glob note: `.claude/hooks/**` are generated mirrors that must not be hand-edited. The glob misses `src/gzkit/validators/**` and `src/gzkit/commands/validate*.py`, where validate scopes also live.

## hexagonal-architecture.md (restored 0.3.1, 6,559 B, glob `**/*.py`) — KEEP-PARTIAL

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| HX0 | Intro: every external dependency is confined to an adapter behind a port | S | as R1a | R |
| CK1 | Cockburn §1.1 quote | U | the canon doc quotes the same; external source not fetched | X |
| SF1 | Strong form; rules 3/4/6 are the bar | T | — | X |
| R1a | **"Any third-party import (networkx, tree-sitter, future deps) is confined to an adapter module behind a port."** | **S** | runtime deps pyyaml, rich, jsonschema, jinja2 are imported directly: yaml in 21 src modules, rich in 65, jsonschema in 7, including `governance/brief_structure.py`, `governance/frontmatter_coherence.py`, `governance/invariants.py`, `ontology/okf.py` (yaml), which canon `docs/governance/hexagonal-architecture.md` element 1 counts as domain ("pure `governance/*` logic"). Only networkx (`ontology/graph.py`), tree-sitter (`ontology/source.py`) and lizard (`complexity/lizard_adapter.py`) are confined. Canon also says "In Python ports aren't declared" | R |
| R1b | Core imports stdlib + Pydantic only | T | `test_import_boundaries.py` `CORE_ALLOWED_THIRD_PARTY = frozenset({"pydantic"})`; 23 tests OK; message names this rule (line 228) | N (the witness is late) |
| R2 | Pydantic the one exception; STDLIB-FIRST interior | T | — | R (AGENTS.md STDLIB-FIRST "Pydantic as the one named departure") |
| R3 | Ports domain-typed; no nx/ast/tree-sitter node crosses; `reachable_from -> set[str]` | T | `ontology/graph.py:65 def reachable_from(self, node_id: str) -> set[str]`; `SourceParser` returns `SourceAnchor`/`CodeCouplingEdge` (`source.py:163`) | N (Judgment, row 64b) |
| R4 | Don't name the technology in core; Protocol not ABC; composition | T | 11 Protocol classes, 0 ABC classes in src (the only hits are a chore's fixture strings) | N |
| R5 | Encapsulate first; formalize the port at the second adapter | T | `SourceParser` Protocol has two adapters (ast, tree-sitter); networkx and lizard each have one adapter and no Protocol; canon: "A port ABC over a single/zero impl ... speculative" | N (more specific than AGENTS.md DO IT RIGHT 10) |
| R6 | Core testable without an adapter | T | follows from R1b | R |
| C1 | Cascade DDD -> HA -> BDD -> TDD | T | canon doc | X (BDD/TDD = Gate Covenant) |
| C2 | Narrative: "~50 top-level modules", core/models.py vs models/, triangle.py | **S** (number) | `ls src/gzkit/*.py \| wc -l` -> 128; models/ and triangle.py exist | X |
| R7 | `core/` stays; no domain/application/adapters/contexts dirs | T | none exist; ports/ and tests/fakes retired; cli-standards-v3 § Document status cites this rule as the forbidder | N (cli-standards-v3 still describes the retired tree) |
| R8 | Subsumption: no second, differently-typed model of the same objects | U | `OntologyNode`/`OntologyEdge` exist (`ontology/model.py:84,95`) | N |
| R9 | "Why is this here?": name the cascade stage | U | no surface records the answer | X (inert) |
| W1 | Why: tracer bullets (KEEL/ADR-0.31.0) | T | `airlock-in-hatch-2026-07-07.md:8` "KEEL (v0.31.0)" | X |
| DN1-4 | Do Not list | T | — | R (dups of R1b/R3/R5/R4) |
| V1 | **Verify: `uv run gz lint` / `uv run gz typecheck` check that core imports only stdlib+Pydantic** | **S** | ruff banned-api holds only `"__future__.annotations"` (pyproject:175-176); no banned-module-level config; ty does no import-boundary check. The real witness is `tests/policy/test_import_boundaries.py` ("verify hexagonal architecture boundaries are respected"); 0.4.0 § Witness and scorecard row 64 both name it | R |
| V2 | Verify bullets | T | — | R |
| REL1 | Canon link | T | — | X |
| REL2 | **`pythonic.md` — "idiomatic-code contract (Protocol/DI)"** | **S** | pythonic.md has no Protocol/DI content (grep for "Protocol\|injection" is empty) | X |
| REL3 | AGENTS.md STDLIB-FIRST | T | — | X |

Counts (25): T 17 / S 5 / U 3. N 6 / R 10 / X 9. Surviving ~1.9 KB: R1b scoped to `src/gzkit/core/`, R3, R4, R5, R7, R8, a Witness line naming `tests/policy/test_import_boundaries.py`, and the canon pointer. This is close to the 0.4.0 stub (3,180 B), which already dropped R1a's overclaim from its prose and replaced V1 with the right witness.
Glob: `**/*.py` loads on tests/features too. The clauses bind core plus the adapters in ontology/ and complexity/. 0.4.0's `core/** + pyproject.toml` leaves out ontology/ and complexity/, where R3 and R5 actually apply.

## mode-contract.md (1,956 B) — KEEP

| # | Clause | V | Evidence | U |
|---|---|---|---|---|
| MC0 | Every new control/module/skill/rule/surface carries the mode contract from its first commit | T | `docs/rnd/contractor-kit.md:2311` decision, operator verbatim | N |
| MC1 | Behavior at operational/hangar/drydock; the condition is on only when the marker is present, parses, is bound to an open `mx_session_opened` and is not exiting | T | `checkpoint.py hangar_demotes -> marker.condition(...).on`; docstring "An unreadable or unbound marker demotes nothing, and neither does the marker gz mx exit holds"; `events.py:1055`. Omits `GZKIT_MX_FULL_STRENGTH`, which also turns demotion off | N |
| MC2 | MEL entry fields | T | canon | N |
| MC3 | Built-in self-test with interval | T | canon | N |
| MC4 | `GATE5_INVARIANTS` never listed | T | `checkpoint.py:33` pins them to CRITICAL | N |
| MC5 | Level applied at the place of call, never by the declaration | T | `checkpoint.resolve` | N |
| MC6 | Until RO-13, state the contract in the design artifact's § Mode Contract | T | `.gzkit/templates/adr.md:39`, `obpi.md:59` carry § Mode Contract pointing at this rule | N (the template covers ADR/OBPI work; nothing covers a direct GHI repair) |
| MC7 | Advisory; RO-13 planned witness; record pointer | T | scorecard rows 99-99c | X |

Counts (8): T 8 / S 0 / U 0. N 7 / R 0 / X 1. Surviving ~1.4 KB.

## Scorecard rows (docs/governance/advisory-rules-audit.md) that score a STALE clause or carry stale facts

- **Row 20 (Modules <=600)**: "the canonical threshold table's `radon_raw_nloc` block band is 1031.9 with a *warn* band at 733.2 ... Two authorities disagreeing in both directions, neither of them running." Stale on three counts. The metric is now `lizard_file_nloc` (radon retired, GHI #1183, pyproject comment). The block band is 3130.24 (p99), with warn bands 716.5/1031.9. The table's band does run, as gz check "Module size" (`quality.py:2324`).
- **Row 26 (`ConfigDict(frozen=True, extra="forbid")`) is scored Mechanical**, but `audit_pydantic_models` checks only that `model_config` is present (`_has_model_config`), never frozen or extra. 8 models use `extra="allow"`. The verify clause M11 has no row.
- **Row 64 (hexagonal rule 1) is scored Mechanical** over a text that includes the stale universal sentence R1a. The witness covers only `src/gzkit/core/`.
- **Rows 22 and 27** cite "ruff UP007" for `Optional`. UP007 is `non-pep604-annotation-union`; Ruff flags `Optional[int]` with UP045 (probe output). The property holds under ALL, but the citation is wrong.
- The STALE clauses pythonic E1 (`core.errors`), cli EX2 (`sys.exit`), hexagonal V1 (Verify via lint/typecheck), hexagonal C2 ("~50") and hexagonal REL2 (Protocol/DI pointer) have no scorecard row.

## Incidental defects observed

- `gzkit/governance/trust_audits/models.py` `_DATACLASS_WAIVERS` holds `obpi_precomplete.py::CheckResult`, which is now `class CheckResult(BaseModel)` (line 47). The waiver is dead, and the stale-waiver check misses it because it tests only that the class exists.
- `docs/governance/hexagonal-architecture.md` repeats "~50 top-level modules" and lists "Test doubles are adapters too (`tests/fakes/`)", but `tests/fakes` does not exist (retired).
- `cli-standards-v3.md` § Document status: "§ Policy Tests — `tests/policy/` location | Superseded", yet `tests/policy/` is live (it holds `test_import_boundaries.py` and `test_executable_resolution.py`).
