# R&D run — hexagonal-specification

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-11-08T21:36Z.

**Challenge.** Opened by disposition row 7(c) of the house-style run
([`house-style.md`](house-style.md)), on the operator's *"Proceed with 7(c)"* (booked through
`gz handoff decide` against `.gzkit/handoffs/20261108T213120Z-house-style-hex-spec-next.md`).
The operator's words on family F1, item 1, the primary hexagonal directive, verbatim:

> *"and we need a better specification. I'd like for a strong adoption - for all adopters too. strengthen"*

The rest of the F1 rulings that send their subject here, verbatim:

> 3. yes, but that is ha core - we'll want some rnd to define this it seems
> 4. yes, see the need to rnd ha spec
> 5. yes, again, rnd
> 6. yes, but we need ha rnd.
> 7. I disagree with this now.
> 8. I am not sure what this mean, ha rnd
> 10. yes, sounds like ddd/ontology ha rnd work. I agree with this whole thing

And the operator's correction that frames the whole run, verbatim:

> *"Don't forget that not all hex architecture is core. It's the entire system. So we've got to
> either do upfront design or just be mindful of at designing time when we add, what the current
> big picture of the architecture is."*

---

## source · the house-style run's rulings, as this run's inputs

[`house-style.md`](house-style.md) · read 2026-11-08 (the challenge, the F1 entries, the
whole-system correction, the upfront-map and freeze decisions, and the disposition map)

> (c) a hexagonal specification run: domain-typed ports, Protocol and composition, the
> second-adapter rule, parameter injection, folder layout (canon rule 7, which the operator now
> disagrees with), what subsumption into one typed model means, the DDD and ontology relation, the
> remainders of items 49 and 53, config loaded once at the boundary (item 87), and layered state
> with an append-only event log (borderline B9), briefed by *"strengthen"* and strong adoption by
> every adopter

> *"Upfront map, kept current (Recommended)"* · *"At the freeze (Recommended)"*

Entered as a source, not as decisions of this run. The house-style run settled that hexagonal is
the house style's first member, that it names the whole system, that the whole-system map is drawn
up front as data, approved as a classic ADR and enforced at the work package freeze, and that
code-design facts live in `pyproject.toml`'s `[tool.py-gzkit]`. This run specifies what that map
and the member contain; it does not re-open those rulings.

## source · the hexagonal rule

`.gzkit/rules/hexagonal-architecture.md` (rule version 0.4.1) · read in full 2026-11-08

> 1. **Dependencies live in adapters, never in the core.** [...] Core domain logic imports **stdlib + Pydantic ONLY**.

> 5. **Encapsulate first; formalize the port when the SECOND adapter is real.** [...] One adapter → no formal port yet (a port ABC over a single impl is speculative generality).

> 7. **`core/` stays; do NOT add `domain/`/`application/`/`adapters/`/`contexts/` folder partitions to "do DDD."** Hexagonal governs the boundary, not internal layout [...]. Bounded contexts are **subgraphs of the ontology** (corpus / work / source), not directories.

> 8. **Prefer subsumption to a parallel model.** A new domain type joins the ontology's `OntologyNode`/`OntologyEdge` type system; never stand up a second, differently-typed representation of the same objects

> Neither `gz lint` nor `gz typecheck` checks an import boundary; `tests/policy/test_import_boundaries.py` is the witness, and it covers `src/gzkit/core/` only.

The rule names no region beyond "core" and "adapter", and its witness covers one directory.

## source · the hexagonal canon page

`docs/governance/hexagonal-architecture.md` · read in full 2026-11-08

> | 1 | **App / System / Hexagon / Core** | All business logic, technology-agnostic [...] | 2 | **Ports** | The app's true boundary; each is a set of interactions with one *intention*, named "For &lt;verb&gt;-ing" [...] In Python ports aren't declared — a port is "all the calls the app makes" at that seam. | 3 | **Actors (driving / driven)** [...] | 4 | **Adapters** | Code that fits an actor's interface to a port; lives *outside* the app [...] | 5 | **Configurator** (5th, officially outside) | Instantiates driven adapters, instantiates the app injecting them, then instantiates driving adapters passing the app (Fig 2.1)

> **Not part of the pattern at all:** how the app is structured *internally* (DDD or not, function-vs-model or not).

> 3. **gzkit makes the port/adapter distinction structural, not architectural.** [...] This is a conceptual borrowing, not a code-organization rule.

The canon page maps Cockburn's five elements onto gzkit; its § Departures item 3 contradicts the
primary-directive section (house-style row 4(c)).

## source · the gz-skills hexagonal audit

`tvproductions/gz-skills` at `cfb34f8d2b6e6eebb268581ac07664a6b8074ebf`, `skills/gzs-hexagonal-architecture-audit/SKILL.md` and `references/audit-criteria.md` · read in full 2026-11-08

> - **Domain policy:** business meaning, invariants, decisions, and rules [...] - **Application behavior:** use-case orchestration [...] - **Inbound ports:** application-owned entry contracts [...] - **Outbound ports:** application-owned contracts [...] - **Driving adapters:** [...] - **Driven adapters:** [...] - **Composition root:** outer wiring that selects and constructs concrete adapters [...] - **Anti-corruption layer:** an owned translation seam

> An interface, a folder named `domain` or `adapter`, a dependency-injection container, or a diagram is not by itself evidence of a boundary.

> 10. **Promised boundary without acceptance witness:** a declared hexagonal direction or isolation rule lacks a test or check capable of detecting its collapse.

An eight-part component model and ten implementation failure classes, written for any language.

## source · the output formatter

`src/gzkit/cli/formatters.py` · read in full 2026-11-08

> `from rich.console import Console` · `from rich.table import Table` · `def table(self, rich_table: Table) -> None:` · `def emit_table(self, rich_table: Table) -> None:`

The output chokepoint's methods take Rich's native `Table`: the port is not domain-typed (rule 3).

## source · the airlock model and its call sites

`src/gzkit/airlock/model.py`, `src/gzkit/airlock/enter.py` · read in full 2026-11-08; `git grep -n 'TransitSlice(\|parent_invariants'` · run 2026-11-08

> `def _default_reach(node_id: str) -> list[str] | None:` [...] `Lazily imports the ontology surface so the core stays exercisable with NO projection built (hexagonal rule 6) — tests inject a fake ``reach_fn``.`

> `reach_fn: Callable[[str], list[str] | None] = _default_reach,`

Call sites: `airlock/enter.py:87`, `airlock/exit.py:241` and `:347`, `work_package_transit.py:127`
(which passes no `parent_invariants`). The airlock takes its reach as an injected callable, a port
shaped as a parameter, and its reach is the ontology graph, not imports.

## source · the ontology model

`src/gzkit/ontology/model.py` · read in full 2026-11-08

> `class ObjectType(enum.StrEnum):` [...] `PRD`, `CONSTITUTION`, `ADR`, `OBPI`, `REQ`, `GHI`, `RECEIPT`, `DOC`, `TASK`, `CLI_VERB = "CliVerb"`, `VALIDATOR`, `SKILL`, `CHORE`

The ontology seats governance objects and a few product objects; no Python module and no
architectural region is an object type.

## source · the import-boundary witness and the dependency spread

`tests/policy/test_import_boundaries.py` (767 lines, outline read 2026-11-08); `pyproject.toml` `dependencies`; `git grep -lE` per package over `src/gzkit/**/*.py` · run 2026-11-08

> `CORE_DIR = SRC_ROOT / "core"` · `CORE_ALLOWED_THIRD_PARTY = frozenset({"pydantic"})` · `CORE_FORBIDDEN_STDLIB = frozenset({"argparse"})`

