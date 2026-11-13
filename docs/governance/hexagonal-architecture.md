# Hexagonal Architecture — gzkit's specification

> **Status.** This page is gzkit's hexagonal specification. Its rulings come from the R&D run
> [`docs/rnd/hexagonal-specification.md`](../rnd/hexagonal-specification.md), signed off funded on 2026-11-11.
> Each ruling there quotes the operator verbatim, and the record, not this page, holds that authority. The
> per-turn form is [`.gzkit/rules/hexagonal-architecture.md`](https://github.com/tvproductions/gzkit/blob/main/.gzkit/rules/hexagonal-architecture.md).
>
> **gzkit's code does not yet conform.** § Present state lists the measured gaps, each tracked. The structures
> (kernel, package map, widened checker, test checkers) land in the open drydock. gzkit's use cases migrate into them
> one at a time after return to service. Until then, read this page as the target, and the rule as what binds today.

## What hexagonal means here

Alistair Cockburn, *Hexagonal Architecture* (2005), also called *Ports and Adapters*
(<https://alistair.cockburn.us/hexagonal-architecture/>). Its load-bearing demand, from § 1.1:

> "Never explicitly name any external object or technology. Always take a parameter for any external object or
> technology you wish to access."

gzkit applies the pattern **strictly, to the whole system**, not only to a core. It applies to **every project built
with gzkit, whatever its size**: lighter projects have their own tools (gz-skills, its starter template,
Superpowers-Backplane), so gzkit carries no right-sizing exemption. gzkit is opinionated in the way Django is: it
imposes one correct hexagonal design on itself and on its adopters.

### Sources

Each point below is weighed against a **constellation** of six sources:

- **hexagonal (four):** Cockburn and Garrido de Paz, *Hexagonal Architecture Explained* (2024), what the pattern is;
  Montenegro, *Clean Applications with Hexagonal Architecture* (Manning MEAP), the inside structure, enforcement and
  testing; Percival and Gregory, *Architecture Patterns with Python* (Cosmic Python), the Python idiom; Khorikov,
  *Unit Testing Principles, Practices, and Patterns*, where logic lives and how it is tested;
- **domain-driven design (two):** Evans, *Domain-Driven Design*; Khononov, *Learning Domain-Driven Design*.

Details are worked from Montenegro and Cosmic Python. Where Montenegro's answer is Java Spring's rather than the
pattern's, gzkit does not follow it. Licensed texts are cited by chapter and page only.

## The parts

Six parts, in the order a request crosses them:

1. **driving adapters**: the CLI today, which turns a request into a command or query;
2. **input ports**: the use-case `Protocol`s, with the commands, queries and results they take and return;
3. **handlers**: one per input port, orchestrating a use case;
4. **the domain**: entities, value objects, aggregates and domain services;
5. **output ports**: the `Protocol`s the handlers call;
6. **driven adapters**: the code behind each output port (files, git, the ledger, GitHub).

A **configurator** wires them at start-up: it builds the driven adapters, injects them into the handlers, and hands
those to the driving adapters (Cockburn Fig. 2.1). _Avoid_: composition root, bootstrap, assembly.

## The principles

- **Purity** is a design principle and nothing else. A pure method depends only on its inputs, has no side effects,
  and returns the same output for the same input (Montenegro § 3.2). The domain has no outside access: no files, git,
  subprocesses, network, environment, clock or randomness. A domain object may still change its own in-memory state
  through guarded methods. No check, fence or folder is called *purity*.
- **Encapsulation** applies to the domain and to commands and queries:
  - **E1:** state changes only through the object's own methods;
  - **E2:** an object is created only through a factory that validates, so an invalid object never exists;
  - **E3:** every module declares its public surface (`__all__`, leading underscores), and a test refuses a reach
    into another module's underscored names.
- **Completeness** applies wherever a closed set is handled:
  - **C1:** handling is exhaustive (`match` with `assert_never`), checked by ty;
  - **C2:** expected failures are returned as values; exceptions are kept for faults.

DTOs, request records and the configurator carry or wire data and hold no rules, so neither principle governs them.

## The five points

1. **The application owns its ports.** Each port is a `typing.Protocol`, never an ABC, defined by the application and
   named in business terms. Repository `Protocol`s use domain types and live in the domain. Other driven ports carry
   DTOs. Input ports take primitive commands and queries and return results. Adapters satisfy a port by its shape,
   never by inheriting from it.
2. **The domain is pure**, as above. What it needs is passed in as values. It records domain events and never
   dispatches them.
3. **The handler is the only caller of ports.** It holds no business decision. It gathers what the domain needs
   through output ports, calls the domain, persists the result and dispatches the recorded events. When a decision
   needs more data part way through, the handler splits it into steps; it never injects a port into the domain.
4. **Testing follows one recipe per artifact** (§ Testing).
5. **One configurator wires everything.** It passes finished adapters and frozen values, never a raw path from which
   inner code builds its own. No other module names a concrete adapter. In tests, the test case is the configurator.

## The packages

- **`core/` is the whole hexagon**, holding `domain/`, `ports/driving/`, `ports/driven/` and `handlers/`. The inner
  packages' final names are set when they land.
- **Each adapter is its own sibling package of `core/`.** The CLI (`src/gzkit/cli/`) is the driving adapter that
  exists today.
- **One `configurator` module** wires them.
- **The kernel** is one package, a sibling of `core/`, holding the building blocks adopters build on:
  - the bases `ValueObject`, `Entity`, `DomainEvent`, `Command`, `Query` and `Dto`, all frozen Pydantic models;
  - the error-value types;
  - the command and query buses;
  - the dependency checker.

  It imports stdlib and Pydantic only and holds no gzkit governance concept. It is not Evans' *shared kernel*, which
  is a model two teams own jointly.
- **The hexagonal architecture system package map** is a list in `pyproject.toml` `[tool.py-gzkit]` naming each
  top-level package's part of the hexagon. A change to it is a recorded decision.
- **gzkit is one distribution.** `uv_build` and uv workspaces restrict no import, so they take no part in enforcement.

### The dependency rules

Each region's permitted imports are listed below. Each also imports stdlib.

| Region | May import |
|---|---|
| kernel | Pydantic |
| `core/domain` | the kernel |
| `core/ports/driving`, `core/ports/driven` | the kernel |
| `core/handlers` | the domain, both port packages, the kernel |
| driving adapters | the driving ports, the kernel, their own library |
| repository adapters | the domain, the kernel, their own library |
| other driven adapters | the driven ports, the kernel, their own library |
| configurator | everything |

No adapter imports another adapter, the handlers or the configurator. Driving adapters never import the domain; only
the repository adapter sees it. The table binds gzkit and is strongly recommended to adopters.

The dependency rules are enforced by gzkit's own stdlib checker, `gzkit.kernel.dependency_checker`, which ships in
the kernel for adopters to run. It reads every region the package map names, and gzkit runs it in
`tests/policy/test_import_boundaries.py` and as `gz validate --hexagon-dependencies` on every per-change `gz check`.
It also cross-checks each class's base against its region: an `Entity` outside `core/domain` fails, and so does a
command with a domain-typed field, which its region's row refuses to import. Existing violations sit in the
shrink-only `data/hexagon_dependency_baseline.json`. _Avoid_: core purity, import purity.

## Values, entities and storage

- **A value object** is a frozen Pydantic model, created through `create(...) -> Self | ValidationErrors`. A rule about
  a value is a method on its type (for example, ordering identifiers by semver lives on the identifier type).
- **An entity is frozen.** A change is a method that checks its rule and returns the new version together with the
  event it records. Three sources make entities mutable; gzkit departs because its system of record is an
  append-only ledger.
- **Commands and queries carry primitives** and validate them in their own `create`. The handler builds the value
  objects, whose factories check again. Raw strings with rules never enter the domain.
- **A DTO** is frozen and checked for types only, with no `create`.
- **A closed set** in the domain is an `enum.StrEnum`: one spelling, exhaustive handling.
- **Rebuilding from storage never validates.** Only the repository adapter may rebuild a stored object, and the
  dependency test holds that.
- **Old state under a new rule.** Each tightened rule declares its strategy for old state when it is tightened:
  revalidate on next change (the default), grandfather terminal entities, or migrate by appended events only.
- **The stored shape is a separate model**, mapped both ways inside the repository adapter. Writes use the canonical
  form only; tolerance of old spellings lives in that adapter alone.
- **Widening a closed set needs a recorded ruling.** That applies to a schema `enum`, a `StrEnum` or a `Literal`.
- **Inside the walls** (domain and handlers), expected outcomes are values in closed unions, and no `GzkitError` is
  raised. **Outside** (adapters and the configurator), `GzkitError` is the shared error structure. A driving adapter
  turns a returned error into a `GzkitError`, an exit code and a message. A fault may surface inside as an exception;
  it propagates to the boundary uncaught.

## Messages and decorators

- **A command bus and a query bus** live in the kernel, stdlib only. Their registries are built at start-up and fail
  fast on a missing handler. Cross-cutting work wraps the bus once, as middleware the configurator chooses: the ledger
  event, the mode level, `Task:` attribution and the guards.
- **Ports and handlers are identified by `Protocol` and name.** Every handler explicitly inherits exactly one use-case
  `Protocol` and takes its name from it (`XUseCase` to `XHandler`). No marker decorators identify them.
- **Decorators by region.** A decorator enforces a contract, applies a policy the configurator chose, or declares a
  fact. It never makes a business decision.

  | Kind | Lives in |
  |---|---|
  | contract checks (`@transition`, `@validate_call` at handler entry) | the domain, handlers and ports |
  | caching (`functools.cache`) | pure domain functions and adapters |
  | cross-cutting work with I/O | bus middleware, and adapters for their own technology |
  | gates (a held lock, an attestation, a stage) | declared per command, applied by bus middleware |
  | retry and timeout | driven adapters |
  | declarations (`@covers`, the mode-contract declaration) | tests and controls |

  A parameterised decorator states its contract at the definition, so the declaration and the check cannot drift
  apart.

## Events and the ledger

- **A domain event and a ledger event are one fact in two shapes.** An entity method records the event. The handler
  passes it to the ledger repository, and the ledger adapter writes its stored shape. A ledger row exists only
  because an entity method recorded it.
- **Every ledger event type belongs to an entity, and none leaves the ledger.** Which aggregates exist, and how each
  event names its owner, is decided when gzkit's contexts are designed (§ Domain-driven design).
- **Follow-on reactions are listeners on the bus**, dispatched after the event is in the ledger. Each listener sends a
  new command. A missed reaction is found by replay.
- **Outside readers get a small set of versioned integration events, never ledger rows.** The application layer
  chooses which facts are published and shapes each one. Each published event is a contract gzkit owns and versions,
  listed in a contract map. The ledger stays gzkit's internal record.

## Configuration

Configuration is read once, at start-up, by the configurator, through one config adapter. The adapter merges gzkit's
defaults with the adopter's overrides (`.gzkit.json` and `manifest.json`) and validates the result into frozen
settings. Each part is passed as values to whatever needs it. No handler, domain code or other adapter reads a
configuration file.

## Testing

- **Hexagon tests are `unittest`**, under the red witness, the mutation witness, the tautology scanner, the
  REQ-coverage gate and the independent replay.
- **Fakes only, inside the hexagon.** Each driven port gets a hand-written fake adapter that satisfies its `Protocol`
  and can force a failure and record calls. `unittest.mock` and `patch` are banned in hexagon tests. A mock is allowed
  only at an adapter's outer edge, for a dependency gzkit does not own. Every driven port therefore has a second
  adapter from its first test.
- **Labels.** Every hexagon unit test carries *given*, *when*, *then* labels in order, checked from the source with
  `tokenize`.
- **Every hexagon test names the REQ it proves** with `@covers`.
- **Variants.** Each hexagon REQ declares its **variants**, and each test proves one REQ under one variant. No two
  tests share a REQ and a variant. A variant is one member of a handler's result union: the success value or one named
  error, such as not found, a persistence failure, or a business-rule violation (Montenegro Table 8.3). _Avoid_:
  scenario, outcome, outcome row, path, case.
- **Behave proves outward-facing behaviour**: the CLI and the published integration events. Nothing inside the walls
  is a Behave feature. In the operator's words: *"if we are dealing with the contract of outward/consumer-facing, then
  Behave and BDD are warranted."*

## Building and migrating

- **New use cases are built outside-in, each step's test first.** The order is:
  1. the command and its use-case `Protocol`;
  2. the handler, against fake driven ports;
  3. the domain;
  4. the driven ports the handler needed;
  5. the adapters;
  6. wiring in the configurator, with one end-to-end check through the bus.
- **Existing code enters by the five phases**: Extract, Define, Wrap, Refactor, Replace (Montenegro § 2.4).
  - It moves one use case at a time; there is no big-bang rewrite.
  - A tracer use case goes through all five phases before a second starts.
  - Old and new paths run side by side, their outputs compared, until the new one is proven.
- **Timing.** The structures land in the open drydock; use-case migration follows return to service.
- **Proving ground.** rhea is gzkit's proving ground: the first adopter to build on the kernel.
- **For adopters**, `gz init` lays down the hexagon for a new project:
  - `core/` with its four packages;
  - a driving-adapter package and a `configurator` module;
  - the package map;
  - the kernel as a dependency;
  - a test running the dependency checker.

  An existing project gets the package map and the checker. `--no-skeleton` skips the folders, never the check.

## Domain-driven design

- **Derivation order.** REQs and use cases are admitted to the requirements catalog first. **Subdomains** are
  discovered in them, as sets of interrelated, coherent use cases (Khononov ch. 1). **Bounded contexts** are designed
  over the subdomains, by the consistency of their language and by lifecycle (Khononov ch. 3).
- **Ownership** does not split gzkit's contexts: gzkit has one human owner, and personas are not teams.
- **The ontology depicts** the result. It does not define the domain.
- **Earlier context lists are evidence, not canon.** gzkit's earlier statements of its contexts are read as evidence
  when subdomains are discovered: the ontology subgraphs, the PRD's two contexts, the AirlineOps six, and the
  design-pivot areas.
- **Inside each context, once designed:**
  - name the context before coding;
  - state what it owns and what it does not own;
  - stop when no context fits;
  - let the dependency checker audit imports that cross contexts.
- **The language** of gzkit's own domain is the drydock's ruled names for its records, not today's legacy ones.
- **Still to be decided, on admitted REQs:** the list of contexts, the aggregates, and each ledger event type's
  owner and new name.

## Present state

What gzkit's code does today against this specification:

| Gap | Tracked |
|---|---|
| Most of gzkit's code is outside every region: 161 packages and modules unmapped, 16 out-of-region imports from `gzkit.cli` (the shrink-only `data/hexagon_dependency_baseline.json`, 2026-11-12) | #1267, row 5 programme |
| `project_root` is threaded inward rather than finished adapters passed (point 5) | use-case migration (§ Building and migrating), row 5 programme |
| The output port's `table` methods take Rich's `Table` | #1321 |
| *Purity* names an ontology fence and the import check | #1322 |
| Configuration is loaded by 50 modules for themselves | row 5 programme |
| `GzkitError` lives in `core/` | row 5 programme |
| A capitalised `lane` was admitted by widening the schema | #1319 |
| No falsifiability instrument reads a Behave feature | #1323 |
| The package map is a draft until RP-6's identity crossover; the kernel, its buses and the checker landed (RP-15 tranche 6); no fakes exist yet | row 1 work packages |

The *row* entries refer to the run's disposition map.

---

## Legacy: the governance-artifact mapping

> **Legacy, reconciled separately.** The sections below predate this specification. They map Cockburn's port and
> adapter onto gzkit's ADR kinds, which organise governance artifacts, not code. They are kept here unchanged as
> legacy decisions, reconciled through the drydock's exit inventory (item 9), not rewritten by the specification
> above. Their *Departures* item 3, which calls the pattern *"not a code-organization rule"*, contradicts the
> specification above. That contradiction is reconciled by the house-style run's disposition row 4(c).

### Mapping to gzkit ADR taxonomy

gzkit's ADR-kind taxonomy maps directly onto Cockburn's pattern:

| Cockburn term | gzkit ADR kind | Semver | Examples |
|---|---|---|---|
| **Port** | `foundation` | `0.0.x` | ADR-0.0.50 (validation pipeline port + redteam-terminal doctrine), ADR-0.0.51 (milestone-maintenance port + `/goal`-first-class doctrine) |
| **Adapter** | `feature` | `0.y.z` | ADR-0.13.0 (OBPI pipeline runtime surface — adapter implementing ADR-0.0.14's deterministic-OBPI-command port), ADR-0.18.0 (subagent-driven pipeline execution — one execution-strategy adapter), ADR-0.12.0 (OBPI pipeline enforcement parity — one enforcement implementation) |
| **Pool** (gzkit-specific) | `pool` | none | Backlog: not yet classified as port or adapter |

Foundation ADRs (ports) define what every implementation MUST honor; feature
ADRs (adapters) plug into existing foundation ports with one specific
implementation.

### Why this mapping holds

The invariance test (*"Without this ADR, would the project still be the
project?"*) is structurally identical to Cockburn's port test (*"Is this an
invariant the application depends on, or one specific way of satisfying an
invariant?"*).

- If the answer is *"the project would still be the project; this is one way
  of doing X"* → adapter (feature kind).
- If the answer is *"the project would not be the project without this
  invariant"* → port (foundation kind).

The hexagonal lens clarifies edge cases the invariance test alone can leave
fuzzy. When considering whether a new ADR is foundation or feature, ask: *"Is
this defining the contract every implementation must honor (port / foundation),
or is this one implementation behind an already-defined contract (adapter /
feature)?"*

### Worked examples

#### Ports (foundation)

- **ADR-0.0.50 — validation pipeline + redteam-terminal doctrine.** The port
  specifies the multi-skill orchestrator contract (stage sequence, persona
  dispatch, receipt shape, redteam terminal, fail-closed gating) every
  validation-phase implementation must honor. `gz-adr-validation-pipeline` is
  the canonical adapter.
- **ADR-0.0.51 — milestone-maintenance pipeline + `/goal`-first-class doctrine.**
  The port specifies when the maintenance milestone fires, what must be
  checked, and how convergence is bounded.

#### Adapters (feature)

- **ADR-0.13.0 — `gz obpi pipeline` runtime surface.** One specific runtime
  implementation of ADR-0.0.14's deterministic-OBPI-command port: it elevates
  the `gz-obpi-pipeline` workflow into a first-class command contract (launch,
  stage progression, resume, abort, sync). The port is the command contract;
  this adapter is the specific runtime surface behind it.
- **ADR-0.18.0 — subagent-driven pipeline execution.** One execution strategy
  for the pipeline runtime — subagent dispatch — behind the same OBPI-pipeline
  contract. Its declared single-driver fallback preserves inline execution, which is
  the adapter tell: it is *one way* of executing, not the invariant.
- **ADR-0.12.0 — OBPI pipeline enforcement parity.** One specific
  AirlineOps-style enforcement implementation behind the pipeline contract.
  Still an adapter; the enforcement invariants are what it conforms to.

#### Pool ADRs are pre-classification

A pool ADR has not yet been classified as port or adapter. Promotion via
`gz adr promote --kind {foundation,feature}` is when the classification is
recorded. Pool ADRs may eventually promote to either kind based on the
invariance test outcome.

### Where this is cited

Operational guidance and the invariance test itself live in
[`docs/user/concepts/foundation-feature-invariance-test.md`](../user/concepts/foundation-feature-invariance-test.md).
That document is the canonical home for the *how do I choose* answer; this
document is the canonical home for the *what's the conceptual origin* answer.

The `gz-design` skill body cites both: the framing question presented to the
operator during ADR design is *"Is this ADR a port (an abstract contract every
implementation must honor) or an adapter (one implementation behind an
existing port)?"*

### Departures from Cockburn

Three deliberate departures from Cockburn's original framing:

1. **gzkit's "pool" kind has no Cockburn analog.** Pool ADRs are pre-port
   pre-adapter — backlog items awaiting classification. Cockburn's pattern
   has no notion of an unclassified node.
2. **Adapters don't always map to external systems.** Cockburn's adapters
   typically wrap external dependencies (DB, framework, UI). gzkit's adapters
   (feature ADRs) frequently implement internal capabilities that don't cross
   process boundaries. The pattern still holds — internal capabilities are
   "outside" the invariant core — but the framing is broader than Cockburn's
   original DB/UI/framework examples.
3. **gzkit makes the port/adapter distinction structural, not architectural.**
   Cockburn used the pattern to organize code; gzkit uses it to organize
   *governance artifacts*. The ADR is the unit, not the module. This is a
   conceptual borrowing, not a code-organization rule.

### Why this codification exists

Before this document, gzkit's ADR scaffold and `gz-design` skill body used
the term *"plug"* in place of Cockburn's canonical *"adapter."* The
terminology drifted from the source and operators picked up the wrong term
through the template scaffold. GHI #489 (filed 2026-05-18) tracks the
mechanical fix; this canon document is the durable answer to *"where did
gzkit's port/adapter framing come from"* — and prevents the next drift by
naming the source explicitly.
