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

## decision · candidates are admitted by family; the grouping drafted for the operator to adjust

Put to the operator: A, by family, about a dozen, each ruled admit, set aside, or admit except named
items, the grouping shown first; B, the operator names the wanted candidates and only those are put;
C, all 108 one at a time. Operator, by selection: *"By family (Recommended)"*.

The grouping below is the agent's draft over the inventory's numbering (source: the candidate
inventory). It binds nothing until the operator has seen it and moved what is misplaced. Operator, by
selection: *"Grouping is fine"*.

| Family | Inventory items |
|---|---|
| F1 Architecture (the admitted hexagonal member's content) | 1–10 |
| F2 Dependency posture | 11, 12, 13, 14, 21, 89 |
| F3 Data models | 15, 16, 17, 19, 90 |
| F4 Typing | 18, 27, 46, 47 |
| F5 Errors and suppression | 44, 45, 55, 56 |
| F6 Astral toolchain | 22–26, 28–40, 43 |
| F7 Project structure and distribution | 41, 42, 93 |
| F8 Code craft | 48–54, 57, 58, 92, 105, 106 |
| F9 Complexity | 59–63 |
| F10 Cross-platform and I/O | 64–74 |
| F11 CLI shape | 75–85, 87 |
| F12 Testing | 20, 91, 96–104 |
| F13 Docs, config and surfaces as code | 86, 88, 94, 95, 107, 108 |
| Borderline | the inventory's 14 borderline items |

## decision · family F1 put and not answered

Put to the operator, what the admitted hexagonal member contains (inventory items 1–10): A, admit all
ten, contradiction 1 reconciled in favour of the primary directive; B, admit with named exceptions.
The operator sent a message in place of an answer. Open.

## decision · family F1 ruled item by item; a hexagonal specification R&D run is opened by it

The operator asked for the family as a numbered list (*"please show as a numbered list so I can
indicate and/or ask questions by number"*), then ruled each item, verbatim:

> 1. and we need a better specification. I'd like for a strong adoption - for all adopters too. strengthen
> 2. yes, stdlib first (Pydantic being an exception for hexarch core).
> 3. yes, but that is ha core - we'll want some rnd to define this it seems
> 4. yes, see the need to rnd ha spec
> 5. yes, again, rnd
> 6. yes, but we need ha rnd.
> 7. I disagree with this now.
> 8. I am not sure what this mean, ha rnd
> 9. yes
> 10. yes, sounds like ddd/ontology ha rnd work. I agree with this whole thing

So, of the inventory's items 1–10 (source: the candidate inventory):

- **Admitted:** 1 (the primary directive, to be strengthened with a better specification and strong
  adoption by every adopter), 2 (stdlib first, Pydantic the exception for the hexagonal core), 9
  ("why is this here?"), 10 (the DDD, HA, BDD, TDD cascade).
- **Admitted, their specification commissioned to a hexagonal R&D run:** 3 (domain-typed ports),
  4 (Protocol and composition), 5 (the port at the second adapter), 6 (parameter injection, no DI
  framework).
- **Not admitted; held for that run:** 7, the rule against folder partitions, which the operator
  now disagrees with. It is canon (`.gzkit/rules/hexagonal-architecture.md` rule 7, hexagonal
  directive v0.2.0), so the disagreement reopens a ruled doctrine; canon is unchanged until the
  operator's go on a row that changes it. 8, subsumption into one typed model, whose meaning the
  operator asks to have defined.
- **Opened:** a follow-on R&D run on the hexagonal specification, its subject items 3 to 8 and the
  DDD and ontology relation item 10 names, with the operator's *"strengthen"* and *"strong
  adoption - for all adopters too"* as its brief.

This changes the disposition map: row 6's *no folder partitions* is withdrawn, since the question is
now the follow-on run's; row 7 gains the hexagonal specification run.

## decision · family F2 ruled item by item

Operator, verbatim:

> 11. strong yes. we need a chore that updates cli-standards (hygiene maintenance)
> 12. Still agree
> 13. I am 1000% astral aligned and potentially hostile to anything else - exceptions need strong justification
> 14. rich would be when TUI-like behavior is needed. jinja2 is for CMS templates I'd like to review why jsonschema and pyyaml are being used.
> 21. yes, argparse is stdlib
> 89. Yes, rich for TUIs if they become necessary

- **Admitted:** 11 (stdlib first, *"strong yes"*), 12 (five-year aging, against the recommendation to
  set it aside; its five years is a value in Markdown, so admission carries moving it to data), 13
  (the exception register, hardened: *"potentially hostile to anything else - exceptions need strong
  justification"*), 21 (argparse, *"argparse is stdlib"*), 89 (rich, *"for TUIs if they become
  necessary"*).
- **Commissioned:** a hygiene chore that keeps `docs/design/cli-standards-v3.md` current (row 3); the
  inventory's contradictions 5, 6, 7, 11 and 12 show it stale today.
- **14, ruled in part, three readings open:** rich *"when TUI-like behavior is needed"*, jinja2 *"for
  CMS templates"*, and a review asked of why jsonschema and pyyaml are used.

## source · why jinja2, jsonschema, pyyaml and rich are in gzkit today

`data/astral_exceptions.json` (the four entries) and `git grep -n -E "^\s*(import <dep>|from <dep>)" -- 'src/gzkit/**/*.py'` · read and run 2026-11-08

> jsonschema: "Validates documents against the JSON Schema files under src/gzkit/schemas/ at runtime (ADR-0.0.30), in the ARB validator, the catalog, the vendor manifest and the frontmatter audits. Stdlib has no JSON Schema validator, and Pydantic validates its own models, not arbitrary schema documents (RO-9 tranche 6)."

> pyyaml: "Parses YAML frontmatter, mkdocs.yml and workflow files across the governance audits. Stdlib has no YAML parser (tomllib reads TOML only) (RO-9 tranche 6)."

> jinja2: "Renders the control-surface renditions and the justify walkthrough from template files with loops, conditionals and StrictUndefined (src/gzkit/content/render/pipeline.py, src/gzkit/justify/walkthrough.py)."

> rich: "Renders the CLI's tables, styled text and markup across 65 modules, the human-first output the CLI doctrine requires. Stdlib has no table or markup renderer (RO-9 tranche 6)."

Import sites: pyyaml in 12 files (frontmatter readers in `governance/`, `rules/`, `personas/`,
`models/persona.py`, `ontology/okf.py`, `knowledge/generate.py`, two trust audits, two commands);
jsonschema in 7 (`arb/validator.py`, `commands/validate_cmd.py`, `complexity/advisor/archetype_rules.py`,
`governance/invariants.py`, two trust audits); jinja2 in 2 (`content/render/pipeline.py`,
`justify/walkthrough.py`). Two readings conflict with item 14 as ruled: rich's registered reason is
all CLI output, not TUIs; jinja2 renders gzkit's control surfaces, not CMS templates.

## decision · pyyaml admitted as necessary, its reason to be stressed

Operator, verbatim, on item 14c: *"then it would seem pyyaml is necessary - we should stress why"*.
Admitted as a curated exception: stdlib has no YAML parser, and gzkit's records carry YAML
frontmatter (source: why jinja2, jsonschema, pyyaml and rich are in gzkit today). *"Stress why"*
asks for a stronger register reason than the one-line entry in `data/astral_exceptions.json`;
drafting it is row 4's.

## source · which schemas a Pydantic model already produces

`git grep -n "model_json_schema" -- src` and the six jsonschema call sites read at the lines named · run and read 2026-11-08

> `src/gzkit/models/catalog.py:349:    return {kind: model.model_json_schema() for kind, model in FILE_MODELS.items()}`

> `src/gzkit/governance/trust_audits/catalog.py:86:        validator = Draft202012Validator(load_schema(f"catalog_{kind}"))`

> `src/gzkit/airlock/model.py:162:    return SeamMap.model_json_schema()`; `src/gzkit/ontology/model.py:139:    return OntologyNode.model_json_schema()`; `src/gzkit/core/obpi_state_machine.py:171-172`; `src/gzkit/ontology/work.py:159-162`

`src/gzkit/schemas/` holds 39 entries. At least the catalog, seam map, ontology node, OBPI state
machine and work-edge schemas have a Pydantic producer, and the catalog audit validates data
with jsonschema against the schemas its own models produce: a round trip through a schema file
when the model could validate directly. The other jsonschema sites (the ARB receipts under
`data/schemas/`, the manifest, the vendor manifest, constitutional invariants, section ownership,
the advisor's archetype rules) validate against hand-authored schemas with no model behind them.
Whether each committed schema file equals its producer's output was not traced, and why models were
not written for the hand-authored ones is not on record: RP-9's register gives only *"Pydantic
validates its own models, not arbitrary schema documents"*, which holds only where no model exists.

## decision · the operator asks why jsonschema was not replaced by Pydantic models

Operator, verbatim: *"jsonscema: as you point out: why didn't we then make Pydantic models to wrap
those schema and handle it that way?"* The record has no answer to *why*; the read above shows the
round trip and the hand-authored remainder. Whether jsonschema leaves gzkit, every schema becoming
a model's output, is put next.

## decision · jsonschema is retired: every schema becomes a Pydantic model's output

Put to the operator: retire jsonschema by making every schema a model's output, every validator
calling the model directly, any schema published to others kept as a generated file; or keep it for
some schemas. Operator, by selection: *"Yes, models first"*. The register entry for jsonschema in
`data/astral_exceptions.json` is to be removed when the last call site moves, and the hand-authored
schemas (source: which schemas a Pydantic model already produces) each gain a model first.

## decision · jinja2 admitted for rendering gzkit's control surfaces

Operator, verbatim: *"this is what I meant by "CMS templates:" It renders gzkit's own control
surfaces (content/render/pipeline.py, which builds AGENTS.md and its renditions)."* Admitted for that
use. The second site, `justify/walkthrough.py`, the justify walkthrough, was not named in the
ruling and stays to be confirmed.

## source · how gzkit uses rich today

`git grep` over `src/gzkit/**/*.py` for rich imports, grouped, and for call names · run 2026-11-08

> `51 from rich.markup import escape` · `14 from rich.table import Table` · `7 from rich.console import Console` · `4 from rich import box` · `2 from rich.panel import Panel` · `1 from rich.text import Text` · `1 from rich.rule import Rule` · `1 from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn` · `1 from rich.markdown import Markdown` · `1 from rich.console import Group`

> `console.print(` 1,357 call sites; `Table(` 31; `escape(` 167

41 files import rich for `escape` alone, which exists only to protect text from rich's own markup.
Tables are built in 14 files. A `Console` is constructed in 7: `cli/formatters.py`, `cli/progress.py`,
`commands/ceremony_data.py`, `commands/common.py`, `commands/tidy_claims.py` and three modules
under `content/tui/` (`panels.py`, `status.py`, `tables.py`), a package already named for TUIs. The
progress bar and the Markdown renderer are each in one file (`cli/progress.py`;
`commands/ceremony_steps.py`, `cli/formatters.py`). The formatter chokepoint that would put all of
this behind one surface is *"Live, UNMET"* (source: the candidate inventory, item 77). Counts of
`Rule(`, `Status(` and `Text(` call names include gzkit classes of the same names and are not used.

## decision · rich held for more discussion

Put to the operator, after the read of how rich is used: stdlib behind one output port, or rich
behind one output port. Operator, by selection: *"Discuss more first"*.

## source · the output formatter gzkit already has

`src/gzkit/cli/formatters.py` lines 1–30 and its method list; `src/gzkit/content/tui/__init__.py`; `git grep` counts · read and run 2026-11-08

> """Output formatter — single chokepoint for all CLI output.

> `    def table(self, rich_table: Table) -> None:` · `    def emit_table(self, rich_table: Table) -> None:`

> """Light TUI affordances for gz content commands (OBPI-0.0.34-05)."""

The port exists: `OutputFormatter` (418 lines, five modes: human, json, quiet, verbose, debug),
with `NO_COLOR` and forced-terminal handling in `gzkit.color_env`. 11 files use it; 77 call
`console.print(` directly. Its table methods take a rich `Table`, a library-native type crossing the
port, which F1 item 3, admitted, forbids. The markup styles in direct calls are few and semantic:
red 91, bold 58, green 55, yellow 40, dim 8 (counted on `console.print("[style]` openings only).

## decision · rich stays, behind the output port, corrected

Operator, verbatim: *"so, since this is house style, we've poorly architected rich use it seems. In
anycase, with arhictectural corrections, it seems that the benefits of rich outweigh demerits."*

Rich is admitted as the renderer of the CLI's human mode, behind `OutputFormatter` (source: the
output formatter gzkit already has). This refines item 89 as first ruled (*"rich for TUIs if they
become necessary"*): rich renders the human mode, and the TUI wording no longer limits it. The
admission carries the two corrections the read named, both now row 5's: every direct
`console.print` routed through the formatter, with semantic calls (error, success, warning,
emphasis) in place of markup; and the port made domain-typed, a table passed as plain rows and
columns, never a rich `Table`. They also discharge the CLI rule's formatter chokepoint, *"Live,
UNMET"* (source: the candidate inventory, item 77). Family F2 is ruled, save the justify
walkthrough's use of jinja2, still to confirm.

## decision · family F3 ruled in part

The operator numbered the replies 15 to 19 in order, where the list put inventory items 15, 16, 17,
19 and 90; the replies are read in that order (reply 18 is item 19, reply 19 is item 90).
Verbatim:

> 15. yes, in for a penny, in for a pound. Good practice says we should dataclass only in the core, but the Pydantic exception seems safe.
> 16. yes, use those features of Pydantic to achieve those effects
> 17. I assume those are HA Pydantic constraints?
> 18. Yes, is TypedDict stdlib?
> 19.

- **Admitted:** 15 (Pydantic for every data model, the core included, no dataclasses; contradiction
  4 settled in its favour), 16 (frozen and `extra="forbid"`, achieved through Pydantic's own
  features), 19 (TypedDict for shapes; it is stdlib, `typing.TypedDict`).
- **17, a question back:** whether field descriptions are hexagonal Pydantic constraints. Answered
  in session; open until ruled.
- **90, no reply:** open.

## decision · family F3: items 90 and 19 admitted

The operator, having said *"hold on, I wasn't done"*, continued, verbatim: *"yes admit 90, yes admit
19, but is TypedDict Pydantic or stdlib?"* Item 90 (models hold data, business logic in services) is
admitted; item 19 (TypedDict for shapes) is confirmed admitted. TypedDict is stdlib: `typing.TypedDict`
(`uv run python -c "import typing; print(typing.TypedDict.__module__)"` printed `typing`, 2026-11-08);
Pydantic can validate one, but does not provide it. Item 17 stays open on the operator's question.

## decision · family F3: item 17 admitted; F3 complete

Item 17 (field descriptions) was answered as a model's self-documentation, not a hexagonal
constraint: with jsonschema retired, every published schema is generated from a model and a
field's `description` becomes that schema's documentation, while a field's checking constraints
are validation, which item 90 leaves on the model. Operator, by selection: *"Admit 17"*. Family F3
(items 15, 16, 17, 19, 90) is admitted whole.

## decision · family F4, typing, admitted whole; MAXX Astral for gzkit and every adopter

Operator, verbatim:

> 18 - absolutely, I want a VERY HIGH level of aggressive ruff/ty compliance - MAXX
> 27 - yes. House style is this: when we move to a Python version, strict conformance/refactoring to its new language features and idioms
> 46 - bsolutely, I want a VERY HIGH level of aggressive ruff/ty compliance - MAXX
> 47 - bsolutely, I want a VERY HIGH level of aggressive ruff/ty compliance - MAXX
>
> MAXX Astral in gzkit and all of its adopters.

Items 18, 27, 46 and 47 are admitted. Item 27 is ruled as a general principle of the house style,
not only the PEP 563 ban: moving to a Python version means strict conformance and refactoring to
its new features and idioms (it also covers inventory item 26, in family F6). The closing line
settles contradiction 7 for adopters: the `gz init` scaffold's nine Ruff families
(`init_cmd.py:366`, source: the candidate inventory) fall short of the ruled *"MAXX Astral in gzkit
and all of its adopters"*; the scaffold selects `ALL` with gzkit's curated exceptions, and ty's
rules at full strength. That shortfall is a correction of RP-9 tranche 7, which closed on
2026-10-29; its route is row 2's.

## decision · family F5 ruled in part; `gz init` and `uv init` checked

Operator, verbatim:

> btw, `gz init` needs to consider using `uv init` as a part of its bootstrapping
>
> 44 - agree, WIDEN. I think AGENTS.md still has some maxim/mantra that says, more or less, fix it now.
> 45 - sounds flakey, is this maxx astral?
> 55 - 1000%
> 56 - 1000%

- **Admitted:** 44, widened from chores to every finding: a finding is never closed by suppressing
  it. The maxim the operator recalls is `AGENTS.md` § PRIME DIRECTIVE 2, *"COMPLETE ALL WORK FULLY.
  Fix broken/misaligned things immediately."* 55 (typed errors, no broad `except`) and 56 (a typed
  exception class per raise).
- **45, a question back:** whether the reasoned-`noqa` clause is MAXX Astral. Answered from Ruff's own
  rules below; open until ruled.
- **`gz init` and `uv init`:** it already bootstraps through `uv init`. `src/gzkit/commands/init_cmd.py:470–497`,
  `_uv_project`, runs `uv init --<project-type> --name <package> --python <floor> --no-workspace --vcs
  none --author-from none .`, then `uv add --dev --frozen` for the dev tools, and writes only what uv does
  not (RP-9 tranche 7, ruled *"even `gz init` should look carefully at `uv init`"*).

## source · Ruff's own suppression rules

`uv run ruff rule RUF105`, `PGH004`, `RUF100`; `pyproject.toml:129–130` · run and read 2026-11-08

> # noqa-comments (RUF105) [...] This rule is in preview and is not stable. [...] Checks for the use of `noqa` comments instead of Ruff-specific `ruff: ignore` comments. [...] `ruff: ignore` comments allow the use of rule names instead of codes and can be used in more places than `noqa` comments.

> # blanket-noqa (PGH004)

> # unused-noqa (RUF100)

> `# a justified one at a genuine boundary; RUF100 already refuses a stale one` · `# (ruled 2026-10-23, "RUF105 exception (Rec.)").`

Ruff governs its own suppressions: PGH004 refuses a `noqa` that names no code, RUF100 refuses one that
suppresses nothing, and RUF105, in preview, moves suppressions to `ruff: ignore[<rule name>]`. gzkit
holds RUF105 as a standing exception (ruled 2026-10-23). Checking that a suppression carries a written
reason is no Astral rule; it would be gzkit's own check.

## decision · family F5: item 45 made Ruff-native; F5 complete

Item 45 (the reasoned `noqa`) was answered from Ruff's own rules (source: Ruff's own suppression
rules): a written reason is no Astral check. Put to the operator: rely on Ruff's and ty's own
suppression rules at full strength and lift the RUF105 exception, dropping the gzkit-made reason
clause; or keep RUF105 excepted. Operator, by selection: *"Yes, Ruff-native"*. Item 45 is admitted in
that form: PGH004, RUF100 and ty's unused-ignore check govern suppressions, RUF105's standing
exception (ruled 2026-10-23) is lifted, every `# noqa` moves to `# ruff: ignore[<rule name>]`, and the
reason clause leaves the pythonic rule. Family F5 (items 44, 45, 55, 56) is admitted.

## decision · family F6, the Astral toolchain, admitted save item 43

Put to the operator: admit the nineteen (items 22–26, 28–40, 43), RP-9's rulings gathered; treat
the scaffold as automation under its own witness, its CI on `uv run gz check` with gzkit locked
(contradiction 13; RP-15 tranche 3); settle contradiction 9 for `uv version` as the version's one
home, correcting `AGENTS.md`; deliver items 30, 38, 39 and 40 to adopters through the scaffold.
Operator, verbatim: *"agree, what is 43?"* The eighteen and the four recommendations are admitted;
item 43 (shrink-only baselines) waits on the operator's question, answered in session.

## source · whether gzkit's shrink-only baselines ever reach zero

`data/waiver_ratchet_registry.json` read in full and each registered file's entry count computed; `git log --since=2026-10-01 --oneline` on two baselines · run 2026-11-08

> "every gate-bearing waiver/grandfather/baseline surface declares exactly one honesty mechanism (closed-set-lock | dated-cutover | shrink-ratchet) so it cannot launder 'not built' into 'attested green'. Shrink-ratchet baselines were committed at the current entry count on 2026-06-19 (OBPI-0.0.73-09)"

37 registered surfaces: 35 shrink-ratchet, 2 closed-set-lock, none dated-cutover. Of the 35, 6 hold zero
entries. The largest by committed count, against entries now: `ruff_baseline.json` 4,613 against
2,567; `behave_coverage_waivers.json` 522 against 522; `cognitive_complexity_baseline.json` 260
against 260; `adversarial_validation_grandfather.json` 225 against 225; `tautological_test_baseline.json`
202 against 202; `sensitivity_floor_grandfather.json` 87 against 87. The two baselines repair orders
drove to zero, RP-2's id seam and RP-9's Astral discipline, did so as those orders' done conditions
(sources: RP-9; the RP-2 row of the contract). `ruff_baseline.json` changed in 44 commits since
2026-10-01, as RP-9 tranche 4's repairs lowered it.

A baseline reaches zero when an owned piece of work names zero as its done condition; otherwise it
stands where it was committed. The ratchet stops growth, not debt.

## decision · item 43 admitted: every baseline owned to zero; F6 complete

Measured (source: whether gzkit's shrink-only baselines ever reach zero): the ratchet stops growth,
not debt, and a baseline reaches zero only when owned work names zero as its done condition. Put to
the operator: admit 43 only with an owner and a close-at-zero plan per baseline, a named chore or
work package whose done condition is an empty baseline, with a target date (the registry's unused
`dated-cutover`); the baselines that have not moved each get an owner or an operator's ruling that
the debt is accepted. Operator, by selection: *"Yes, owned to zero"*. Family F6 is admitted whole.

## decision · family F7 ruled in part

Operator, verbatim:

> 41 - yes, and elaborate/explain - are these all astral?
> 42 - what convention is this?
> 93 - ok, we may suggest to adopters - but yes, define.

- **Admitted:** 41 (maximal project structure), its parts explained below by origin.
- **93, admitted as a definition to write:** binary versus wheel by audience, offered to adopters
  as a suggestion, not a requirement (*"we may suggest to adopters"*), defined before it binds.
- **42, a question back:** whose convention the project types are. Answered below; open.

## source · what `uv init` writes for each project type

`uv init <type> --vcs none --name demo .` run in four scratch directories on uv 0.13.7, files listed and `pyproject.toml` read, then deleted; `uv init --help`; `docs/governance/harbor-ro9-uv-project-norms.md` § 3 · run and read 2026-11-08

> `--package  Set up the project to be built as a Python package` · `--app  Create a project for an application` · `--lib  Create a project for a library` · `--bare  Only create a pyproject.toml` · `--script  Create a script`

> "uv prefers to define a build system and place source files in a dedicated `src/<project_name>/` directory." · "Libraries always require a packaged project." · "We strongly recommend configuring a build system."

Observed on uv 0.13.7: with no flag, `uv init` wrote the same project as `--app` and as `--package`:
`src/demo/__init__.py`, `.python-version`, a `uv_build` build system and a `[project.scripts]` entry.
`--lib` wrote the same less the script entry, plus `src/demo/py.typed`. None wrote a `tests/`
directory. uv's default is the application shape; gzkit's `gz init` defaults to `lib` (source: RP-9,
§ Ruled for tranche 7).

By origin, the parts of item 41: from uv itself, the `src/<name>/` package, a declared build backend
(`uv_build`), commands in `[project.scripts]` (written for app and package), `py.typed` on a library
(written by `--lib`), and refusing uv's legacy `tool.uv.dev-dependencies` and `managed = false`, which
opts out of uv's project management. Not from uv: a separate `tests/` (no type writes one; Python
convention and the starter's), no `sys.path` injection (Python practice that a packaged project
makes unnecessary), and no competing `uv.toml`, `ruff.toml` or `ty.toml`, which uv and Ruff both
permit (source: the `[tool]` table) and gzkit refuses under its own declare-once rule.

## decision · item 42: `gz init` follows uv's default, the application shape; F7 complete

Answered from the observed run (source: what `uv init` writes for each project type): the project
types are uv's own convention, and uv's default is the application shape where `gz init` defaults to
`lib`. Put to the operator: follow uv, `app` the default; or keep `lib`. Operator, by selection:
*"Follow uv: app"*. This supersedes RP-9 § Ruled for tranche 7's *"`lib` the default"* (RP-9 closed
2026-10-29); the change joins row 2's corrections of tranche 7. Family F7 (items 41, 42, 93) is
admitted, 93 as a suggestion to adopters still to be defined.

## decision · family F8 held for discussion: how judgment style reaches the model

Operator, verbatim: *"these need to be discussed, unless they are enforceable. maybe Pythonic style
is appropriate in a pythonic rule? I agree on chore vs. rule, but do we have no recourse to get the
model to do coding style under house style rules? discuss"*. Not ruled.

## source · the write-time and review-time mechanisms gzkit already has

`.claude/hooks/post-edit-ruff.py` lines 1–30; `.claude/settings.json` (its `PostToolUse` `Edit|Write` entry, line 173); `.claude/agents/quality-reviewer.md` lines 1–22 · read 2026-11-08

> PostToolUse hook that runs `gz lint` (Ruff against data/ruff_baseline.json, lint-only, no fix) on edited Python files immediately after each Write/Edit operation, so only findings the baseline does not hold show.

> On non-zero exit, the first N lines of ruff output are written to stderr so the agent sees the warning in the same turn and can correct course

> description: Evaluates code architecture, SOLID, test coverage, maintainability. Independent review by reading; cannot execute commands (GHI #968).

Two recourses exist besides rule and chore. At write time, every edit of a Python file is linted at
once and the finding reaches the agent in the same turn, so anything Ruff can check is enforced as it
is typed (whether `gz init` delivers this hook to adopters was not traced). At review time, an
independent reviewer agent judges the change before it is accepted, but its rubric is generic
(*"SOLID principles adherence"*) and names neither the house style nor the pythonic or hexagonal
rules.

## decision · family F8 admitted, each item placed at its enforcement moment

Put to the operator after the discussion (source: the write-time and review-time mechanisms gzkit
already has): four moments, write time (the post-edit Ruff hook), work entry (the airlock's brief),
review (an independent reviewer with the house style as its rubric) and sweep (the chore); the
pythonic rule kept as the house style's Python chapter, its role the rubric's source text, not the
enforcement. Operator, verbatim: *"agree, specify where each will go please"*.

Ruff rule names below were read with `uv run ruff rule <code>` on 2026-11-08.

| # | Item | Canon home | Enforced at | Mechanism |
|---|---|---|---|---|
| 48 | Clarity over cleverness | pythonic rule | review | the reviewer's house-style rubric; the chore sweeps |
| 49 | Separation of concerns | hexagonal member, via the hexagonal specification run | review and work entry | the rubric; the airlock's brief names the slice's regions; the hexagonal tidying chore |
| 50 | EAFP for IO, LBYL for contracts | pythonic rule | write time, in part; review for the rest | Ruff `SIM105` (suppressible-exception) and the `TRY` family; the rubric |
| 51 | Context managers | pythonic rule | write time, in part; review for the rest | Ruff `SIM115` (open-file-with-context-handler); the rubric |
| 52 | No mutable defaults | Ruff configuration only; the rule's prose retires | write time | Ruff `B006` (mutable-argument-default), `B008` (function-call-in-default-argument) |
| 53 | No implicit globals | hexagonal member (parameter injection, F1 item 6), via the hexagonal specification run | write time, in part; review | Ruff `PLW0603` (global-statement); the rubric |
| 54 | Top-level imports only | Ruff configuration only; the rule keeps the carve-outs | write time | Ruff `I` (`I001` unsorted-imports), `PLC0415` (import-outside-top-level) |
| 57 | Extra parameters by keyword | Ruff configuration only | write time | Ruff `PLR0917` (too-many-positional-arguments) |
| 58 | Google docstrings | Ruff configuration only | write time | Ruff `D` with the Google convention, `DOC201` (docstring-missing-returns), `D417` (undocumented-param) |
| 92 | Naming conventions | Ruff configuration only | write time | Ruff `N` (`N801` invalid-class-name and the family) |
| 105 | Simplicity first | `AGENTS.md`, cited by the pythonic rule | review | the rubric; the second-adapter rule (F1 item 5) is its hexagonal instance |
| 106 | Surgical changes | `AGENTS.md` only | — | not admitted: it governs how an agent edits, not how code is designed |

Admitted: every item but 106. For adopters, each *write time* row arrives with the scaffold's Ruff
`ALL` (F4 ruling); each *review* row arrives only if the reviewer and its rubric reach the adopter,
which is untraced; each *Ruff configuration only* row means its prose leaves the pythonic rule, the
check being the authority. Commissions: the reviewer's rubric rewritten to the house style (row 4),
and the delivery of the post-edit hook and the reviewer to adopters traced (row 7).

## decision · items 48 and 53 reopened as possibly unenforceable

Operator, verbatim: *"48 is borderline unenforceable, maybe 53 is too? Don't we use tools for
59-63?"* Item 48 (clarity over cleverness) and item 53 (no implicit globals) are reopened from the F8
placement; the F9 recommendation is held on the operator's question.

## source · the tools that carry complexity

`data/astral_exceptions.json` (the `lizard` and `cohesion` entries); `.gzkit/rules/pythonic.md` § Size Limits (its enforcement table); `uv run ruff rule RUF012` · read and run 2026-11-08

> lizard: "Cyclomatic scores and module means for the C/C/C gate (GHI #1183's selection, operator 2026-10-09); Ruff C901 is per-function pass/fail with no metrics."

> cohesion: "LCOM4 class cohesion for the complexity thresholds (ADR-0.0.27); Astral ships no cohesion metric."

> | Modules <=600 | nothing reads 600; `gz check`'s "Module size" step runs `.gzkit/chores/module-sloc-cap-radon/check_module_size.py`, which enforces the table's `lizard_file_nloc` `block` band over `src/` with the shrink-only `data/module_size_grandfather.json` | 600 is authoring-time guidance only; the **live gate** is the table's band |

> `# mutable-class-default (RUF012)`

Items 60 to 63 are tool-held: Ruff `C901` (per function, pass or fail), Lizard (cyclomatic scores,
module means, function and file NLOC), gzkit's own cognitive scorer over stdlib `ast`, and cohesion
(LCOM4), Lizard and cohesion both curated exceptions with recorded reasons. Item 59 is partly held:
the class limit by gzkit's `gz validate --class-size`, modules by Lizard's file NLOC band; the rule's
50-line function and 600-line module numbers are read by no tool.

## decision · 48 set aside, 53 narrowed, family F9 admitted with the tools as authority

Put to the operator: 48 not admitted, its intent carried by the complexity gates and Ruff's `SIM`
rules and noted in the pythonic rule; 53 admitted as Ruff `PLW0603` (global-statement) and `RUF012`
(mutable-class-default), its remainder sent with F1 item 6 to the hexagonal specification run; F9's
items 60 to 63 admitted; item 59 keeping the class limit, its 50-line function and 600-line module
numbers replaced by the threshold table's bands (contradiction 8 settled for item 60's one table);
the cognitive ceiling on by default for adopters. Operator, verbatim: *"confirm"*. This supersedes
the F8 placement's rows for 48 and 53.

## decision · family F10, cross-platform and I/O, admitted whole

Operator, verbatim: *"any not worth admitting? I think I agree with admit all 11. are we now
managing and keeping these all in one place?"* Items 64 to 74 are admitted. None was found not worth
admitting; two are scoped by what a project ships: 72 (UTF-8 console at the entry point) binds a
project with a CLI, 73 (no machine-local paths in delivered text) one that ships instruction text.
Ruff checks verified with `uv run ruff rule` on 2026-11-08 for the move off the review checklist:
`PLW1514` (unspecified-encoding) for 67, `PTH118` (os-path-join) and `PTH123` (builtin-open) in the
`PTH` family for 65; 74 (`newline=""` for CSV) has no rule found and stays with 68 for the chore.

## decision · the house style has no one place yet

The operator's question, *"are we now managing and keeping these all in one place?"*, is answered no.
The rulings live in this record, which is diamond 1 and authorizes nothing; the admitted members still
sit where they were found, across eight rules, `AGENTS.md`, ADRs, `cli-standards-v3.md` and RP-9's
records (source: the candidate inventory). Row 4(a), the house style named in canon, is where one
place would come from, and its shape is now a frontier question.

## decision · the house style lives in one data register, with a page generated from it

Put to the operator: A, one data register of the members, schema-backed by a Pydantic model, each
member carrying its statement, family, enforcement moment (write, entry, review, sweep), the exact
check that holds it, whether `gz init` delivers it and its owner; a validator failing any member whose
named check does not exist or runs on no gate; one canon page generated from the register; rules and
`AGENTS.md` citing members by id instead of restating them. B, one canon page as the home. C, members
left where they are, with an index. Operator, by selection: *"A register plus one page
(Recommended)"*. The register's file name is illustrative until diamond 2.

## decision · family F11, CLI shape, admitted whole, with three fixes

Operator, verbatim: *"admit all, fix 76, 82, 87"*. Items 75 to 85 and 87 are admitted, scoped to
projects with a CLI. The three fixes, as recommended:

- **76** (`--json` on every leaf, *"Live, UNMET"*): closed by giving each leaf without it the flag or
  a waiver with rationale. The RP-7 change-order record measured 73 of 180 leaves without `--json`
  (its finding F18, deferred to the CLI rule's placement); the work joins row 5.
- **82** (seven obligations per new subcommand): binding for gzkit, offered to adopters as a
  suggestion, since its manpage, runbook and skill obligations come from gzkit's own docs model.
- **87** (config loaded once at the CLI boundary, injected inward): sent to the hexagonal
  specification run with F1 item 6, the composition root.

## decision · family F12, testing, admitted whole, with its fixes

Operator, verbatim: *"roger, all 11. yes, that is gzkit contract - no pytest ever. 100's 40%,
agree... make it so. Chore should not be named as such. 98 and 102, fix"*. Items 20, 91 and 96 to 104
are admitted.

- **20:** *"no pytest ever"* is gzkit's contract and the house style's, for every adopter; the
  `forbid-pytest` hook is to reach adopters through `gz init`, which the inventory could not confirm
  (the scaffolded pre-commit declares only the pre-push `gz check`).
- **100:** the coverage floor becomes a value in data, read by a gate, instead of a number in Markdown
  checked by a chore; its level is not ruled, only *"maybe higher"* recommended. The chore
  `coverage-40pct` is renamed: a name must not carry the value it checks, which then drifts from it.
- **98 and 102:** their measurable parts (no network or external services; a unit test under 200 ms)
  are to be enforced by the test runner, not left as rule text.

## decision · family F13 admitted; item 86 made explicit

Operator, verbatim: *"agree on 88, 95, 107 and 108. Agree on 86, but make explicit as much as
possible. agree on 94."* Items 86, 88, 94, 95, 107 and 108 are admitted, 94 for gzkit and for
adopters once RP-13 defines a mode contract outside gzkit.

Item 86, *"JSON everywhere"*, made explicit from the rulings already taken, one kind of fact to one
format and home:

| Kind of fact | Home | Format | From |
|---|---|---|---|
| How the project's code is designed (the architecture map, the cognitive ceiling, later members' values) | `pyproject.toml` `[tool.py-gzkit]` | TOML | Q8, Q15 |
| Tool configuration (uv, Ruff, ty, coverage) | `pyproject.toml` `[tool.<tool>]`, never a competing tool file | TOML | RP-15; F7 item 41 |
| gzkit's governance settings for the project | `.gzkit.json` | JSON | Q8 |
| Registers, baselines and thresholds a gate reads | `data/*.json` | JSON | F6 item 43; F9; RP-9 |
| Events and transitions | `.gzkit/ledger.jsonl` | JSON Lines | `docs/governance/state-doctrine.md` |
| Schemas | generated from Pydantic models, never hand-written | JSON Schema | F2, *"models first"* |
| Front matter of Markdown records | in the record | YAML | F2, pyyaml admitted |
| Third-party files that dictate their own format (`mkdocs.yml`, CI workflows, `.pre-commit-config.yaml`) | where that tool reads them | YAML | — |
| A value in prose | nowhere authoritative | Markdown | item 88 |

Family F13 is complete; the 14 borderline items remain.

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | commissioned | The upfront whole-system architecture map, approved once as a classic ADR (the first map edition); and the new machinery admitted at civil rule through the R&D door as catalog outcomes: the map as data under `[tool.py-gzkit]`, the intake signal, the freeze check, the airlock feed, `gz init` delivery to adopters | The map passes the admission question: hard to reverse, surprising without context, a real trade-off. Proposed only: the operator initiates. It waits for the classic ADR form and crossover (CO-1, CO-2 on RP-6) |
| 2 | GHI / direct fix | commissioned | Under RP-7's placement change order: book H1 ruled to the whole package with a shrink-only baseline, and repair F22 so the boundary test runs in the per-change `gz check`; and the `gz init` scaffold's Ruff selection raised from nine families to `ALL` with gzkit's curated exceptions and ty at full strength, its default project type moved from `lib` to uv's `app`, the cognitive ceiling on by default rather than opt-in, and the `forbid-pytest` hook delivered; both corrections of RP-9 tranche 7 (closed), their owner to be ruled | Corrections of shipped intent (decision: corrections go into the drydock under RP-7); both already tracked there, so no new GHI |
| 3 | chore | commissioned | A hexagonal tidying chore: the implementation-mode audit of what neither gate nor door judges (ports typed in domain terms, policy kept out of adapters, construction at the edge), after gz-skills' `gzs-hexagonal-architecture-audit`, findings filed as GHIs; and a hygiene chore keeping `docs/design/cli-standards-v3.md` current (F2, item 11) | The third reach the operator ruled (*"chore tidyings"*); advise only, the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | commissioned | (a) the house style named in canon as one data register of its members, each with statement, family, enforcement moment, named check, adopter delivery and owner, a validator over it, and one page generated from it, rules and `AGENTS.md` citing members by id; (b) the hexagonal rule cut to its judgment residue once gate, doors and chore carry the rest (RP-7 placement); (c) the canon page's § Departures *"not a code-organization rule"* reconciled with *"primary code directive"*; (d) the design-time imperative written into the design surfaces; (e) `data/waiver_ratchet_registry.json` given an owner, a close-at-zero plan and a target date per shrink-ratchet, the 29 non-empty ones each owned or ruled accepted debt; (f) the `quality-reviewer` agent's rubric rewritten to the house style, the pythonic rule its Python source text, and the rule's prose retired wherever a Ruff rule is the check (F8); (g) the pythonic rule's size numbers replaced by the threshold table's bands, and item 48's intent noted as carried by the complexity gates (F9); (h) the coverage floor moved into data and read by a gate, the `coverage-40pct` chore renamed, and the test runner enforcing no network and the 200 ms unit limit (F12) | Drafted on the operator's go per item |
| 5 | one-shot refactoring | commissioned | gzkit's import sites outside their mapped region driven to zero through the shrink-only baseline; the cognitive ceiling moved from `.gzkit.json` to `[tool.py-gzkit]`; jsonschema retired, each hand-authored schema given a Pydantic model and every validator calling the model, the dependency and its register entry removed at the last site; rich behind the output port, every direct `console.print` routed through `OutputFormatter` with semantic calls and the port made domain-typed; every `# noqa` converted to `# ruff: ignore[<rule name>]` as RUF105's exception is lifted; every CLI leaf given `--json` or a reasoned waiver (F11 item 76; RP-7 finding F18) | The whole-package scope and the split config home, ruled; the operator selects the route |
| 6 | no action | not pursued | Registering `gzkit` on PyPI | The operator chose `[tool.py-gzkit]`; revisit if the CLI's name and the distribution's are ever unified. (Folder partitions, listed here first, withdrawn 2026-11-08: the operator disagrees with canon rule 7 now, and the question moves to row 7(c).) |
| 7 | further research | commissioned | (a) withdrawn: the other candidates are admitted in this run; (b) an intent trace of ADR-0.33.0's airlock: no production caller supplies `parent_invariants`, and reach is the ontology graph, not imports; (c) a hexagonal specification run: domain-typed ports, Protocol and composition, the second-adapter rule, parameter injection, folder layout (canon rule 7, which the operator now disagrees with), what subsumption into one typed model means, and the DDD and ontology relation, briefed by *"strengthen"* and strong adoption by every adopter; (d) whether `gz init` delivers the post-edit Ruff hook and the reviewer agent to adopters | (b) opened by the read of what the doors are fed; (c) opened by the F1 rulings. The operator opens each |

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