> `rich 61` · `networkx 1` · `jinja2 2` · `jsonschema 6` · `yaml 12` · `pydantic 134` (files importing each; tree-sitter not counted by this pattern)

The package has 128 top-level modules and 29 subpackages. Only `core/` is held to a boundary;
Rich is imported in 61 files.

## decision · question 1 put and not answered; the run slows down (operator correction)

Put to the operator: what regions the whole-system map has. A, four regions (core, driving adapter,
driven adapter, composition root), ports as domain-typed contracts between them; B, Cockburn's five
with ports as a region; C, gz-skills' eight-part model. Operator, verbatim, in place of an answer:
*"let's slow down and go slower in terms of what you are asking, are we shaping the specification
of our hex arch implementation?"*

The question came before the run had said plainly what it shapes. It is withdrawn until the
framing is confirmed. Booked as insight `2026-11-08T21:40:27Z` (scope `skill/gz-rnd`).

## decision · the run steps through hexagonal's parts, phases and steps, agreeing each

The agent's framing (a specification of what hexagonal means in gzkit, precise enough to judge
code against, for gzkit and every adopter) was put; the operator answered *"Not quite"*, then gave
the run's method, verbatim:

> *"let's step through hexagonal architecture parts, phases, and steps and agree on things. I might
> ask questions or counter design preferences."*

So the run walks the pattern piece by piece. For each piece the agent sets out what the source says
and what gzkit has, and states a design preference. The operator agrees, asks or counters, and each
agreement is entered here as it lands. The walk: the parts (Cockburn's five elements, source: the
hexagonal canon page), then the steps that wire them (the configurator's order, Fig 2.1), then the
phases of gzkit's work where hexagonal is applied.

## decision · the parts, the transformation sequence and the core's contents (operator ruling); the run's question set

Part 1, the core, was put as Cockburn's App: every module holding governance meaning, wherever its
file sits, importing stdlib and Pydantic only. The operator answered with the parts to agree on, the
sequence for transforming existing code, what the core holds, and the run's questions. Verbatim:

> *"let's agree to parts: primary (driving) adapters, input ports, input handler/services, domain
> entities, output ports, secondary (driven) adapters. DDD relationships when we are transforming
> existing code: extract domain logic, entities, and ubiquitous language; define port interfaces in
> domain language; wrap/facade code (existing usually) behind ports; refactor into handlers (if
> existing code); swap facades for real adapters.*
>
> *Things in the domain layer (the core): entities, value objects, aggregates, domain services.*
>
> *principles (you seem to have them too): purity, encapsulation, completeness (you used different
> terms we need to reconcile.*
>
> *Always-valid domain models (Pydantic can help here?). Pydantic would need to emulate frozen
> dataclasses to work too. let's discuss value objects. Let's agree that sometimes business logic
> necessitates domain services. Do we want to create factory methods when config matters? This is
> about establishing identity at instantiation.*
>
> *Pydantic should help with validation: input/creation validation and business invariant
> (semantic) validation. How do we establish consistency/business rules guards?*
>
> *Shall we entertain Command and Query objects?*
>
> *what is the value of end-to-end use cases for validation of business invariants?*
>
> *How do we identify errors (likely validation) in the domain?*
>
> *Do we want command, query, and message bussing?*
>
> *Shall we design/accommodate domain events and handling?*
>
> *what about aggregates and bounded contexts?*
>
> *DTOs and repositories?*
>
> *what about core isolation via mapping? (maybe it is dataclasses within core?)*
>
> *If mapping, one way? two-way? A bridge?*
>
> *What about core module/package design (Python)?*
>
> *Can the uv-build system help with boundary/package/module enforcement?*
>
> *How will bootstrapping work? how does gzkit's init help there? how much design is needed before
> anything else can proceed?*
>
> *can we enforce immutability/readonly when needed?*
>
> *How can some events (integration events?) become known outside the core? maybe message queues?
> inbox/outbox?*
>
> *Can we test and validate the architecture to prevent decay/drift?*
>
> *How will we handle config and properties? adopter config? gzkit config? merged config?*
>
> *How will we ensure dependency control?*
>
> *Can strict stdlib use in core become a dependable shared kernel?*
>
> *How do we prevent core bleedthrough? (we have it now).*
>
> *Perhaps we layer: shared kernel -> domain -> application/handlers -> adpaters as a strict chain?*
>
> *Can we use decorators to help?*
>
> *Do we want structural enforcement between the key components (commands, queries, input/output
> ports, domain entities, handlers, adapters)?*
>
> *Shall DDD results drive naming rules?*
>
> *What should we do if we find an integrity violation within the core?*
>
> *How shall we employ BDD and TDD?*
>
> *How shall we do mocking (if at all?)?*
>
> *How shall we define known external contracts? synchronous calling? event-driven integration?
> orchestration?*
>
> *Those are the initial questions I have."*

Settled by the operator's words:

- **The parts are six:** primary (driving) adapters, input ports, input handlers or services, domain
  entities, output ports, secondary (driven) adapters. This replaces the agent's walk of Cockburn's
  five elements; part 1 as put is withdrawn.
- **The domain layer, the core, holds** entities, value objects, aggregates and domain services.
- **Domain services are admitted:** *"sometimes business logic necessitates domain services."*
- **Transforming existing code runs in five steps:** extract domain logic, entities and ubiquitous
  language; define port interfaces in domain language; wrap or facade the existing code behind
  ports; refactor into handlers; swap facades for real adapters.

Not yet settled: the principles' names (*purity, encapsulation, completeness*) against the agent's
terms, which the operator asks to reconcile; every question in the list above.

A canon conflict is noted here, not ruled: the operator's *"maybe it is dataclasses within core?"*
meets `.gzkit/rules/models.md`, *"Use **Pydantic `BaseModel`** for all data models; no stdlib
`dataclasses`."* It is put to the operator, quoting both, when that question is reached.

The agent's grouping of the questions into a design tree, a draft that binds nothing until the
operator has seen it: (A) vocabulary and principles; (B) the domain layer: value objects, always-valid
models, identity and factories, the two kinds of validation, guards, domain errors, immutability,
integrity violations; (C) core isolation: mapping, DTOs and repositories, package design, the
layered chain, the shared kernel, bleed-through; (D) the application layer: commands and queries,
handlers, the bus, domain events, aggregates and bounded contexts, end-to-end use cases; (E) the
edges: integration events and inbox/outbox, external contracts, configuration, bootstrapping and
`gz init`; (F) enforcement and verification: uv-build, decorators, structural enforcement between
components, architecture tests, dependency control, BDD and TDD, mocking; (G) transforming gzkit
itself through the five steps. A comes first, because every later answer is worded in its terms.

## decision · the operator's sources are Cosmic Python and Montenegro; the agent's Khorikov guess is withdrawn

Put to the operator: which texts the terms are drawn from, the agent guessing Khorikov and Cosmic
Python. Operator, verbatim: *"cosmic but also Montenegro's "Clean Applications with Hexagonal
Architecture" MEAP (its Java Centric). I have used cosmic python, I do not know the other source you
listed)."*

So the run reads two texts: Percival and Gregory, *Architecture Patterns with Python* (Cosmic
Python), and Enrique Medina Montenegro, *Clean Applications with Hexagonal Architecture* (Manning
MEAP V01, 184 pages, Java-centric; the operator's licensed copy, held outside the repository).
Khorikov is not the operator's source and enters nothing. The principles' names (*purity,
encapsulation, completeness*) are taken from whichever of the two uses them, once read. Because
this repository is public and the MEAP is licensed, its source entries cite chapter and page with
short quotations only; the book is never copied in.

## decision · Cockburn's book is a third source; its text is held in Kindle form

Operator, verbatim: *"there's also "Hexagonal Architecture Explained" from Cockburn, which I have in
Kindle form"*. So the run reads a third text: Alistair Cockburn and Juan Manuel Garrido de Paz,
*Hexagonal Architecture Explained* (Humans and Technology Press, 2024, ISBN 978-1-7375197-8-2).

What the agent can reach: the figures companion the canon page already cites,
<https://alistaircockburn.com/figs%20hexarch%20book.pdf>, fetched 2026-11-08 (56 pages, *"The
figures from the Preview Edition of Hexagonal Architecture Explained"*, V0.9a 20240507-1836). It
carries the figures and their captions, not the book's text. The Kindle edition is DRM-protected;
the agent does not work around that, so the text reaches the run through the operator.

Put to the operator: how the Kindle text reaches the run, the operator pasting passages as a
question turns on them, or the figures companion for now. Operator, by selection: *"Figures PDF
for now"*.

## source · Cockburn and Garrido de Paz, the figures companion

<https://alistaircockburn.com/figs%20hexarch%20book.pdf> (V0.9a 20240507-1836, 56 pages) · read
2026-11-08: every caption, with figures 2.1 to 5.2 and 6.18 to 6.28 viewed as images; the others
(the ACL, CQRS, Strategy, Adapter and Observer figures, 5.3 to 5.8 and 6.1 to 6.17, 6.29 to 7.1) by
caption only. Figures and captions only; the book's text is not in it.

> *"Figure 5.2. Ports & Adapters only specifies two layers, inside and outside."*

The work is copyrighted (*"©Alistair Cockburn 2024 all rights reserved"*), so the remaining figures
are cited by number with paraphrase only:

- Figure 5.2's labels leave the organization of each layer to the designer and note that a port is
  only an interface, with no depth of its own in a layer diagram.
- Figure 4.6, captioned as the suggested folder structure, shows a .NET solution of five projects:
  a file adapter and a mock adapter as separate projects, the application project with folders for
  driving ports, driven ports and services, an API project holding the controllers and startup, and
  a test project.
- Figures 6.24 and 6.25: the sender owns the interface it requires, and receivers can sit in other
  modules; the reverse, where the receiver owns the interface, is shown as the case to avoid.
- Figure 4-7: the development sequence puts tests and mocks first.
- Figure 3.1: the BlueZone example names its ports *For ...-ing* (parking cars, obtaining rates)
  and sets a test double (stub, fake or spy) beside each driven port's real adapter.
- Figures 6.26a, 6.26b and 6.28: the configurator tells the application which adapter to use, or the
  application asks it, or main provides a broker that looks adapters up.

What bears on the run, read from the figures alone and to be checked against the text when it is
in reach: the pattern has two layers, and their inside layout is left to the designer; the
application owns its ports; tests and test doubles come first; and the authors suggest a folder
structure that puts each adapter in its own project and the ports in named folders. That last one
meets canon rule 7, which cites Cockburn *against* folder partitions (source: the hexagonal rule).

## source · Montenegro, *Clean Applications with Hexagonal Architecture* (MEAP V01), the reading report

A research report of all 184 pages of the operator's licensed copy · read 2026-11-08. Held outside
the repository by the operator's ruling (see the decision *Montenegro-derived reports stay out of the
repository*). The MEAP holds chapters 1 to 6 and Appendix A; chapters 7 to 14 are titles only. What
bears on group A, cited to the book:

- the book's six standard components (§2.3, Table 2.1, PDF pp.32–33) are the operator's six parts,
  in the same order, the book saying *handler* or *application service* where the operator says
  *input handlers/services*, and *input/output adapters* from chapter 4 on;
- purity, encapsulation and completeness are named together as the three principles that shape the
  domain (§3.2, Table 3.1, PDF pp.47–48), the book saying that perfect adherence to all three is not
  realistic; the *CEP theorem* it promises for trading them off is not in this MEAP;
- the five-phase migration map, *Extract, Define, Wrap, Refactor, Replace* (§2.4, PDF pp.36–40), is
  the operator's five steps one for one; §1.2.6 orders handlers before the facade wrap, and phase 1
  does not name *ubiquitous language*.

## source · Montenegro's companion repository

<https://github.com/emedina/hexagonal-architecture-manning> at `74e3b48a66f9aa91b0a22021708f84325af0180b`
(Apache-2.0) · `README.md` and the chapter 3 to 9 `README.md` files read in full, the chapter 7
and 8 `LISTINGS.md` read in full, 2026-11-08. Pointed to by the operator: *"Montenegro's companion
repo"*.

> `ch07-archunit/README.md`: *"Dependency enforcement: allowlists for inner layers, denylist for adapters"* · *"Annotation enforcement: required (`@UseCase`, `@ApplicationService`), forbidden, allowed-or-none"* · *"Structural enforcement: interfaces for ports, `validateThenCreate` contract, no public default constructors"* · *"Naming conventions: `XUseCase` → `XHandler`"* · *"`FreezingArchRule` for incremental adoption"*

> `ch08-testing/README.md`: *"Handler recipe: mock ports, stub responses, verify interactions"* · *"BDD structure: `// given` / `// when` / `// then` inline comments"*

> `README.md`: *"Companion code for **Clean Hexagonal Architecture with Java and Spring Boot** (Manning Publications, forthcoming)."*

The repository carries the chapters the MEAP lacks, enforcement (7) and testing (8), as listing
maps to code in its submodules (`architecture-kernel`, `archunit-hexagonal`,
`hexagonal-spring-ref-app`, the bus starters); the code itself was not read. It names the book
*Clean Hexagonal Architecture with Java and Spring Boot*, a different title from the MEAP's.
Chapter 7's freeze mechanism is the same shape as gzkit's shrink-only baselines.

## decision · the Montenegro copy the run read is V01, through chapter 6; the operator's MEAP reaches chapter 10

Operator, verbatim, on the report's statement that the MEAP holds chapters 1 to 6: *"no, the meap goes
up to chapter 10"*. Checked against the file: the copy in the operator's Downloads is MEAP V01 (PDF
metadata *"MEAP V01"*, modified 2026-10-05), and its chapter bodies begin at PDF pages 26 (ch. 2), 73
(ch. 4), 111 (ch. 5) and 144 (ch. 6), with Appendix A at page 171; its table of contents lists 14
chapters. So the reading report is correct about that file, and the operator's statement is about a
later MEAP release. Chapters 7 to 10 (enforcement, testing, the WriteFlow build, integration modes)
are not yet read; until they are, the report's *"not in this MEAP"* findings hold for V01 only.

