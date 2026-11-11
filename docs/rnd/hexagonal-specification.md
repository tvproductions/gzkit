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

## decision · one kernel package, the adopter-facing toolkit, a sibling of `core/` (operator ruling)

Question put: should gzkit have a small package below the hexagon that every region may import,
holding only building blocks and no governance concepts? Rated 1/4: only Montenegro has one (his
architecture kernel, §4.1.1 and Appendix A, which he says is not a DDD shared kernel; his WriteFlow
also keeps a separate project `shared` module, V02 §9.2.1/§9.2.4). Cosmic Python, Khorikov and
Cockburn have none.

The agent's reasoning: Montenegro's kernel exists because his input-ports module may not depend on the
domain, so for gzkit's own code the bases could live in `core.domain`. The case for it is adopters: if
gzkit imposes hexagonal on every adopter, as Django imposes `Model` and `View`, their code needs
something to import, and that cannot be gzkit's `core/`, which holds governance. The recommendation was
one kernel, stdlib and Pydantic only, with no gzkit domain in it, imported by gzkit's hexagon and by
adopters' hexagons alike. Operator, verbatim: *"ok"*.

Settled:

- one kernel package, a sibling of `core/`, named in the hexagonal architecture system package map;
- it is the piece adopters build on: candidate contents are the command, query and domain-event bases
  (frozen Pydantic models), the error-value types such as `ValidationErrors`, and the dependency-rules
  test; any handler or port markers wait on the decorators question (group F);
- it depends on stdlib and Pydantic only, and holds no gzkit governance concept. This answers the
  operator's opening question: strict stdlib use is what makes it a dependable kernel.

Held open: its contents item by item (groups B to F); its name (diamond 2); the DDD shared kernel
between bounded contexts, which waits for Evans and the bounded-context question (group D). The
operator's proposed strict chain, shared kernel → domain → handlers → adapters, is answered by this
entry only for the kernel's place at the bottom.

## source · gzkit's existing identifier value types

`src/gzkit/core/models.py` lines 475 to 515, read 2026-11-09: `AdrId` and `ObpiId`, frozen Pydantic
models (`extra="forbid"`) with one `raw: str` field held to a pattern, a `parse` classmethod and
`__str__`. Measured the same day: no module outside `core/models.py` names either type, and 449 fields
in `src/gzkit` are typed `adr_id: str` or `obpi_id: str`.

## decision · value objects are frozen Pydantic models, and a value's rules are methods on its type (operator ruling)

Put to the operator: three Python shapes for a value object. (A) A frozen Pydantic model: it
validates, ty tells one type from another, and it can carry behaviour. (B) `Annotated[str,
StringConstraints(...)]`: it validates only as a model field, and ty sees `str`. (C) `typing.NewType`:
ty tells the types apart, but there is no validation and no behaviour. The agent recommended A, as
your E2 ruling already makes Pydantic the validating factory. The example given was semver ordering
held as `AdrId.__lt__`, so the `AGENTS.md` rule *"never lexicographically"* lives on the type rather
than at every place that sorts. Operator, verbatim: *"yes, A"*.

Constellation: Montenegro, Khorikov (primitive obsession named as a defect) and Cosmic Python
(frozen value objects such as `OrderLine`) agree; Cockburn is silent. 3/4.

Settled: a value object is a frozen Pydantic model created through `create(...) -> Self |
ValidationErrors` (E2), and a rule about the value is a method on its type. Held open: whether raw
strings convert at the hexagon's walls, which was put in the first form of the question and not
answered there, so it is put again.

## decision · raw strings become value objects at the hexagon's walls (operator ruling)

Put to the operator: does a raw string become a value object at the walls, so that no value with
rules enters the hexagon as a plain `str`? Inbound, the adapter calls `create(...)` and reports a bad
string itself; inside, handlers, ports and the domain take the value type, and ty refuses a `str`;
outbound, the adapter writes `str(value)`. The alternative, conversion inside handlers, puts `str` on
the input ports, against point 1 (ports in domain types). Montenegro (the adapter's mapping), Khorikov
(validate at the edge, trust inside) and Cosmic Python (entrypoints) agree; Cockburn is silent. 3/4.
Operator, verbatim: *"yes"*.

**Correction, 2026-11-09, after the ruling.** The Montenegro citation above is wrong. Read against the
V02 key notes (§9.3.1, PDF p.268; p.270): his commands and queries carry primitives only, never domain
value objects, so the input-ports module does not depend on the domain, which he calls the most
important decision in that section; the value-object factories validate again on the way into the
domain, a deliberate double check. Montenegro therefore disagrees with this ruling, and the rating is
2/4 (Khorikov, Cosmic Python). His reason is the Maven module constraint already weighed in the kernel
entry; gzkit's ports may import `core.domain`. Put back to the operator in the next entry.

**Second correction, the same day, on the operator's challenge** (verbatim: *"its not that simple, what
does maven do? what is our rationale for this?"*). Montenegro's pages read in full (§6.1, PDF
pp.145–149; §9.3.1, PDF pp.268–271). Maven is the fence, not the reason. A Maven module declares its own
dependencies and the compiler refuses an import from an undeclared one (p.145); his NOTE names Gradle
subprojects, .NET projects, npm workspaces and Go modules as the same idea. The reason is architectural:
*"If a command exposed an ArticleId, then every caller of that command—the REST controller, the bus, any
future adapter—would drag in the domain"* (p.268). Table 6.1 (p.149) bars the REST adapter from the
domain; only the persistence adapter may see it. And the agent's claim that "ports and adapters may
already import `core.domain`" under a ruled table is unsourced: no entry in this record rules who may
import whom. Both this ruling and the kernel entry's reasoning rested on it. The ruling is reopened.

Settled: only adapters hold raw strings for a value with rules. The mapping mechanics stay in group C.

## decision · entities are frozen; each change returns a new version (operator ruling)

Put to the operator: (A) a mutable entity changed in place by its methods, the practice of Montenegro
(ch. 9 `publish`), Cosmic Python (`Batch.allocate`) and Khorikov; or (B) a frozen entity whose method
checks its rule and returns a new version. The agent recommended B against all three, for gzkit's own
reasons: the system of record is an append-only ledger, so a state is rebuilt from events and never
overwritten; `models.md` already requires frozen models; a frozen object cannot be changed through a
reference someone else holds. The cost named: a method returns `Self`, `model_copy(update=...)` does not
validate, so the method checks its rule or rebuilds through `create`. The operator asked whether this
holds whatever the states are; the agent answered that it does, that the example states were
illustrative and will take the drydock ladder's names, and that a state in gzkit is derived from
ledger events, never set. Operator, verbatim: *"yes, B"*.

Settled: entities are frozen Pydantic models; a change is a method that checks its rule and returns the
new version (with the event it records, under point 2). This departs from the three sources that rule on
it, and the reason is gzkit's event-sourced ledger.

## decision · driving adapters never import the domain; commands carry primitives; the handler converts (operator ruling)

Put to the operator after the second correction: (A) Montenegro's Table 6.1, where driving adapters see
only the input ports, commands and queries carry primitives validated in their own `create`, and the
handler converts them into value objects as they enter the domain; (B) driving adapters may import value
objects, never entities; (C) domain types everywhere, as first ruled. The agent recommended A, as it
blocks the bypass in which a CLI command builds entities and calls them without a handler. Operator,
verbatim: *"if this constrains vibe coding, then it is worth doing"* and *"but, yes, let's do A"*.

Settled, replacing the walls ruling's mechanics:

