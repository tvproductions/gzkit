# R&D run — house-style

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-11-08T15:55Z.

**Challenge.** The operator, after the session found that the hexagonal rule has one gate (core
import purity, run only under `gz check --full`) and no chore, verbatim:

> *"I'm concerned that we don't have a way to reliably or strongly express our design intents
> with hexagonal architecture. And I'm not sure how to get the model to be aware of this when
> designing new features or even doing repairs or just any code work. Do we have a strong
> hexagonal chore and, more importantly, if a rule isn't it, because the rule is whenever we
> touch a Python file, then what is?"*

> *"What we're really going to need is something that's pretty close to a house style . I think
> we have that in little places, even like the preference for pedantic in certain circumstances,
> but for instance, I think sometime in the last month I made it clear that I wanted ultra
> strong, tight alliance with astral project philosophies and astral tooling. So it feels like we
> need to be a little bit more emphatic and explicit about our desires for the hexagonal
> architecture as a foundation for not only GZKit, but whatever is built with GZKit."*

Started on the operator's *"Yes, R&D first"*. The words are booked as insight
`2026-11-08T15:48:11Z` (scope `governance/house-style`).

---

## source · the Astral alliance, RP-9's rulings and witness

`docs/governance/harbor-ro9-astral-toolchain.md` · read in full 2026-11-08

> *"I want strict https://docs.astral.sh/uv/concepts/projects/ compliance for gzkit and all of its
> adopters."*; *"I want tight compliance - even gzkit itself might need to change."*

> One rule carries the rest: **each fact is declared once, in the place Astral's tools read it, and
> every restatement is removed rather than validated against its copies.**

> **Adopters.** The same rules run against a project `gz init` scaffolds in a temporary directory, so the
> scaffold cannot regress, and the scope ships in the wheel so an adopter's own `gz check` runs it.

> **The baseline.** `data/astral_discipline_baseline.json` lists today's violations keyed by rule and
> file, never by line, registered as a `shrink-ratchet` in `data/waiver_ratchet_registry.json`.

> Curated exceptions, where Astral ships nothing: `unittest` and unittest-parallel (doctrine is unittest
> only), coverage, behave, mkdocs, the pre-commit framework [...] Each keeps a one-line reason in the
> exception register tranche 1 lands