The operator then supplied MEAP V02 (352 pages, PDF metadata *"MEAP V02"*), held beside V01 outside
the repository. A page-by-page text diff of PDF pages 1 to 170 against V01 finds three changed pages
(2, 81, 160), each a version stamp or a single space, so chapters 1 to 6 are unchanged and the V01
report stands for them. V02 adds chapter 7 (p.171), chapter 8 (p.215), chapter 9 (p.254) and
chapter 10 (p.324), with Appendix A at p.339. *"CEP"* occurs once in V02, so the trade-off theorem
promised in §3.2 is still not delivered. A reader is on chapters 7 to 10.

## source · Montenegro MEAP V02, chapters 7 to 10, the reading report

A research report of V02 PDF pages 171 to 352 · read 2026-11-08. Held outside the repository by the
operator's ruling (see the decision *Montenegro-derived reports stay out of the repository*). What
bears on the run, cited by chapter:

- chapter 7 enforces four rule families (dependencies by allowlist for inner layers and denylist for
  adapters, stereotype placement, structural shape, one naming rule), configured in data and adopted
  through a committed freeze store that only shrinks;
- chapter 8 gives one fixed test recipe per artifact type, given/when/then as comments, fakes allowed,
  domain objects never mocked; no TDD and no Gherkin; no automated end-to-end tests;
