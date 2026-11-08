# Research report — house-style candidate inventory

Landed verbatim, as the research subagent returned it on 2026-11-08 for the house-style R&D run. It
is a secondary record: its cells cite primary sources by path and line, and a cell it marks
*unverified* was not settled. It ranks and admits nothing.

---

Files read in full: `.gzkit/rules/` — AGENTS.md, adr-audit.md, agent-failure-modes.md, agents-md-map-doctrine.md, brief-heading-conventions.md, changelog-release-notes.md, chores.md, cli.md, complexity-doctrine.md, complexity-thresholds.json, complexity-thresholds.md, cross-platform.md, gate5-runbook-code-covenant.md, gh-cli.md, guardrail-feedback-prose.md, hexagonal-architecture.md, mode-contract.md, model-selection.md, models.md, mx-mode.md, pythonic.md, security-sensitivity.md, skill-authoring.md, skill-surface-sync.md, task-discovery.md, tests.md, token-block-discipline.md, tool-skill-runbook-alignment.md, weaponeering.md; root `AGENTS.md` (as loaded); `docs/governance/hexagonal-architecture.md`, `harbor-ro9-astral-toolchain.md`, `harbor-ro15-project-structure.md`, `harbor-ro9-uv-project-norms.md`; `docs/design/cli-standards-v3.md` (all of it); `src/gzkit/commands/init_cmd.py` (all of it); plus `src/gzkit/rules/_scaffolder.py` (lines 1–80) and `src/gzkit/templates/agents.md:89–107`, read to settle the delivery column.

**Abbreviations.** Rules (all under `.gzkit/rules/`): hexR = hexagonal-architecture.md, py = pythonic.md, mod = models.md, tst = tests.md, xp = cross-platform.md, cli = cli.md, cth = complexity-thresholds.md, cdoc = complexity-doctrine.md, gfp = guardrail-feedback-prose.md, g5 = gate5-runbook-code-covenant.md, ssync = skill-surface-sync.md. Docs: hexD = docs/governance/hexagonal-architecture.md, RO9 = harbor-ro9-astral-toolchain.md, UVN = harbor-ro9-uv-project-norms.md, RO15 = harbor-ro15-project-structure.md, CLI3 = docs/design/cli-standards-v3.md, AG = root AGENTS.md, init = init_cmd.py.

**What gz init delivers.**
- **R:** yes. `scaffold_core_rules` (init:1579) copies every wheel rule `.md`, plus `complexity-thresholds.json`, into the adopter's `.gzkit/rules/`, and `sync_all` mirrors them. The rule *text* arrives; gzkit's own `tests/` witnesses do not.
- **A:** likely. `src/gzkit/templates/agents.md:89–107` carries the STDLIB-FIRST text, but I did not verify the path that renders it into an adopter's AGENTS.md.
- **S:** yes, through the scaffold: `uv init`/`uv add` (init:471–518), the Ruff block (init:360–370), CI (init:384–407), pre-commit (init:646–667), the seeded baseline (init:859–871).

## Candidates

