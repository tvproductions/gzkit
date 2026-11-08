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

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | | | |
| 4 | control surface, rule, doc, skill, hook | | | |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |
| 7 | further research | | | |

## Close

**Challenge restated.** —

**Frontier.** —

**Review.** —

**Sign-off.** —

## What this record does not license

No ADR, OBPI, chore, rule, gate or change order is started by this run. Every row awaits the
operator's go on that row.