- chapter 9 builds inside out (domain, ports, handlers, adapters, composition root, verification),
  names the *composition root*, keeps the aggregate always valid but not immutable, and guards the
  `reconstitute` back door with a project-specific architecture rule;
- chapter 10 separates integration direction from requests and facts, gives three integration
  modes (synchronous, event-driven, orchestrated) and a contract map per bounded context;
- purity, encapsulation and completeness get no new definition, and the CEP theorem is still absent.

## decision · Montenegro-derived reports stay out of the repository (operator ruling)

Operator, verbatim: *"that should NOT go into the repo - it is copyrighted material with my name on
it."* The two Montenegro reading reports were removed from `sources/` before any commit and are held
outside the repository with the licensed copies. The book is cited here by chapter, section and
page only, with the operator's licensed copy as the place to read it. No report carried the
licensee line; checked with a search for the operator's name and address, no hit.

Operator, verbatim, following: *"montenegro's pdf should not be retained as sources. perhaps key notes
from it can."* So the run keeps no Montenegro text, report or excerpt; the two source entries above
are the key notes, each a short paraphrase cited to chapter, section and page.

## decision · purity means Montenegro's; the run tightens gzkit onto classic hexagonal and imposes it on adopters (operator ruling)

Put to the operator: purity applied to the whole domain layer, or to entities and value objects only,
the import rule kept as the outer check. Operator, verbatim:

> *"it seems that Montegro's is more consistent with canonical hexagonal arch. so real purity
> matters/means more for this rnd.*
>
> *I would think we would want a correct hexagonal design and impute that design on adopters (like
> Django, gzkit is opinionated).*
>
> *Your OR there is false, we rely on domain services and ports to touch the outside anyhow. The
> point of this rnd is to TIGHTEN UP on classic/pure hexagonal as I think the implementation has been
> vibe coded thus far."*

Settled: *purity* in this specification is Montenegro's (§3.2, Table 3.1: a method depends only on its
inputs, has no side effects, returns the same output for the same input), which agrees with
Cockburn's strong form (source: the hexagonal canon page) and Cosmic Python's functional core
(source: the Cosmic Python report). The import rule is not purity and needs its own name. The run's
aim is a correct, classic hexagonal design, imposed on gzkit and on every adopter, as an opinionated
framework imposes its shape. The operator judges the present implementation vibe coded.

Put back to the operator, not yet settled: who touches the outside. Montenegro's domain service is
pure; the handler gathers what it needs through output ports and passes it in, and the domain
service needs no interface and no mock (§3.5 and Listings 3.12–3.13, PDF pp.61–63, read by the agent
in the operator's licensed copy 2026-11-08). On that reading only handlers call ports; domain services
and entities do not.

## decision · strict hexagonal, for every project built with gzkit, whatever its size (operator ruling)

The agent's input was put: the strict chain (handlers the only callers of ports; domain services,
entities and value objects pure; adapters holding all I/O; the composition root wiring); the
evidence that the present implementation drifted (rule 5 against Cockburn's test double as an
adapter, rule 7 against Figure 4.6, the formatter port taking Rich's `Table`, the airlock mixing
decision and I/O, one boundary witness, the canon page contradicting itself); and the gz-skills
audit's right-sizing against imposition on adopters. Operator, verbatim:

> *"1. I want strict*
> *2. Yes, the vibe coding is runaway out of control*
> *3. I am not sure, what is the harm of hex regardless of size? I've since developed gz-skills,
> gz-skills-first-starter template, and Superpowers-Backplane for lighter-weight projects, so why NOT
> just adopt a dependable hex arch?"*

Settled: the specification is strict. Hexagonal applies to every project built with gzkit regardless
of size; lighter projects have their own tools (gz-skills, the gz-skills-first-starter template,
Superpowers-Backplane), so gzkit carries no right-sizing exemption. The gz-skills audit keeps its
own Not Applicable verdict for the projects it serves; that is gz-skills' posture, not gzkit's.
This tightens the house-style ruling that admitted *Not Applicable only with a reason*: within gzkit
the reason no longer exists. The handlers question (only handlers call ports) is held for
discussion against a triangulated set of sources.

## decision · the core triangulation set of sources (operator direction)

