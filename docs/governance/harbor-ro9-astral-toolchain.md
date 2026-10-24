<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-9 specification — the toolchain realigned to Astral's project discipline

**2026-10-19. Status: tranche 1 landed (the witness, uv and the Astral tools current, Python declared once at 3.14); tranche 2 landed 2026-10-21 (lock discipline: `--locked` everywhere, docs from a locked group, every project tool through `uv run`); tranche 3 landed 2026-10-22 (`uv_build`, `uv publish` with attestations from a credential-only job, `uv version` writing the version); tranches 4 to 7 open.** Operator: **g0**. Repair order RO-9 of the
[harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), mandate item 7: gzkit
and every project `gz init` scaffolds follow [uv's project model](https://docs.astral.sh/uv/concepts/projects/)
strictly and use Astral's tools to the maximum, on Python 3.14, with stdlib first and curated
exceptions only. It absorbs GHI #1184 (the 3.14 assessment) and GHI #1183 (the complexity tools).

## Rulings

Operator, verbatim, 2026-10-19, each recorded as an insight (scopes `toolchain-alignment` and `drydock-ro9`):

- *"I want strict https://docs.astral.sh/uv/concepts/projects/ compliance for gzkit and all of its
  adopters."*; *"I want tight compliance - even gzkit itself might need to change."*
- *"this includes maximal use of astral tools themselves - MAX, EXTENSIVE, THOROUGH."*
- *"using a new version mandates updating to new features of the version - max stdlib with select ad
  curated exceptions."*; *"i want to keep up with the idioms of new releases - newer statements replace
  the older rule."*
- On the Python version restated in eleven places: *"this is insane slop"*, *"this is proof positive
  that we need the astral project discipline"*.
- **Floor:** *"1. 3.14"*. **Preview features:** *"2. yes, MAXX astral... MAXX"*. **Build backend,
  hatchling to `uv_build`:** *"3. yes, MAXX astral... MAXX"*. **Route:** *"4. A we are in dry dock"*.
- **Currency:** *"also, keep all astral tools up to date"*; *"all ruff rules up to date (ty too)"*. uv,
  Ruff, ty and setup-uv move to their current releases in tranche 1 and at each release after; tranche 4
  selects every current Ruff rule (`ALL`, preview included) and every ty rule, with curated per-rule
  exceptions only.
- **Scaffold:** *"even `gz init` should look carefully at `uv init`"*. Tranche 7 reads `uv init`'s whole
  contract (application, packaged application, library, `--bare`, the files each writes) and builds
  `gz init` on it, writing only what `uv init` does not.

uv's own rules, read end to end, are recorded in [`harbor-ro9-uv-project-norms.md`](harbor-ro9-uv-project-norms.md).

**What the rulings supersede.** Newer statements replace older rules (the operator's ruling above), so:

- GHI #1184's *"Do not modernize syntax merely because it exists"* and its instruction to preserve
  3.13 import and parse behaviour are superseded: the floor is 3.14, and adopting a version means
  adopting its idioms, with each exception recorded.
- ADR-0.0.27's radon dependency is superseded by GHI #1183's 2026-10-09 selection (Ruff, complexipy and
  Lizard; its complexipy leg reversed 2026-10-23, § Amended for tranche 4). The attested ADR-0.0.27/0.0.28/0.0.29 REQs are repaired at the surface, never deleted
  (`docs/governance/attested-req-subject-retirement.md`).
- `AGENTS.md` § STDLIB-FIRST stands and tightens: a third-party runtime dependency is a curated
  exception with a recorded reason, re-read against each new stdlib.

## The discipline

One rule carries the rest: **each fact is declared once, in the place Astral's tools read it, and
every restatement is removed rather than validated against its copies.** The measured instance:

| Fact | Its one home | Restatements today |
|---|---|---|
| Python floor | `pyproject.toml` `requires-python` (Ruff and ty infer their target from it) | `[tool.ruff] target-version = "py313"`, `ty.toml` `python-version = "3.13"`, the `gz init` scaffold's Ruff target |
| Interpreter | `.python-version`, written by `uv python pin` (`uv python install` with no argument reads it) | four workflows' `setup-python` `"3.13.16"`, `release.yml` `uv python install 3.13.16` twice, `.readthedocs.yaml` `python: "3.13"`, the gz-deps-upgrade skill's `uv python install 3.13` |
| uv version | `[tool.uv] required-version` (setup-uv reads it) | none |
| Dependencies | `pyproject.toml` tables and `uv.lock` | `requirements-docs.txt` (three packages, mkdocstrings, mkdocstrings-python and griffe, exist only there) |
| Tool versions | the locked `dev` group, run by `uv run` | unpinned `uvx` in chores and `gz arb`; bare `ruff` and `coverage` from `PATH` |

`gz validate --python-version-pins` exists to keep the interpreter copies in step. Under the
discipline its subject is gone: it becomes "no restatement exists" inside the RO-9 witness, then retires.

## The population, measured 2026-10-19

Read from uv's documentation source end to end (uv 0.13.x), from every tracked file of the tree, and
from Astral's tool catalogue. The figures are illustrative; tranche 1's witness replaces them with its
own baseline.

**gzkit against uv's project model.**

| # | Today | The discipline (uv's wording) |
|---|---|---|
| 1 | Every workflow runs `uv sync --frozen`; nothing checks lock freshness | `uv sync --locked` ("If the lockfile is not up-to-date, uv will raise an error") |
| 2 | Docs tooling outside the lock: `requirements-docs.txt`, `uv pip install -r` in `docs.yml`, `pip install -r` on Read the Docs | "we recommend against using both a `uv.lock` and a `requirements.txt` file"; "It is _not_ recommended to modify the project environment manually, e.g., with `uv pip install`" |
| 3 | `mkdocs` is a published `docs` extra | development dependencies are "local-only" and belong in `[dependency-groups]` |
| 4 | `release.yml` runs a bare `uv sync` and `uv add --dev pyinstaller`, editing `pyproject.toml` inside CI | `uv sync --locked`; pyinstaller is already locked |
| 5 | `actions/setup-python` beside setup-uv in four workflows | uv provides the interpreter |
| 6 | hatchling | `uv_build`, uv's default backend (operator ruling 3) |
| 7 | `pypa/gh-action-pypi-publish` and `twine check` | `uv publish` with trusted publishing, separate build and publish jobs |
| 8 | uv pinned `==0.12.23`, setup-uv v10.2.0, Ruff 0.16.10 | current uv (the docs describe 0.13.x), setup-uv v10.3.0, Ruff 0.17.x; lockfiles may break across uv minors, so uv moves first |
| 9 | Project tools through unpinned `uvx` (chores, `gz arb ty`) or bare `PATH` (`gz arb ruff`, `gz arb coverage`) | `uv run` for a tool that needs the project; `uvx` for one-off tools only |
| 10 | `bandit`, `detect-secrets`, `pygount` and `vulture` declared and never invoked | removed |
| 11 | No `exclude-newer` cooldown, `required-environments`, build constraints, `uv audit` or malware check | adopted (operator ruling 2: preview allowed) |

**What `gz init` hands an adopter.** `src/gzkit/commands/init_cmd.py` writes `pyproject.toml` by hand:
Ruff under `[project.optional-dependencies] dev` (a published extra uv does not sync by default),
hatchling, Ruff's `py313` restated, no `[dependency-groups]`, no ty, no `[tool.uv]`, no
`.python-version`, no lock handling, a bare `uv sync`, and no CI template. Adopter docs still offer
`pip install py-gzkit`. Nothing checks an adopter project afterwards.

**Astral replacements and curated exceptions.**

| Replace | With |
|---|---|
| xenon, radon | Ruff C901 and Lizard, with cognitive complexity scored by gzkit over `ast` (GHI #1183; complexipy, selected for it, retired 2026-10-23) |
| interrogate | Ruff `D1xx` (already selected) and the preview `DOC` rules; the coverage percentage is retired, and its two thresholds (50 in pre-commit, 85 in the chore) disagree today |
| bandit | Ruff `S` |
| the `grep` TODO hook | Ruff `FIX` and `TD` |
| whitespace hooks | Ruff `W` for Python files |
| hatchling, `twine`, the PyPI action | `uv_build`, `uv build --no-sources`, `uv publish` |
| hand-written version bumps | `uv version --bump`, with `__init__.py` and the README badge derived from it |
| the empty security slot | `uv audit` (OSV) and the malware check |
| hand-rolled import-boundary tests | kept: the AST allowlist test stays, and `ruff analyze graph` moves to the transitive direction check (GHI #1267; § Amended for tranche 4, 2026-10-24) |
| no `[tool.ty]` | a `[tool.ty]` table, with the warn-level rules raised |
| the hand-written scaffold | `uv init` and `uv add` inside `gz init`, where they produce the same project |

Curated exceptions, where Astral ships nothing: `unittest` and unittest-parallel (doctrine is unittest
only), coverage, behave, mkdocs, the pre-commit framework (Astral ships hooks for it, not a runner),
gitleaks, pyinstaller, Lizard, cohesion, networkx and tree-sitter. Each keeps a one-line reason in the
exception register tranche 1 lands, and the register is re-read at each new uv, Ruff, ty or Python
release.

## The witness

Tranche 1 lands `gz validate --astral-discipline`, one scope in the default `gz check`, shaped like
RO-2's `--id-seam`:

- **The rules.** One machine-checked rule per row of the population tables: a Python version stated
  outside its two homes; `--frozen` or a bare `uv sync` in automation; `pip`, `uv pip` or a
  `requirements*.txt` in the project; `setup-python`; dev tooling in `optional-dependencies`; a project
  tool run by `uvx` or from `PATH`; a dependency declared and never invoked; a non-Astral tool not in
  the exception register; and the scaffold's output failing any of these.
- **The baseline.** `data/astral_discipline_baseline.json` lists today's violations keyed by rule and
  file, never by line, registered as a `shrink-ratchet` in `data/waiver_ratchet_registry.json`. A
  violation not in the baseline fails; a row whose violation is gone must be removed.
- **Adopters.** The same rules run against a project `gz init` scaffolds in a temporary directory, so the
  scaffold cannot regress, and the scope ships in the wheel so an adopter's own `gz check` runs it.
- **Close condition.** The baseline is empty; the exception register names every non-Astral tool with
  its reason; `gz check --full` passes on Python 3.14 on every CI platform.

## Tranches

Each tranche is one act under § Records of the contract: one commit with a `Task:` trailer
(`TASK-ro9-<slug>`), a failing test observed first, `gz arb red --commit` with its verdict, a
passage-log row with before and after counts read from the baseline, and every reader it touches moved
in the same commit. Tranche 1 lands first; 2 to 7 follow in order, because they share the baseline and
`pyproject.toml`.

| # | Scope | Done when |
|---|---|---|
| 1 | The witness and its baseline; the exception register; uv to current (`required-version`, setup-uv, a regenerated lock); the Python version declared once at 3.14 (`uv python pin 3.14`, `requires-python = ">=3.14"`, the classifier; Ruff's and ty's restatements deleted; CI, Read the Docs and release taking Python from uv); `--python-version-pins` folded into the witness | The baseline is seeded; no version restatement row remains; `gz check --full` passes on 3.14 locally and in CI |
| 2 | Lock discipline: `--locked` everywhere; a `docs` group replacing `requirements-docs.txt`, `uv pip` and Read the Docs' `pip`; the `docs` extra retired; `release.yml` repaired; every project tool through `uv run`; unused dev dependencies removed; the uv-pre-commit `uv-lock` hook | No lock or tool-provenance row remains |
| 3 | Build and publish: `uv_build` with `--distribution` and `--wheel-path-literals` ported to its configuration in the same commit; `uv build --no-sources`; `uv publish` with trusted publishing and attestations in separate jobs; `uv version --bump` driving the version surfaces | `gz validate --distribution` passes on a `uv_build` wheel; a dry-run publish succeeds |
| 4 | Lint and type to the maximum: the Ruff selection widened (`S`, `C901`, `FIX`, `TD`, `W`, `TID251`, preview `DOC`, the `PLR09xx` family), xenon and radon retired for Ruff, complexipy and Lizard (GHI #1183, with the C/C/C contract re-derived and changed verdicts reviewed; complexipy then retired for gzkit's own cognitive score, 2026-10-23), interrogate retired, `[tool.ty]` landed with the warn rules raised, the PEP 563 import removed and `TID251` refusing it with no baseline row (the graph moved to GHI #1267, 2026-10-24) | No lint or type row remains; GHI #1183 closes |
| 5 | Supply chain: `uv audit` in `gz check`, the malware check, `exclude-newer`, `required-environments` for the CI matrix, build constraints, a CycloneDX export at release | The security slot is filled; the release carries an SBOM |
| 6 | Python 3.14 idioms and stdlib first: Ruff's `UP` rules at the 3.14 target, deferred annotations and `annotationlib` where they apply, the 3.14 stdlib APIs over third-party or hand-rolled code (GHI #1184's candidates, adopted unless an exception is recorded), and every runtime dependency re-read against the stdlib | GHI #1184 closes with an adopt or exception record per candidate; every runtime dependency is in the register |
| 7 | Adopters: `gz init` builds the project through `uv init` and `uv add` (a `dev` group with Ruff and ty, `.python-version`, `uv.lock`, the 3.14 floor, `uv_build`), ships a CI workflow template on setup-uv with `--locked`, and runs the witness on the result; adopter docs give `uv tool install` and `uvx` only | A fresh `gz init` project passes `gz validate --astral-discipline` and `uv lock --check`; the baseline is empty, and RO-9 closes |

**Boundaries.** RO-9 changes no governance doctrine beyond the rulings above, populates no catalog
(that is RO-3), and leaves the test runner on `unittest`. A tranche that would change an attested REQ's
subject repairs it at the surface and records the amendment. The witness checks the tree and the
scaffold, never the operator's machine.

**Read at tranche 1 (2026-10-19).**

- Every runtime and dev dependency locks and installs on Python 3.14.8, and every compiled dependency
  (tree-sitter, pydantic-core, pyyaml, rpds-py, markupsafe, coverage, charset-normalizer) ships 3.14
  wheels for Windows, Linux and macOS.
- At the 3.14 target Ruff's formatter writes PEP 758 (`except A, B:` without parentheses), reformatting
  158 files; Ruff 0.17 at the old 3.13 target changes nothing, so the reformat is the floor's idiom, not
  the upgrade's. ty 0.0.89 deprecates `-> Iterator[T]` on `@contextmanager`; 21 sites move to
  `Generator[T]`.
- Every current Ruff rule (`ALL`, preview, the 3.14 target) reports 52,043 findings across 161 rules;
  PT009 (22,528) and COM812 (5,504) conflict with the unittest-only doctrine and the formatter and are
  curated exceptions for tranche 4.
- `--python-version-pins` retires: the witness's `version-restated` rule replaces it, and two checks of one
  fact are the duplication RO-9 removes.
- A tree with no `data/astral_discipline_baseline.json` (an adopter before tranche 7) has its violations
  announced as advisories, not failed; tranche 7 gives adopters their baseline and makes it fail closed.

**Ruled for tranche 4 (2026-10-22).** Measured on Ruff 0.17.1, ty 0.0.89, Lizard and complexipy 8.1.0,
then ruled by the operator by selection:

- *"PT + COM812 + CPY001 (Rec.)"*: the `PT` family (24,354 findings, pytest idioms; unittest is doctrine),
  `COM812` (5,814, conflicts with Ruff's formatter) and `CPY001` (1,484, no copyright-header doctrine
  exists) are standing exceptions, each recorded with its reason. A copyright header is a separate ruling.
- *"Package-strict, tests curated (Rec.)"*: `ALL` runs on the whole tree. Tests, features and scripts
  carry a recorded per-directory exception list (docstrings, annotations, private access, `assert`,
  no-self-use, unused arguments). This extends the 2026-08 package-only rulings for `D`, `BLE` and `PTH`.
- *"15 with shrink-ratchet (Rec.)"*: cyclomatic C/C/C moves to Ruff `C901` and Lizard at 20/20/20
  (maximum, each module's mean, function-weighted overall mean), with no changed verdict on `src/gzkit`:
  xenon, C901 at 20 and Lizard all pass. Lizard's maximum is 20, its worst module mean 18.0 and its overall
  mean 4.49 over 5,212 functions. complexipy's cognitive ceiling of 15 is new, and 307 functions exceed it
  (58 over 25, maximum 50). They enter a keyed baseline registered as a shrink-ratchet, and new or changed
  code is held to 15.
- *"Map or retire each (Rec.)"*: `raw_lloc`, the maintainability index and the three Halstead metrics
  retire, and `radon_cc` gives way to Lizard's `lizard_ccn`. Each retirement is recorded at the surface
  against the ADR-0.0.27/0.0.28/0.0.29 REQs it touches, and no dependency is added. Module size was
  drafted as "maps to Lizard's `nloc`", which is per function where `raw_nloc` is per file; re-ruled
  *"Lizard file NLOC, re-distilled (Rec.)"*: a per-file `lizard_file_nloc`, its bands re-derived by
  `gz complexity distill` over the cached exemplar corpus.
- The gate's home, *"gz validate scope (Rec.)"*: `gz validate --complexity-ceiling` in the default
  `gz check`, its ceiling read from `[tool.ruff.lint.mccabe] max-complexity` and its population the Python
  the wheel ships. REQ-0.0.29-05-01, -02 and -03 (the auto-chain hook chains on xenon),
  REQ-0.0.28-01-10 (three bootstrap metrics, `radon_mi` among them) and REQ-0.0.27-03-05 (a missing
  `radon` binary) are each *"Amend in place (Rec.)"*.

**Read at tranche 4, Radon against Lizard per function (2026-10-22, scratch `uvx radon@6.0.1`).**
Over `src/gzkit`, 5,221 functions pair by `def` line; 5,183 (99.3%) score identically and 38 differ
by one or two. No verdict changes at the ceiling of 20 (both tools' maximum is 20). One verdict changes at
the advisor's block band (`commands/adr_demote.py:106`, Radon 11, Lizard 10: block becomes warn), and two near
its warn band (`obpi_complete.py:966` and `specify_cmd.py:692`, Radon 9 and 8, Lizard 7). The two functions
only Radon scores are the inline `...` stubs the ceiling exempts.

**Amended for tranche 4 (2026-10-23): complexipy retired for a gzkit-owned score.** The operator ruled
it a poor replacement (verbatim: *"so, this is a poor replacement: \"complexipy\""*) and selected
*"gzkit-owned, stdlib ast (Rec.)"* over Lizard's `-Ecognitive`, Ruff's `PLR09xx` counts alone, and keeping
complexipy with upstream reports. Measured on complexipy 8.1.0 before the ruling (a dated record): with
`-q` a failing run printed nothing on either stream, so the Lint step went red undiagnosed; its snapshot
keyed files by `strip_prefix(...).to_str()` with no separator normalization (`runner.rs`
`analyze_file_shared`), so on Windows no committed row matched and windows-latest Lint was red from
`25287b8e0`; it scored nine conditional expressions 0 (`plan.py:_build_scorecard_and_checklist`); and it
agreed with Lizard's `-Ecognitive` on 73.5% of 5,112 paired functions. `gzkit.complexity.cognitive`
implements Campbell's Cognitive Complexity (SonarSource) over CPython's `ast`, with the paper's worked
examples as fixtures; over `src/gzkit` it finds 263 of 5,185 shipped functions over 15, maximum 46. The
ruling "15 with shrink-ratchet" carries over unchanged: `gz validate --complexity-ceiling` holds the ceiling
`.gzkit.json` declares (`complexity.cognitive_ceiling`, opt-in for adopters), and
`data/cognitive_complexity_baseline.json`, an exact shrink-ratchet keyed by POSIX path and qualified name,
holds the 263. complexipy leaves the dependencies, the lockfile, the pre-commit hooks, the Lint step and
the chores; `python -m gzkit.complexity.cognitive` prints the scores the chores read.

**Ruled for tranche 4 (2026-10-23): Ruff `ALL` held by a counted baseline.** Measured on Ruff 0.17.1 with preview, less the standing exceptions: 9,324 findings over 117 rules in `src/gzkit`, and 6,559 over 97 in tests, features and scripts under the curation list (a dated record). The operator ruled the package findings into *a keyed shrink-ratchet baseline* (verbatim *"b"*) over fixing all of them, and by selection how it is held: counted per (file, rule) and judged by gzkit, *"Counted, gz-run (Rec.)"*, over Ruff's own `per-file-ignores`, which would admit a new finding of a rule a file already carries; in its own file, *"Own file (Rec.)"*, over rows in the astral-discipline baseline, so this tranche's done condition reads the witness and not the lint debt; and `RUF105` (every `# noqa` flagged) a standing exception, *"RUF105 exception (Rec.)"*, with `DOC201` and `DOC501` baselined. `data/ruff_baseline.json` holds the rest, `gz lint` judges it, and `gz lint --ratchet` lowers it.

The rules tranche 4 still reads site by site: S506 (`quality.py`, the YAML loader), S608
(`trust_audits/cli.py`), two S701 (jinja2 autoescape off on non-HTML renders), and about 260
S603/S607/S404 subprocess sites. Each gets a fix or a reasoned `# noqa`. Three preview findings read as
false positives: F822 against `cli/__init__.py`'s lazy `__getattr__`, PLE1141 on a list of tuples, and
RUF027 on a `.format` template. Under "every ty rule", the 2026-08-08 exclusion of `features/` from
`ty check` (behave's `context` annotations) gets a ruling when the tranche lands.

**Amended for tranche 4 (2026-10-24): the import-boundary row and the PEP 563 ban.** Measured on Ruff 0.17.1, `ruff analyze graph` reports first-party files only: `core/models.py` imports Pydantic and its entry lists `src/gzkit/skill_contract.py` alone, so the graph cannot carry the core's stdlib-and-Pydantic allowlist, and `TID251` banned-api is a ban list, which cannot state an allowlist either. The hand-written AST test in `tests/policy/test_import_boundaries.py` therefore stays. What the graph does that the test cannot is follow imports transitively, and that reading found `core/id_resolver.py` reaching 76 `cli`/`commands` files through a function-local import at `req_kind_support.py:320`. The operator ruled that work out of this tranche (verbatim *"okay - do 1-3"*, accepting the recommendation to file it), so the graph lands as the direction check under GHI #1267. The `TID251` ban on `__future__.annotations` is ordered after the import's removal (selection *"Remove first, then ban (Rec.)"*): 1,058 files carried it, and holding them would raise `data/ruff_baseline.json` above its `baseline_count` of 4,613 in `data/waiver_ratchet_registry.json`, which a shrink-ratchet forbids. With every copy removed the ban enters with no row.

**Known uncertainties.** Each is read by the tranche that owns it:

- Whether `uv_build` ships the wheel's non-Python data (the `.md` and `.json` under `src/gzkit`) with
  `data` or the module root alone, and what the distribution baseline manifest then reads. *Read by
  tranche 3:* the module root alone. uv_build has no wheel includes and ships the module tree whole,
  less its excludes; the wheel matched hatchling's payload file for file (880), and
  `wheel_shipped_files` predicts it from `[tool.uv.build-backend]` (877 files against a real build of a
  tree with `__pycache__` present). The baseline manifest is unchanged. An anchored `wheel-exclude`
  removed nothing on uv 0.13.1, so the predictor refuses one.
- Whether Read the Docs can build through uv with a locked group, or the docs build moves to the
  `docs.yml` workflow alone.
- Whether `uv init` produces the scaffold `gz init` needs, or `gz init` writes the same files through
  `uv add` and `uv python pin` after a `uv init --bare`.
- What replaces `twine check --strict`; uv documents no metadata check. *Read by tranche 3:* the
  smoke test uv's GitHub guide recommends, each built distribution installed into a throwaway
  environment with `uv run --isolated --no-project --with` and its CLI run.
- Which of `uv check`, `uv format` and `uv audit` are preview on the pinned uv, and what each changes in
  the `CANONICAL_STEP_COMMANDS` receipts the lockstep tests pin.

## Before-figures

Read 2026-10-19 and re-read when RO-9 closes: the Python version stated in 11 places; 4 workflows on
`setup-python`; 4 `uv sync --frozen` and 1 bare `uv sync` in workflows; 1 `requirements*.txt`; 2 `uv pip`
or `pip install` sites in automation (`docs.yml`, Read the Docs); 51 `uvx` sites under `src/gzkit`; 4 declared, never-invoked dev
dependencies; 0 lock-freshness checks; uv `==0.12.23`.