- driving adapters import the input ports (commands, queries, results) and the kernel, never the domain;
- commands and queries carry primitives and validate them in `create(...) -> Self | ValidationErrors`;
  the handler builds the value objects, whose factories check again through the same kernel helpers
  (Montenegro's deliberate double check, PDF p.270);
- point 1's "ports in domain types" now reads: driven ports in domain types; input ports in primitive
  commands, queries and results;
- the persistence adapter is the one adapter that sees the domain, as repositories do (Table 6.1).

Constellation: Montenegro explicit; the others silent or contrary by default. Held open: the dependency
table for every region (this ruling fixes the driving adapter's row), and how it is enforced, which the
operator raised in the same message (*"don't we need something like this too? … does astral supply it?
does it exist for Python?"*).

## source · Python's import-boundary tooling, a web search (secondary)

Two web searches, 2026-11-09, secondary sources only, none read in full: no Astral tool (ruff, ty, uv)
enforces which module may import which (ty checks only that an import resolves; pydevtools, *How Astral
uses its own tools*); ruff's `flake8-tidy-imports` `banned-api`, which `pyproject.toml` already uses, bans
a name project-wide, with per-file ignores; uv workspace members declare their own dependencies but share
one environment, so an import is not refused. Third-party: import-linter (layers and forbidden contracts,
`lint-imports` exit 1), tach (`tach.toml` declared dependencies, written in Rust; the DTach fork calls it
unmaintained, 2026 status unconfirmed), modguard (tach's predecessor). gzkit's own witness,
`tests/policy/test_import_boundaries.py`, read 2026-11-09: stdlib `ast`, fences `src/gzkit/core/`
against three prefixes and a third-party allowlist.

## decision · the dependency rules are enforced by gzkit's own stdlib test, read from the package map (operator ruling)

Put to the operator: enforce the dependency rules with gzkit's own stdlib test reading every region's
row from the hexagonal architecture system package map, or with import-linter or tach. Python has no
compile-time fence, so Montenegro's two layers (Maven and ArchUnit, §7.1) become one. The agent
recommended gzkit's own test: no new dependency (STDLIB-FIRST), the ruled package map as the single
source both humans and the test read, and it ships in the kernel for adopters. Operator, verbatim: *"yes,
fortify what gzkit already does."*

Settled: `tests/policy/test_import_boundaries.py` is widened from `core/` alone to every region the
package map names, and the checker is the kernel's for adopters to run. Held open: the per-region table
it enforces.

## decision · the per-region dependency table, with repositories in the domain and DTO-only driven ports (operator ruling)

Put to the operator: Montenegro's Table 6.1 (§6.1, PDF p.149) mapped onto gzkit's regions. The kernel
imports stdlib and Pydantic only. `core.domain` (entities, value objects, events, repository Protocols)
imports the kernel. `core.ports.driving` (commands, queries, results, use-case Protocols) and
`core.ports.driven` (non-repository Protocols) import the kernel only. `core.handlers` imports the
domain, both port packages and the kernel. Driving adapters import the driving ports, the kernel and their
library. Repository adapters import the domain, the kernel and their library. Other driven adapters
import the driven ports, the kernel and their library. The configurator imports everything. No adapter
imports another adapter, handlers or the configurator. Two departures were named: repository Protocols
live in the domain (Montenegro §5.3, §6.1), and non-repository driven ports carry DTOs only, with the
handler mapping to and from domain types. Operator, verbatim: *"yes, and we strongly recommend adopters
do this."*

Settled: the table above is the dependency rules for gzkit, and the widened test enforces it. Point 1 now
reads: repository Protocols in domain types, in the domain; other driven ports in DTOs; input ports in
primitive commands, queries and results. For adopters, the table is a strong recommendation, which the
kernel's checker supports.

## source · rhea, the repository harness gzkit governs

`github.com/tvproductions/rhea` (private), read 2026-11-09 through `gh api`: README, `pyproject.toml`,
the file tree and the last five commits (newest 2026-05-29). The README calls it a *"Repository Harness
for Entity Abstraction"*: the Repository pattern only, read-only by design, a `ReadRepo[T]` contract with
a small predicate DSL (`Eq`, `Gt`, `In_`, `And`, `Or`), in-memory and SQLite adapters planned, inspired by
the stalled Red Bird library, and *"the first end-to-end development target for gzkit"*. The source tree
holds `src/rhea/__init__.py` only; the design tree holds a foundation ADR with six OBPIs, a constitution and
a PRD. `pyproject.toml` lists `py-gzkit>=0.28.0` as a runtime dependency and builds with hatchling.
Raised by the operator, verbatim: *"we have an opportunity that is deliciously "meta" - we use rhea as a
target for gzkit proving … and it is an entity repo. so do we adopt rhea?"*

## decision · rhea is gzkit's proving ground (operator ruling)

Put to the operator: (1) rhea as the hexagonal specification's first adopter and proving ground, built
to the spec from its first commit, the first user of the kernel and its dependency checker outside gzkit;
(2) gzkit consuming rhea in its own repository adapters, which the agent recommended setting aside: rhea
lists `py-gzkit` as a runtime dependency, so the two would depend on each other; gzkit's ledger repository
writes and rhea is read-only; STDLIB-FIRST asks for a named capability and rhea holds no code yet.
Operator, verbatim: *"rhea is gzkit's proving ground."*

Settled: rhea is the proving ground, where the specification and the kernel are tried by an adopter
before anyone else meets them. Not ruled: part (2); the agent's recommendation and its revisit condition
(rhea ships a write side, or gzkit needs several backends at once) are held for the disposition map, and
should it return, the dependency table places rhea inside a repository adapter as its library, never in
the domain.

Finding, carried for row 2 and not executed: rhea's `pyproject.toml` lists `py-gzkit>=0.28.0` under
`[project] dependencies`; governance tooling belongs in its dev dependencies.

**commissions:** the proving-ground work in rhea, whose route (rows 1, 4 or 5) the disposition map
settles.

**Note, 2026-11-09, on the operator's concern** (verbatim: *"shame, it seems we'll end up duplicating
rhea as an internal feature of gzkit anyhow."*). The agent's answer: the two sit at different levels.
rhea is a generic engine, `ReadRepo[T]` with a predicate DSL and parity across backends; gzkit's
repositories are domain Protocols in governance terms (`events_for(adr_id)`), each backed by a small
adapter over JSONL or frontmatter, with no DSL and no multi-backend parity. What they share is the
pattern and the kernel, and the direction without a cycle is that rhea builds on gzkit's kernel (its
bases, error values and dependency checker), not the reverse. Should gzkit need real querying, the
revisit condition fires and rhea enters a repository adapter as its library: reuse, not duplication.
Moving rhea's `py-gzkit` dependency to dev dependencies clears that path. Operator, verbatim: *"record
note, push."*

## decision · rebuilding never validates; each tightened rule declares its strategy for old state (operator ruling)

Put to the operator, from Montenegro V02 §9.2.3 (PDF pp.261–264) and §9.5.1 (p.290): creation checks
every current rule; rebuilding (his `reconstitute`, Vernon's idiom) takes stored state as ground truth,
does not validate, raises no events and cannot fail, and its back door is closed by an architecture
rule. When a rule is tightened after data was stored, a domain strategy decides: migrate, grandfather, or
revalidate on the next modification. In gzkit terms: migrate means appending a correcting event, as the
ledger is append-only (precedent: `gz migrate-semver`, `artifact_renamed`); grandfather means a roster or
cutoff (precedent: `data/foundation_grandfather.json`, `data/module_size_grandfather.json`, terminal OBPI
briefs exempt as sealed records); revalidate means the entity's next changing method checks the full
current rule. Example: ADR-0.0.59's REQ-kind rule against OBPIs completed before it. Operator, verbatim:
*"go with recommendations"*.

Settled:

- rebuilding from the ledger never validates; only the repository adapter may call it (E2's
  `model_construct()` exemption), and the dependency test enforces that;
- every tightened rule declares its strategy for old state when it is tightened; the default is
  revalidate on next change; terminal entities are grandfathered; migration is only by appended events;
- a tightened rule with no declared strategy is incomplete, on the pattern of the mode contract.

Group B (value objects, entities, rebuilding and old state) is settled.

## decision · the run keeps its method after the accepted-recommendation check (operator ruling)

Per gz-rnd's red flag, the agent said that apart from the operator's pushbacks (purity, ABC, Maven) the
recommended option had won nearly every question, two recommendations had rested on wrong claims, and
asked whether the questions were the right ones, offering fewer recommendations, a counter-case per
question, or different questions. Operator, verbatim: *"carry on"*.

## decision · the stored shape is a separate model, mapped both ways in the repository adapter; the domain uses enums (operator ruling)

Put to the operator, with `ObpiFrontmatter` (`src/gzkit/core/models.py` line 372) as the instance: a
storage shape in `core/` whose `lane` admits `"lite"`, `"heavy"`, `"Lite"`, `"Heavy"` and whose `status`
admits eleven values from different eras, `extra="allow"`. (A) a separate stored-shape model in the
repository adapter, mapped two ways by a mapper inside that adapter; (B) the domain entity doubles as the
file schema. The agent recommended A: Montenegro explicit (separate persistence model, NOTE PDF p.289;
mappers are collaborators inside adapters, p.286), Cosmic Python in part, Khorikov contrary (§11.1.3),
Cockburn silent; 2.5/4. Sub-answers: two-way at repository adapters, one-way each direction at driving
adapters, no bridge region, Pydantic not dataclasses. Operator, verbatim: *"yes, A and we'd normalize to
enums (or whatever is close in Python) in the domain to avoid that spelling nonsense. also, Pydantic and
schema would have avoid that spelling vibe coding because it came from models working in markdown."*

Settled:

- each repository adapter keeps its own stored-shape model and a two-way mapper; the frontmatter models
  leave `core/`;
- a closed set in the domain is an `enum.StrEnum` (stdlib, Python 3.11+): one spelling, a named type, and
  exhaustive `match` with `assert_never` under C1; tolerance of old spellings is the adapter's job.

Finding, measured 2026-11-09, on the operator's second sentence: the schema and the Pydantic model existed
and were widened to admit the drift rather than refuse it. `src/gzkit/schemas/obpi.json` enumerates
`"lite"`, `"heavy"`, `"Lite"`, `"Heavy"` for `lane`; 479 files under `docs/`, `design/` and `.gzkit/` carry
`lane: Lite` or `lane: Heavy` against 397 with the lowercase form. The status list is partly a ruled
two-vocabulary mapping (its description cites ADR-0.0.16's `STATUS_VOCAB_MAPPING`), not spelling drift
alone; the lane capitals are drift. Carried to the write-side question.

## decision · canonical on write, tolerant on read (operator ruling)

Put to the operator: new writes canonical only, the schema admitting one spelling for them; old spellings
accepted on read only, by the adapter's stored-shape model, and handled under the old-state ruling
(grandfathered or migrated per rule). Also recommended in the same message: widening a schema enum needs a
recorded ruling. Operator, verbatim: *"agree ==> yes, canonical on write and tolerant on read."*

Settled: the adapter writes only the canonical spelling, produced from the domain enum; the read-side
tolerance lives in that adapter's stored-shape model alone. Not ruled: the enum-widening rule, which the
operator's words did not take up, so it is put again.

## decision · widening a closed set needs a recorded ruling (operator ruling)

Put again to the operator: widening a schema `enum`, a `StrEnum` or a `Literal` needs a recorded ruling,
witnessed by a shrink-only baseline of each closed set's members that `gz validate` compares in `gz
check` (precedent: `data/ruff_baseline.json`, `data/module_size_grandfather.json`); a new member fails
unless its commit carries the ruling. The mechanism it stops: a write fails the schema, the agent widens
the schema, the drift becomes legal (the 479 capitalised-lane files). Operator, verbatim: *"yes to this
too: "Then add a rule of its own: widening a schema enum needs a recorded ruling, the same as any change
to doctrine, so the next agent that hits a validation error can't quietly add "Lite".""*

**commissions:** 4, the closed-set widening rule and its shrink-only validator.

## decision · a DTO is a frozen Pydantic model with types and no domain rules (operator ruling)

Put to the operator: a DTO (what a non-repository driven port carries, or a query returns) is a frozen
Pydantic model checked for types only, built by plain construction, with no `create` factory, exempt from
the always-valid rule; a command or query is a validated message with `create`; a value object or entity
holds every domain rule. Montenegro explicit (§9.3.3, PDF pp.271, 273), Cosmic Python's read models
plain; Khorikov and Cockburn silent; 2/4. A DTO that enforced domain rules would be a second domain model,
which canon rule 8 forbids. Operator, verbatim: *"agree with your yes to DTOs"*.

## decision · group C closes; the operator's strict chain is answered as a strict graph (derived, not a new ruling)

The operator's opening question, *"Perhaps we layer: shared kernel -> domain -> application/handlers ->
adpaters as a strict chain?"*, is answered by the per-region dependency table already ruled: the kernel is
at the bottom; the domain and both port packages each depend on the kernel alone, side by side; handlers
join them; each adapter reaches only the inner part it needs; the configurator sees everything. A strict
graph, not a chain, enforced by the widened dependency test. Bleed-through is answered by the same table
and by the stored-shape ruling. Group C (mapping, DTOs, repositories, package design, the chain, the
kernel, bleed-through) is settled; uv-build enforcement belongs to group F.

## decision · a command bus and a query bus in the kernel (operator ruling)

Put to the operator: (A) the driving adapter sends each command through a bus, a startup registry from
command type to handler that fails fast on a missing handler, with cross-cutting work (ledger event, mode
contract level, `Task:` attribution, guards) in one place, decorators around the bus (Montenegro §4.5.4);
(B) the configurator injects use-case Protocols into the CLI. Montenegro (§4.5–§4.6; bus contracts in his
kernel) and Cosmic Python (the message bus is *"the main entrypoint to the service layer"*, ch. 9) are
explicit; Khorikov and Cockburn have no bus; 2/4. The agent recommended A, stdlib only, use-case Protocols
kept as the handlers' signatures. Operator, verbatim: *"yes to bus, but montenegro uses @usecase decorators
too, which you so here: "he use-case Protocols remain as the handlers' signatures.""*

Settled: a command bus and a query bus, stdlib only, in the kernel; the registry is built at startup and
fails fast; cross-cutting concerns wrap the bus once. The operator's second clause opens the stereotype
question (Montenegro's `@UseCase` and its siblings), put next.

## decision · stereotype decorators: the agent's revised case challenged on three counts (operator correction)

The agent had revised its recommendation to no stereotype decorators, arguing that location (the package
map) and kernel base classes already carry a class's region and kind, and citing `@advances` as a
decorator that goes stale. Operator, verbatim: *"this sounds more like unfinished work rather than a flaw:
"gzkit also has the opposite case: @advances, the TASK decorator.""*; *"I thought we wanted Prototype
instead of ABC?"*; *"models will vibe location, I need an answer on kernel base classes. also, decorators
are method wrappers, so don't we get added business logic enforcement, validation, qc opportunities?"*

The agent's answers:

- `@advances` is withdrawn as evidence. Under the correction-vs-enhancement doctrine, a channel whose
  declared intent is unmet is a correction, not proof that decorators fail. Carried for row 2: whether
  `@advances` (`.gzkit/rules/task-discovery.md`, *"advisory and expected to be empty"*, GHI #752)
  fulfils its declared intent.
- Canon rule 4's `typing.Protocol` governs ports, whose implementations are swapped by composition. A
  value object, entity, event, command or DTO is not a port: it already inherits Pydantic's `BaseModel`,
  and a Protocol cannot carry `model_config` or a validating factory, and would admit any look-alike
  object. A kernel base class for these kinds does not conflict with rule 4.
- Location alone can be vibed, so region and kind cross-check each other: the test requires each kernel
  base to be subclassed only in its region, and each region's classes to subclass the right base.
- Behaviour-carrying decorators are a separate question from marker stereotypes, put after the base
  classes.

## decision · the kernel ships the domain and message base classes, cross-checked against region (operator ruling)

Put to the operator: the kernel ships `ValueObject` (frozen, `extra="forbid"`, `create(...) -> Self |
ValidationErrors`), `Entity`, `DomainEvent` (frozen, primitives), `Command` and `Query` (frozen, primitives,
`create`) and `Dto` (frozen, types only, no `create`), all Pydantic `BaseModel` subclasses; the dependency
test cross-checks each class's base against its region (an `Entity` outside `core/domain` fails; a class in
`core/domain` with no domain base fails; a command with a domain-typed field fails). Ports stay
`typing.Protocol` under canon rule 4. Operator, verbatim: *"yes: "does the kernel ship these base classes,
with the test cross-checking each class's base against its region?""*

## source · decorator use cases, pasted by the operator from Gemini (secondary)

Pasted 2026-11-09, a model's generic list, unverified and cited as secondary: logging, timing and
profiling, authentication, and caching (`functools.lru_cache`) as common decorator uses that keep code
DRY. Operator's framing, verbatim: *"i want to settle the decorator question because we may be leaving a
LOT of power on the table"*.

## source · the mode contract names a decorator as a declaration shape

`.gzkit/rules/mode-contract.md`, read 2026-11-09: *"Until RO-13 builds the declaration shapes (decorator,
Markdown MEL block, `gzkit.mx.alarms` arguments)"*, and *"The level is applied at the place of call, never
by the declaration."*

## decision · decorator kinds are mapped to regions; a decorator never makes a business decision (operator ruling)

Put to the operator: a map of decorator kinds to regions. Contract QC (`@transition` re-validating the new
version, checking its type and that an event was recorded; Pydantic `@validate_call` at handler entry) may
live in the domain, handlers and ports. Caching (`functools.cache`) may live on pure domain functions,
which point 2 makes safe, and in adapters. Cross-cutting work with I/O (logging, timing, the ledger event,
the mode level, `Task:` attribution) lives in bus middleware chosen by the configurator, and in adapters for
their own technology. Gates (a held lock, an attestation, a pipeline stage) are declared per command and
applied by bus middleware, while a business authorisation rule stays in the entity method (Montenegro,
`Article.publish`). Retry and timeout live in driven adapters (Montenegro §10, PDF p.328). Declarations
(`@covers`, `@advances`, the mode-contract declaration) live in tests and controls. Mode levels follow
`mode-contract.md`: a decorator declares, the middleware applies at the place of call. The rule over all:
a decorator enforces a contract, applies a policy the configurator chose, or declares a fact; it never makes
a business decision (Montenegro's handler litmus test, §4.4.2). Operator, verbatim: *"decorators can take
args, which really increases our power to keep behaviors right"* and *"yes ==> "does gzkit adopt this map
of decorator kinds to regions, under that rule?""*

Settled: the map and the rule above. The operator's point on arguments is part of it: a parameterised
decorator states the contract it enforces at the definition, for example a transition's source and target
states and the event it must record, or the gates a command requires, so the declaration and the check
cannot drift apart.

## decision · a decorator opportunity review is a follow-on run (operator ruling)

The operator asked, verbatim: *"it sounds like a decorator use opportunity review is a new rnd session?"*
The agent agreed: this run settles the rules for decorators; surveying gzkit's code, guards, hooks and the
RO-13 mode-contract shapes for where parameterised decorators can enforce contracts, declare gates and mode
levels, and move cross-cutting work into bus middleware has its own sources and would stall the
specification; it builds on the kernel and the bus, so it fits after this run signs off. Put: add it to row 7
as (b). Operator, verbatim: *"yes: shall I add the decorator opportunity review to row 7 as (b)?"*

**commissions:** 7, (b) a decorator opportunity review within the decorator map this run ruled.

## decision · a domain event and a ledger event are one fact in two shapes (operator ruling)

Put to the operator: an entity method returns its new version and the event it recorded; the handler passes
the event to the ledger repository (a Protocol in the domain); the ledger adapter writes the event's stored
shape, canonical on write; rebuilding replays the same events. Sources: entities recording events, 3/4
(Montenegro, Cosmic Python, Khorikov; Cockburn silent); the domain event as the stored record, 0/4, since
none of them stores state as events, and the ruling follows from the frozen-entity ruling instead. Held: events
no entity records, such as `mx_session_lease_expired`, written by the session-orientation script. Operator,
verbatim: *"agree and this should bring much better cohesion and discipline: "My recommendation is yes: the
domain event and the ledger event are one fact, in two shapes.""*, quoting the held case as their *"for
instance"*.

Settled: a ledger row exists because an entity method recorded the event; no handler, command, hook or script
writes a ledger row any other way.

## source · the ledger's event types, measured

`.gzkit/ledger.jsonl`, counted 2026-11-09: 20,390 rows across 78 event types. The largest are
`artifact_edited` (5,494), `agent_sync_completed` (1,578), `obpi_created` (969) and `gate_checked` (943).
Two names break the snake-case convention: `adr-evaluation` (168) and `patch-release` (35). Many types record
an observation (a check, a sync, an edit) rather than an entity's state change.

## decision · every ledger event type belongs to an entity (operator ruling)

Put to the operator, on the measurement above: (A) every ledger event type has an owning entity, and an event
with no owner is an entity not yet modelled or does not belong in the ledger; (B) two kinds, entity-owned domain
events and typed but unowned observations. The agent recommended A as the strict reading that keeps the
one-fact ruling without exception, warning that under B "observation" becomes the label for whatever nobody
models. Operator, verbatim: *"oh gosh, that means they've been terribly VIBED!"*; *"yes, you example above
means strict! A"*; and on the cost, *"gzkit has suffered from sporadic software engineering, so this is the
challenge: "The cost is real: 78 types each need an owner, a rename into the drydock vocabulary, or a decision
to leave the ledger.""*

Settled: the principle. Held for the bounded-context question: assigning each of the 78 types an owning entity,
a drydock name, or an exit from the ledger. The operator's last sentence is carried to the close as material for
the restated challenge.

**Amended the same turn by the operator**, verbatim: *"we will NOT  leave the ledger"*. Read as removing the
exit: no event type leaves the ledger; each of the 78 receives an owning entity and a drydock name, telemetry
such as `artifact_edited` included. The agent's reading was stated to the operator for correction.

## source · `src/gzkit/commands/obpi_complete.py`, surveyed

Read 2026-11-09 by line count and a search of its definitions and calls, not in full: 2,074 lines in one
command module. It imports `subprocess`; runs the security-review gate inline (reading `arb-step-security-*`
receipts from disk and checking their age); runs the attestation receipt-binding gate; builds evidence
payloads; and emits several ledger events itself (`obpi_receipt_emitted`, `audit_receipt_emitted`, a
meta-receipt-bind event).

## decision · follow-on reactions are listeners on the bus, dispatched after the event is in the ledger (operator ruling)

Put to the operator: (A) a handler appends the event first; the bus then dispatches it to listeners, each of
which sends a new command, its own use case; a failed reaction leaves the fact recorded and can be retried or
replayed; (B) the handler performs reactions inline. Montenegro (listeners are driving adapters re-entering the
command bus; one event, two phases, §9.4.3), Cosmic Python (event handlers on the message bus, ch. 8–9) and
Khorikov (dispatch after persistence, ch. 7) agree; Cockburn silent; 3/4. In gzkit the ledger is already the
outbox Montenegro builds separately (§9.5.2), so a missed reaction is found by replay. `obpi_complete.py`
emitting its events inline was shown as B. Operator, verbatim: *"yes, A"*.

Material for the restated challenge, operator's words during group D: *"gzkit is a vibe coding paradise"*;
*"gzkit has been a vibe-coder's Valhalla"*; and of the ledger, *"this is a vibe coding megalodon"*, *"the
epitome and apex of vibe coding"*.

## source · Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software*, key notes

The operator's licensed copy, PDF, read 2026-11-09 by a research subagent in full for Ch. 2 (Ubiquitous
Language), Ch. 6 (Aggregates, Factories, Repositories), Ch. 14 (Maintaining Model Integrity) and Ch. 15
(Core Domain, Generic Subdomains, Segregated Core), with related passages in Ch. 7, 11 and 16 and the Glossary.
The report is held outside the repository; only these cited key notes land. The ebook carries no printed page
numbers; printed pages are anchored from its Photo Credits page and marked "~" where interpolated.

- **Aggregates.** Invariants inside an aggregate hold at every commit; rules spanning aggregates may lag and be
  settled by event processing, batch processing or other update mechanisms (PDF 166, p. ~128). Evans states no
  one-aggregate-per-transaction rule; that strict form comes from later authors. Ch. 7 refactors the cargo
  design so a Handling Event no longer touches the Cargo aggregate (PDF 224, p. ~178).
- **Events.** No domain-event pattern and no Glossary entry for "event". The precursors keep history as data in
  the model: Handling Event is its own aggregate root and Delivery History is derived from it by a repository
  query (PDF 214, 224–225); Ch. 11 accounting Entries are never removed (PDF 368).
- **Bounded Context.** Its boundary is drawn by team organisation, by use within parts of the application, and by
  code bases and database schemas (PDF 413, p. ~336); it is not a Module, and module namespaces can hide an
  accidental model split (PDF 415, p. ~338); one team per context is the usual correspondence (PDF 470, p. ~387).
- **Shared Kernel.** A subset of the model with its code and database design, often the Core Domain or Generic
  Subdomains, changed only after consulting the other team, with both teams' tests passing (PDF 434, p. ~355).
  For Evans the term means jointly owned model and code, not a runtime core: it collides with this run's
  *kernel*, which holds no domain (PDF 433–434).
- **Published Language.** The interchange language is not the host's model and stays stable while the model
  changes (PDF 481, p. ~397).
- **Ubiquitous Language.** Each context speaks its own dialect, and context names enter the language (PDF 414,
  423).
- **Repository.** A collection-like access point for aggregate roots only, leaving commits to the caller (PDF
  191–196).

## decision · new use cases are built outside-in, test first; brownfield code enters by the five-phase migration (operator ruling)

Put to the operator: every new use case is built in this order, each step's test first: (1) the command
(primitives, `create`) and the use-case Protocol, tested valid and invalid; (2) the handler against fake driven
ports, the domain never doubled; (3) the domain (entity method, value objects, recorded event), pure unit tests;
(4) the driven ports the handler needed; (5) the adapters, tested by dependency kind; (6) wiring in the
configurator, one end-to-end check through the bus. Montenegro's assembly checklist (§7.2, PDF p.175), Cosmic
Python's test-driven service layer (ch. 4–5) and Khorikov's humble controller agree; Cockburn silent; 3/4. Each
REQ maps to a step and its `@covers` test is that step's test; step 2 catches a handler reaching for
`subprocess` or the file system. Brownfield code such as `obpi_complete.py` enters by the five-phase migration
(Extract, Define, Wrap, Refactor, Replace); the order binds everything new from its first commit, rhea included.
Operator, verbatim: *"do, and we are going to need this, big time"*, quoting the brownfield sentence, and
*"yes ==> "The open question is still: is every new use case built outside-in in that order … with each step's
test written first?""*

Group D is settled except aggregates and bounded contexts, which wait for Khononov's passages (the 78
event-type assignment rides on them).

## decision · the run resumes in a new session (operator ruling)

The handoff `.gzkit/handoffs/20261109T235408Z-hex-spec-lease-renewed.md` advised resuming this run. Operator,
verbatim: *"Yes, resume"*, booked through `gz handoff decide` (`proceed`). The record was checked against git:
it is unchanged since `df0719fe6`, `main` level with origin, 54 decision entries, the newest the outside-in build
order. The frontier was recomputed from the subject, not taken from the handoff's list: groups B to D are settled
except aggregates and bounded contexts, which wait for Khononov's passages; group E is open and its first question,
configuration, was put in the previous session but never entered here, so under this skill it is put again rather
than carried; F and G wait on E.

## source · how gzkit reads configuration today, measured

Read 2026-11-09: `src/gzkit/config.py` in its loading part (lines 206–330), and a search of `src/gzkit`.
`GzkitConfig` is already a frozen Pydantic model (`frozen=True, extra="forbid"`) with sub-models for paths,
vendors, ARB, authorship, smoke and complexity. `load_config()` is documented as the *"Single entry point for
config loading"* with the precedence *"defaults → config file → CLI args"*: the model's own defaults are gzkit's,
`.gzkit.json` is the adopter's override, and the file is read relative to the current directory unless a path is
passed. It is not the only reader: 50 modules call `GzkitConfig.load` or `load_config` (76 call sites), each
loading for itself, and 35 modules read `manifest.json` directly, a second configuration surface `load_config`
does not cover. The previous session's figure of 59 modules is not reproduced by either search and is withdrawn.
Cosmic Python's position (App. B, Ch. 13, from this run's reading `sources/cosmic-python-reading-2026-11-08.md`):
configuration is immutable, `config.py` exposes functions, and the bootstrap is the only importer of config.

## decision · configuration is read once, by the configurator, and passed as frozen values (operator ruling)

Put to the operator, on the measurement above: configuration is read only at start-up, by the configurator,
through one config adapter; it merges gzkit's defaults with the adopter's overrides, `manifest.json` included
with `.gzkit.json`, validates the result into frozen settings, and passes each part as values to what needs it;
no handler, domain code or adapter reads a configuration file. Cosmic Python (App. B, Ch. 13) states it directly;
Montenegro's figures (6.26a/b, 6.28) have the configurator choose adapters, his text on configuration not read;
Cockburn's configurator passes finished adapters inward without discussing configuration; Khorikov silent; 2/4
direct, 3/4 counting Cockburn's shape. It follows the earlier rulings that values are taken as parameters and the
configurator never passes a raw path inward. The cost was stated: 50 modules move from loading to receiving, and
two configuration surfaces become one. Operator, verbatim: *"Yes"*.

Settled. Carried to the disposition map: the move of the 50 loading modules and the 35 `manifest.json` readers.

## source · who reads gzkit's records from outside, surveyed

Searched 2026-11-09, not read in full: gzkit publishes 39 JSON schemas under `src/gzkit/schemas/`, one of them
`ledger.json`, and every ledger row carries `"schema":"gzkit.ledger.v1"`. Outside the package, rhea's
`scripts/session_orientation.py` parses `.gzkit/ledger.jsonl` line by line on its own (line 137 onward), and
none of rhea, airlineops or flightops imports `gzkit`. So the stored ledger shape is already read across a
boundary by code gzkit does not own, with no published contract for that reader beyond the schema file.

## source · Montenegro, Ch. 10 and the configuration, event and outbox sections, read in full

The operator's licensed MEAP V02, extracted text held outside the repository, read 2026-11-09 after the operator
challenged a question that cited Ch. 10 from notes (*"why? you have the text"*): Ch. 10 in full (PDF pp.324–338),
§7.2 and §7.2.1 (pp.175–178), §9.2.4 (pp.266–267), §9.5.2 (pp.293–295) and §9.6.4 (pp.310–311). Key notes only.

- **What leaves is chosen, not leaked** (§10.5, rule 2, p.334): the application layer decides whether a domain
  event becomes an integration event and what shape it takes outside; the domain never learns it left. Table 10.2
  (p.335) assigns *what crosses the boundary* to the application layer.
- **The outbox payload is not the domain event** (§9.5.2, p.295): the domain event is an in-process signal; what
  goes to external consumers is a stable, serialization-friendly contract that can outlive a deployment.
- **Owned contracts are versioned** (§10.6, p.336; §10.7, p.338): the facts a system publishes and the commands
  and queries it accepts are the contracts it owns, versioned and kept stable; a consumed contract's changes are
  absorbed inside an adapter. One contract map per bounded context, drawn before the adapter.
- **Each interaction is classified** by direction, request or fact, mode (synchronous call, event, external
  orchestration) and owner (§10.1–§10.4); internal orchestration by a handler is not a mode.
- **An event with no consumer is pure cost** (§9.2.4 sidebar, p.267): raise events only for facts others care
  about.
- **Configuration** (§7.2, §9.6.4): settings live in an external file bound into a typed properties record and
  injected; the configuration code connects the elements and *"should not contain business decisions"* (p.175).

Two corrections follow. The configuration ruling cited Montenegro's text as unread; it is now read and supports
the ruling. The follow-on-reactions ruling's reasoning said gzkit's ledger *"is already the outbox Montenegro
builds separately (§9.5.2)"*; §9.5.2 says the outbox holds integration events, not domain events, so the claim
holds only for the durable-record half (a missed reaction found by replay), not as an outbox of published facts.
The ruling itself, listeners dispatched after the append, is unaffected.

## decision · the agent's published-language recommendation is withdrawn

The question put before the source above was read recommended that the stored ledger shape, `gzkit.ledger.v1`, be
gzkit's published language. Montenegro (§10.5 rule 2, §9.5.2), Cosmic Python (internal and external events kept
distinct, Ch. 11, `sources/cosmic-python-reading-2026-11-08.md`) and Evans (the published language is not the
host's model) all place the published contract apart from the stored record. The recommendation is withdrawn and
the question is put again in a corrected form.

## decision · outside readers get a small set of versioned integration events, never ledger rows (operator ruling)

Put to the operator, on the source above: the application layer chooses which ledger events gzkit publishes and
shapes each as an integration event; each published event is a contract gzkit owns and versions; rhea's
orientation script, the generated hooks and adopters read only those, never `.gzkit/ledger.jsonl`; the ledger stays
gzkit's internal record, so the drydock rename of the 78 types breaks no outside reader. Montenegro (§10.5 rule 2,
§9.5.2, §10.6), Cosmic Python (Ch. 11) and Evans (Published Language) agree; Cockburn and Khorikov silent; 2/4
hexagonal, 3/6 with DDD, Khononov unread. The cost was stated: a publishing step, a contract map naming each outside
reader, and rhea's script moved off the raw ledger. Operator, verbatim: *"Yes"*.

Settled. Carried to the disposition map: the contract map, the publishing step, and rhea's reader. Held for the
78-type assignment: Montenegro's *"an event with no consumer is pure cost"* (§9.2.4), which the strict
every-type-has-an-owner ruling must be read against.

## source · how an adopter starts: `gz init` today, and Montenegro's Appendix A

`docs/user/manpages/init.md` § What It Does, read 2026-11-09 in full: with no `pyproject.toml`, `gz init` runs
`uv init --<project-type>` (`lib` by default), adds ruff and ty, `tests/` and a CI workflow; otherwise it lays down
governance only (`.gzkit/`, `.gzkit.json`, control surfaces, hooks, the pre-push gate). It scaffolds no part of a
hexagon, no package map and no dependency check. `--no-skeleton` skips the Python skeleton.

Montenegro, Appendix A (MEAP V02, PDF pp.339–352), read 2026-11-09 in full, held outside the repository. The
adopter's path is three pieces: the architecture kernel, which declares intent and contracts and *"has no runtime
behavior"* (A.1, p.340); the enforcement library, adopted by adding it as a test dependency, writing a YAML file
naming the project's packages and one test class per architectural scope (A.6, pp.349–350); and the reference
application, a template to *"fork and replace the WriteFlow domain with your own"* (A.7, p.351), laid out as a
shared kernel, an application core holding domain, input ports, output ports and handlers, one module per adapter,
and an assembly module holding the bootstrap and the architecture tests. He ships no generator.

## decision · `gz init` scaffolds the hexagon for new projects; existing projects get the map and the checker (operator ruling)

Put to the operator, on the source above: for a project with no `pyproject.toml`, `gz init` lays down
`src/<pkg>/core/` with `domain/`, `ports/driving/`, `ports/driven/` and `handlers/`, a driving-adapter package, a
`configurator` module, the hexagonal architecture system package map in `[tool.py-gzkit]`, the kernel as a
dependency, and a test running the kernel's dependency checker from the first commit; an existing project gets the
package map and the checker test, its code entering by the five-phase migration. Montenegro's Appendix A gives the
three pieces (kernel, enforcement library, forkable reference application) and ships no generator; none of the four
hexagonal sources addresses scaffolding; the ruling follows from strict hexagonal imposed on every adopter and the
outside-in order binding from the first commit. The cost was stated: a skeleton template that must track the
specification. Operator, verbatim: *"Yes"*.

Settled. Not settled: whether `--no-skeleton` may skip the checker test as well as the folders; the two readings
were put as alternatives and the answer did not choose between them.

## decision · `--no-skeleton` skips the folders, never the checker test (operator ruling)

Put to the operator: (A) `--no-skeleton` skips the folders, while the package map and the dependency-checker test
always land; (B) it skips both, as it skips the whole skeleton today. The agent recommended A under the strict
rulings (*"I want strict"*; *"what is the harm of hex regardless of size?"*), naming its cost: a project that is
not Python, or wants no hexagon, cannot take `gz init` without the checker. No source addresses it. The agent also
noted that the operator had taken the recommended option on every question this session, and asked whether the
questions were the right ones. Operator, verbatim: *"Yes, never the check"*.

Settled: no project initialised by gzkit is without the architecture check.

## decision · group E closes (derived, not a new ruling)

Group E's questions are answered: configuration (read once by the configurator), external contracts and
integration events (a small versioned set of owned integration events; the ledger internal), bootstrapping
(the configurator, ruled under point 5 of the core model) and what `gz init` scaffolds (the two rulings above).
The operator's *"how much design is needed before anything else can proceed?"* is answered by the house-style
run's rulings, *"the whole-system map is drawn up front and kept current; a change to it is a classic ADR"* and
placement against it *"enforced at the work package freeze"* (`docs/rnd/house-style.md`), whose map this run
renamed the hexagonal architecture system package map, together with the outside-in build order. Inbox and queues
are not taken up: no integration this run found needs a broker, and Montenegro defers the relay and inbound
consumption to later chapters not yet in the MEAP. The frontier moves to group F.

## source · Montenegro, Ch. 7 on annotation, structural and naming rules and the freeze, read in full

MEAP V02, extracted text held outside the repository, read 2026-11-09: §7.1 (PDF pp.172–174), §7.4 (pp.191–195,
prose and tables; the listings skimmed), §7.5–§7.6 (pp.196–207), §7.8–§7.9 (pp.212–214). Key notes only.

- **Two layers of defence** (§7.1, Table 7.1): build modules reject wrong imports at compile time; the rule
  library catches at test time what modules cannot: a handler taking a concrete adapter, a class carrying another
  layer's stereotype, a handler with an unpredictable name.
- **Annotation rules** (§7.4, Table 7.3): each stereotype belongs to one layer. `@UseCase` is required on every
  input port, `@OutputPort` on every output port, `@ApplicationService` on every handler, and each is forbidden
  elsewhere. The domain may carry its own stereotypes *"or no annotation at all"*. Adapters carry no required
  stereotype; `@Adapter` exists on output adapters because the assembly's component scan discovers them by it.
- **Structural rules** (§7.5): ports must be interfaces; commands and queries implement their marker, expose the
  validating factory and no public default constructor; a use-case interface's type arguments must be a command
  or a query.
- **One naming rule** (§7.6): a handler is named after the use-case interface it implements, `XUseCase` to
  `XHandler`.
- **The freeze** (§7.8): existing violations are recorded in a committed store, new ones fail, the store only
  shrinks, and a baseline is never refreshed to make new violations pass. This is gzkit's shrink-only baseline.

What the record already rules against these: the dependency rules and their test; kernel base classes for domain
and message kinds, cross-checked against region; ports as `typing.Protocol`. Not yet ruled: how a port and a
handler are identified and cross-checked, which is where Montenegro uses stereotypes, and the naming rule.

## source · uv's documentation on the build backend and workspaces, researched for the uv-build question

[`sources/uv-boundary-enforcement-2026-11-09.md`](hexagonal-specification/sources/uv-boundary-enforcement-2026-11-09.md)
· a research subagent's report on the uv 0.13.7 documentation, landed verbatim 2026-11-09, with the report's own
marks for what it observed in a scratch workspace and what it inferred. Not yet put to the operator.

> "uv can't ensure that a package uses its declared dependencies and nothing else."

> "There must only be one top level module, and all data files must either be under the module root or in the
> appropriate data directory."

What bears on the run: `uv_build` governs which files enter a distribution and restricts no import; a workspace
member run with `uv run --isolated --package <member>` gets an environment without undeclared sibling members,
which uv documents as environment selection and not as enforcement; workspace members are separate
distributions, and the docs describe no way for one wheel to bundle them.

## decision · ports and handlers are identified by Protocol and name, not by marker decorators (operator ruling)

Put to the operator, on the Ch. 7 source above: (A) shape and name, no markers: every class in a ports package is
a `typing.Protocol` or a kernel message base; every handler explicitly inherits exactly one use-case Protocol and
takes its name from it (`XUseCase` to `XHandler`, Montenegro §7.6); a driven port appears as a handler's
constructor parameter; (B) Montenegro's stereotypes as decorators, required in their region and forbidden
elsewhere (§7.4). The agent recommended A as a departure from Montenegro on the markers alone: his stereotypes
also feed Spring's component scan, which gzkit's explicit configurator replaces, and a marker is a second
declaration that can disagree with the type. Cosmic Python uses neither; Cockburn and Khorikov silent. Operator,
verbatim: *"i like the typing.Protocol approach but I also realize that decorators can serve additional purposes
for support and checking since they are method wrappers. I don't want to over-follow Montenegro as his project is
Java Spring. So, I favor A but wanted to discuss it a bit."*

The agent's answer: a marker declares what a class is and wraps nothing; a wrapper checks or changes what a method
does. A drops only the marker. Wrappers stay governed by the ruled decorator map (`@validate_call` at handler
entry, gates declared per command, `@transition` on entity methods, middleware around the bus), and they sit on
the implementing handler, because a decorator on a Protocol method does not carry to the class that implements
it. A's limit: a handler that omits its Protocol is caught by the checker test, not at import, as a forgotten
marker would be. Operator, verbatim: *"yes: "Shall I record A with that clarification: identity comes from the
Protocol and the name, and wrapper decorators stay governed by the decorator map?""*

Settled: A, with that clarification. The checker's structural and naming rules are Montenegro's §7.5–§7.6 in
Python's terms; his annotation rules (§7.4) are not adopted. Existing violations enter a shrink-only baseline,
gzkit's standing practice and Montenegro's freeze (§7.8). Recorded as a caution for the specification, the
operator's words: do not over-follow Montenegro where his answer is Java Spring's.

## decision · gzkit stays one distribution; the checker test is the only fence (operator ruling, against the agent's recommendation)

Put to the operator, on the uv source above, answering *"Can the uv-build system help with boundary/package/module
enforcement?"*: `uv_build` restricts no import; a uv workspace is a partial fence. The agent named a conflict in
the record: the kernel ruling has adopters subclass the kernel's bases at runtime, while the rhea finding puts
`py-gzkit` in rhea's dev dependencies, and both cannot hold while the kernel ships inside the `py-gzkit` wheel.
Options: (A) one distribution, the checker test the only fence, adopters taking `py-gzkit` at runtime; (B) the
kernel as its own distribution in a uv workspace with `py-gzkit`, as Montenegro's kernel is its own artifact
(Appendix A.1); (C) every region a workspace member. The agent recommended B and named its cost: a second PyPI
name and release, the distribution validator and the version-release rule each extended to two packages.
Operator, verbatim: *"Keep one distribution"*.

Settled: A. `uv_build` and uv workspaces take no part in boundary enforcement; the dependency-rules test, read
from the package map, is the fence, as ruled.

The agent's reading of what follows, stated to the operator for correction: the conflict resolves toward the
kernel ruling. An adopter that builds on the kernel takes `py-gzkit` as a runtime dependency, so the rhea finding
(*"governance tooling belongs in its dev dependencies"*) is withdrawn and rhea's `[project] dependencies` entry
stands; the note that moving it to dev dependencies *"clears that path"* for gzkit consuming rhea no longer
holds, and that route stays set aside under its revisit condition.

## source · Montenegro, Ch. 8 on the testing conventions, and how gzkit's features run today

MEAP V02, extracted text held outside the repository, read 2026-11-10: §8.1–§8.2 (PDF pp.216–220), the opening of
§8.4 with Table 8.3 (pp.224–225), §8.6.5 with Table 8.5 (pp.247–248) and §8.7–§8.8 (pp.249–253). Key notes only.

- **Given, when, then in every unit test** (§8.2.1): the three phases are labels in ordinary unit tests, *"without
  Cucumber"*; Cucumber is *"useful when executable scenarios need to be shared with stakeholders and exercised
  through broader application behavior"*. The structure is *"non-negotiable across all test typologies"*.
- **Handlers** (§8.4): *"Use mocks or small in-memory fakes for the output ports"*; pass a real command; prefer
  assertions on results or state, and verify a port call only when the interaction is itself the contract.
- **Adapters** (§8.6.5): the test follows from the dependency: an in-memory structure is used for real, an
  interface or HTTP client is simulated in-process.
- **Not tested** (§8.7): accessors, framework internals, private methods, domain objects as mocks, domain state
  inside handler tests; and no *"integration tests disguised as unit tests"*.

gzkit, surveyed 2026-11-10 by search, not read in full: 82 feature files under `features/`; their steps drive the
CLI, in process through `gzkit.cli.main` or as a subprocess, against real temporary repositories. Of 802 test
modules under `tests/`, 287 use `unittest.mock` or `patch`. Cosmic Python's position, from this run's reading
(`sources/cosmic-python-reading-2026-11-08.md`, Ch. 3 and Ch. 13): fakes over mocks, in the classicist camp;
patching *"couples tests to implementation"* (paraphrased there); the recipe for an adapter includes building a
fake for unit, service-layer and handler tests.

## decision · fakes only inside the hexagon; `unittest.mock` is banned there (operator ruling)

Put to the operator, on the source above, answering *"How shall we do mocking (if at all?)"*: each driven port
gets a hand-written fake adapter that satisfies its Protocol; handler tests wire the fakes, the test case being the
configurator; `unittest.mock` and `patch` are not used inside the hexagon; a mock or stub is allowed only at an
adapter's outer edge, for a dependency gzkit does not own. Montenegro allows mocks or fakes (§8.4); Cosmic Python
argues for fakes (Ch. 3, Ch. 13); Khorikov keeps mocks for unmanaged out-of-process dependencies; Cockburn sets a
test double beside each real adapter (Fig. 3.1); 3/4 toward fakes, Montenegro permitting. The cost was stated: 287
of 802 test modules use `unittest.mock` or `patch` today.

The operator asked for the case on both sides, verbatim: *"discuss the pro's and con's of fake vs mock. what are
the mock risks?"* The agent's account: a mock accepts calls the port no longer has; a mock test restates the
implementation; `patch` names a string path and hides a missing port; each test scripts its own version of the
dependency; and, the agent's own reasoning and not a source's, an agent can make a failing test pass by patching
one more thing. For mocks: no code to keep, easy failure injection, interaction contracts (Montenegro: verify a
call only when the interaction is the contract), and honesty about dependencies one does not own. Against fakes: a
fake can diverge from the real adapter, costs code up front and can grow. The agent offered a middle position (no
`patch`, fakes by default, an injected mock only to force a failure).

Operator, verbatim: *"if I take the middle position, what imposes discipline?"* The agent's answer: only the
`patch` ban is checkable; *"a mock only to force a failure"* is a rule about intent with no witness, and canon
decides between the two: *"Between two options, choose the one that leaves less to unverified guesswork.
Maintenance burden, speed and lighter ceremony are not reasons to choose."* (AGENTS.md § MAKE LLM STOCHASTIC VIBES
INERT). The middle position was withdrawn. Operator, verbatim: *"yes ==> "Shall I record the strict rule: fakes
only inside the hexagon, enforced by banning the unittest.mock import there, with mocks allowed only at an
adapter's outer edge?""*

Settled: the strict rule. The ban is by the region a test covers, so the outer-edge exception is checkable too.
Each fake carries what the ban removes: a way to force a failure and a record of calls. Every driven port thereby
has a second adapter from its first test, which removes canon rule 5's second-adapter threshold as a reason to
defer a port. Existing uses enter a shrink-only baseline and are reworked as each area migrates. Not ruled, noted:
a shared contract test run against both the fake and the real adapter is general practice against a fake
diverging; no source read in this run mandates it.

## decision · where given, when, then is at play, the test is a Behave feature (operator ruling, departing from Montenegro and amending canon)

Put to the operator: must every unit test of the hexagon carry Montenegro's given, when, then labels (§8.2.1), with
the checker failing one that lacks them. Operator, verbatim: *"yes, but let's call this what it is... BDD and
Behave and directly embrace this."* The agent asked which was meant, the name or the tool, quoting what the tool
reading departs from: Montenegro's *"without Cucumber"*, and canon, *"`behave` belongs to heavy-lane OBPI work and
to CI, never to a per-change gate; Gate 4 precedes Gate 5 on the heavy lane and nowhere else."* (AGENTS.md § Gate
Covenant). The agent recommended Behave for handlers only. Operator, verbatim:

> *"whereever the use case/given, when, then Gherkin logic is at play. It seems that we are indeed describing
> behaviors with/to/from handlers/adapters. I just hate to act-as-if and not just go ahead and lean into it. If
> Behave comes with overhead so too does our design architectural choice. What we need is VERY STRICT oversight on
> how an agent executes on any of this as drift and "vibing" on tautological tests is a VERY common
> oversight/failure mode for agents. The models tend too write too many trivial/trite/tautological tests."*

Settled: the tool. Behaviour to and from handlers and adapters is described and tested as Behave features, driven
through the port with the fake adapters wired; labelled comments in unit tests standing in for Gherkin are not
adopted. The agent's reading, stated to the operator for correction: commands, queries and domain objects, whose
recipes are input and output checks with no collaborators, stay `unittest`. The canon sentence quoted above and the
`@covers` proof channel are amended by this ruling's consequence, carried to disposition row 4 and not executed
here. The operator's second requirement, strict oversight against tautological tests, is put next.

## source · gzkit's instruments against tests that cannot fail, surveyed

Read 2026-11-10, module docstrings and the rationale section in full, the code not: `gzkit.red_witness` (GHI #642)
runs a BEHAVIOR-REQ test against the base tree with the production code withheld and classes the result
`assertion`, `error`, `none` or `not-applicable`, a `none` being *"the test PASSED without the production code. It
cannot fail."*; `gzkit.mutation_witness` (GHI #963) deletes a guard and reports `killed`, `survived`, `invalid` or
`inconclusive`, isolating each mutant in its own subprocess; guard canaries bind one reviewed mutant to one claim
(`data/guard_canaries.json`, GHI #1154); `gzkit.tautological_tests` is an AST scanner over `tests/` with a
shrink-only baseline; `gzkit.test_shape` is an advisory screen; and the REQ-coverage gate requires a passing
`@covers` test per BEHAVIOR REQ (`docs/governance/tests-rationale.md` § Mutation-sweep integrity;
`.gzkit/rules/tests.md`). All of them read `unittest`: `gzkit.unit_run_provenance` parses `unittest -v` output,
`@covers` decorates unit tests, and the scanner walks `tests/`, not `features/`. None reads a Behave scenario.

## source · the red witness's reconstructed base and the Step 4b adversary's replay, read to check the agent's critiques

Read 2026-11-10, docstrings only: `gzkit.red_witness` records a `base_provenance` of `working-tree` or
`reconstructed (pre-test parent)`, the second added because the HEAD base is *"vacuous once it lands"* (GHI #849),
so the witness also runs for work already landed. `gzkit.adversary_workspace` (GHI #961) gives the pipeline's
Step 4b independent adversary a disposable checkout in which it must *"REPLAY the proof it is judging"*: run the
baseline, apply the substitution, watch the named test fail on its own assertion, restore the source and re-run.
The pipeline's Stage 2 reference makes proving a test can fail *"the orchestrator's duty (GHI #968)"*, through
`gzkit.mutation_witness.run_mutation_sweep`, and says *"Do not build an all-assertions classifier or count
mutations as coverage."* The cross-family critic at decision moments (`ADR-0.36.0`, `Proposed`) is unbuilt; it
concerns choices put to the operator, not tests.

## decision · the Behave ruling is reversed: hexagon tests stay `unittest`; Behave is for external contracts (operator ruling)

After the Behave ruling the agent put an oversight standard (a hexagon test accepted only when tied to a REQ, seen
red, and killing a mutant) and named that gzkit's four instruments read `unittest` only. The operator chose to
discuss; the agent listed six weaknesses of its own proposal. Operator, verbatim:

> *"i can see there are real tradeoffs with behave vs unittest and I am uncertain now. I am not sure if your
> proposal means to balance them, but these are strong and hard-fought facilities of gzkit:  red witness, the
> mutation witness, the tautology scanner, and the REQ-coverage gate.*
>
> *your critiques:*
>
> *1. same-agent judicial review remains a risk*
> *2. test proliferate under a model like rabbits multiply - tests require discretion and taste.*
> *3. agree with the care of requirements and this may be my (human) fault in that I let too many requirements
> docs to be expressed in a model's writing and not my own hand. If I always direct/produce, and never write, then
> these things can happen.*
> *4. can't that be updated?*
> *5. agree, but don't we have good systems of adversarial review here?*
> *6. i wonder if this means that our review of Behave testing needs even more strident and stringent review?*
>
> *in any case, the decision to lean towards Behave/BDD seems to be somewhat problematic."*

The agent's answers, from the source above: critique 4 was wrong, the red witness already reconstructs a pre-test
base; critique 5 was understated, Step 4b's adversary replays the proof in its own checkout through a different
model family; on 6, yes, and gzkit's 82 existing features already sit outside all four instruments. The agent
recommended reversing: moving handler and adapter tests to Behave would take the hexagon's tests out from under
the instruments and the Step 4b replay, and the operator's objection to acting-as-if is met by dropping the
given, when, then label rule, so that nothing imitates Gherkin. Operator, verbatim: *"Yes, reverse it"*, and,
while the entry was being written: *"Behave stays at the CLI ==> behave is about external contracts"*.

Settled, superseding the previous Behave decision, which stands in the record as made and reversed:

- Hexagon tests (commands, queries, domain, handlers, adapters) stay `unittest`, under the red witness, the
  mutation witness, the tautology scanner, the REQ-coverage gate and Step 4b.
- No given, when, then label rule is adopted.
- Behave is for external contracts. Canon's Gate Covenant sentence on `behave` is not amended.

The agent's reading of the operator's principle, stated for correction: the external contracts are the ones gzkit
owns in Montenegro's sense (§10.6), the commands and queries it accepts at the CLI and the integration events it
publishes, so a Behave feature proves an owned contract and nothing inside the walls.

The operator then gave the reason in their own terms, verbatim: *"it is on the CLI because that is outward-facing
system behavior."* The test of whether something belongs to Behave is therefore whether it is outward-facing system
behaviour. Whether the published integration events fall under it, as the agent's reading had it, was put back to
the operator: for, a published event is the one contract outside readers may rely on, and changing it breaks them
as a changed command breaks an operator; against, the events do not exist yet. The agent recommended including
them, the features written only when the events are. Operator, verbatim: *"Yes, those too"*.

Settled: Behave proves gzkit's outward-facing system behaviour, which is the CLI and the published integration
events; nothing inside the walls.

## decision · hexagon tests follow Montenegro's outcome rows, one test per outcome (operator ruling, in part)

Put to the operator, answering critique 2 (tests multiply): every test of the hexagon names the REQ it proves
(`@covers`), and a REQ has at most one test per distinct outcome, the success case or one named failure, following
Montenegro's handler recipe (Table 8.3: happy path, not found, persistence failure, business-rule violation) and
his command recipe (one valid test, one invalid, §8.3). The agent named the limit: the REQ-naming half is checkable
today; the one-per-outcome half needs each REQ to enumerate its outcomes and is advisory until it does. Operator,
verbatim: *"yes to the use of table 8.3"*.

Settled: the outcome rows. A handler's tests are one per row of Table 8.3 that applies to it; a command's or
query's are one valid and one invalid. The agent's reading, stated for correction: the answer rules the outcome
half and not the REQ-naming half, which is put again after the question below.

## decision · the given, when, then label rule is reopened (operator correction)

The reversal above recorded *"No given, when, then label rule is adopted"*, the agent's own proposal, offered to
meet the operator's objection to acting-as-if. Operator, verbatim: *"I am not sure I agree here: "No given-when-then
label rule, so nothing imitates Gherkin." If it helps for alignment, then it is more harmless than the option to
strictly use Behave within the Hex core."* That bullet of the reversal is withdrawn pending the operator's ruling;
the question is put again.

## decision · hexagon unit tests carry given, when, then labels, and a checker enforces them (operator ruling)

Put to the operator: every unit test of the hexagon carries the three labels in order (Montenegro's *"BDD
contract"*, §8.2.1), aligning unit tests with the Behave features' vocabulary and exposing a test with more than
one action in *when*; (A) checked, a test failing a hexagon unit test that lacks the labels in order, existing
tests in a shrink-only baseline, the one-action rule left to review; (B) convention only. The agent recommended A
under canon's *"choose the one that leaves less to unverified guesswork"*. Operator, verbatim: *"Yes, checked"*.

Settled: A. A correction to the agent's description: the labels are comments, which Python's `ast` discards, so
the checker reads the test source with `tokenize`, not the AST the tautology scanner walks.

The operator then stated the rule as a whole, verbatim: *"the rules for using BDD in gzkit seem clear: if we are
dealing with the contract of outward/consumer-facing, then Behave and BDD are warranted."* Recorded as the rule's
canonical wording. The agent's reading, stated for correction: the labels inside unit tests are a layout adopted
for alignment, not BDD in this sense, although Montenegro calls them *"the BDD contract"*; BDD in gzkit's sense is
Behave proving an outward-facing contract.

## decision · every hexagon unit test names the REQ it proves (operator ruling)

Put to the operator, the half the Table 8.3 ruling left open: must every unit test in the hexagon's test modules
carry `@covers` naming the REQ it proves? Canon requires a `@covers` test per BEHAVIOR REQ but refuses no test that
names none, and a test proving no requirement is never counted. The agent recommended yes, scoped to the hexagon's
test modules, with fake-adapter tests exempt by declaration, existing unnamed tests in a shrink-only baseline;
Montenegro's *"if you cannot explain what bug a test would catch, the test probably should not exist"* (§8.7) made
checkable. Operator, verbatim: *"yes"*.

Settled. With the outcome-row ruling, a hexagon test exists only for a named REQ and one of its outcomes.

## decision · group F closes (derived, not a new ruling)

Group F's questions are answered: uv-build (one distribution; `uv_build` and workspaces enforce nothing; the
checker test is the fence); decorators (the map of kinds to regions, ruled under group D; no marker stereotypes);
structural enforcement between components (Protocol and name for ports and handlers; kernel bases cross-checked
against region); architecture tests and dependency control (the widened dependency-rules test and its per-region
table, ruled under group C); BDD and TDD (Behave for outward- or consumer-facing contracts; hexagon tests in
`unittest` under the existing instruments, labelled given, when, then, one per outcome row, each naming its REQ);
mocking (fakes only inside the hexagon). The frontier moves to group G, transforming gzkit itself, much of which
the five-phase migration and the outside-in build order already rule, and to the held aggregates and bounded
contexts, which wait for Khononov's passages.

## source · Montenegro §2.4, the five-phase migration map, read in full

MEAP V01, extracted text held outside the repository, read 2026-11-10 (PDF pp.32–38), the map the record had cited
from a reading report. Key notes only.

- **No big bang** (§2.4): *"never do a big bang rewrite. Every phase delivered working software. The old path and
  the new path ran in parallel until the new path was proven."*
- **Each phase has a goal, a key question and a trap.** Extract: what logic must survive deleting every
  framework, the trap anemic shells. Define: ports named in domain language, one per collaboration surface and
  not per method. Wrap: facade adapters over the old code with old and new paths compared, the trap business logic
  in the facade. Refactor: handlers depending only on ports, the trap *"the fake hexagonal anti-pattern"*, a
  handler calling an adapter directly. Replace: facades swapped for real adapters one at a time, verified by the
  architecture rules, which *"is not optional"*.
- **The first deliverable is one use case** (§2.4.6): *"a working prototype of one use case, demonstrating
  millisecond test runs and a successful adapter swap. Build that first"*; the migration goes *"one bounded
  context at a time"*.
- **Timing** (§2.4.6): *"If you are already in crisis ... stabilize first."*
- **Two named mistakes** (§2.4.7): validation in adapters, and ports that mirror the implementation.

Cosmic Python's Epilogue, from this run's reading (`sources/cosmic-python-reading-2026-11-08.md`, § Transforming
existing code), agrees on the unit and differs on the order: build the service layer first, one handler per use
case, tie the clean-up to feature work, then identify aggregates, then a strangler fig by event interception.

## decision · gzkit migrates one use case at a time, old and new paths compared, no big bang (operator ruling)

Put to the operator, on the source above: gzkit's transformation proceeds one use case at a time; no big-bang
rewrite; the first use case is a tracer taken through all five phases before a second starts; old and new paths
run side by side, their outputs compared, until the new path is proven and the old is deleted; a use case is
complete when its tests pass the instruments and the dependency checker shows no leak. Montenegro (§2.4, §2.4.6)
and Cosmic Python's Epilogue agree on the use case as the unit; Cockburn and Khorikov not read on migration. The
agent noted that the ledger lets old and new paths each run against a copy and their events be compared. The cost
was stated: two paths per use case during its migration. Operator, verbatim: *"Yes"*.

Settled. Which use case goes first is held for the disposition map. Montenegro's timing advice is put next.

## source · the drydock's purpose and its open contract, read for the timing question

`docs/governance/safe-mode-doctrine.md`, read in full 2026-11-10: the drydock *"designs and lands the new
structures; it does not populate them"* (operator, 2026-10-17, *"repair and realign the structure, don't populate
it"*); *"The pivot happens in this drydock"* (operator: *"this is the best time to pivot, this is exactly why we
are in dry dock"*); normal voyages are *"ordinary operations under the new structures"*. The open contract,
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`, read by its headings and its rulings of 2026-11-08: the
session open since 2026-10-20; change orders placed on owning orders under § Repair orders' frozen scope, among
them RP-7's placement change order and the classic ADR change orders (RP-6); the hexagonal direction filed under
RO-9 tranche 4 on 2026-10-24. Not read: the contract's general arrangement in full.

## decision · the hexagon's structures land in this drydock; use-case migration follows return to service (operator ruling)

Put to the operator, on the source above and Montenegro's *"If you are already in crisis ... stabilize first"*
(§2.4.6): gzkit's transformation splits along the doctrine's line. In this drydock, as change orders on their owning
repair orders: the kernel package, the hexagonal architecture system package map, the widened dependency checker,
the rewritten canon rule 7 and canon page, and the testing rules. After return to service, as normal voyages under
full ceremony: migrating gzkit's use cases into those structures one at a time. The agent noted that one tracer use
case migrated through the new structures could serve as the sea trial's better form, and named the cost: the
drydock's scope grows again and return to service moves later, with the MX session's advisory debt aging (567 hours
at this session's start). Alternative put: everything after return to service. Operator, verbatim: *"Yes"*.

While this entry was written, the operator pasted the full passage of Montenegro §2.4.6 on timing, without comment;
it adds to *"stabilize first"* that hexagonal architecture rewards patience and that a rushed migration introduces
the accidental complexity it is meant to remove. The agent put back whether the passage reopens the ruling, naming
where its own recommendation was weaker than stated (much new design landed with guards advisory; a drydock grown
all week; structures arriving before any use case exercises them) and a narrower third option (only the package map
and the rule 7 rewrite in the drydock, the kernel, checker and testing rules built outside-in with the first tracer
after return to service). Operator, verbatim: *"Ruling stands"*.

Settled: the direction. Not executed and not placed: each change order is opened on the contract, through its own
amendment where § Repair orders' frozen scope requires one, only on the operator's go on the disposition row that
carries it. Whether the tracer serves as the sea trial is the contract's question (§ Exit), carried there and not
ruled here.

## decision · group G closes (derived, not a new ruling)

Group G's questions are answered: the five-phase migration (ruled under group D), the use case as the unit with old
and new paths compared (above), the outside-in order for new work, rhea as the proving ground, and the split between
structures landed in the drydock and use cases migrated after return to service. Held for the disposition map: which
use case goes first. The frontier now holds only items that wait on sources not yet in reach: aggregates and bounded
contexts, the ontology's DDD role, *"one team per context"* for one operator and many agents, and each of the 78
ledger event types' owning entity and drydock name, read against Montenegro's *"an event with no consumer is pure
cost"*. All wait on Khononov's passages.

Derived, not put as a question because canon answers it: the oversight standard for hexagon tests is the
instruments as they stand. A behaviour REQ needs a passing `@covers` test; the red witness shows it failed before
the implementation; proving it can fail by mutation is the orchestrator's duty and Step 4b replays it.

Carried to the disposition map: extending the instruments to read Behave, so that the 82 existing features come
under oversight (critique 6). Carried to the close as material for the restated challenge: the operator's point 3,
on requirements written in a model's hand. Open, put next: a limit on how many tests a requirement may have
(critique 2).

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | catalog, packages, orders and decision records (the skill's *ADR / OBPI* row, relabelled; see the entries below the map) | commissioned (operator, 2026-11-10, verbatim: *"Commission row 1"*) | **Proposed only, mapped from the old system as the contract's ruling of 2026-10-30 and § 12 map it.** (a) **Catalog outcomes**, what an mADR's checklist items were, entering by the R&D-disposition door with this run as their `source`, each admitted on the operator's word and its REQ text in the operator's hand (the agent drafts for rewriting only): the kernel's bases; the hexagonal architecture system package map; the dependency checker widened to every region with the base-to-region and Protocol-and-name checks; the test-discipline checks (the `unittest.mock` ban, the given, when, then labels, `@covers` on every hexagon test, the outcome rows, each hexagon REQ declaring its variants with one test per REQ and variant); configuration read once by the configurator; the published integration events and their contract map; the `gz init` scaffold. The last two are `user_facing`, so each BEHAVIOR REQ under them needs a tagged Behave scenario besides its `@covers` test (§ 10). Families proposed from the legend (in the one-letter codes `families.json` still carries; `GAT`, `LED` and `PKG` under the 2026-10-30 ruling): G for the checkers, L for the integration events, P for `gz init`; the run's cross-cutting constraints possibly as Q outcomes with `applies_to` (decision 8.1); the kernel and configuration unplaced. (b) **One feature package**, the epic: this run's challenge as its story (*"strengthen"*, strong adoption by every adopter), listing those outcomes; its value attested at a work package's or Release Package's attestation. (c) **Work packages**, the mADR's successors, each carrying its bounded advance's intent, rationale, scope and constraints as its story and grouping work orders for cohesion: the structures, the test discipline, configuration, the outward contracts, the `gz init` scaffold. Under the timing ruling the structures land in the drydock as repair packages and repair orders. After return to service, one work package per use case migrated, the tracer first, chosen by the first of those packages in diamond 2, drawing that use case's existing REQs as invariants. Once REQs are admitted, subdomains are discovered in them and bounded contexts designed over them, and the families are checked against those subdomains (decision *the order things derive in*, 2026-11-11). Inside each context, the practice carried from AirlineOps applies: named before coding, its owns and does-not-own stated, a stop when none fits, cross-context imports audited by the dependency checker (decision *the AirlineOps context practice is carried*, 2026-11-11). (d) **Work orders**, the OBPI's successors, each delivering REQs through its tasks, with its freeze, inspection, buy-back and Gate 5, sized by the rekeyed decomposition matrix. (e) **Release Packages**: the new structures are construction and ride a minor; each migrated use case is a refactor and advances the patch (§ 12, the input table). (f) **Classic ADRs** only where a consequential choice (ownership, dependencies, interfaces, persistence, recovery, trust, deployment) must stand as its own record: recognised when it arises, put to the operator one at a time, none authored before the RP-6 crossover and none Current without separate approval of its edition; this run's rulings are not that approval. Legacy decisions this run touches (canon rule 7, the canon page's ADR-taxonomy mapping, `ADR-pool.hexagonal-folder-structure-realization`, `ADR-0.32.0`) stay where they are and are reconciled through exit item 9's inventory | The admission question applies to (f) alone, each choice on its own. (a) to (e) follow canon's records and levels. The operator admits each outcome and initiates each package, or not |
| 2 | GHI / direct fix | commissioned (operator, 2026-11-10, verbatim: *"Commission row 2"*); filed only on the operator's go on this row | (a) whether `@advances` fulfils its declared intent (a correction under the intent test, GHI #752's *"advisory and expected to be empty"*); (b) the 479 files carrying `lane: Lite` or `Heavy`, and the schema widened to admit them, migrated by appended events or grandfathered under the old-state ruling; (c) canon's `project_root` conformance claim, withdrawn by core-model points 2 and 5; (d) the formatter port taking Rich's `Table`, failing point 1; (e) the Harness-Purity Invariant's name, which uses *purity* against the ruled meaning (or row 4); (f) the 82 Behave features outside all four test instruments; (g) the OBPI brief template's architectural checkpoint, which prescribes AirlineOps's six contexts, HOT and COLD contracts and dataset formats, and an OWNS list from a manifest that declares no contexts | Each is a defect in a shipped surface, found by this run; filed through `ghi-author` on the operator's go on this row. The rhea dependency finding is not here: it was withdrawn by the one-distribution ruling |
| 3 | chore | commissioned (operator, 2026-11-10, verbatim: *"Commission row 3"*); admission to the registry on the operator's direction | Advise: a baseline drawdown chore over the run's new shrink-only baselines (the dependency checker, the `unittest.mock` ban, the given, when, then labels, the `@covers`-per-test rule, the closed-set widening baseline), Montenegro's *"Make reducing the freeze store part of regular sprint work"* (§7.8); and a contract-map currency check, the map updated *"the moment an owned contract changes"* (§10.6) | Baselines that only shrink still need someone to shrink them; the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | commissioned (operator, 2026-11-10, verbatim: *"Commission row 4"*); each drafted only on the operator's go on this row | Draft: canon rule 7 and the canon page rewritten to the package design, rule 5's second-adapter threshold retired (every port has a fake); `pythonic.md` § Error Handling (`GzkitError` outside the walls); `tests.md` (fakes only inside the hexagon, given, when, then labels, one test per outcome row, `@covers` on every hexagon test, Behave for outward- or consumer-facing contracts in the operator's wording); the configuration rule (read once by the configurator); the closed-set widening rule (commissioned earlier); the drydock contract's change orders placing the structures on their owning repair orders; disposition row 1's label in the `gz-rnd` skill, `rnd-discipline.md` and the record template, relabelled to the requirements model's records; the Behave ruling citing requirements-model § 10; the specification worded in the new records' terms (outcomes, work packages, work orders), carrying no ADR or OBPI vocabulary forward. Listed for the operator, never drafted over: root `AGENTS.md` § Gate Covenant's Behave sentence and its *"ADR Feature Checklist items and OBPI briefs correspond 1:1"*, which only the operator cuts (RP-7 stage 7) | Canon must say what the run ruled before code is held to it; each on the operator's go on this row, the contract change orders through the contract's own amendment where its frozen scope requires |
| 5 | one-shot refactoring | commissioned (operator, 2026-11-10, verbatim: *"Commission row 5"*, against the agent's recommendation of *not pursued*: its programmes are row 1's work packages, and two records would describe one subject); each programme is routed by pointing to its row 1 work package, never restated here | Propose a program, inside the drydock under the timing ruling: land the kernel package, the package map in `[tool.py-gzkit]`, the widened dependency checker with its region cross-checks, and the test-discipline checkers. Outside it, after return to service and per use case: consolidating configuration (50 loading modules, 35 `manifest.json` readers), moving `GzkitError` out of `core/`, the contract map and the publishing step, and moving rhea's orientation script off the raw ledger | The operator selects each program's route: a repair order in the drydock, a work order after return to service, or a GHI |
| 6 | no action | not pursued (operator, 2026-11-10, verbatim: *"Record row 6"*) | (a) gzkit consuming rhea; (b) a separate kernel distribution or uv workspace; (c) Behave inside the hexagon; (d) marker stereotype decorators; (e) a message broker, inbox or queue; (f) the middle position on mocks | (a) revisit when rhea ships a write side or gzkit needs several backends at once; (b) revisit when an adopter needs the kernel without gzkit at runtime; (c) revisit when the four instruments read Behave; (d) ruled out, Protocol and name identify; (e) revisit when an integration needs one; (f) ruled out, its second half has no witness |
| 7 | further research | commissioned | (a) a knowledge and memory management run: graphify, graphiti and the LightRAG fork against the ontology, the handoff rulings store and the insights log; (b) a decorator opportunity review: where parameterised decorators can enforce contracts, declare gates and mode levels, and move cross-cutting work into bus middleware, across gzkit's code, guards, hooks and the RO-13 mode-contract shapes | (a) opened by the operator's graphify/graphiti question, 2026-11-08, outside the hexagonal subject; (b) opened by the operator's question of 2026-11-09, within the decorator map this run ruled, best after sign-off. The operator opens each |

## decision · row 1 is redrafted on the requirements catalog and the four levels (operator correction)

The agent first drafted row 1 as a feature ADR per use case with OBPIs per phase, following the skill's row label,
*ADR / OBPI*. Operator, verbatim: *"this entire system is meant to be deprecated and superseded by the requirements
catalog, the feature package, the work package, the work order, and the release package ==> "ADR and OBPI""*. The
agent then read `docs/governance/ieee/requirements-model.md` § The records, § 6, § 7, § 9, § 10 and § 12 in full and
redrafted row 1 on its records: the classic ADR as a decision record peer of the catalog (§ 9: *"An ADR carries only
a decision status ... no checklist, no work packages, no release"*); outcomes and REQs in the catalog; the feature
package, work package, work order and task (§ 12's level table); the Release Package. Row 5's routes were corrected
in the same edit from *OBPI* to *a work order*. Booked as an `improvement` insight (scope `gz-rnd`).

Two findings, carried to row 4 and not executed: the `gz-rnd` skill, `docs/governance/rnd-discipline.md` and the
record template still label disposition row 1 *ADR / OBPI*; and § 10 of the requirements model already places BDD
on `user_facing` outcomes, a CLI, API, schema or runtime contract used by humans or external systems, which agrees
with this run's Behave ruling and should be cited by it.

## source · how the old system maps onto the new records, read after two further corrections

The redraft above was not accepted. Operator, verbatim: *"none of that convinces me you understand the new system and
the role of the ADR within it."*; *"what about requirements catalog, feature package, work package, work order, release
package?"*; *"the work package is the old mADR, the work order is the old OBPI."*; and, of the agent's claim that
*"What used to sit inside those mADRs as decisions moves out into classic ADRs"*, *"this is not true either ... can you
look, gather evidence and see for yourself?"* Read 2026-11-10, in full unless stated:
`docs/governance/harbor-classic-adr-change-order.md`; `docs/rnd/four-records.md`; the contract's § The records, by
band and § How work moves; its ruling of 2026-10-30 *The four mapped to what gzkit had* (that entry only);
`docs/rnd/repair-work-organization.md`, the mADR rulings of 2026-11-03 (that section only);
`docs/governance/ieee/design-candidates.md` role 2; the campaign plan § 3 (that bullet); and the section headings of a
legacy mADR, `ADR-0.30.0-okf-documentation-knowledge-structure`.

- **The mADR's jobs were mapped, not extracted** (ruling of 2026-10-30): *"The ADR did five jobs, and only the decision
  stays with it"*; each Feature Checklist item *"is a catalog outcome and its briefs' `REQ-<semver>-NN-MM` are the
  outcome's REQs"*; its semver is the Release Package's version and its closeout that package's close; grafted
  corrections and prerequisites are loose items in the cart. Amended 2026-11-03: the work package is the mADR's
  successor, the story; the work order the OBPI's; the feature package the epic, succeeding no earlier record.
- **What the mADR retained** (design-candidates role 2; campaign § 3): *"mADRs retain design intent, decisions,
  rationale, scope, and constraints for a bounded advance."* The legacy mADR's headings carry them: Intent, Decision,
  Interfaces, Boundary Invariants, Rationale, Consequences, then Checklist and OBPI Briefs.
- **Legacy decisions stay where they are** (the change order, § Crossover): legacy ADRs and mADRs *"keep their files,
  ids, dates and evidence; no blanket rename or deprecation"*, and *"Freezing a legacy container does not retire the
  choices recorded in it; each is reconciled on its own"*, at handback by exit item 9's inventory (retained, captured
  with provenance, retired). § How work moves: *"Completed legacy ADRs stand as legacy evidence, unstarted ones as
  decision records"*.
- **The classic ADR is a separate, new form**, brought in from another project on 2026-11-08, for a consequential
  choice recognised as it arises (*"surfaced as a decision before it is built in"*); an accepted one is cited and
  reused; it starts work only through a queued outcome it governs.

The agent's claim is withdrawn: nothing moves out of an mADR. For new work, the bounded advance's intent, rationale,
scope and constraints are the work package's story; what an mADR checklist item was is a catalog outcome, not a work
order; the work order is what an OBPI was. Row 1 is redrafted only after the operator confirms this reading.

## decision · the run resumes in a new session; the frontier is recomputed (operator ruling)

The handoff `.gzkit/handoffs/20261110T105134Z-hex-spec-groups-e-to-g.md` advised resuming this run. Operator,
verbatim: *"renew mx lease, resume rnd"*, booked through `gz handoff decide` (`proceed`) under this session's own id,
`4d976f7c-1c1a-432d-b098-6a0487a56124`; the MX lease was renewed in the same act. The record was checked against git:
it is unchanged since `9a492caa8`, `main` level with origin, 75 decision entries, all seven disposition rows carrying
a state. Row 1 stands as redrafted on the reading above: the row was commissioned with that text, and the
commissioning is read as the operator's confirmation of it.

The frontier was recomputed from the subject, not taken from the handoff, which said every remaining item waits on
Khononov. That is not so. The group G close left one question *"Open, put next"*: critique 2's remaining half, a limit
on how many tests a requirement may have. The Table 8.3 ruling settled the rows and the `@covers` ruling settled
REQ-naming; the agent had said the one-test-per-row half *"is advisory until"* each REQ enumerates its rows. Whether a
REQ declares its rows, so the limit is checkable, was never put. Its prerequisites are settled, so it is the frontier,
and it is put next. The Khononov items stay held behind it.

Re-read for the question, 2026-11-11, from the held Montenegro text: Table 8.3 is titled *"Handler testing recipe"*,
its rows are *happy path*, *entity not found*, *persistence failure* and *business rule violation*, and its first
column is headed *Scenario*. Two name collisions follow and are held, not ruled: Montenegro's *Scenario* is gzkit's
Behave scenario, and this record's *outcome row* is the catalog's Outcome (`SES1.4`, `requirements-model.md`, § The
records). The row's name is put only after the model is ruled.

## decision · each hexagon REQ declares its Table 8.3 rows, and a checker holds one test per row (operator ruling)

Put to the operator: should each hexagon BEHAVIOR REQ declare the Table 8.3 rows it is proved under, so a checker
refuses a second test for the same REQ and row, and a test for a row the REQ does not declare? Options put: (A)
declare and check, recommended: the discretion critique 2 asks for is spent once, in the REQ and in the operator's
hand (point 3), and a machine holds it after; the cost is a REQ field and one checker; (B) stay advisory, judged by
the Step 4b adversary and the quality reviewer, which leans on the same-agent review critique 1 names as a risk.
Operator, verbatim: *"A"*.

Settled. Critique 2 closes: a hexagon test exists only for a named REQ and one of the rows that REQ declares, and no
two tests share a REQ and a row. Carried to row 1 (a field on the hexagon REQ and the test-discipline checks) and
held: the row's name, put next.

## decision · term: a Table 8.3 row is a *variant* (operator ruling)

Put to the operator: what a Table 8.3 row is called, since Montenegro's column heading *Scenario* is gzkit's Behave
scenario and this record's *outcome row* is the catalog's Outcome. Options put: (A) *variant*, recommended: the group B
ruling makes the hexagon's expected outcomes *"values in closed unions"*, so each row is one variant of the handler's
result union, the success value or one named error, a pretrained term with no gzkit meaning yet, and one a checker can
compare against the handler's declared result type; (B) *path*, Montenegro's *happy path*, but also a file path and
an Outcome's `modules`, and it names how execution runs, not what the handler returns. Operator, verbatim:
*"A: variant"*.

Settled, held here as a term until the project glossary's home is named: a **variant** is one member of a hexagon
handler's result union, the success value or one named error; each hexagon BEHAVIOR REQ declares the variants it is
proved under, and each hexagon test proves one REQ under one variant. _Avoid_: *scenario* (the Behave scenario),
*outcome* or *outcome row* (the catalog Outcome), *path*, *case*. This departs from Montenegro's *Scenario*; the rows
themselves (happy path, entity not found, persistence failure, business rule violation) are his. Earlier entries in
this record that say *outcome row* mean a variant and stand as written.

## decision · the run resumes in a third session; the frontier is recomputed (operator ruling)

The handoff `.gzkit/handoffs/20261111T061225Z-hex-spec-critique2-closed.md` advised resuming this run. Operator,
verbatim: *"resume rnd"*, booked through `gz handoff decide` (`proceed`) under this session's own id,
`28be5a76-7522-4bcb-89d2-5979ba71b97e`. The record was checked against git: unchanged since `67c110bf6`, 78 decision
entries and 38 source entries before this one, all seven disposition rows carrying a state.

The frontier was recomputed from the subject by walking every entry that holds an item open. Each was traced to the
entry that later settled it: the principles' names (the purity rulings), who touches the outside and the handlers
question (constellation point 3, *"The handler is the only caller of ports"*), raw strings at the walls (the raw-strings
ruling), the per-region dependency table (its own ruling), port and handler identification and the naming rule (the
Protocol-and-name ruling, Montenegro §7.5–§7.6), and critique 2 (the variant rulings). One hold has no settling entry:
the use-case migration ruling held *"which use case goes first"* for the disposition map, and row 1 says only *"the
tracer first"* without naming it. Its prerequisites are settled, so it is the frontier, and it is put next. The
Khononov items stay held behind it.

## decision · the tracer use case is chosen in diamond 2, not in this run (operator ruling)

Put to the operator: is the use case that goes first named in this run, or left to diamond 2? Options put: (A) leave
it to diamond 2, recommended: the tracer is the first work package's opening choice after return to service, made
against the code as it then stands, and naming it here enumerates downstream tasks inside diamond 1, which gz-rnd
lists as a red flag; the cost is that the run closes without knowing which use case proves the design first; (B) name
it here, from a reading of the CLI's use cases now, which binds the choice to the code as it stands mid-drydock and
adds a reading pass ahead of the Khononov items. Operator, verbatim: *"a"*.

Settled. Row 1 now says the tracer is *"chosen by the first of those packages in diamond 2"*. The frontier holds only
the items that wait on Khononov's passages.

## source · Khononov, *Learning Domain-Driven Design*, Ch. 3, 4, 6 and 7, key notes

Vlad Khononov, O'Reilly, ©2022; the operator's licensed copy, supplied as a PDF 2026-11-11 (not as pasted
passages, which the entry *"Evans and Khononov are held in Kindle form"* had expected), read by the agent in full for
Ch. 3 *Managing Domain Complexity* (pp. 33–47), Ch. 4 *Integrating Bounded Contexts* (pp. 49–60), Ch. 6 *Tackling
Complex Business Logic* (pp. 75–97) and Ch. 7 *Modeling the Dimension of Time* (pp. 99–116). The text is held
outside the repository; only these cited key notes land, paraphrased except where quoted, by printed page. Ch. 1
(subdomains: core, supporting, generic) is not read.

- **What a bounded context is.** Where domain experts' models conflict on a term (the *lead* of marketing and of
  sales), the language is split and each part is assigned to the context where it applies: bounded contexts are
  *"the consistency boundaries of ubiquitous languages"* (p. 36). Prefixing the term (*marketing lead*) is rejected:
  it adds cognitive load and no one speaks that way (p. 35). The language's consistency sets only the widest
  boundary; narrower ones are a design choice for teams, lifecycles or scaling, and their cost is integration
  overhead (pp. 37–38). Coherent use cases on the same data are not split across contexts (p. 38).
- **Subdomains are discovered, bounded contexts designed** (p. 41). A subdomain is *"a set of interrelated use
  cases"* the business defines (p. 39); one context may hold several subdomains.
- **Physical boundary.** Each context is *"implemented as an individual service/project"*, evolved and versioned
  independently; when a context holds several subdomains, the context is the physical boundary and each subdomain a
  logical one, a namespace, module or package (p. 41).
- **Ownership boundary.** A context is owned by one team only; no two teams work on one context; one team may own
  several contexts (p. 42).
- **Integration** (Ch. 4). Touchpoints between contexts are contracts (p. 49). Cooperation: partnership, and the shared
  kernel, an overlapping model that couples the contexts' lifecycles, kept to integration contracts and data
  structures where possible, justified only when duplication costs more than coordination, and fit for contexts owned
  by one team because it makes their contracts explicit (pp. 50–52). Customer–supplier: conformist, anticorruption
  layer, open-host service with its published language, which may be versioned (pp. 53–56). Separate ways (p. 56).
  The context map plots them (p. 57).
- **Aggregates** (Ch. 6). An aggregate is an entity and a consistency boundary: only its own methods, the commands,
  change its state; outside code only reads it (p. 84). It is a transaction boundary: *"one aggregate per database
  transaction"*, and a need to commit several signals wrong boundaries (p. 87). It holds a hierarchy of entities and
  value objects that must be strongly consistent; anything that may be eventually consistent stays outside and is
  referenced by ID (pp. 87–90). One entity is the aggregate root (p. 90). Concurrency is guarded by a version field
  (p. 86). Entities are not used independently, only inside aggregates (p. 84).
- **Domain events** are past-tense messages *"part of an aggregate's public interface"*, which the aggregate
  publishes and others subscribe to (pp. 91–92).
- **Domain services** are stateless business logic over several aggregates. Khononov's example reads two
  repositories inside the service, and the service is no loophole round one aggregate per transaction (pp. 92–93).
  *Contradicts* constellation point 3 (*"The handler is the only caller of ports"*), which follows Montenegro; the
  ruling stands, and the contradiction is recorded here.
- **Event sourcing** (Ch. 7). Every state change is persisted as an event, and the events are the source of truth;
  state, and any number of other models, are projections, and new projections can be added later (pp. 101–107). The
  event store is append-only, fetches by entity and appends with an expected version (p. 107). The pattern is likened
  to a ledger: *"an append-only log that documents transactions"* (p. 108). In an event-sourced domain model every
  change to an aggregate is a domain event (p. 108). A log table written beside a state model degrades: nothing
  enforces that every record is written, or written in the right shape (p. 115).

## source · gzkit's own statements of its bounded contexts, read for the bounded-context question

Read 2026-11-11 in full where each statement sits. Canon names gzkit's bounded contexts four ways:

- `.gzkit/rules/hexagonal-architecture.md` rule 7, and `docs/governance/hexagonal-architecture.md` § Why gzkit's
  domain lives in the ontology: *"Bounded contexts are **subgraphs of the ontology** (corpus / work / source), not
  directories."* The campaign (`docs/governance/build-to-1.0-campaign-2026-06-30.md`, HULL) calls the same three
  *"three typed **domains (subgraphs)** within one ontology"*.
- `docs/design/prd/PRD-GZKIT-1.0.0.md` § 2.2 declares two contexts under ADR-0.0.43's schema, `skill-evaluation` and
  `governance-triage`, both owned by `main-session`, and § 2.3 maps them as a `shared-kernel` over three cross-cutting
  rubric terms.
- `src/gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md` and
  `docs/governance/GovZero/architectural-enforcement.md` offer `[Discovery | Planning | Acquisition | Ingestion |
  Validation | Reporting]`, a list that reads as carried over from AirlineOps.
- `docs/governance/ieee/design-pivot-session-2026-09-25.md` declines *"the pasted assertion that every capability
  is a bounded context"*, and `docs/governance/ieee/requirements-model.md` keeps the catalog's areas apart from
  bounded contexts.

The four do not agree, and none states the term that carries two meanings, which is Khononov's criterion. The run's
own precedent ran the other way: when *purity* was found carrying two meanings, the operator ruled the second a
misnomer to be renamed (*"that's semantic drift"*), keeping one language, not splitting a context.

## decision · the bounded-context question is held for discussion, not ruled (operator response)

Put to the operator: is gzkit one bounded context, its ontology subgraphs and PRD contexts becoming subdomains, or
several contexts inside one distribution? Options put: (A) one context, recommended; (B) several. The operator did not
rule. Operator, verbatim: *"Montenegro uses a repository. 1. let's review, that might be too ontology defined rather
that aligned 2. again, we need to more broadly reconcile the various gzkit conceptualizing epochs 3. even if so, quite
a bit of maturity developed while gzkit was opsdev within AirlineOops 4. aren't bounded contexts derived from, and
categorically organize, REQs?"*, and *"on A vs. B, we need to discuss here more - but guidance on DDD seems to be more
relevant that ontology guidance, but I think these are related."*

On the repository point, Montenegro's text was re-read (MEAP V02, §3.5 Listings 3.12–3.13, §6.3.4 Table 6.2): he does
use a repository, called by the handler inside its transaction; his domain service is handed the existing slugs as
values and calls nothing (*"No interface needed—there is nothing to invert"*). Khononov's domain service calls the
repository itself. Both books use repositories; they differ on who calls one. The contradiction recorded under the
Khononov key notes is that difference, and constellation point 3 stands.

Held, not ruled: whether DDD guidance or the ontology defines gzkit's contexts, the operator leaning to DDD with the two
related. The question is put again after the four points are discussed.

## source · Khononov Ch. 1, and gzkit's requirements catalog and AirlineOps checkpoint, read for point 4

Khononov, Ch. 1 *Analyzing Business Domains* (pp. 3–18), read by the agent in full 2026-11-11. Subdomains are core
(competitive advantage, complex, volatile, built in-house), generic (solved, bought or adopted) and supporting
(simple, CRUD-like, built in-house) (Table 1-1, p. 11). They are *"already there"* and identified by domain analysis
(p. 11). Their finest boundary: *"From a technical perspective, subdomains resemble sets of interrelated, coherent use
cases"*, sharing an actor, the business entities and closely related data (p. 12). Read with Ch. 3: requirements and
use cases are grouped into subdomains, which are discovered; bounded contexts are designed over subdomains, by the
language's consistency, ownership and lifecycle, and one may hold several (pp. 38–41).

`docs/governance/ieee/requirements-model.md` § The records, decision 8.3 and § Family schemes, read 2026-11-11. A REQ
is *"one atomic obligation"*, a member of an outcome, grouped into capabilities and those into eleven families
(Scheme A, product responsibility), banded on MIL-STD-881's model into *product elements* (AIR, SES, CTL, MNT, PKG,
DEC) and *common elements* serving every product family (RQW, GAT, ATT, LED, QUA). Families were chosen as
responsibilities *"that stay put when the delivery method changes"*; Scheme B, by loop stage, was rejected because the
workflow is what the drydock redesigns. Decision 8 § 5 keeps areas and bounded contexts apart.

`docs/governance/GovZero/architectural-enforcement.md` (*Status: Proposed*, last reviewed 2026-02-04) § Layer 2 and
§ Layer 3, read 2026-11-11. Its six contexts (`Discovery | Planning | Acquisition | Ingestion | Validation |
Reporting`) sit beside HOT and COLD contracts, dataset formats (`YYYY-Qn`, `YYCC`) and BTS adapters: AirlineOps's
data-warehouse pipeline, its domain, not gzkit's. Around the names stands a practice: name the context before coding,
state what it owns and does not own, stop when no context fits, and audit cross-context imports.

## decision · two findings on the families, recorded on the operator's correction (operator ruling)

The question *"Do the catalog's families stand as gzkit's subdomains, with contexts drawn over them?"* was put, A
recommended on the ground that the families *"already sort REQs"*. Operator, verbatim: *"what families?"*. Reading
`data/catalog/families.json` and its siblings, 2026-11-11, gave two findings. The agent stated them in conversation and
did not record them. Operator, verbatim: *"These are VERY IMPORTANT and I am disappointed that they are not
canonized"*. They are recorded here as stated.

1. **The families were not derived from REQs.** `data/catalog/outcomes.json` and `data/catalog/reqs.json` are empty
   (`"outcomes": []`, `"reqs": []`). The eleven families were drawn top-down from the `gz` verb surface and
   `src/gzkit` as of 2026-10-18 (`docs/governance/ieee/requirements-model.md` § Family schemes: *"Three schemes
   follow, drawn from the `gz` verb surface and `src/gzkit` as of 2026-10-18"*). The recommendation's ground, that the
   families already sort REQs, overstated them: they are a legend with nothing filed under it. This bears on the
   operator's point 4 and weakens option A. A's best remaining support is that the `gz` verbs are near Khononov's use
   cases, so the families may come near his coherent-use-case test (Ch. 1, p. 12); that is unchecked.
2. **The family codes in the data are stale.** On 2026-10-30 the operator ruled the codes a fixed three letters,
   `AIR`, `SES`, `CTL`, `MNT`, `PKG`, `DEC`, `RQW`, `GAT`, `ATT`, `LED`, `QUA` (`docs/governance/harbor-ro11-intake.md`
   rulings 4 and 5; `requirements-model.md` decision 8.3, amended 2026-10-30). `families.json` still carries one letter
   each (`X`, `H`, `C`, `M`, `P`, `D`, `R`, `G`, `A`, `L`, `Q`), and its `_doc` still cites only decision 8.3's
   original ruling. The re-code is tracked: RP-11 ruling 5 assigns it and RP-11 tranche 1 names `families.json`
   re-coded, with `Family.code`, `OUTCOME_CODE_PATTERN` and the lookup at
   `src/gzkit/governance/trust_audits/catalog.py:114`; RP-11 is a sequenced row of the drydock contract
   (`docs/governance/harbor-pilotage-candidate-2026-10-15.md`), not yet landed. Until it lands, canon and data
   disagree, and any text naming a family must say which code form it uses.

Carried: finding 1 to the bounded-context question, which is put again with it; finding 2 to row 2 as a tracked
discrepancy owned by RP-11, not a new filing.

## decision · finding 1 is carried into the requirements model (operator ruling, row 4)

Put to the operator: should finding 1 also go into the requirements model as an amendment? Options put: amend it, or
leave the record as enough. Operator, verbatim: *"Yes, amend it"*. Done under row 4:
`docs/governance/ieee/requirements-model.md` § Family schemes carries an amendment dated 2026-11-11 stating that the
families were drawn top-down before any REQ, that none is filed under them, and that whether they match the
subdomains the REQs would show is unchecked and held by this run; its status line names the amendment.

## decision · the order things derive in: REQs, then subdomains, then contexts; the ontology depicts (operator ruling)

Put to the operator, after finding 1 left no REQ to discover subdomains in: rule the derivation order now and leave
the list of contexts to evidence, or derive subdomains now from the legacy REQs in the OBPI briefs. Options put: (A)
rule the order, recommended; (B) read the legacy REQs, a population read with a count of what was read against what
exists. Operator, verbatim: *"A: rule the order"*.

Ruled, on Khononov Ch. 1 (p. 12) and Ch. 3 (pp. 36–42), both read before the question was put:

1. REQs and use cases are admitted to the catalog first.
2. Subdomains are discovered in them, by Khononov's test of interrelated, coherent use cases, and each is classed core,
   supporting or generic.
3. Bounded contexts are designed over the subdomains, by the language's consistency, ownership and lifecycle; one
   context may hold several subdomains.
4. The ontology depicts the result. It does not define it.

What this settles. The operator's point 4 is answered yes: contexts organise REQs, by way of the subdomains found in
them. Point 1 is answered: DDD guidance defines, and the ontology, related as the operator said, is the picture of
what DDD found. Point 2 gets its reconciliation rule: the four earlier statements of gzkit's contexts (the ontology
subgraphs, the PRD's two contexts, the AirlineOps six, the areas of the design pivot) are evidence read when
subdomains are discovered, none of them canon for the list. The ontology's DDD role, one of the items riding on the
bounded-context question, is ruled here as item 4.

What it leaves. Whether gzkit is one context or several is not ruled in this run: it waits on admitted REQs and is
row 1's work in diamond 2, where the catalog's eleven families are checked against the subdomains found and kept,
redrawn or retired. Option B's population read is not pursued in this run; the legacy REQs stay frozen as the catalog
ruled, and diamond 2 may read them as evidence. The operator's point 3, the context practice that matured in
AirlineOps, is not settled by this ruling and stays on the frontier.

## decision · the AirlineOps context practice is carried; its six names are not (operator ruling)

Put to the operator, on `docs/governance/GovZero/architectural-enforcement.md` § Layer 2 and § Layer 3 (read
2026-11-11): carry forward the practice that matured in AirlineOps without its six context names, or hold the practice
until diamond 2 names gzkit's contexts. Options put: (A) carry the practice, recommended; (B) hold it until there are
contexts. Operator, verbatim: *"A: carry practice"*.

Carried, as how work proceeds inside each context once diamond 2 has designed them: name the context before coding;
state what it owns and what it does not own; stop when no context fits; audit imports that cross contexts. The last
is the same check as row 1's widened dependency checker and adds no separate machinery. This answers the operator's
point 3. The operator then added, verbatim: *"a + b is really best"*, and confirmed the reading: the practice is
carried now (A) and applied once diamond 2 has designed the contexts (B). The entry already said both; nothing else
changed.

Not carried: the six names (`Discovery | Planning | Acquisition | Ingestion | Validation | Reporting`), which are
AirlineOps's data-warehouse pipeline. Read 2026-11-11, the OBPI brief template
(`.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md`, the Lite checkpoint at line 279 and the Heavy one at
line 603) still prescribes them, and with them more AirlineOps residue: HOT and COLD contract invariants, a
*"Canonical format for this dataset"* line (`YYYY-Qn | YYYY-MM | YYCC | ...`), and an OWNS list said to come *"from
.gzkit/manifest.json"*, which declares no contexts (no `context` or `owns` key, checked 2026-11-11). A brief author
following the template must pick an AirlineOps context or invent one. Carried to row 2 as item (g), filed on the
operator's go on that row. The template's own future rides on row 1, the OBPI's successors.

## decision · ownership does not split gzkit's contexts (operator ruling)

Put to the operator, on Khononov Ch. 3's ownership boundary (recorded under the Khononov key notes above: a context is
owned by one team only, and one team may own several, p. 42) and gzkit's side, one human owner with agents taking
roles from `.gzkit/personas/` per task: drop ownership as a criterion for splitting gzkit's contexts, or count personas
as teams. Options put: (A) drop ownership, recommended; (B) personas as teams, weak because a persona is a role an
agent takes for a task, not a standing group that keeps owning something. Operator, verbatim: *"A: drop ownership"*.

Ruled: with one human owner of all of gzkit, ownership never separates one context from another. When diamond 2
designs contexts over the discovered subdomains, it splits them by the language's consistency and by lifecycle only.
Khononov's rule is not broken, since one team may own several contexts; it gives no split here. Personas are not
teams. Revisit if gzkit gains a second human owner of part of the system.

## Close

**Challenge restated.** Not yet.

**Frontier.** Open, 2026-11-11: the derivation order is ruled (REQs, then subdomains, then contexts; the ontology
depicts), and the list of contexts goes to row 1 in diamond 2. The AirlineOps context practice is carried without its six
names. Ownership does not split contexts (one human owner). Still open: aggregates, and each of the 78 ledger event
types' owning entity and drydock name. All seven disposition rows carry a decision; rows 1 and 5 may change once those
items are ruled.

**Review.** Not yet written.

**Sign-off.** Not yet put.

## What this record does not license

No ADR, OBPI, chore, GHI or canon change is started by this run. Canon rule 7 of
`.gzkit/rules/hexagonal-architecture.md` stands unchanged until the operator's go on a row that
changes it.