The agent proposed a core set: Cockburn, Montenegro, Cosmic Python, Evans and Vernon, with Khorikov for
purity and testing, and the Pydantic, uv and PEP 544 texts read only when their questions arrive.
Operator, verbatim: *"He also has the "art of unit testing" do we need those? I have evans, I think I
have vernon. On handlers, let's discuss. Let's triangulate on a few solid sources and sort through from
those. What else do we need? sources wise?"* The agent advised that *The Art of Unit Testing* is not
needed beside Khorikov's *Unit Testing Principles, Practices, and Patterns*. The operator then supplied
that book (Manning, the operator's licensed copy, held outside the repository). It is read under the
same terms as Montenegro: a report kept outside the repository, key notes only in this record. Evans
and Vernon await the operator's copies.

Operator, verbatim, following: *"I don't have vernon, I do have khononov's "Learning Domain-Driven
Design" - also Kindle."* So Vernon leaves the set and Vlad Khononov's *Learning Domain-Driven Design*
(O'Reilly) joins it. Evans and Khononov are held in Kindle form, which the agent does not work around:
their text reaches the run as passages the operator pastes, each requested by the agent when a question
turns on it and entered as a short cited key note. Until a passage is read, nothing attributed to
either book becomes a decision.

## source · Khorikov, *Unit Testing Principles, Practices, and Patterns*, key notes

Vladimir Khorikov, Manning, ©2020; the operator's licensed copy, read in full by a reader 2026-11-08;
the report is held outside the repository. Key notes, paraphrased, cited by section and PDF page:

- The book's hexagon has two layers, domain and application services; it calls the application
  service a *controller* and has no port or adapter vocabulary (§5.3.1, pp.128–131).
- Domain classes depend only on in-process collaborators. They must not reach out-of-process
  dependencies, not even through an interface; only the application service does (§7.2.2–§7.2.3,
  p.182). The application service is a Humble Object: thin, holding no decisions (§7.1.2, pp.177–180).
- Functional architecture (a pure core, a shell that only acts) is hexagonal taken to its extreme;
  hexagonal tolerates a domain object changing its own in-memory state, never persisting itself
  (§6.3.3, p.156).
- When a decision needs more data mid-way, the book weighs domain testability, controller simplicity
  and performance, one of which is always conceded. It rejects injecting dependencies into the domain
  and prefers splitting the decision into steps the controller runs, guarded by CanExecute/Execute
  and domain events (§7.4, pp.191–200).
- Domain events are values collected by the domain object; the application service dispatches them
  after the operation (§7.4.2, pp.197–200).
- Mocks are for unmanaged out-of-process dependencies only (those other systems observe, such as a
  bus or mail), in integration tests, verified at the system's edge, on types the project owns; the
  application's own database is managed and is used for real (§8.2, pp.212–215; §9.1–§9.2, pp.241–249).

## decision · the handler rule put and opened for discussion

Put to the operator, triangulated across Montenegro, Cosmic Python, Khorikov and Cockburn's figures:
the domain never holds a port, not even as an interface; the handler is the only caller of ports;
mid-decision data comes by splitting the decision (CanExecute/Execute), never by injection; domain
objects may change their own in-memory state and record domain events, never dispatch them.
Operator, by selection: *"Let's discuss"*. Open.

## decision · the constellation of agreement: four sources for hexagonal, two for DDD

The operator asked which sources make the *"constellation of agreement"*. The agent proposed six, each
governing what it is strongest on, and a settling rule: a point is agreed when its governing sources
agree and none of the others contradicts them; where they disagree, the governing source leads and
the operator rules. Operator, verbatim: *"they are both DDD, so we'll bring them in for that when
needed (which the core does). So we are down to four for Hex?"*

Settled, the agent confirming the operator's count:

- **Hexagonal, four sources:** Cockburn (what the pattern is: inside and outside, application-owned
  ports, the configurator, test doubles as adapters); Montenegro (the operator's vocabulary and the
  classic inside structure: the six parts, the three principles, the migration phases, enforcement);
  Cosmic Python (the Python idiom); Khorikov (where logic lives and how it is tested).
- **DDD, two sources, brought in when the core's contents are specified:** Evans and Khononov, through
  passages the operator pastes.

Agreed already across the read hexagonal sources, as the agent drafted it: the application owns its
ports and adapters implement them; the domain is pure, with no out-of-process access, not even
through an interface; the handler is thin orchestration and the only caller of ports; tests run at
the boundary with test doubles for the outside; one composition root wires everything, and nothing
else names a concrete adapter.

## decision · the five points rated against the four hexagonal sources (agent's assessment)

Operator, verbatim: *"give me a 4/4 rating on the constellation for those five points (do 6/6 when DDD
comes into play). Montenegro is fresh so favor it a bit unless you have reason to disagree."*

Scored 1 for support, ½ for partial support, 0 for silence; a contradiction is named.

| Point | Cockburn | Montenegro | Cosmic Python | Khorikov | Score |
|---|---|---|---|---|---|
| 1 The application owns its ports; adapters implement them | 1 (Fig. 6.24) | 1 (§1.2.3; ports in core modules, §6.1) | ½ (ports are ABCs kept beside their adapters, Ch. 4) | ½ (no port vocabulary; owns wrappers, §9.2.4) | 3/4 |
| 2 The domain is pure, no out-of-process access even through an interface | 0 (the inside is the designer's, Fig. 5.2) | 1 (§3.5; repository interfaces sit in the domain module, called by handlers) | 1 (Ch. 3, functional core) | 1 (§7.2.2) | 3/4 |
| 3 The handler is thin and the only caller of ports | ½ (Fig. 4.6's services implement driving ports) | 1 (§4.4; ch. 9 pipeline) | 1 (Ch. 4, 9) | 1 (Humble Object, §7.1.2) | 3.5/4 |
| 4 Tests at the boundary, test doubles for the outside | 1 (Figs. 3.1, 4.4, 4-7) | 1 (ch. 8: mocked or fake ports) | 1 (fakes, no mocks, Ch. 3) | ½, contradicts in part: the managed database is used for real, doubles only for unmanaged dependencies (§8.2) | 3.5/4 |
| 5 One composition root; nothing else names a concrete adapter | 1 (Figs. 2.1, 6.22) | 1 (§9.6 and its sidebar) | 1 (Ch. 13, bootstrap) | 0 (not discussed) | 3/4 |

No point is contradicted on its core claim. Two refinements the ratings surface:

- **Point 2's "pure" allows in-memory state change.** Montenegro's aggregate is always valid but not
  immutable (ch. 9), and Khorikov lets a domain object change its own state, never persist itself
  (§6.3.3). So the point reads: no out-of-process access and no hidden inputs (clock, randomness,
  environment); a domain object may change its own state.
- **Point 4 is the one disagreement, and the agent departs from favoring Montenegro there.** gzkit's
  managed dependency is its own files (the ledger, canon), and its tests already build real temporary
  ones (source: the hexagonal canon page, its testing paragraph). Khorikov's position, the real
  managed dependency in integration tests and doubles only for what other systems observe, fits gzkit
  at no cost; Montenegro's mocked ports fit the handler unit tests. Proposed reading: handlers are
  unit-tested with fakes of their ports; integration tests use real temporary files; mocks only for
  unmanaged dependencies (GitHub, for example).

## decision · ports are `typing.Protocol`, never ABC (canon, restated)

Operator, verbatim: *"I thought we were going to NOT do ABC but do Typing.Prototype?"* Canon already
rules it: the hexagonal rule's item 4, *"Port shape via `typing.Protocol`, not `ABC`; inject adapters
by composition, not inheritance"* (source: the hexagonal rule). Nothing reopens it. The ½ given to
Cosmic Python on point 1 described that book's own practice (abstract classes kept beside their
adapters), not a proposal; the book itself offers `typing.Protocol` as the alternative (Ch. 2 sidebar,
Ch. 8; source: the Cosmic Python report). For gzkit, point 1 reads: the application owns its ports,
each a `typing.Protocol`, and adapters satisfy them structurally.

## source · Cockburn and Garrido de Paz, §2.4, pasted by the operator

*Hexagonal Architecture Explained*, §2.4 *What is required, optional, and outside the pattern*,
pasted by the operator from the Kindle edition 2026-11-08. Key notes, paraphrased:

- **Required, six items:** the app defines a provided or required interface for every external
  interaction; driving ports for provided interfaces and driven ports for required ones, which may
  not be explicitly visible in languages that do not declare interfaces; driven actors configurable
  at run time; no source dependency from the app on its actors; external actors reach the app only
  through its ports; ports expressed in business terms only.
- **Tips, not required:** the configurator's form is open; ports named *"For doing something"*;
  few ports, starting with one per primary actor and one per secondary; a recommended code
  organization of two port folders (driving and driven) beside the app folder, as part of the app,
  and two adapter folders (driving and driven) in a separate space; driving adapters do not normally
  talk to driven adapters except in tests; the pattern does not nest.
- **Outside the pattern:** how the application is structured internally, DDD or not.
- **Strong conformance:** the driven port is expressed purely in the application's language; the app
  cannot know a database exists.

This confirms Cockburn's 0 on point 2 (the inside is outside the pattern) and his 1 on point 1. It
also bears on canon rule 7, which cites this section to forbid folder partitions: §2.4 leaves the
app's *internal* structure open but recommends port and adapter folders. Rule 7 reads the first
statement as if it covered the second. Held for the package-design question.

## decision · details come from Montenegro and Percival; the constellation is consulted throughout (operator ruling)

The operator asked which of the four hexagonal sources gives structure beyond Cockburn. The agent's
answer: Montenegro gives the full inside structure (the domain's building blocks, the application
layer, modules with a may-and-must-not dependency table, enforcement, a test recipe per artifact, the
build order, integration, migration); Cosmic Python gives a lighter version of the same shape in Python,
held by convention; Khorikov gives placement and testing guidance, not structure; Cockburn leaves the
inside open. Operator, verbatim: *"So, we look at Percival and Montegro when we want to contemplate
details, but keep constellation consultation alive throughout - plus you can look things up along the
way."*

Settled, as the run's working method: questions of detail are worked from Montenegro and Percival and
Gregory (Cosmic Python); every point is still rated against the whole constellation (four for
hexagonal, six once DDD enters); and the agent may look facts up as the run goes, each lookup entered
as a source before it bears on a decision.

## decision · point 4 follows Montenegro's explicit testing recipes (operator ruling)

The agent put point 4's one disagreement: whether handlers are tested through fakes of their ports
(Montenegro, Cosmic Python, Cockburn's test doubles) or only through integration tests on the real
managed dependency (Khorikov), recommending both, split by purpose. Operator, verbatim, before the
answer was finished: *"DDD guys come in as needed. (BDD and TDD in where needed too), Montenegro is
explicit here too (and he has that repo)."*

Settled: testing follows Montenegro's chapter 8, one recipe per artifact type, with his companion
repository's chapter 8 listing map as the reference implementation (source: Montenegro's companion
repository). The domain is never doubled; handlers are tested with mocked or fake ports; commands and
queries with the valid-and-invalid recipe; adapters by the kind of dependency they hide. Khorikov's
real-dependency integration test enters only where Montenegro himself calls for a focused integration
test, on framework behaviour the code relies on (§8.7, PDF p.251). The agent's departure from
Montenegro on this point is withdrawn. Evans and Khononov enter where DDD is in play; BDD and TDD
enter where their questions arise.

## decision · the wiring point is named *configurator* (operator ruling)

The operator asked what a composition root is. The agent explained: the one place, run at start-up,
that builds the driven adapters, injects them into the handlers and hands those to the driving
adapter, so that nothing else names a concrete adapter; Cockburn's *configurator* (Fig. 2.1, §2.4),
Montenegro's and Cosmic Python's *composition root* (Montenegro §9.6; Cosmic Python Ch. 13, after
Mark Seemann). Operator, verbatim: *"configurator is better"*.

Settled as a term: **configurator**. *_Avoid_: composition root, bootstrap, assembly* as names in
gzkit's specification; each is recorded as the same thing in its source. The canon page's claim that
gzkit's command layer is its configurator because it threads `project_root` inward does not meet point
2: a configurator passes finished adapters, never the raw path from which inner code builds its own.

## decision · the five points of the constellation, approved (operator ruling)

Put to the operator as refined. Operator, verbatim: *"Approve"*.

1. **The application owns its ports.** Each port is a `typing.Protocol` defined by the application,
   never by an adapter, named in business terms (*For doing something*) and using only domain types,
   never a library's own types. Adapters satisfy a port by its shape, never by inheriting from it.
2. **The domain is pure.** Entities, value objects, aggregates and domain services have no outside
   access, not even through a port or interface: no files, git, subprocesses, network, environment,
   clock or randomness. What the domain needs is passed in as values. A domain object may change its
   own in-memory state through guarded methods; it records domain events and never dispatches them.
3. **The handler is the only caller of ports.** Each handler implements one input port and holds no
   business decisions: it gathers what the domain needs through output ports, calls the domain,
   persists the result and dispatches the recorded events. When a decision needs more data part way
   through, the handler splits it into steps (CanExecute/Execute); it never injects a port into the
   domain.
4. **Testing follows Montenegro's chapter 8 recipes.** The domain is never doubled; handlers are
   tested with mocked or fake ports; commands and queries with a valid-input test and an invalid-input
   test; adapters by the kind of dependency they hide; focused integration tests only for framework
   behaviour the code relies on. The companion repository's chapter 8 is the reference.
5. **One configurator wires everything.** At start-up it builds the driven adapters, injects them into
   the handlers, then hands those to the driving adapters, in Cockburn's Figure 2.1 order. It passes
   finished adapters, never a raw path from which inner code builds its own. No other module names a
   concrete adapter. In tests, the test case is the configurator.

Ratings (Cockburn, Montenegro, Cosmic Python, Khorikov): 3/4, 3/4, 3.5/4, 3.5/4, 3/4; no point is
contradicted on its core claim. Consequences for gzkit's present code, carried forward and not put as
questions: canon's `project_root` conformance claim is withdrawn by points 2 and 5; the formatter port
taking Rich's `Table` fails point 1; the airlock's gate functions that read the brief and book the
ledger are handler work under point 3; canon rule 5's second-adapter threshold meets point 1 and
Cockburn's test double as an adapter.

## decision · the import check is named *the dependency rules* (operator ruling)

Put to the operator: name the check that core modules import only stdlib and Pydantic *the dependency
rules*, after Montenegro §7.3 (*Dependency rules: who may import whom*, PDF p.182), matching
Cockburn's required item 4 (no source dependency on the actors, §2.4). Operator, verbatim: *"Yes,
dependency rules"*.

Settled as a term: **the dependency rules**, the may-and-must-not imports of each region, today
witnessed for `src/gzkit/core/` only by `tests/policy/test_import_boundaries.py`. *_Avoid_: core
purity, import purity* for this check; *purity* is Montenegro's principle (point 2).

## decision · purity is a design principle only; every other use of the word is a naming defect (operator ruling)

Put to the operator: adopt encapsulation and completeness as Montenegro defines them. The operator chose
*"Discuss one"*, then, verbatim: *"you had other names when we started - ontology being one, but you
also had purity. I think purity is a design principle and not a folder/physical separation like you had
shown me originally."*

Settled: *purity* names Montenegro's design principle (point 2) and nothing else. A check that fences
a folder, a package or a classification is not purity. Measured 2026-11-08 (`git grep -l -i purity`,
108 files), the word carries at least three other meanings in gzkit:

- the import check on `src/gzkit/core/`, renamed *the dependency rules* (decision above);
- the ontology's **Harness-Purity Invariant** (`docs/governance/ontology-ownership-plane-doctrine.md`
  § The Harness-Purity Invariant; ADR-0.32.0 BI #4; `src/gzkit/ontology/purity.py`;
  `gz validate --ontology-purity`), which fences gzkit's product object types out of
  `ownership:harness`: a classification fence, not a design principle;
- the advisory-rules audit's rows 64 to 64e (`docs/governance/advisory-rules-audit.md`), which score
  the hexagonal rule's items under the old reading.

Renaming the Harness-Purity Invariant changes a validator scope and a CLI flag, so it is a correction
for the disposition map (rows 2 or 4), not something this run executes. Encapsulation and completeness
remain open.

Operator, verbatim, following: *"it that a misnomer in 2 above? "purity?" 3. that's semantic drift. we
aren't ready to adopt both without discussing both."* The agent read the invariant's definition
(`docs/governance/ontology-ownership-plane-doctrine.md` § The Harness-Purity Invariant, read
2026-11-08): it admits only GovZero-universal object types to `ownership:harness` so that the harness
image stays *"portable/universal"*, and calls itself *"a **fence, not a preference**"*. In plain English
*pure* means unmixed, so the name is not wrong outside gzkit; inside gzkit's specification it is a
misnomer, because it names an admission fence with the word now reserved for a design principle. Its
own text gives the better name, its purpose: portability. Item 3 is recorded as semantic drift, as the
operator named it. Encapsulation and completeness are discussed one at a time before either is adopted.

## decision · encapsulation, as gzkit's Python builds it (operator ruling)

Montenegro's encapsulation (§3.2, Table 3.1: internal state is private; interaction only through public
methods) rests on Java's private constructors and package-private classes; Python enforces neither.
Put to the operator: encapsulation in gzkit is three requirements. Operator, verbatim: *"Yes, those
three"*.