> | hand-rolled import-boundary tests | kept: the AST allowlist test stays, and `ruff analyze graph` moves to the transitive direction check (GHI #1267; § Amended for tranche 4, 2026-10-24) |

> that reading found `core/id_resolver.py` reaching 76 `cli`/`commands` files through a function-local import at `req_kind_support.py:320`.

The operator's named precedent. The shape: operator rulings, then one declaration where the tool
reads it, a shrink-only witness in the default `gz check`, run against gzkit and a fresh scaffold,
shipped in the wheel. It also shows the boundary test already passed through RP-9 once, and the
transitive direction check was routed to GHI #1267.

## source · RP-15, project structure for gzkit and every project it governs

`docs/governance/harbor-ro15-project-structure.md` · read in full 2026-11-08

> gzkit and every project it governs follow [uv's project model](https://docs.astral.sh/uv/concepts/projects/) to the maximum, as [`tvproductions/gz-skills-first-starter`](https://github.com/tvproductions/gz-skills-first-starter) does.

> Operator, by selection: *"Report, then prove (Recommended)"*. `gz init` never breaks a working build and never refactors a project's code. It inventories every gap, and adoption stays incomplete until a governed migration passes the structure rules.

The precedent for reach into adopters' existing (brownfield) code: report, then prove.

## source · the hexagonal rule

`.gzkit/rules/hexagonal-architecture.md` 0.4.1 · read in full 2026-11-08

> 1. **Dependencies live in adapters, never in the core.** Any third-party import
>    (networkx, tree-sitter, future deps) is confined to an adapter module behind
>    a port. Core domain logic imports **stdlib + Pydantic ONLY**.

> Hexagonal is the **second stage** of gzkit's architectural spine, not a standalone
> rule. The order is load-bearing for gzkit and every adopter project:

> Neither `gz lint` nor `gz typecheck` checks an import boundary; `tests/policy/test_import_boundaries.py` is the witness, and it covers `src/gzkit/core/` only.

Loads on `paths: "**/*.py"`, so on every Python file read.

## source · the hexagonal canon page

`docs/governance/hexagonal-architecture.md` · read in full 2026-11-08

> **gzkit conformance (resolved 2026-07-06 — the injection seam IS the canonical hexagon):** gzkit satisfies the pattern **through parameter injection, and that is its blessed hexagon** (operator ruling, 2026-07-06).

> **Retired facade (the resolution):** the former `src/gzkit/ports/` + `src/gzkit/adapters/` + `tests/fakes/` layer [...] was built and conformance-tested but wired into **zero** production code and injected into **zero** domain tests — by Cockburn's own test, *"a nice drawing but not much more."*

> 3. **gzkit makes the port/adapter distinction structural, not architectural.**
>    Cockburn used the pattern to organize code; gzkit uses it to organize
>    *governance artifacts*. The ADR is the unit, not the module. This is a
>    conceptual borrowing, not a code-organization rule.

The third quotation is § Departures from Cockburn, written for the ADR-kind mapping. It reads
against the rule's *"primary code-architecture directive"*: one page holds both a code directive
and a statement that the borrowing is not a code-organization rule. The ADR-kind mapping is
already recorded as stale (classic ADR CO-1).

## source · the one gate and why it runs late

`tests/policy/test_import_boundaries.py` lines 1–80; `src/gzkit/commands/quality.py:1382–1415` · read 2026-11-08

> #: `.gzkit/rules/hexagonal-architecture.md` rule 1 says core imports "stdlib +
> #: Pydantic ONLY", and rule 2 names Pydantic the single ratified exception. That
> #: is an ALLOWLIST, and it cannot be expressed as a denylist

> a changed production module selects test modules whose
> filename contains its stem. Name matching is not a dependency graph — it will
> miss a test that exercises a module it is not named after.

The test carries no `@smoke`. Recorded as F22 in the RP-7 change-order record (`ea30d8274`).

## source · the scorecard rows for the rule

`docs/governance/advisory-rules-audit.md` rows 64 to 64e · read 2026-11-08

> | 64b | **Ports are domain-typed contracts** — a port's methods accept/return domain types, never adapter types | **Judgment** | Whether a type is "domain" or "adapter" is a modelling reading; a checker would grade by module path, which is the `shape-graded-not-substance` signature this scorec

> | 64e | The core is testable without any adapter | **Promotable** | The property is decidable: import every `core/` module in a process with the third-party dependencies absent

Row 64 is Mechanical, 64a, 64c and 64e Promotable, 64b and 64d Judgment. Unlike the Astral
discipline, part of hexagonal is judgment no gate can grade.

## source · the outside-core population, RP-7 held ruling H1

`docs/governance/harbor-ro7-placement.md` row H1 · read 2026-11-08

> | H1 | hexagonal rule 1, *"Any third-party import … is confined to an adapter module behind a port"* | yaml in 21 modules, rich in 65, jsonschema in 7 (`governance/`, `ontology/okf.py`) behind no port; the witness covers `src/gzkit/core/` only; row 64 scores the universal sentence Mechanical | narrow to the core plus new heavy dependencies through an adapter |

H1 is unruled. Whatever this run settles about the scope of the boundary moves H1's answer.

## source · gz-skills' hexagonal audit

`tvproductions/gz-skills@50e2de11` `skills/gzs-hexagonal-architecture-audit/SKILL.md` and `references/audit-criteria.md` · read in full 2026-11-08

> Analyze greenfield designs and brownfield implementations against right-sized hexagonal architecture, then coach boundary-preserving design or refactoring.

> This is a read-only audit. [...] Return findings to that workflow and honor its scope, state, ordering, gates,
> locks, receipts, reviewer independence, and attestation.

> 10. **Promised boundary without acceptance witness:** a declared hexagonal
>     direction or isolation rule lacks a test or check capable of detecting its
>     collapse.

> - **Not Applicable:** small leaf libraries, schemas, data-only or generated
>   artifacts, and simple scripts without meaningful architectural boundaries.

The operator named gz-skills as the thing to look at. It carries the judgment half as an audit
with a design mode and an implementation mode, and it holds that hexagonal is not every
project's target ("right-sized", "Not Applicable").

## source · stdlib-first, the posture hexagonal protects

`AGENTS.md` § STDLIB-FIRST DOCTRINE · read 2026-11-08

> Use stdlib by default. A runtime dependency, new or existing, needs ADR or OBPI rationale naming the capability stdlib cannot supply; popularity or recency is not rationale. Standing choices: `unittest` (pytest is blocked by the `forbid-pytest` hook), `argparse` (ADR-0.0.2), and Pydantic as the one named departure, for validation (`.gzkit/rules/models.md`).

The other house-style pieces the operator's *"in little places"* points at: stdlib first,
unittest, argparse, Pydantic, each held at a different strength (a hook, an ADR, a rule).

## decision · a house style is ruled preferences in the RP-9 shape, with an audit for the judgment part

What made the Astral alliance strong is its shape, not its subject (source: RP-9's rulings and
witness): the operator rules a preference; it is declared once where a tool reads it; a shrink-only
witness in the default `gz check` holds it against gzkit and a fresh scaffold and ships in the wheel.
Hexagonal cannot be carried by that shape alone, because part of it is graded Judgment (source:
the scorecard rows). gz-skills carries that part as an audit with a design mode (source: gz-skills'
hexagonal audit).

Put to the operator: A, the RP-9 shape wherever a check can detect a violation, the judgment part
carried by a design-time audit at the start of work and a periodic chore, prose explaining and never
the authority; B, witness only, judgment left as rule text; C, a written style manual agents read at
design time, gates where possible. Operator, by selection: *"RP-9 shape, plus judgment
(Recommended)"*.


## decision · the house style gathers every pillar under one name; this run designs hexagonal

The operator's *"we have that in little places"* names a population (source: stdlib-first, the
posture hexagonal protects): the Astral alliance, stdlib first, Pydantic as the one ratified
exception, unittest, argparse and hexagonal, each held at its own strength. Astral is already
witnessed (sources: RP-9, RP-15), so gathering it carries it and rebuilds nothing.

Put to the operator: A, all pillars under one name, each keeping its own witness, this run designing
hexagonal; B, hexagonal only, the name deferred; C, all pillars redesigned together, reopening RP-9
and RP-15. Operator, by selection: *"All, under one name (Recommended)"*.

## decision · every project built with gzkit declares its boundary; Not Applicable only with a reason

The reach follows RP-15's brownfield precedent (source: RP-15) and gz-skills' right-sizing (source:
gz-skills' hexagonal audit): every `gz init` project declares which modules are core and which may
hold each dependency; a fresh scaffold starts conformant; an existing project is reported, then
proven through a governed migration; a project may declare itself Not Applicable with a recorded
reason, in the shape of RP-9's exception register.

Put to the operator: A, declared by every project, Not Applicable by recorded reason; B, strict for
all, no Not Applicable; C, opt-in. Operator, by selection: *"Declared by every project
(Recommended)"*.

## decision · the questions are the right ones

Three recommendations accepted in a row, so the run asked whether the questions were the right ones
before computing the next. Operator, by selection: *"Right questions, go on"*.

## source · third-party import sites in gzkit's package, measured

`git grep -l -E "^\s*(import <dep>|from <dep>)" -- 'src/gzkit/**/*.py'`, and the same over
`src/gzkit/commands/**` and `src/gzkit/cli/**` · run 2026-11-08 at `6df793052`

| Dependency | Files importing it | Of them in `commands/` or `cli/` |
|---|---|---|
| rich | 61 | 56 |
| yaml | 12 | 2 |
| jsonschema | 6 | 1 |
| jinja2 | 2 | 0 |
| networkx | 1 | 0 |
| tree_sitter | 0 | 0 |

A dated measurement, counting files with an import line, function-local imports included. It does
not agree with H1's figures (rich 65, yaml 21, jsonschema 7), whose method the H1 row does not
state; the difference is unexplained and recorded, not reconciled. The canon page names the CLI
layer a driving adapter (source: the hexagonal canon page), so most rich sites already sit in an
adapter.

## decision · the boundary covers the whole of gzkit's package, its debt held by a shrink-only baseline

The measurement (source: third-party import sites in gzkit's package) shows most rich sites already
in the CLI layer, a driving adapter by canon (source: the hexagonal canon page), and the rest of
the outside-core population H1 named (source: the outside-core population, RP-7 held ruling H1).
RP-9's *"even gzkit itself might need to change"* (source: RP-9) is the precedent for holding the
whole tree rather than narrowing the rule to where its test already looks.

Put to the operator: A, the whole package, the map declaring core and each dependency's allowed
adapter modules, every other site in a shrink-only baseline closing at zero; B, core only, H1's
recommendation; C, the whole package with today's sites permanently grandfathered. Operator, by
selection: *"Whole package, baseline (Recommended)"*. This settles the direction of RP-7's H1; the
ruling is booked there only on the operator's go on that row.

## source · gzkit's project configuration file

`.gzkit.json` (top-level keys) and `src/gzkit/commands/init_cmd.py:291,1162-1175` · read 2026-11-08

> `['mode', 'paths', 'authorship', 'smoke', 'project_name', 'vendors', 'complexity']`

> `config = GzkitConfig.load(project_root / ".gzkit.json")`

`gz init` reads and writes `.gzkit.json`, and the cognitive ceiling already lives in its
`complexity` key, *"opt-in for adopters"* (source: RP-9, § Amended for tranche 4, 2026-10-23).
`pyproject.toml` carries no `[tool.gzkit]` table. No Astral tool reads an import boundary: RP-9
measured that `ruff analyze graph` reports first-party files only and `TID251` is a ban list that
cannot state an allowlist (source: RP-9).

## decision · the boundary is declared in `.gzkit.json`, its baseline beside it in `data/`

No Astral tool reads an import allowlist (source: RP-9), so gzkit's own witness is the reader,
and the one home is the file `gz init` already scaffolds and repairs, where the cognitive ceiling's
precedent sits (source: gzkit's project configuration file).

Put to the operator: A, a `house_style.boundary` key in `.gzkit.json`, the shrink-only baseline in
`data/` as RP-9's is; B, a `[tool.gzkit]` table in `pyproject.toml`, a second gzkit config home; C,
a dedicated `data/` file. Operator, by selection: *"A `.gzkit.json` key (Recommended)"*. The key's
name is illustrative until diamond 2 specifies it.

## decision · what the project holds today is candidates, not the house style (operator correction)

Operator, verbatim, while the run moved to the next question: *"It's not necessarily the case that
everything we have in the project now will be the house style, by the way. So I just see you listing
different things and I wanted to make that clear."*

This corrects the decision *the house style gathers every pillar under one name*. Its ruling
stands as a ruling on scope, one named house style, each admitted preference keeping its own
witness. But the six preferences it listed (the Astral alliance, stdlib first, Pydantic, unittest,
argparse, hexagonal) are **candidates**, not members. None is admitted by being present in the
project. Which candidates enter, and by what test, is now a frontier question that comes before any
further placement question. The hexagonal decisions already taken (reach, scope inside gzkit, the
declaration's home) stand as design of the candidate this run was opened for.

## decision · the declaration's home is reopened: `.gzkit.json` against `pyproject.toml`

Put next was the admission question (how a candidate enters the house style: the operator's ruling
against a stated test; the ruling alone; or the test admitting). The operator answered with a message
instead, verbatim: *"Also not sure, so you go between our internal settings file, pyproject.toml, and
that'll be something to discuss as well."*

This reopens the decision *the boundary is declared in `.gzkit.json`*. Its selection stands as
recorded, but it is no longer settled: whether a house-style fact lives in gzkit's own settings file
or in `pyproject.toml` is a frontier question for discussion, wider than the boundary key, since
it decides where every admitted preference is declared. The admission question stays open, not
answered.

## decision · a candidate enters the house style by the operator's ruling, against a stated test

Following the operator's correction that presence in the project admits nothing. Put to the
operator: A, the operator's ruling, one candidate at a time with its reason recorded, the agent
reporting a stated test that informs and never admits (does the candidate shape how every project
built with gzkit is designed, not only how gzkit runs its own governance?); B, the ruling alone, no
stated test; C, the test admits and the operator rules only the test. Operator, by selection:
*"Your ruling, against a test (Recommended)"*.

## decision · hexagonal architecture is the house style's first member

The test reported: it passes, shaping how every project built with gzkit is designed. The
operator's reason, from the challenge: *"a foundation for not only GZKit, but whatever is built with
GZKit"*. Put to the operator: A, admit it now, the other five candidates waiting for their own
rulings; B, hold admission until the config home and the start-of-work audit are designed.
Operator, by selection: *"Admit hexagonal (Recommended)"*.

## source · the `[tool]` table, uv's and Ruff's configuration files

[`house-style/sources/pyproject-tool-table-2026-11-08.md`](house-style/sources/pyproject-tool-table-2026-11-08.md), a research report landed verbatim, of the PyPA specification, PEP 518, uv's configuration page and Ruff's · read 2026-11-08

> "The `[tool]` table is where any tool related to your Python project, not just build tools, can have users specify configuration data as long as they use a sub-table within `[tool]`"

> "Our rule is that a project can use the subtable `tool.$NAME` if, and only if, they own the entry for `$NAME` in the Cheeseshop/PyPI."

> "Note: `uv.toml` files take precedence over `pyproject.toml` files, so if both `uv.toml` and `pyproject.toml` files are present in a directory, configuration will be read from `uv.toml`"

Read by a subagent; cited as a secondary record of the pages. Both Astral tools accept either
`pyproject.toml` or their own file. gzkit's own ruling picks one: RP-15 tranche 1's structure rules
refuse *"a competing `uv.toml`, `ruff.toml` or `ty.toml"* (source: RP-15).

## source · who owns the `gzkit` name on PyPI

`curl -s -o /dev/null -w "%{http_code}" https://pypi.org/pypi/<name>/json`; `pyproject.toml:2` · run 2026-11-08

> `gzkit 404` · `py-gzkit 200` · `name = "py-gzkit"`

gzkit's distribution is `py-gzkit`. Nobody holds `gzkit` on PyPI, so by PEP 518's rule gzkit may
not use `[tool.gzkit]` until it registers that name; `[tool.py-gzkit]` is its own today.

## source · what gzkit's `pyproject.toml` carries

`grep -n '^\[tool' pyproject.toml` · run 2026-11-08

> `[tool.uv.build-backend]`, `[tool.uv]`, `[tool.ruff]` (and nine subtables), `[tool.ty.terminal]`, `[tool.ty.environment]`, `[tool.ty.overrides.rules]` (twice), `[tool.coverage.run]`, `[tool.coverage.report]`

Every tool gzkit runs reads its configuration from `pyproject.toml` except gzkit, which reads
`.gzkit.json` (source: gzkit's project configuration file).

## source · `.gzkit.json` in full, and its readers

`.gzkit.json` (898 bytes) · read in full 2026-11-08; `git grep -l '\.gzkit\.json' -- 'src/**/*.py'` · 54 files

> `"mode"`, `"paths"` (prd, constitutions, obpis, adrs, source_root, tests_root, docs_root, design_root), `"authorship"` (required_email_suffix, attestor_handle), `"smoke"`, `"project_name"`, `"vendors"` (claude, codex, opencode, each enabled, surface_root, instruction_format), `"complexity"` (`"cognitive_ceiling": 15`)

What the file holds is gzkit's governance settings for the project: where its records live, who
attests, which agent vendors it renders for. One key, `complexity.cognitive_ceiling`, is a fact about
how the project's code is written. 54 source files name the file (a text count; how many read it
through `GzkitConfig` was not traced).

## decision · house-style facts go in `pyproject.toml`'s tool table; `.gzkit.json` keeps governance settings

Read both sides in full (sources: the `[tool]` table, uv's and Ruff's configuration files; what
gzkit's `pyproject.toml` carries; `.gzkit.json` in full, and its readers). Every other tool gzkit
runs reads `pyproject.toml`, and RP-15 refuses a competing tool file (source: RP-15); `.gzkit.json`
holds governance settings no other tool reads, and one code fact.

Put to the operator: A, split by kind, code-design facts (the hexagonal boundary, the cognitive
ceiling, later members) in a `[tool.<gzkit name>]` table and governance settings in `.gzkit.json`;
B, all of `.gzkit.json` into the tool table, the file retired; C, all in `.gzkit.json`. Operator, by
selection: *"Split by kind (Recommended)"*. This supersedes the reopened decision *the boundary is
declared in `.gzkit.json`*. The cognitive ceiling's move is a consequence, not yet a ruling. The
table's name waits on the PyPI ownership question (source: who owns the `gzkit` name on PyPI).

## source · the airlock, gzkit's start-of-work and end-of-work doors

`src/gzkit/airlock/model.py` lines 1–160, `src/gzkit/airlock/enter.py:80–125`, `src/gzkit/airlock/exit.py:345–412`; `gz permitted-entry --help` · read 2026-11-08

> ``bodies`` is seam-as-BODY: contiguous regions of similarity — the FOOTPRINT.
> ``push_edges``/``pull_edges`` are seam-as-BOUNDARY: the join. ``unaccounted``
> holds edges present but undeclared, and is never folded into the joins.

> """Three-beat airlock-IN gate — DECLARE -> PING -> RECONCILE -> decide."""

> `seam_map = _reconcile(target, declared.declaration, declared.bodies, reach, declared.parent_invariants)`

> `compute_drift_diff(tuple(reach), declared.parent_invariants)`

> Cross the airlock for an ad-hoc/spurious entry: reconnaissance for comprehension with light repair at most. The acknowledge-and-decide gate fires on EVERY transit (permissive ceremony, never skipped).

Every unit of work already crosses a door at its start and its end: a brief or a work package
through `gz airlock in` and `out`, ad hoc work through `gz permitted-entry`. Entry reconciles the
declared footprint and `parent_invariants` against observed reach and decides; exit adjudicates drift
against the same invariants. `Provenance` separates declared LAW from OBSERVED fact. What
`parent_invariants` holds today and who supplies it was not traced past these call sites.

## decision · where the pillar reaches the model is held for discussion

Put to the operator: A, the boundary declaration feeding the airlock as LAW (told at entry, drift
judged at exit), the audit at design time in design mode, and a periodic chore in implementation
mode; B, design time and a chore, no airlock wiring; C, a chore only. Operator, verbatim: *"I like
your recommendation, but I think we need to discuss these options so I understand more clearly."*
Not ruled; the run walks the options through before putting the question again.

## source · what the airlock's doors are fed today

Callers of `airlock_enter` and `enter_slice` (LSP references), read at `src/gzkit/pipeline_runtime.py:686–698`, `src/gzkit/commands/airlock.py:120–124`, `src/gzkit/commands/permitted_entry.py:258–266`, `src/gzkit/commands/mx_cmd.py:172–181`, `src/gzkit/work_package_transit.py:125–132,180–191`, `src/gzkit/airlock/enter.py:49–62` · read 2026-11-08

> `preflight = airlock_enter(obpi_id, brief_path, ledger=ledger)` (the OBPI pipeline)

> `return enter_slice(package_slice(package, ledger), reach_fn=_no_reach, ledger=ledger if book else None)` (the work package)

> `# Diagnostic-only FOR NOW: a NO-GO is surfaced rather than blocking — a staged posture per parent ADR § Calibration frontier, not the declared end state (BI-4 blocks).` (`gz permitted-entry`)

> `"""Default reach adapter: transitive blast-radius via the ontology projection.` (`_default_reach`)

Four findings, each read from the call sites:

1. No production caller passes `parent_invariants`; every door enters with the default empty
   tuple. The channel that would carry declared LAW to the doors exists and carries nothing.
2. *Reach* is the governance ontology's graph (artifacts and their links), not Python imports. A
   work package enters with no reach at all (`_no_reach`), and the mx door with an empty one.
3. A work package's footprint is its declared `modules`, the code paths it owns; that is the one
   place a door already knows which files the work will touch.
4. `gz permitted-entry`'s NO-GO is diagnostic only, *"for now"*. No hook under `.claude/hooks`,
   `.gzkit/hooks` or `src/gzkit/hooks` names the airlock or permitted entry (a text search of those
   three directories, not a read of every hook), so nothing found makes a session cross a door
   before it edits.

Whether finding 1 falls short of ADR-0.33.0's declared intent for the airlock was not traced; it is a
question for `gz-intent-trace`, not a conclusion.

## decision · the pillar reaches the model three ways: a design-time imperative, airlock guidance, chore tidyings

After the walk-through and the read of what the doors are fed (source: what the airlock's doors are
fed today), the operator, verbatim: *"The reason I wanted to go deeper is it feels like we really
need all three, right? We need design time imperative, we need perhaps airlock guidance so that we
know this particular entry is sensitive to that design, and we need sure tidyings so you didn't
really give me something that was all three unless your A was all three."*, then *"chore tidyings,
chore, C-H-O-R-E, chore."*

Option A was all three: design time, the airlock, and a periodic chore. Options B and C were A with
parts removed, so the question put a whole against its own subsets and offered no real alternative.
The ruling is the operator's words: all three.

1. **A design-time imperative.** The operator's word is *imperative*, which is stronger than the
   audit the earlier options named: a design states where the boundary falls before it is approved.
2. **Airlock guidance.** The door tells the model *"this particular entry is sensitive to that
   design"*. The read shows the doors carry no declared invariants today and reach the ontology
   graph, not imports; a work package's declared `modules` is where a door already knows the files.
3. **Chore tidyings.** A periodic chore sweeps what neither the gate nor the doors catch.

## decision · where design happens is unresolved; question 10 held

Put to the operator: A, a required § Boundary section in every design artifact that changes code,
after the mode contract; B, a design-dialogue step in `gz-design`; C, classic ADRs only. Operator,
verbatim: *"Yeah, but what design dialogue step? Does it go into requirements? Does it go into a
requirements package? Is it a part of how requirements manifest inside a work package or a work
order? Is it part of R&D? Do we always do R&D when we know it's going to be required? So I just
don't know how the reminder that this requires that something requires extra design goes. So that's
kind of why I'm hesitant."*

The question assumed a design moment the run had not located in the new arrangement. Not ruled;
the run reads the arrangement before putting it again.

## source · the processes and their edges, and the outcome's `modules`

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § The processes and their edges and § The records, by band · read in full 2026-11-08

> | 4 | Design | the dialogue opened | the ADR accepted, the fifth intake door | `adr_created` only; no acceptance event |

> | 5 | Intake | a pull through one of the five doors | the outcome `queued` | none; `outcome_transitioned` has no production writer |

> | 6 | Work package | commenced, its baseline frozen | closed through Gate 5, moving the outcome | `work_package_transitioned` |

> an outcome is one reviewable deliverable with its statement, owner, `user_facing`, `governed_by`, `depends_on`, its `source` (the door it came through and the record behind it) and its `modules` (the code paths it owns: its contract)

In the arrangement, Design is its own process, ending in an accepted ADR; R&D is another, ending in
a disposition map. Neither sits inside intake, a work package or a work order, and no process says
when work must detour through them. But the code paths are declared early: an outcome names its
`modules` at intake, and a work package's footprint is drawn from them (source: what the airlock's
doors are fed today, finding 3). That is the first point at which the arrangement knows which code
a requirement will touch.

## decision · the boundary-sensitivity signal first fires at intake

Reframed from *where design lives* to *where the reminder comes from*: it is computed, not
remembered, by comparing declared code paths with the boundary declaration (source: the processes
and their edges, and the outcome's `modules`). Put to the operator, three first points, each
consumed by the later ones: A, at intake, from the outcome's `modules`; B, at the work package
freeze; C, at airlock entry. Operator, by selection: *"At intake (Recommended)"*. It depends on
`modules` being declared at admission, which RP-11 lands.

## decision · question 11 put and not answered

Put to the operator, what a boundary-sensitive outcome must do before its work can start: A, state
its boundary placement before its package can freeze, checked against the declaration, and route to
Design for a classic ADR only when the placement moves the boundary; B, always a classic ADR; C, a
warning carried into the airlock, no freeze block. The operator sent a message in place of an
answer. Open.

## decision · hexagonal is the whole system, not the core (operator correction)

Operator, verbatim, before answering question 11: *"Don't forget that not all hex architecture is
core. It's the entire system. So we've got to either do upfront design or just be mindful of at
designing time when we add, what the current big picture of the architecture is."*

This corrects the run's framing since the reach decision: the boundary was spoken of as which
modules are core and which may hold each dependency, and sensitivity as an outcome touching core.
Hexagonal names every part of the system: the core, its ports, the driving and driven adapters and
the composition root (sources: the hexagonal canon page, its five elements; gz-skills' hexagonal
audit, its component model). So:

- the declaration is a **map of the whole system's architecture**, every module placed in a
  region, not a core list with an allowlist;
- every outcome's `modules` land in some region, so every addition is placed against the map, not
  only additions that touch core;
- the decisions on reach, gzkit's scope and the config home stand, read with *boundary* meaning this
  whole-system map;
- question 11 as put, which asked what a *core-sensitive* outcome must do, is withdrawn; its
  premise was the corrected framing.

The operator names two ways to keep the picture in view, *"upfront design"* and being *"mindful
of at designing time when we add, what the current big picture of the architecture is"*; which,
or how they combine, is the next frontier question.

## decision · the whole-system map is drawn up front and kept current; a change to it is a classic ADR

Put to the operator: A, an upfront map, every module placed in a region (core, a port, a driving or
driven adapter, the composition root), declared as data and approved once as a classic ADR, each
addition placed against it at intake, a map change amended by a new ADR; B, no drawn map, the
picture derived from the code each time; C, an upfront map shown but never checked. Operator, by
selection: *"Upfront map, kept current (Recommended)"*.

This answers most of the withdrawn question 11: an addition that fits the map proceeds; one that
changes it goes through Design for a classic ADR (the classic ADR change orders, the approval rule).
What remains is where that is enforced.

## decision · placement against the map is enforced at the work package freeze

Put to the operator: A, at the freeze, no baseline frozen until every footprint module is placed in
the map and any map change cites a Current classic ADR, the airlock carrying the placement as
guidance and the chore sweeping drift; B, at intake, which RP-11 holds to *"admitting a
requirement, nothing more"*; C, at the airlock exit, after the code is written. Operator, by
selection: *"At the freeze (Recommended)"*.

A consequence, not a ruling: ad hoc work through `gz permitted-entry` freezes nothing, so it is
reached by the airlock's guidance and the chore only; its *"light repair at most"* ceiling (source:
the airlock) is what keeps a map change out of it.

## decision · corrections go into the drydock under RP-7; the new machinery is built at civil rule

Put to the operator: A, split by kind, the corrections of shipped intent (H1 ruled to the whole
package with a shrink-only baseline, F22's per-change gate) under RP-7's placement change order, and
the new machinery (the upfront map, the intake signal, the freeze check, the airlock feed, the chore,
`gz init` delivery) admitted at civil rule through the R&D door and built as work packages; B, all in
the drydock by change order; C, all at civil rule. Operator, by selection: *"Split by kind
(Recommended)"*.

Under the operator's doctrine that *"discovering that more is needed to fulfill the intent of a
feature is not an enhancement, it is a correction"* (`AGENTS.md` § Operator Doctrine), the machinery
is carried as correction of the hexagonal directive's intent, not as enhancement; *civil rule* names
when it is built, not what kind of work it is.

## decision · the tool table is `[tool.py-gzkit]`

PEP 518's ownership rule and the PyPI read (sources: the `[tool]` table; who owns the `gzkit` name
on PyPI). Put to the operator: A, register `gzkit` on PyPI and use `[tool.gzkit]`; B,
`[tool.py-gzkit]`, matching the distribution gzkit owns today. Operator, by selection:
*"[tool.py-gzkit]"*, against the recommendation.

## decision · the deferral of the other candidates was the agent's, not ruled

At review, the operator, verbatim: *"We didn't talk about admitting quite a few other choices. So I'm
not sure if that was going to be something we did here."*

Row 7(a) sent the admission of the other candidates to a follow-on run on the agent's own call; no
question put it to the operator. The candidate list was also the agent's: six preferences read from
`AGENTS.md` § STDLIB-FIRST and the Astral sources, never drawn up with the operator, and *"quite a
few other choices"* says it is longer. The frontier is reopened by this: whether admission happens in
this run is the operator's to rule.

## decision · the other candidates are admitted in this run, after the full list is drawn up

Put to the operator: A, here, the list drawn up first from canon with where each is held and how
strongly, the operator adding what is missing, then each admitted or set aside one question at a
time; B, a follow-on run, this one signed off on hexagonal and the model. Operator, by selection:
*"Here, list first (Recommended)"*. Row 7(a) is withdrawn as a follow-on when the admissions land
here. The inventory is commissioned from a research agent, its report to be landed verbatim under
`house-style/sources/`.

## source · the candidate inventory

[`house-style/sources/candidate-inventory-2026-11-08.md`](house-style/sources/candidate-inventory-2026-11-08.md), a research report landed verbatim · read 2026-11-08

> Files read in full: `.gzkit/rules/` — AGENTS.md, adr-audit.md, [...] weaponeering.md; root `AGENTS.md` (as loaded); [...] `docs/design/cli-standards-v3.md` (all of it); `src/gzkit/commands/init_cmd.py` (all of it)

> **R:** yes. `scaffold_core_rules` (init:1579) copies every wheel rule `.md`, plus `complexity-thresholds.json`, into the adopter's `.gzkit/rules/`, and `sync_all` mirrors them. The rule *text* arrives; gzkit's own `tests/` witnesses do not.

> 13. **The scaffold against its own witness.** RO9:129 forbids "`--frozen` or a bare `uv sync` in automation", but init:914 runs a bare `[resolve_executable("uv"), "sync"]` and init:498 runs `uv add --dev --frozen`.

A secondary record: 108 candidates, 14 borderline items and 13 contradictions, each cell citing
its primary source by path and line, some marked *unverified*. It admits nothing. Two findings bear
on the whole run: the rule text reaches every adopter through `gz init` while gzkit's own witnesses
do not, so for an adopter nearly every candidate is a weak rule; and the 13 contradictions are
defects in canon whatever is admitted, each to be tracked under disposition 4.

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | The upfront whole-system architecture map, approved once as a classic ADR (the first map edition); and the new machinery admitted at civil rule through the R&D door as catalog outcomes: the map as data under `[tool.py-gzkit]`, the intake signal, the freeze check, the airlock feed, `gz init` delivery to adopters | The map passes the admission question: hard to reverse, surprising without context, a real trade-off. Proposed only: the operator initiates. It waits for the classic ADR form and crossover (CO-1, CO-2 on RP-6) |
| 2 | GHI / direct fix | commissioned | Under RP-7's placement change order: book H1 ruled to the whole package with a shrink-only baseline, and repair F22 so the boundary test runs in the per-change `gz check` | Corrections of shipped intent (decision: corrections go into the drydock under RP-7); both already tracked there, so no new GHI |
| 3 | chore | commissioned | A hexagonal tidying chore: the implementation-mode audit of what neither gate nor door judges (ports typed in domain terms, policy kept out of adapters, construction at the edge), after gz-skills' `gzs-hexagonal-architecture-audit`, findings filed as GHIs | The third reach the operator ruled (*"chore tidyings"*); advise only, the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | commissioned | (a) the house style named in canon, its admission rule and its first member; (b) the hexagonal rule cut to its judgment residue once gate, doors and chore carry the rest (RP-7 placement); (c) the canon page's § Departures *"not a code-organization rule"* reconciled with *"primary code directive"*; (d) the design-time imperative written into the design surfaces | Drafted on the operator's go per item |
| 5 | one-shot refactoring | commissioned | gzkit's import sites outside their mapped region driven to zero through the shrink-only baseline; the cognitive ceiling moved from `.gzkit.json` to `[tool.py-gzkit]` | The whole-package scope and the split config home, ruled; the operator selects the route |
| 6 | no action | not pursued | Folder partitions (`domain/`, `adapters/`) to express the map; registering `gzkit` on PyPI | Canon rule 7 forbids folder partitions, and the map is data, not layout. The PyPI name: the operator chose `[tool.py-gzkit]`; revisit if the CLI's name and the distribution's are ever unified |
| 7 | further research | commissioned | (a) the admission of the other five candidates (the Astral alliance, stdlib first, Pydantic, unittest, argparse), one at a time against the stated test; (b) an intent trace of ADR-0.33.0's airlock: no production caller supplies `parent_invariants`, and reach is the ontology graph, not imports | (a) opened by the correction that presence admits nothing; (b) opened by the read of what the doors are fed. The operator opens each |

## Close

**Challenge restated.** Restated on purpose at the close. The challenge opened as *"a way to reliably
or strongly express our design intents with hexagonal architecture"* and *"how to get the model to
be aware of this"*, and the opening read it as the hexagonal rule's missing gate and chore. Restated:
gzkit needs a **house style**, a named set of preferences each admitted only by the operator's
ruling, of which hexagonal is the first member; hexagonal is the **whole system's** architecture,
drawn up front as a map, kept current through classic ADRs, and brought to the model three ways, a
design-time imperative enforced at the work package freeze from a signal computed at intake,
guidance at the airlock, and chore tidyings, for gzkit and for every project built with it.

**Frontier.** Reopened 2026-11-08 at review (decision: the deferral of the other candidates was the agent's). Before that: empty. Every open question whose answer would move a disposition is ruled; what
remains (the map's region vocabulary, the key names, the checks' shapes) is diamond 2.

**Review.** —

**Sign-off.** —

## What this record does not license

No ADR, OBPI, chore, rule, gate or change order is started by this run. Every row awaits the
operator's go on that row.
