# Hexagonal specification — review account

A readable view over [the run's record](../hexagonal-specification.md), written at the close (2026-11-11) for the
operator's review before sign-off. It holds no authority; the record does, and every ruling there is quoted verbatim.
Each name or claim is marked **ruled** (the operator ruled it), **sourced** (a read source states it), **contradicted**
(a read source states otherwise, named), or **unsourced** (no read source addresses it; it follows from other rulings
or from gzkit's own facts).

## The problem

The run was opened by the house-style run's row 7(c), on your *"we need a better specification. I'd like for a strong
adoption - for all adopters too. strengthen"*, with your correction that hexagonal is *"the entire system"*, not only
the core. What existed was weak (**sourced**):

- the rule named no region beyond *core* and *adapter*, and one test fenced `src/gzkit/core/` alone;
- canon rule 7 forbade port and adapter folders, citing Cockburn, whose §2.4 recommends them;
- the canon page contradicted itself, and called the CLI the configurator because it passes `project_root` inward;
- the output formatter's port takes Rich's `Table`;
- *purity* carried at least three meanings across 108 files;
- 50 modules load configuration for themselves, and 35 more read `manifest.json` directly;
- 479 files carry `lane: Lite` or `Heavy`, and the schema was widened to let them through;
- the ledger's 78 event types were never designed around an owner. 48 use `id` to name a governed artifact, 30 use it
  to name the event itself, and none carries a version.

**Challenge restated** (**ruled**, *"A: adopt draft"*):

> gzkit grew by sporadic, vibe-coded engineering. Its ledger is the clearest case, its bounded contexts were stated
> four different ways across its epochs, and its families were drawn before any requirement existed. Strengthen it
> with a hexagonal specification that every adopter can take up strongly. That means one package design for the whole
> system, not only the core, enforced by checkers rather than prose. Requirements are written in the operator's hand;
> subdomains and bounded contexts are derived from them, and the ontology depicts the result. Every ledger event gets
> an owner and a name in the drydock's vocabulary.

## How the run decided

- **Strict, for every project built with gzkit, whatever its size** (**ruled**, *"I want strict"*). Lighter projects
  have gz-skills and its starter template, so gzkit carries no right-sizing exemption.
- **The constellation** (**ruled**): four hexagonal sources, Cockburn, Montenegro, Cosmic Python and Khorikov; two DDD
  sources, Evans and Khononov. Each point is scored against them, with details worked from Montenegro and Cosmic
  Python. Your caution stands beside it: *do not over-follow Montenegro where his answer is Java Spring's*.
- **Licensed texts stay out of the repository** (**ruled**). Montenegro, Khorikov, Evans and Khononov are cited by key
  notes only.

## The model

### The parts and the principles

- **Six parts** (**ruled**, Montenegro's Table 2.1 in your words): driving adapters, input ports, handlers, domain
  entities, output ports, driven adapters. The domain holds entities, value objects, aggregates and domain services.
- **Purity** is Montenegro's design principle and nothing else (**ruled**): no outside access and no hidden inputs, with
  a domain object free to change its own in-memory state. Any other use of the word is a naming defect, the
  Harness-Purity Invariant among them (**ruled**; its rename is row 2(e)).
- **Encapsulation** (**ruled**): state changes only through the object's methods (3/4); creation only through a
  validating factory (**contradicted** by Cosmic Python, App. E); a declared public surface checked by a test.
- **Completeness** (**ruled**): closed sets handled exhaustively, checked by ty, everywhere a closed set is handled.
  Expected failures are returned as values (**contradicted** by Cosmic Python, which raises domain exceptions).

### The five points of the constellation (**ruled**, *"Approve"*)

1. **The application owns its ports**, each a `typing.Protocol`, never an ABC (canon rule 4). Since refined: repository
   Protocols in domain types, inside the domain; other driven ports in DTOs; input ports in primitive commands,
   queries and results (3/4).
2. **The domain is pure** (3/4; Cockburn leaves the inside to the designer).
3. **The handler is the only caller of ports**, and holds no business decision (3.5/4). **Contradicted** by Khononov,
   whose domain service reads repositories itself (pp. 92–93). The ruling stands and the contradiction is recorded.
4. **Testing follows Montenegro's chapter 8 recipes** (3.5/4; Khorikov contradicts in part, using the managed
   dependency for real).
5. **One configurator wires everything** (3/4). *Configurator* is the term (**ruled**, *"configurator is better"*);
   avoid *composition root*, *bootstrap* and *assembly*.

### The packages

- **Canon rule 7 is overturned** (**ruled**, *"Yes, rule it"*; 3/4, and no source supports rule 7). `core/` is the
  whole hexagon: `domain/`, `ports/driving/`, `ports/driven/`, `handlers/`. Each adapter is a sibling package, the CLI
  being the one that exists today. One `configurator` module wires them.
- **The hexagonal architecture system package map** (**ruled**, your wording) in `pyproject.toml` `[tool.py-gzkit]`
  names each top-level package's part.
- **One kernel package**, a sibling of `core/` (**ruled**). It uses stdlib and Pydantic only and holds no gzkit concept.
  It ships the base classes `ValueObject`, `Entity`, `DomainEvent`, `Command`, `Query` and `Dto`, the error values, the
  command and query buses, and the dependency checker, so adopters build on it. Only Montenegro has a kernel (1/4).
  The name collides with Evans' *shared kernel*, which means a model jointly owned by two teams (**sourced**).
- **The dependency rules** (**ruled**, *"Yes, dependency rules"*): the may-and-must-not imports of each region. The
  per-region table follows Montenegro's Table 6.1, with two departures. Driving adapters never import the domain, and
  only the repository adapter sees it. The rules are enforced by gzkit's own stdlib test, widened to every region and
  read from the package map (**ruled**, *"fortify what gzkit already does"*). Each class's base is cross-checked
  against its region.
- **One distribution** (**ruled**, *"Keep one distribution"*, against the agent's recommendation). The checker test is
  the only fence; `uv_build` and uv workspaces restrict no import (**sourced**, uv documentation). Adopters take
  `py-gzkit` at runtime.

### Values, entities, storage

- **Value objects** are frozen Pydantic models, built through `create(...) -> Self | ValidationErrors`, and a rule
  about a value is a method on its type (**ruled**, 3/4).
- **Entities are frozen**; each change returns a new version together with the event it records (**ruled**, *"yes,
  B"*). **Contradicted** by all three sources that address it. The reason is gzkit's append-only ledger.
- **Commands carry primitives**, and the handler converts them (**ruled**, Montenegro explicit). Raw strings never
  enter the domain.
- **Rebuilding never validates.** Only the repository adapter may rebuild, and each tightened rule declares its
  strategy for old state: migrate by appended events, grandfather, or revalidate on next change (**ruled**).
- **The stored shape is a separate model**, mapped both ways inside the repository adapter. A closed set in the domain
  is a `StrEnum`. Writes are canonical; reads are tolerant (**ruled**).
- **Widening a closed set needs a recorded ruling**, held by a shrink-only baseline (**ruled**; **unsourced**, it
  answers the 479-file drift).
- **DTOs** are frozen and checked for types only, with no `create` (**ruled**, 2/4).
- **Inside the walls** (domain and handlers), expected failures are values. **Outside**, `GzkitError` is the shared
  structure (**ruled**). `GzkitError` therefore leaves `core/`.

### Messages, events and the ledger

- **A command bus and a query bus** in the kernel. The registry is built at start-up and fails fast; cross-cutting work
  wraps the bus once (**ruled**, 2/4).
- **Ports and handlers are identified by Protocol and name**, `XUseCase` to `XHandler`, not by marker decorators
  (**ruled**). Decorators are mapped to regions under one rule: a decorator enforces a contract, applies a policy or
  declares a fact, and never makes a business decision (**ruled**). Parameterised decorators state their contract at
  the definition.
- **A domain event and a ledger event are one fact in two shapes.** A ledger row exists only because an entity method
  recorded it (**ruled**). This is **unsourced** as a storage model: none of the four hexagonal sources stores state as
  events. It follows from the frozen-entity ruling. Khononov's event sourcing (Ch. 7) agrees, though it was read after
  the ruling.
- **Every ledger event type belongs to an entity, and none leaves the ledger** (**ruled**, *"A"* and *"we will NOT
  leave the ledger"*).
- **Follow-on reactions are listeners on the bus**, dispatched after the event is in the ledger (**ruled**, 3/4).
- **Outside readers get a small set of versioned integration events, never ledger rows** (**ruled**; Montenegro,
  Cosmic Python, Evans). Rhea's orientation script moves off the raw ledger.
- **Configuration is read once, by the configurator**, and passed in as frozen values (**ruled**, 2/4 direct).

### Testing

- **Fakes only inside the hexagon**; `unittest.mock` is banned there (**ruled**, 3/4 toward fakes). Every driven port
  has a fake from its first test, which retires rule 5's second-adapter threshold.
- **Hexagon tests stay `unittest`**, under the red witness, the mutation witness, the tautology scanner, the
  REQ-coverage gate and Step 4b (**ruled**, *"Yes, reverse it"*). The earlier Behave-inside ruling stands in the record
  as made and reversed.
- **BDD in gzkit** (**ruled**, in your words): *"if we are dealing with the contract of outward/consumer-facing, then
  Behave and BDD are warranted"*. That means the CLI and the published integration events.
- **Given, when, then labels** in every hexagon unit test, checked with `tokenize` (**ruled**, *"Yes, checked"*).
- **Every hexagon test names its REQ** with `@covers` (**ruled**).
- **Each hexagon REQ declares its variants**, and a checker holds one test per REQ and variant (**ruled**, *"A"*). A
  **variant** is one member of a handler's result union (**ruled**, *"A: variant"*; a pretrained term). Montenegro's
  column heading is *Scenario*. Avoid *scenario*, *outcome row*, *path* and *case*.

### Adopters and transformation

- **`gz init` scaffolds the hexagon for a new project.** An existing project gets the map and the checker.
  `--no-skeleton` never skips the check (**ruled**; **unsourced**, since no source addresses scaffolding).
- **New use cases are built outside-in, test first** (**ruled**, 3/4). **Brownfield code enters by Montenegro's five
  phases**, one use case at a time, with old and new paths compared and no big bang (**ruled**).
- **The structures land in this drydock; use-case migration follows return to service** (**ruled**, *"Ruling stands"*,
  after Montenegro's *"stabilize first"* was pasted). The tracer use case is chosen in diamond 2 (**ruled**, *"a"*).
- **Rhea is gzkit's proving ground** (**ruled**).
- **The domain's ubiquitous language is the drydock's ruled ladder**, not today's ADR and OBPI names (**ruled**).

### DDD: what this run ruled and what it sent on

- **The derivation order** (**ruled**, *"A: rule the order"*; Khononov Ch. 1 and 3). REQs are admitted first,
  subdomains are discovered in them, and bounded contexts are designed over those. The ontology depicts the result and
  does not define it. The four earlier lists of gzkit's contexts become evidence for diamond 2, not canon.
- **The catalog's families were drawn before any REQ** and group none yet (**sourced**). The requirements model now
  says so (row 4, *"Yes, amend it"*). The one-letter codes in `families.json` are stale against the three-letter ruling,
  which RP-11 tracks (**sourced**).
- **The AirlineOps context practice is carried; its six names are not** (**ruled**, *"a + b is really best"*). Name the
  context before coding, state what it owns and does not own, stop when none fits, and audit cross-context imports.
  The practice applies once diamond 2 has designed the contexts.
- **Ownership does not split gzkit's contexts**: there is one human owner, and personas are not teams (**ruled**, *"A:
  drop ownership"*).
- **The aggregate rule is left to diamond 2** (**ruled**, *"B: leave to diamond 2"*, against the agent's
  recommendation). So are the list of contexts and each of the 78 event types' owner and drydock name.

## What each row would produce

Every row carries a decision. None executes without your go on that row.

1. **Catalog, packages, orders and decision records** (commissioned; proposed only). This row produces:
   - catalog outcomes, each REQ in your hand: the kernel's bases, the package map, the widened dependency checker, the
     test-discipline checks, configuration, the integration events and their contract map, and the `gz init` scaffold;
   - one feature package, with the restated challenge as its story;
   - work packages: the structures (as repair orders in the drydock), the test discipline, configuration, the outward
     contracts, and the scaffold. After return to service, one work package per migrated use case, the tracer first;
   - (c′) diamond 2's design work once REQs exist: subdomains, then contexts, then the AirlineOps practice, then
     aggregates, then the 78 event types' owners and names;
   - work orders, Release Packages, and classic ADRs only where a consequential choice must stand as its own record.
2. **GHIs** (commissioned; filed on your go). (a) whether `@advances` fulfils its intent; (b) the 479 `lane` capitals
   and the widened schema; (c) canon's `project_root` claim; (d) the formatter port taking Rich's `Table`; (e) the
   Harness-Purity name; (f) the 82 Behave features outside the instruments; (g) the OBPI template's AirlineOps
   checkpoint.
3. **Chores** (commissioned; advice only). A drawdown chore for the run's shrink-only baselines, and a contract-map
   currency check.
4. **Canon** (commissioned; each drafted on your go). This row covers:
   - rule 7 and the canon page rewritten, and rule 5's threshold retired;
   - `pythonic.md` § Error Handling;
   - `tests.md`;
   - the configuration rule and the closed-set widening rule;
   - the drydock contract's change orders;
   - row 1's label in gz-rnd, its doctrine and the record template;
   - the specification worded in the new records' terms.

   Done already: the requirements-model amendment on the families. Listed for you alone: the Gate Covenant's Behave
   sentence and the 1:1 checklist sentence.
5. **One-shot refactoring** (commissioned, against the agent's *not pursued*). In the drydock: the kernel, the package
   map, the checker and the test checkers. After return to service: configuration consolidation, moving `GzkitError`,
   the contract map and publishing, and rhea's reader. Each programme is routed through its row 1 work package.
   Revisited at the close and unchanged.
6. **No action**: gzkit consuming rhea, a separate kernel distribution, Behave inside the hexagon, marker stereotypes, a
   broker or queue, and the middle position on mocks. Each has its revisit condition or the reason it was ruled out.
7. **Further research** (commissioned; you open each). (a) a knowledge and memory run: graphify, graphiti and the
   LightRAG fork; (b) a decorator opportunity review, best after sign-off.

## Where the record departs from its sources

- **Point 3 against Khononov's domain service.** The ruling follows Montenegro.
- **Frozen entities against Montenegro, Cosmic Python and Khorikov.** The reason is the ledger.
- **Validating factories and returned errors against Cosmic Python.**
- **The kernel** is Montenegro's alone, and its name collides with Evans' *shared kernel*.
- **Identification by Protocol and name** in place of Montenegro's stereotypes.
- **The given, when, then labels** are adopted for alignment, not as BDD, though Montenegro calls them *"the BDD
  contract"*.
- **The variant** replaces Montenegro's *Scenario*.
- **Unsourced and ruled on gzkit's own grounds:** the event-as-stored-record model before Khononov was read, the
  closed-set widening rule, the `gz init` scaffold, and `--no-skeleton` never skipping the check.