1. **State changes only through the object's own methods.** Value objects are frozen Pydantic models;
   an entity changes state only through guarded methods (Montenegro's `publish`, ch. 9); no outside code
   sets a field.
2. **Creation only through a named factory that validates** (Montenegro's `validateThenCreate`, §3.3), so
   an invalid object never exists. Rebuilding a stored object is the one other way in, open only to the
   persistence adapter and guarded by an architecture test (Montenegro §9.2.3, §9.7.2).
3. **Every module declares its public surface** with `__all__` and leading underscores for internals,
   and an architecture test refuses a reach into another module's underscored names. The private
   cross-package import baseline in `tests/policy/test_import_boundaries.py` is the existing start.

## decision · encapsulation and completeness rated against the constellation; their scope asked (agent's assessment)

Operator, verbatim: *"how do those stack up with the constellation? why do we need these anyway? for
domain entities?"* Scored as before (1 support, ½ partial, 0 silence), contradictions named:

| Requirement | Cockburn | Montenegro | Cosmic Python | Khorikov | Score |
|---|---|---|---|---|---|
| E1 state changes only through the object's methods | 0 | 1 (ch. 9 `publish`) | 1 (aggregates changed only through their methods, Ch. 7) | 1 (domain objects guard their own state, §6.3.3, §7.3.3) | 3/4 |
| E2 creation only through a validating factory | 0 | 1 (§3.3) | contradicts: constructors do not validate, and the book does not code defensively inside the domain (App. E) | ½ (preconditions guard invariants, §7.3.3) | 1.5/4 |
| E3 declared public surface, checked by a test | ½ (actors reach the app only through ports, §2.4 item 5) | 1 (package-private classes, ch. 7 rules) | 0 | 0 | 1.5/4 |
| C1 exhaustive handling of closed sets, checked by the type checker | 0 | 1 (sealed `Error`, no default branch, §4.3.2, Listing 9.32) | 0 | 0 | 1/4 |
| C2 expected failures returned as values, exceptions for faults | 0 | 1 (§4.2) | contradicts: exceptions express domain concepts (Ch. 1), commands fail noisily (Ch. 10) | 1 (errors returned with the decision, §6.4.4; a Result type, §7.4.1) | 2/4 |

Encapsulation was adopted before it was rated; E2 and E3 rest mainly on Montenegro, and Cosmic Python
contradicts E2. Two gzkit facts bear on the contradictions:

- Pydantic changes E2's cost: a frozen model whose validators carry the invariants is its own validating
  factory, so the factory comes nearly free; and `model_construct()`, which skips validation, is
  Python's equivalent of Montenegro's reconstitution back door.
- C2 meets canon: `.gzkit/rules/pythonic.md` § Error Handling, *"Catch specific exceptions, translate to
  the `GzkitError` hierarchy in `gzkit.core.exceptions`."* gzkit's existing error doctrine is exceptions.

Why these exist (Montenegro §3.2, as recorded): they protect business invariants, so they apply where
invariants live: entities, value objects, aggregates, and in Montenegro commands and queries too;
DTOs and request records are exempt (ch. 9, §9.3.3). Handlers, adapters and the configurator are not
their subject.

## decision · values inside the hexagon, `GzkitError` outside; Pydantic is the validating factory (operator ruling)

Put to the operator: C2, expected failures returned as members of a closed union in the domain and
handlers (ty can then force their handling; exceptions are invisible to it), exceptions kept for faults
and at the boundary, `.gzkit/rules/pythonic.md` § Error Handling revised for the inside; and E2, frozen
Pydantic models whose validators carry the invariants, a named `create(...) -> Self | ValidationErrors`
factory that returns Pydantic's `ValidationError` as a value, and `model_construct()` banned in the
domain except for the persistence adapter's rebuild of stored objects, under an architecture test.
Operator, verbatim: *"So, GzkitError outside the core? I guess common adapter structures and design are
okay. It sounds like GzkitError is part of what we require in adapter land (outside the walls) and values
are what we do in core. Pydantic as validating factory is a good compromise. Do I follow correctly?"*

Confirmed by the agent, with one precision: *inside the walls* is the whole hexagon, the domain and the
handlers, since handlers implement the input ports. Settled:

- Inside (domain and handlers): expected outcomes are values in closed unions; no `GzkitError` is raised.
- Outside (adapters and the configurator): `GzkitError` is the shared error structure; a driving adapter
  turns a returned error into a `GzkitError`, an exit code and a message through an exhaustive `match`;
  a driven adapter turns an infrastructure failure into a returned error or, for a fault, an exception.
- A fault (a defect, an exhausted resource) may still surface inside as an exception; it is not caught
  there and propagates to the boundary.
- E2 resolves as proposed: Pydantic is the validating factory.

Consequences carried forward: `GzkitError` lives in `gzkit.core.exceptions` today, inside `core/`, so it
moves outside the walls; `pythonic.md` § Error Handling is revised to say the same; both are row 4 or 5
work, not executed by this run.

## decision · the principles' scope: encapsulation inside, completeness wherever a closed set is handled (operator ruling)

Put to the operator, after Montenegro's exhaustive error mapping was found in the REST adapter (Listing
9.32), not the domain: encapsulation (E1 to E3) applies inside, to the domain (entities, value objects,
aggregates, domain services) and to commands and queries; completeness C1 (exhaustive handling, checked
by ty) applies wherever a closed set is handled, the domain, handlers and adapters alike; C2 as settled
above. DTOs, request records and the configurator carry or wire data and hold no rules, so neither
principle governs them. Operator, verbatim: *"Yes, that split"*.

Group A's principles are now settled: purity (point 2), encapsulation (E1 to E3) and completeness (C1,
C2). The ontology's DDD role stays open until Evans and Khononov are in reach.