| # | Candidate | Statement (verbatim) | Source | Held today | gz init? |
|---|---|---|---|---|---|
| 1 | Hexagonal primary directive | "Ports & adapters is gzkit's **primary code-architecture directive**." | hexR:14 | `tests/policy/test_import_boundaries.py` (covers `core/` only, hexR:116) | R |
| 2 | Core = stdlib + Pydantic | "Core domain logic imports **stdlib + Pydantic ONLY**." | hexR:42 | same test | R |
| 3 | Domain-typed ports | "A port's methods accept/return domain types (Pydantic models, stdlib types) — NEVER a library's native type." | hexR:46–47 | rule text only | R |
| 4 | Protocol + composition | "Port shape via `typing.Protocol`, not `ABC`; inject adapters by composition, not inheritance." | hexR:51–52 | rule text only | R |
| 5 | Port at second adapter | "Encapsulate first; formalize the port when the SECOND adapter is real." | hexR:53 | rule text only | R |
| 6 | Parameter injection, no DI framework | "Plain constructor/parameter injection — **no DI framework**" | hexD:59 | rule text only | unverified (doc) |
| 7 | No DDD folder partitions | "`core/` stays; do NOT add `domain/`/`application/`/`adapters/`/`contexts/` folder partitions" | hexR:82–83 | rule text only | R |
| 8 | Subsumption into one typed model | "Prefer subsumption to a parallel model." | hexR:87 | rule text only | R |
| 9 | "Why is this here?" | "Every new module, object, and seam earns its place by imaging the *actual* shape, never a convenient one" | hexR:91–92 | rule text only | R |
| 10 | DDD→HA→BDD→TDD cascade | "Hexagonal is the **second stage** of gzkit's architectural spine, not a standalone rule." | hexR:65–66 | Gates 2/4 for the BDD/TDD legs; rest rule text | R |
| 11 | Stdlib first | "Use stdlib by default. A runtime dependency, new or existing, needs ADR or OBPI rationale naming the capability stdlib cannot supply" | AG:70 | ADR/OBPI review; RO-9 exception register | A |
| 12 | Five-year aging | "Five-year aging is the minimum signal for ecosystem trust." | templates/agents.md:100 | rule text only | A |
| 13 | Exception register, re-read per release | "the register is re-read at each new uv, Ruff, ty or Python release." | RO9:119–120 | `gz validate --astral-discipline` ("a non-Astral tool not in the exception register", RO9:132) | witness ships; register unverified |
| 14 | Pydantic the one exception | "**Pydantic is the one ratified exception** admitted to the inner world" | hexR:43 | import-boundary test | R |
| 15 | Pydantic, not dataclasses | "Use **Pydantic `BaseModel`** for all data models; no stdlib `dataclasses`." | mod:14 | rule text only (no witness named) | R |
| 16 | Frozen / extra=forbid | "Use `ConfigDict(frozen=True, extra=\"forbid\")` for immutable models." | mod:15 | rule text only | R |
| 17 | Field descriptions | "Use `Field(...)` with descriptions for required fields; `Field(None, ...)` for optional." | mod:16 | rule text only | R |
| 18 | Modern type syntax | "Use type hints (`str | None`, `list[str]`) — not `Optional`, `List`." | mod:17 | Ruff `UP` | R; S (`UP` selected) |
| 19 | TypedDict for shapes | "**Pydantic BaseModel for data** — TypedDict for shapes" | py:22 | rule text only | R |
| 20 | unittest, not pytest | "Use **stdlib `unittest`**; no pytest — no pytest syntax, fixtures, parametrization or plugins." | tst:16 | `forbid-pytest` hook (pinned CRITICAL, mx-mode.md:59); Ruff `PT` standing exception | R; hook unverified (scaffolded pre-commit declares only pre-push `gz check`, init:658–666) |
| 21 | argparse | "**CLI:** `argparse` over click/typer. Anchored by ADR-0.0.2." | templates/agents.md:106; AG:70 | ADR-0.0.2 | A |
| 22 | Maximal Astral | "this includes maximal use of astral tools themselves - MAX, EXTENSIVE, THOROUGH." | RO9:20 | `--astral-discipline` (default `gz check`) | S: dev group ruff+ty (init:358,498) |
| 23 | Strict uv project model | "I want strict https://docs.astral.sh/uv/concepts/projects/ compliance for gzkit and all of its adopters." | RO9:18 | `--astral-discipline` | S: `uv init --<type>` |
| 24 | Each fact declared once | "each fact is declared once, in the place Astral's tools read it, and every restatement is removed" | RO9:51–52 | `--astral-discipline` `version-restated` rule | S: floor read from metadata (init:410–433) |
| 25 | Python 3.14 floor, `uv run` | "Python 3.14+ with uv, ruff, ty; always `uv run` for Python commands." | AG:6 | `--astral-discipline` | S |
| 26 | Adopt new version idioms | "using a new version mandates updating to new features of the version" | RO9:21–22 | Ruff `UP`; tranche-6 records | partial (`UP`) |
| 27 | Deferred annotations | "New code writes annotations unquoted and without `from __future__ import annotations`" | py:63 | Ruff `TID251` banned-api; `--astral-discipline` | S (init:368–369) |
| 28 | Tools kept current | "also, keep all astral tools up to date" | RO9:28 | `gz-deps-upgrade` skill; witness unverified | unverified |
| 29 | Ruff ALL + every ty rule | "tranche 4 selects every current Ruff rule (`ALL`, preview included) and every ty rule, with curated per-rule exceptions only." | RO9:30–31 | `gz lint` against `data/ruff_baseline.json` | no: scaffold selects 9 families (init:366) |
| 30 | Package strict, tests curated | "`ALL` runs on the whole tree. Tests, features and scripts carry a recorded per-directory exception list" | RO9:187–188 | pyproject per-file-ignores | no |
| 31 | uv_build backend | "**Build backend, hatchling to `uv_build`:**" | RO9:26 | `--astral-discipline`; `--distribution` | S (via `uv init`) |
| 32 | `--locked` everywhere | "`--locked` vs `--frozen` in CI (RO-9: `--locked`)" | UVN:126 | `--astral-discipline` ("`--frozen` or a bare `uv sync` in automation") | S: CI `uv sync --locked` (init:402) |
| 33 | Dev deps in groups | "Development dependencies go in `[dependency-groups]`, never `[project]`" | UVN:80 | `--astral-discipline` | S (`uv add --dev`) |
| 34 | `uv run` vs `uvx` | "A tool the project needs runs with `uv run`; one-off tools with `uvx` or `uv run --with`" | UVN:99 | `--astral-discipline` | S (but see contradiction 13) |
| 35 | No pip / requirements.txt | "`pip`, `uv pip` or a `requirements*.txt` in the project" | RO9:131 | `--astral-discipline` | witness ships |
| 36 | uv floor, not exact pin | "the uv version is a floor, not an exact pin." | RO9:65 | rule text; RO15:50 | unverified |
| 37 | Supply chain | "`uv audit` in `gz check --full`, the malware check where new versions are installed" | RO9:155 | `Supply chain audit` step; `malware-check-off` rule | partial: CI `UV_MALWARE_CHECK` (init:394) |
| 38 | SHA-pinned actions | "SHA-pinned actions (RO-9: yes, as the guide's examples do)" | UVN:131 | unverified | partial: setup-uv by SHA; `checkout@v6` by tag (init:400–401) |
| 39 | `uv publish`, trusted publishing | "`uv publish` with trusted publishing and attestations in separate jobs" | RO9:153 | release workflow | no |
| 40 | Version via `uv version` | "`uv version --bump`, with `__init__.py` and the README badge derived from it" | RO9:110 | `gz validate --version-release` | no |
| 41 | Maximal project structure | "A `src/` package, a declared backend, commands in `[project.scripts]`, `py.typed` on a library, a separate `tests/`, no `sys.path` injection" | RO15:42 | none ("no tranche started", RO15:8) | partial: `uv init` src layout |
| 42 | Project types, `lib` default | "`gz init --project-type lib|package|app`, `lib` the default" | RO9:309 | `ProjectType` (init:354) | yes |
| 43 | Shrink-only baselines | "A violation not in the baseline fails; a row whose violation is gone must be removed." | RO9:134–135 | `data/waiver_ratchet_registry.json` shrink-ratchet | S: baseline seeded, "it only shrinks" (init:871) |
| 44 | Suppression is not a repair | "**A chore never discharges a finding by suppression.**" | chores.md:70 | `audit_chore_suppression`; `SHELL_OPERATORS_RE` | R |
| 45 | Reasoned noqa | "a genuine boundary catch carries `# noqa: BLE001` with a cited reason" | py:72 | rule text only | R |
| 46 | ty suppression syntax | "a bracketed `# type: ignore[...]` must name a `ty:`-prefixed code" | py:85 | `gz validate --type-ignores` | R |
| 47 | Full annotation, no Any | "**All code is fully type-annotated.** No `Any` unless genuinely unavoidable" | CLI3:987–988 | ty; Ruff `ANN` under ALL | no |
| 48 | Clarity | "**Clarity over cleverness** — explicit, readable, consistent code" | py:16 | rule text only | R |
| 49 | Separation of concerns | "**Separation of concerns** — isolate IO, transforms, QC, persistence" | py:17 | rule text only | R |
| 50 | EAFP/LBYL | "**EAFP for IO, LBYL for contracts** — clear error boundaries" | py:19 | rule text only | R |
| 51 | Context managers | "**Context managers** — for files, DBs, sessions, progress phases" | py:20 | rule text only | R |
| 52 | No mutable defaults | "**No mutable defaults** — use `None` + factory" | py:21 | unverified (Ruff `B` under ALL) | R; S (`B`) |
| 53 | No implicit globals | "**No implicit globals** — explicit configuration and state" | py:25 | rule text only | R |
| 54 | Top-level imports only | "**No lazy imports** unless required for optional dependencies or cycle avoidance." | py:62 | Ruff `I`, `PLC0415` + baseline | R; S (`I`) |
| 55 | Typed errors, no broad except | "Catch specific exceptions, translate to the `GzkitError` hierarchy in `gzkit.core.exceptions`." | py:67 | Ruff `BLE001` | R |
| 56 | Typed exception per raise | "each package site gets a typed exception class that subclasses the type it raises today" | RO9:236 | Ruff `TRY003` + baseline | partial (`TRY`) |
| 57 | Keyword-only extras | "the 94 `PLR0917` sites take their extra parameters by keyword" | RO9:238 | Ruff `PLR0917` | no |
| 58 | Google docstrings | "the Google convention that a one-line summary needs no `Returns:` section" | RO9:234 | Ruff pydoclint `DOC201` | no |
| 59 | Size limits | "**Limits:** Functions <=50 lines | Modules <=600 lines | Classes <=300 lines" | py:29 | `gz validate --class-size` (classes); "Module size" step (the table's band) | R |
| 60 | One threshold table | "gzkit publishes one canonical threshold table" | cth:36 | `gz validate --complexity-thresholds` (shape only) | R (+ JSON) |
| 61 | Three-value triggers | "The trigger-semantic vocabulary is fixed at three values (`block` / `warn` / `advise`)" | cth:39–40 | schema | R |
| 62 | Cyclomatic / cognitive ceilings | "each function, module mean and overall mean CC <=20" | py:46 | `gz validate --complexity-ceiling`; Ruff `C901` | partial: cognitive "opt-in for adopters" (RO9:227) |
| 63 | Exemplar-corpus calibration | "gzkit calibrates complexity decisions against an empirically-grounded corpus of well-architected Python projects" | cdoc:19–20 | `gz validate --complexity-doctrine-links` | R |
| 64 | Platforms co-equal | "**Platforms:** Windows, macOS, Linux — co-equal." | xp:16 | CI matrix | R |
| 65 | pathlib, no separators | "`Path(\"dir\") / \"file\"`" vs avoid "`\"dir/file\"`" | xp:22 | review checklist only | R |
| 66 | `.as_posix()` | "Always use `.as_posix()` when the result is compared against forward-slash literals" | xp:32 | `tests/governance/test_path_separator_portability.py` | R |
| 67 | Explicit UTF-8 | "All file I/O specifies `encoding=\"utf-8\"`" | xp:85 | review checklist only | R |
| 68 | Temp cleanup | "Cleanup through `tempfile.TemporaryDirectory()`; never raw `shutil.rmtree()` in tearDown." | tst:21 | rule text only | R |
| 69 | Subprocess list form | "No `shell=True` in subprocess" | xp:88 | Ruff `S` | R |
| 70 | `errors="replace"` | "Every text-mode subprocess capture that decodes sub-process stdout/stderr MUST pass `errors=\"replace\"`." | xp:80 | `tests/governance/test_subprocess_errors_replace.py` | R |
| 71 | Executable resolution | "The shipped package never hands a bare tool name to the operating system" | xp:76 | `tests/policy/test_executable_resolution.py`; Ruff `S607` | R |
| 72 | UTF-8 console at entrypoint | "The CLI entrypoint handles UTF-8 at startup." | xp:36 | `gz validate --utf8-prefix` | R |
| 73 | Delivered path literals | "Wheel-delivered instruction text names no path only its authoring environment can resolve." | xp:40 | `gz validate --wheel-path-literals` | R |
| 74 | CSV newline | "`newline=\"\"` for CSV" | xp:27 | rule text only | R |
| 75 | `<group> <command>` shape | "The count of depth-1 leaf commands may not increase" | cli:20 | unverified (advisory-rules-audit row) | R |
| 76 | `--json` on every leaf | "Every leaf command declares --json or carries a waiver with rationale." | cli:24 | unverified; CLI3:36 says "Live, UNMET" | R |
| 77 | Formatter chokepoint, stdout/stderr | "User-facing output passes through the formatter, never console.print directly" | cli:28; CLI3:552–553 | none; CLI3:38 "Live, UNMET" | R |
| 78 | Four exit codes | "**0** Success / **1** User/Config / **2** Usage or System/IO / **3** Policy Breach" (table rows) | cli:41–46 | `src/gzkit/cli/helpers/exit_codes.py` | R |
| 79 | BLOCKERS parse errors | "every parse error exits 2 — `StableArgumentParser.error`, attested REQ-0.0.4-02-03." | cli:50 | attested REQ | R |
| 80 | Help-text contract | "Every command responds to `-h`/`--help` (exit 0) with a one-or-two-sentence description, a usage line, every option, at least one example" | cli:69 | `gz cli audit` | R |
| 81 | Light help path | "Building the gz parser tree may not import handler-only dependencies" | cli:26 | `tests/cli/test_help_path_imports.py` | R |
| 82 | Seven per-subcommand obligations | "Seven obligations fire for a new verb, each mechanically checked" | cli:83 | doc_coverage scanner; `audit_skill_alignment` | R |
| 83 | Explicit registration | "§ Command Structure — Explicit Registration — **Live, met**" | CLI3:31 | set_defaults count (CLI3:31) | no |
| 84 | stdlib logging, stderr, snake_case | "Log messages use `snake_case` event names" / "All log output goes to stderr" | CLI3:719–720 | `NC:cli-log-levels-follow-spec` | no |
| 85 | Verbosity map | "the default logs warnings and errors, `--quiet` errors only, `--verbose` INFO, `--debug` DEBUG, all to stderr" | cli:65 | `NC:cli-log-levels-follow-spec` | R |
| 86 | JSON-everywhere config | "gzkit is JSON-everywhere (`.gzkit/manifest.json`, schemas, ledger)" | CLI3:44 | rule text only | yes: `.gzkit.json`, manifest |
| 87 | Config single load point | "Config is loaded once at the CLI boundary and injected into core services." | CLI3:490–491 | unverified (not in status table) | no |
| 88 | Values in JSON/code, not Markdown | "A value written in a Markdown doc is ILLUSTRATIVE, never authoritative." | AG:207 | per-instance validators | unverified |
| 89 | rich for human output | "**rich** — human-readable terminal output" | CLI3:84 | none | no |
| 90 | Models data-only | "Business logic belongs in services, not in model methods." | CLI3:838–839 | rule text only | no |
| 91 | Policy tests as AST scans | "They scan source code via `ast` parsing or regex. They import nothing from `src/`" | CLI3:862–863 | `tests/governance/`, `trust_audits/` | no |
| 92 | Naming conventions | "Modules: `snake_case.py` / Classes: `PascalCase` / Constants: `UPPER_SNAKE_CASE`" | CLI3:1051–1053 | Ruff `N` under ALL | no (`N` not in scaffold) |
| 93 | Binary vs wheel | "Choose the distribution model based on the audience." | CLI3:106 | release pyinstaller (RO9:85) | no |
| 94 | Mode contract | "Every new control, module, skill, rule or surface carries the two-way mode contract from its first commit" | AGENTS.md(rules):38 | "Advisory: no mechanical witness yet" | R |
| 95 | Three-part guardrail prose | "Every fail-closed hook and validator emits agent-actionable three-part recovery prose" | gfp:18 | per-surface tests (`tests/hooks/test_stop_turn_feedback.py`) | R |
| 96 | Tests assert semantics | "Assertions derive from the REQ or skill contract, not from a run of the code." | tst:50 | `gz test-shape` (advisory) | R |
| 97 | TDD per increment | "one test → one observed RED → minimum code to GREEN → next increment." | tst:58 | `gz arb red` | R |
| 98 | Deterministic, offline tests | "Table-driven tests with deterministic seeds; no network or external services" | tst:17 | rule text only | R |
| 99 | Smoke ≤60s | "**Smoke/BVT <=60s**" | tst:18 | `gz smoke` exit 3 | R |
| 100 | Coverage floor | "Coverage >=40.00%" | tst:25 | `coverage-40pct` chore | R |
| 101 | Git fixture isolation | "every `git` a test spawns passes `env=_isolated_git_env()`" | tst:20 | `TestEveryGitSpawnIsInsideTheBoundary` | R |
| 102 | Unit-test contract | "Subprocess boundaries mocked where a fake suffices … deterministic; < 200ms; `tempfile` DBs" | tst:82 | rule text only | R |
| 103 | Mutation-sweep integrity | "A failing mutant run is NOT a kill." | tst:62 | `run_mutation_sweep` | R |
| 104 | Verifier exit-code integrity | "A verifier's truth is its own exit code, never a downstream filter's." | tst:64 | `verifier-pipe-gate.py` hook | R; hook unverified |
| 105 | Simplicity first | "Simplicity first: minimum code that solves the problem, nothing speculative, no abstraction for single-use code." | AG:53 | rule text only | unverified |
| 106 | Surgical changes | "Touch only what you must. Don't improve adjacent code. Match existing style." | AG:55 | rule text only | unverified |
| 107 | Docs in the same patch | "Documentation is a first-class deliverable and must track behavior changes in the same patch set." | g5:15 | `gz cli audit`; `mkdocs build --strict` | R |
| 108 | Canonical source, generated mirrors | "`.gzkit/skills/` and `.gzkit/rules/` are canonical; every other copy is generated." | ssync:60 | `gz validate --surfaces` | R |

## Borderline

| Item | Source | Why borderline |
|---|---|---|
| `Task:` trailer on src/tests commits | task-discovery.md:18 | Commit process, but it binds every code change |
| Work on main, no branches | AG:198 | VCS workflow, not code shape |
| Semver ordering of identifiers | AG:165 | A naming rule for governance IDs, not code |
| Every version bump is a release | AG:161 | Release process that touches pyproject |
| Skill-authoring parsimony | skill-authoring.md:22–29 | Agent surfaces, not product code |
| Model class names, never versioned IDs | model-selection.md:55 | Agent configuration |
| Good Docs changelog templates | changelog-release-notes.md:15–19 | Docs-as-code for release artifacts, not code |
| REQ kinds; constraints sortie before red | tst:91; weaponeering.md:20 | Process, but it orders design before tests |
| Layer 1/2/3 state; append-only ledger | AG § Architectural Boundaries 6 | A data-architecture principle carried as governance |
| Version markers on every edit; delete-on-retire | ssync:61,85 | Surface-maintenance hygiene |
| LSP via ty for symbol lookups | CLAUDE.md:15 | Agent tooling |
| ARB receipts as evidence | g5:33 | Gate process |
| Floor-pinned guards (LEVEL vs NAME) | mx-mode.md:52–57 | Shapes how guards are coded, but is MX governance |
| Brief H3 evidence headings | brief-heading-conventions.md:14 | Document structure |

## Contradictions

1. **Status of hexagonal.** hexD:3 says "**Influence, not wholesale adoption.**" and hexD:248–249 says "This is a conceptual borrowing, not a code-organization rule." hexR:14 says "Ports & adapters is gzkit's **primary code-architecture directive**."
2. **Test fakes.** hexD:58 says "**Test doubles are adapters too** (`tests/fakes/`)." hexD:95 says that layer "was retired", and CLI3:42 lists "§ Testing — Test Fakes (`tests/fakes/`) | **RETIRED**".
3. **The one exception.** AG:70 says "Pydantic as the one named departure". CLI3:81–84 says "The approved scaffold dependencies are: **pydantic** … **rich**". RO9:302 registers "jinja2, jsonschema, pyyaml, rich" with reasons. (hexR:43 scopes its exception to "the inner world", which narrows the conflict.)
4. **Dataclasses.** mod:14 says "no stdlib `dataclasses`". CLI3:494–495 says "deserialized into a typed structure (Pydantic model or dataclass)".
5. **Python floor and target.** AG:6 says "Python 3.14+". CLI3:86 says "Python 3.13+ standard library", CLI3:1017 says `requires-python = ">=3.13"`, and CLI3:1034 says `target-version = "py313"`. The last also breaks the declare-once rule at RO9:51.
6. **Build backend.** RO9:26 rules "hatchling to `uv_build`". CLI3:1026–1028 still shows `requires = ["hatchling"]`, while CLI3:34 marks "§ Build | **Live, met**".
7. **Ruff selection.** RO9:30–31 says "selects every current Ruff rule (`ALL`, preview included)", and RO9:18 asks for strict compliance "for gzkit and all of its adopters". The scaffold writes only `select = ["E", "F", "I", "UP", "B", "SIM", "TRY", "RUF", "TID"]` (init:366), and CLI3:1037 shows yet another list.
8. **Size thresholds.** py:29 says "Functions <=50 lines | Modules <=600 lines". cth:43–44 says "A new threshold authority appearing anywhere else is doctrine drift by another name." py:31–57 flags this itself as "Unreconciled".
9. **Version bump.** AG:161 says "bump `pyproject.toml`, `__init__.py` and the README badge together". RO9:110 says "`uv version --bump`, with `__init__.py` and the README badge derived from it".
10. **Who approves a dependency.** AG:70 says "needs ADR or OBPI rationale". templates/agents.md:98 says "**Departures are foundation-attested.**", while AG § Gate Covenant says `foundation` is "CLOSED to new authoring here". CLI3:87–88 says "requires explicit human approval". CLI3:98–99 sets the domain-dependency test as "not 'can we reimplement it with stdlib?'", which reverses stdlib-first for domain dependencies.
11. **Install route.** CLI3:113 says "(`uv sync`, `pip install`)". RO9:157 says "adopter docs give `uv tool install` and `uvx` only", and RO9:131 lists `pip` as a violation.
12. **Policy-test location.** CLI3:43 says the practice "lives in `tests/governance/` + `src/gzkit/governance/trust_audits/`" and marks `tests/policy/` as Superseded. hexR:113 and xp:76 name their witnesses at `tests/policy/test_import_boundaries.py` and `tests/policy/test_executable_resolution.py`.
13. **The scaffold against its own witness.** RO9:129 forbids "`--frozen` or a bare `uv sync` in automation", but init:914 runs a bare `[resolve_executable("uv"), "sync"]` and init:498 runs `uv add --dev --frozen`. UVN:99 sends one-off tools to `uvx` and project tools to `uv run`, yet the scaffolded CI runs `uvx --from py-gzkit gz check` (init:406). Whether the witness treats `gz init` as "automation" is unverified.