## decision · package design: the hexagon is `core/`, adapters are its siblings, the map names each (put; the operator agrees in principle)

Put to the operator: the six parts become physical packages, overturning canon rule 7 (3/4: Cockburn
§2.4 and Fig. 4.6, Montenegro §6.1, Cosmic Python; Khorikov silent; none supports rule 7). The operator
asked whether these are all within *core*, then whether some stay siblings of core, like the CLI. The
agent answered from the sources: inside the walls, `core/` holds `domain/`, `ports/driving/`,
`ports/driven/` and `handlers/` (Cockburn §2.4: ports *"are part of the app"*; Montenegro's
`application-core`); outside, each adapter is its own sibling package beside `core/` (Montenegro §6.1's
adapter modules; Cockburn Fig. 4.6), the CLI already one (`src/gzkit/cli/`); a `configurator` module
wires them. Because a sibling's name does not say it is an adapter, the house-style run's whole-system
map, a short data list in `pyproject.toml` `[tool.py-gzkit]`, names each package's region, and the
dependency-rules test reads it, as Montenegro's rule configuration names each layer's packages (§7.2).
A worked sketch of the airlock entry use case was shown. Operator, verbatim: *"okay, that seems like
better organization. you say we'd track this in pyproject.toml?"*

The home is settled canon from the house-style run: *"house-style facts go in `pyproject.toml`'s tool
table; `.gzkit.json` keeps governance settings"* (`docs/rnd/house-style.md`, decision of that title,
superseding its earlier `.gzkit.json` ruling), the table named `[tool.py-gzkit]` because gzkit's
distribution is `py-gzkit` on PyPI.

## decision · the package list is named the *hexagonal architecture system package map* (operator ruling)

Operator, verbatim: *"why do you keep calling this a map? map to what?"* The agent answered: it maps
package names to parts of the hexagon; *whole-system map* was the agent's coinage in the house-style
run; Montenegro calls the equivalent his rule configuration (§7.2); the agent proposed *the hexagon
declaration*. Operator, verbatim: *"ok, i get it "hexagaonal architecture system package map" -
pyproject.toml?"*

Settled as a term: **the hexagonal architecture system package map** (the operator's wording, its
spelling corrected), the list in `pyproject.toml` `[tool.py-gzkit]` that names each top-level package's
part of the hexagon. *_Avoid_: hexagon declaration, rule configuration*; the house-style run's *whole-
system map* names the same thing. Its home is confirmed by the house-style ruling above. The table's
key names are diamond 2's.

## decision · canon rule 7 is overturned; the package design is ruled (operator ruling)

Put to the operator: overturn canon rule 7 with the package design above. Operator, verbatim: *"Yes,
rule it"*.

Settled:

- `src/gzkit/core/` is the hexagon, everything inside the walls: `domain/`, `ports/driving/`,
  `ports/driven/`, `handlers/` (names of the inner packages are diamond 2's).
- Each adapter is its own sibling package of `core/`; the CLI (`src/gzkit/cli/`) is the driving adapter
  that exists today.
- One `configurator` module wires them.
- The hexagonal architecture system package map in `pyproject.toml` `[tool.py-gzkit]` names each
  top-level package's part, and the dependency rules are derived from it.

Rule 7's one surviving clause is that `core/` stays; it now holds the whole hexagon. Consequences,
carried to the disposition map and not executed here: rule 7 and the canon page's § *Adapters-outside-
the-core as a folder discipline is NOT adopted* are rewritten (row 4); `ADR-pool.hexagonal-folder-
structure-realization`, marked Superseded by the v0.2.0 directive this ruling reverses, is read before
anything cites it; moving gzkit's 128 top-level modules into the design is the five-phase migration,
and since a change to the package map is a classic ADR, it routes through one (rows 1 and 5).

## source · the ontology describes itself as a read-only projection

`src/gzkit/ontology/unified.py` (module docstring) and `src/gzkit/ontology/corpus.py:1` · read 2026-11-08

> *"**BI#2 derived-never-authority.** READ-ONLY throughout: each domain is composed via its existing
> read path [...] no ledger emission, no graph-state write."*

> *"Corpus-domain projection over ``ledger.get_artifact_graph`` (ADR-0.32.0, OBPI-02)."*

The ontology is assembled from four domains (corpus, work, source anchors, OKF) by reading canon
and the ledger; it holds no behavior and writes nothing. Its object types are gzkit's governance
nouns (source: the ontology model).

## decision · DDD and the ontology are related; how is held for group A

Operator, verbatim: *"DDD and the ontology are clearly related as far as I can see"*. This restates
F1 item 10 (*"sounds like ddd/ontology ha rnd work"*) and agrees with canon's cascade, which says
gzkit's domain *"is **modeled as the ontology**"* and that bounded contexts are *"subgraphs of the
ontology"* (source: the hexagonal rule).

What is not settled is which DDD thing the ontology is. The sources read so far allow at least
three: the ubiquitous language and its context map (it names the object types and their links);
the domain model itself (its node types as the entities); or a read model in Cosmic Python's sense,
a projection of the write side, which is what the ontology says of itself (source: the ontology
describes itself as a read-only projection). A DDD domain model holds behavior and invariants;
the ontology holds neither. The question joins group A, after the principles, because the answer
decides where entities, value objects and aggregates live.

## source · the identifier migration's ruled names

`docs/rnd/renewing-vows/identifier-migration-program.md` § What is migrated, as ruled · read 2026-11-08

> | pool ADR | change proposal | `ECP-<slug>` | [...] | feature ADR, the "(m)ADR" | engineering order | `EO-<semver>-<slug>` | [...] | OBPI | work package | `WP-<NN>-<slug>` | [...] | TASK | task card | `TASK-…` kept | [...] | ADR | architecture decision record | `ADR-<n>` | [...] | release | block | no identifier |

> Ruled 2026-10-05 ('A', the artifact ladder) and carried 2026-10-07 and 2026-10-10 (timed to 1.0,
> full operational capability)

The ladder renames gzkit's governance nouns at 1.0. The ontology's `ObjectType` still carries the
old names (`ADR`, `OBPI`, `TASK`; source: the ontology model).

## decision · the domain's ubiquitous language is the drydock's ruled ladder, not today's names

Operator, verbatim: *"don't forget, the drydock will produce new names to replace mADR, OBPI, etc."*

So wherever this specification names gzkit's own domain, it uses the ruled ladder (change proposal,
engineering order, work package, task card, architecture decision record, block), and today's names
(feature ADR, OBPI) are treated as the legacy terms the five transformation steps migrate from. This
bears on the ontology question above: whichever DDD part the ontology turns out to be, its object
types carry the language, so they move with the ladder.

## source · gzkit's prior record on graphify and model-assisted recall

`docs/design/adr/pool/ADR-pool.artifact-graph-navigation.md` (head, read 2026-11-08);
`docs/governance/airlock-in-constellation-2026-06-30.md:17`; `.gzkit/insights/agent-insights.jsonl`
records of 2026-06-30 and 2026-09-29; `git grep -il graphiti` (no hit) · run 2026-11-08

> *"External refs (graphify / LightRAG / Plumb / BEADS / Symphony) are **bones**"* (the constellation record)

> operator, 2026-06-30, as booked in the insight of that date: *"graphify has the bones, but it is far
> too large to onboard as a dependency ... Yes to tree-sitter + networkx ... No MCP btw, all tool"*

> operator, 2026-09-29: *"also, we want to ensure that the ontology is mature enough. I am still
> considering graphify (a queryable knowledge graph) to augment this."*

graphify was surveyed in April 2026 (the pool ADR rejected direct adoption) and again in June
(ruled as bones, not a dependency; tree-sitter and networkx taken as the floor, which the ontology
now uses). The operator holds a LightRAG fork (`tvproductions/LightRAG`), named as the model-assisted
recall tier in `ADR-pool.rag-anything-governance-retrieval`. graphiti has no record in the repository;
nothing about it has been read.

## decision · graphify and graphiti for knowledge and memory management: outside hexagonal, put to the operator as a follow-on run

Operator, verbatim: *"and, do we want to finally consider graphify and/or graphiti? not as a part of
hex, but for future maturity for knowledge/memory management?"*

The operator places it outside this run's subject. What the run can say: graphify has two prior
rulings (bones, not a dependency) and an open consideration from 2026-09-29; graphiti is unread. A
knowledge and memory question touches the ontology (the read side), the handoff rulings store and
the insights log, which are gzkit's present memory surfaces. The agent recommends it as a row 7
follow-on run, so it gets its own sources and does not ride on the hexagonal rulings.

Put to the operator: name a knowledge and memory R&D run as a row 7 follow-on, or not now.
Operator, by selection: *"Yes, add to row 7"*.

**commissions:** 7, a knowledge and memory management R&D run: graphify, graphiti and the LightRAG
fork weighed against gzkit's present memory surfaces (the ontology, the handoff rulings store, the
insights log), under state doctrine's rule that a derived view never gates; opened by the operator's
question of 2026-11-08 and the open consideration of 2026-09-29.

## source · Percival and Gregory, *Architecture Patterns with Python* (Cosmic Python), the reading report

[`hexagonal-specification/sources/cosmic-python-reading-2026-11-08.md`](hexagonal-specification/sources/cosmic-python-reading-2026-11-08.md),
a research report of the online edition (preface, introduction, chapters 1 to 13, epilogue,
appendices A to E; stamped *Last updated 2023-11-24*; CC BY-NC-ND) · read 2026-11-08

Landed with its 40 numbered quotations withheld, each citation kept. What bears on group A, each with
its citation in the report:

- no *input port* or *output port*: the book's port is an abstract base class or a duck type, kept in
  the same file as its adapters, not in the domain; the inbound side is the service layer, later
  handlers taking commands, with no declared port type;
- *primary/driving* and *secondary/driven* are glosses; the working terms are *entrypoints* and
  *adapters*, and *entrypoint* is used for four different things;
- *purity* is an informal word, qualified at once by the Zen of Python's practicality line;
  *completeness* is not a principle; *encapsulation* is defined; the organising principle is
  dependency inversion, with *Functional Core, Imperative Shell* named;
- the brownfield route builds the service layer (handlers) first, not ports;
- the book avoids mocks and prefers fakes, and has no architecture tests or import-linting.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | | | |
| 4 | control surface, rule, doc, skill, hook | | | |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |
| 7 | further research | commissioned | (a) a knowledge and memory management run: graphify, graphiti and the LightRAG fork against the ontology, the handoff rulings store and the insights log | (a) opened by the operator's graphify/graphiti question, 2026-11-08, outside the hexagonal subject. The operator opens it |

## Close

**Challenge restated.** Not yet.

**Frontier.** Open.

**Review.** Not yet written.

**Sign-off.** Not yet put.

## What this record does not license

No ADR, OBPI, chore, GHI or canon change is started by this run. Canon rule 7 of
`.gzkit/rules/hexagonal-architecture.md` stands unchanged until the operator's go on a row that
changes it.
