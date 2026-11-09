# Reading report: *Architecture Patterns with Python* (Cosmic Python)

## 1. Header

| Field | Value |
|---|---|
| Title | *Architecture Patterns with Python: Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices* (online edition, "Cosmic Python") |
| Authors | Harry Percival and Bob Gregory |
| URL | <https://www.cosmicpython.com/book/preface.html> (chapter pages under `https://www.cosmicpython.com/book/`) |
| Licence | Online edition and code: Creative Commons CC BY-NC-ND (Preface, § License). The print edition is licensed differently. |
| Online edition stamp | Each page footer reads "Last updated 2023-11-24" |
| Chapters read in full | Preface; Introduction; Part I intro; Ch. 1–7; Part II intro; Ch. 8–13; Epilogue; Appendices A–E (23 pages) |
| Date read | 2026-11-08 |
| Reader's role | Recorder only. This report decides nothing. Everything not in quotation marks is the reader's paraphrase. |

**How to read this report.** Text in quotation marks is the book's own wording: under 25 words each, 40 quotations in total, each with chapter, section anchor and URL. All other text is **paraphrase (P)**. Code listings were not reproduced; a class or function name appears only as a one-line identifier. Section anchors are the HTML `id` values on the pages (for example `#what_is_a_port_and_what_is_an_adapter`).

URL shorthand used below: `ch01` = `https://www.cosmicpython.com/book/chapter_01_domain_model.html`, and the same for `ch02_repository`, `ch03_abstractions`, `ch04_service_layer`, `ch05_high_gear_low_gear`, `ch06_uow`, `ch07_aggregate`, `ch08_events_and_message_bus`, `ch09_all_messagebus`, `ch10_commands`, `ch11_external_events`, `ch12_cqrs`, `ch13_dependency_injection`; `intro` = `introduction.html`; `epi` = `epilogue_1_how_to_get_there_from_here.html`; `appA` = `appendix_ds1_table.html`; `appB` = `appendix_project_structure.html`; `appC` = `appendix_csvs.html`; `appD` = `appendix_django.html`; `appE` = `appendix_validation.html`. Each expands to `https://www.cosmicpython.com/book/<file>.html`.

---

**Edition note (editor, 2026-11-08).** This is the reader's report as landed in a public repository. Each numbered quotation (Q1 to Q40) is replaced by *[quotation withheld]*, its number and citation kept, so the repository carries the book's locations and the reader's paraphrase rather than its text (the online edition is CC BY-NC-ND). The few two-to-ten-word phrases the reader quoted inside paraphrase are kept as identifiers. Nothing else is changed.

## 2. The book's names for the architecture's parts

**Framing (P).** The book does not settle on one architecture name. Its Ch. 2 sidebar "Is This Ports and Adapters?" treats ports and adapters, hexagonal, onion and clean architecture as roughly one idea:

> Q1. [quotation withheld] — Ch. 2, `#_applying_the_dip_to_data_access`, sidebar "Is This Ports and Adapters?", ch02_repository

The book's own picture is the onion: the model sits "inside" and dependencies point inward (Ch. 2, "Onion architecture" figure). Its port/adapter definition (Ch. 2, `#what_is_a_port_and_what_is_an_adapter`):

> Q2. [quotation withheld] — ch02_repository `#what_is_a_port_and_what_is_an_adapter`

> Q3. [quotation withheld] — same section

> Q4. [quotation withheld] — same section

> Q5. [quotation withheld] — same section

The book's canonical table of parts is Appendix A, which groups components under four layers: **Domain**, **Service Layer**, **Adapters (Secondary)**, **Entrypoints (Primary adapters)**. A fifth row, the external message bus, is marked N/A.

### Operator term → book term

| Operator's term | Does the book use it? | Book's term and location |
|---|---|---|
| **Primary (driving) adapters** | **Yes, but only as a gloss.** The book's working term is **entrypoints**. | Ch. 4 `#_putting_things_in_folders_to_see_where_it_all_belongs`: Q6 [quotation withheld] Q7 [quotation withheld] Appendix A labels the layer "Entrypoints (Primary adapters)", with the rows **Web** and **Event consumer**. Q8 (App. A): [quotation withheld] Concrete examples (P): `flask_app.py`, `redis_eventconsumer.py`, the CSV CLI (App. C) and Django views (App. D `#_api_django_views_are_adapters`, titled "Django Views Are Adapters"). |
| **Input ports** | **No.** The phrase "input port" does not appear. | (P) What the book offers in this role changes over the course of the book. **Ch. 4–5:** the **service layer** functions are the API; the book calls them "use cases or entrypoints" (Ch. 4 `#_wrap_up`). Ch. 5 `#primitive_obsession` expresses that API in primitives. **Ch. 9–10:** **commands** (and events) become the interface. See Ch. 9 sidebar "From Domain Objects, via Primitive Obsession, to Events as an Interface" (`#_refactoring_service_functions_to_message_handlers`). The **message bus** becomes "the main entrypoint to the service layer" (Ch. 9 figure caption). No abstract interface type is declared for this inbound boundary. |
| **Input handlers / services** | **Yes, both words, with a stated identity between them.** | **Service layer** (Ch. 4). Q9: [quotation withheld] (Ch. 4 `#_introducing_a_service_layer_and_using_fakerepository_to_unit_test_it`). Ch. 4 `#why_is_everything_a_service` calls it an **application service**, as distinct from a **domain service**. In Ch. 9 `services.py` is renamed `handlers.py` and the functions become **handlers** (event handlers, then **command handlers** in Ch. 10). Q10: [quotation withheld] (Ch. 9 `#_wrap_up` trade-off table). App. A lists the **Handler** row under Service Layer. |
| **Domain entities** | **Yes.** | **Entity** (Ch. 1 `#_value_objects_and_entities`), together with **value object**, **aggregate**, **domain service**, **domain exception**, and (Ch. 8) **domain events**. The umbrella term is **domain model** (Ch. 1 `#_what_is_a_domain_model`), which replaces the introduction's "business logic layer". |
| **Output ports** | **No.** The phrase "output port" does not appear. | (P) The book says **abstraction**, **abstract repository** (`AbstractRepository`, later `AbstractProductRepository`), **abstract UoW** (`AbstractUnitOfWork`), and `AbstractNotifications` (Ch. 13). It also writes "the port" generically (Ch. 2; Ch. 4 `#_the_dip_in_action` calls AbstractRepository "the port, in ports and adapters terminology"). On where ports live: Q11 [quotation withheld] (Ch. 4 `#_putting_things_in_folders…`). Ports are **not** placed in the domain package. The Unit of Work and its ABC sit in `service_layer/unit_of_work.py`. Ch. 13 `#_building_an_adapter_properly_a_worked_example` notes (P) that simple outbound dependencies are declared as plain callables (`send_mail`, `publish`). |
| **Secondary (driven) adapters** | **Yes, as a gloss.** The working term is **adapters**. | Q12: [quotation withheld] (Ch. 4 `#_putting_things_in_folders…`). App. A labels the layer "Adapters (Secondary)". Q13: [quotation withheld] The listed rows are **Repository** and **Event publisher**. Examples (P): `orm.py`, `repository.py`, `redis_eventpublisher.py`, `notifications.py`. |

**Overloaded word to flag (P): "entrypoint".** The book uses "entrypoint" for at least four different things:
1. The primary-adapter package (`entrypoints/`, Ch. 4).
2. The service-layer use cases ("a set of use cases or entrypoints", Ch. 4 `#_wrap_up`; also the Preface: "a service layer to define the entrypoints to our system").
3. Aggregates ("Aggregates are your entrypoints into the domain model", Ch. 7 recap).
4. The message bus ("main entrypoint to the service layer", Ch. 9).

The UoW is also called "a single entrypoint to our persistent storage" (Ch. 6).

**Driven/driving direction labels (P).** The book pairs "inward-facing" with secondary adapters and "outward-facing" with primary adapters (Ch. 4). The book does not explain this pairing.

---

## 3. Named principles

| Principle | Found? | Wording and location |
|---|---|---|
| **Purity** | **Present as an informal word. Not defined or named as a principle.** | Ch. 2 `#_inverting_the_dependency_orm_depends_on_model`: Q14 [quotation withheld] The same section immediately qualifies it: Q15 [quotation withheld] "Pure domain model" recurs (P) in the Epilogue (`#_separating_entangled_responsibilities`: "a step toward building a pure domain model") and App. D (`#_why_was_this_all_so_hard`). Ch. 8 calls events "pure data structures". In the Epilogue, David Seddon's case study disclaims being "a purist". Ch. 13 fn 1 uses "pure" for a "pure" OO language, and fn 2 cites Mark Seemann's "Pure DI". |
| **Encapsulation** | **Yes, named and defined.** | Introduction `#_encapsulation_and_abstractions`: Q16 [quotation withheld] (P) The book uses the first sense: give a task to a well-defined object or function, which it calls "an abstraction". Ch. 1 later speaks of "our principles of encapsulation and careful layering". |
| **Completeness** | **Not found as a principle.** | (P) The nearest text is a heuristic in Ch. 5 `#_adding_a_missing_service`: if service-layer tests must reach into the domain, Q17 [quotation withheld] |
| **Dependency inversion principle (DIP)** | **Yes. The book's organising principle.** | Introduction `#dip` gives the formal definition. Q18: [quotation withheld] (P) The second clause covers abstractions vs details. The book says "depends on" does not necessarily mean imports or calls, and calls the whole of Part I "a worked example" of DIP. |
| **Functional Core, Imperative Shell (FCIS)** | **Yes.** | Ch. 3 `#_implementing_our_chosen_abstractions`: Q19 [quotation withheld]. Ch. 3 sidebar "So Which Do We Use…": Q20 [quotation withheld] (P) The Preface admits Harry had only "vague references" to hexagonal, ports and adapters, and FCIS before the book. |
| **Persistence ignorance** | Yes | Ch. 2 `#_the_normal_orm_way_model_depends_on_orm` (P): the model need not know how data is loaded or saved. Ch. 2 fn 1 narrows this: the domain should have "no stateful dependencies"; helper libraries are acceptable. |
| **SOLID / SRP** | Yes | Introduction fn 2 expands SOLID. Ch. 8 `#_single_responsibility_principle` gives a rule of thumb (P): if describing a function needs "then" or "and", SRP may be violated. |
| **Command-query separation (CQS)** | Yes | Ch. 12 `#_postredirectget_and_cqs`: Q21 [quotation withheld] Fn 1 there separates CQS (one class or module) from CQRS (the whole application). |
| **Others named** | Yes | (P) **Coupling and cohesion** (Ch. 3 intro). **Connascence** (of Execution, Timing and Name; Ch. 11 sidebar). **"Don't mock what you don't own"** (Ch. 6 sidebar). **Explicit is better than implicit** (Ch. 13). **Safe by default** (Ch. 6 `#_explicit_versus_implicit_commits`). **Postel's law / robustness principle** and **Tolerant Reader** (App. E). **Preparatory Refactoring** ("make the change easy; then make the easy change", Ch. 9). **Responsibility-driven design** (Introduction note; Ch. 1 fn 1; Ch. 6 fn 1). **12-factor** config (App. B). Antipatterns named: **Big Ball of Mud** (Introduction), **Distributed Ball of Mud** (Ch. 11), **Anemic Domain** (Ch. 4 trade-offs), **primitive obsession** (Ch. 9 sidebar, treated sceptically), and **"ice-cream cone"** inverted test pyramid (Ch. 4). |

---

## 4. Topic-by-topic findings

**Entities** (Ch. 1 `#_value_objects_and_entities`; App. A).
- Q22: [quotation withheld]
- Q23: [quotation withheld]
- (P) Entities implement `__eq__` on their identity attribute (`Batch.reference`). The simplest hash option is `__hash__ = None`. If entities must be hashable, the hash should use the identity attribute, which should be made read-only. The book warns not to change `__hash__` without `__eq__`.

**Value objects; dataclasses, frozen dataclasses, NamedTuple** (Ch. 1 `#_dataclasses_are_great_for_value_objects`).
- Q24: [quotation withheld].
- (P) `OrderLine` is `@dataclass(frozen=True)` from the first listing. The book describes it as "an immutable dataclass with no behavior".
- The "More examples of value objects" listing places three forms side by side: a frozen dataclass (`Name`), a `typing.NamedTuple` (`Money`) and a `collections.namedtuple` (`Line`). The text credits "dataclasses (or namedtuples)" with value equality. Fn 2 says earlier Python versions might have used a namedtuple and points to `attrs`.
- Value objects may carry behaviour, for example arithmetic dunder methods on `Money`. For value-object hashing, the book says immutability comes "for free" with `frozen=True`.
- Ch. 1 sidebar "More Types for More Type Hints" shows `typing.NewType` wrappers. Fn 4 rejects them in Harry's voice ("It is appalling").

**Aggregates and consistency boundaries** (Ch. 7).
- Q25: [quotation withheld] (`#_what_is_an_aggregate`).
- Q26: [quotation withheld] (`#_why_not_just_run_everything_in_a_spreadsheet`).
- (P) The book separates a constraint (restricts possible states) from an invariant (always true). The aggregate has a root entity. Modification happens only by loading the whole aggregate and calling its methods.
- The example is `Product`, keyed by `sku`, which takes over the `allocate()` domain service. Aggregates are the "public" classes of the model.
- Concurrency is handled with a `version_number` on the aggregate, using optimistic concurrency. The book shows REPEATABLE READ isolation and SELECT FOR UPDATE as alternatives. It weighs three placements for the version number (domain, service layer, UoW/repository by magic) and picks the domain.
- Epilogue `#_identifying_aggregates_and_bounded_contexts` (P): one aggregate per use case; replace object references with identifiers; bidirectional links are a warning sign.

**Domain services** (Ch. 1 `#_not_everything_has_to_be_an_object_a_domain_service_function`; Ch. 4 `#why_is_everything_a_service`).
- (P) An operation with no natural home in an entity or value object, written as a plain function (`allocate`) in `model.py`.
- Ch. 1 recap: Q27 [quotation withheld]verbs" in your code be functions".
- Ch. 1 fn 6 separates a domain service (a business concept) from a service-layer service (a use case). The service layer often calls a domain service.

**Always-valid models.** **Not found** under that or any similar name. (P) Related positions:
- Ch. 1 fn 3 defers a SKU-match check to App. E.
- App. E `#_validating_at_the_edge`: Q28 [quotation withheld]
- The constructors shown do no validation. The domain enforces business rules (pragmatics), while syntax and semantics are checked before the domain is reached.

**Factories / identity.**
- (P) No DDD *Factory* pattern. Ch. 1's recap speaks against `BazFactory`-style classes in favour of functions such as `get_baz()`.
- "Factory" appears only as follows:
  - a test-fixture factory on `FakeRepository` (Ch. 5 `#_mitigation_keep_all_domain_dependencies_in_fixture_functions`);
  - a session factory injected into the UoW (Ch. 6, Ch. 13);
  - a "command factory" built with `make_dataclass` (App. E);
  - Flask app factories (Ch. 13 fn 3).
- Identity: entities are identified by a business reference (`reference`, `sku`, `orderid`). Ch. 1 says identity must be defined explicitly. Test helpers generate random references with `uuid` (Ch. 4). The book does not discuss an identity-generation strategy.

**Validation (App. E).**
- Q29: [quotation withheld] (`#_what_is_validation_anyway`).
- (P) The book splits validation into three kinds:
  - **Syntax**: shape and structure. Checked at the edge, on message classes (App. E shows the third-party `schema` library).
  - **Semantics**: meaning. Checked in the service layer or on the message bus with "Ensure"-style preconditions (`ensure.py`, `MessageUnprocessable`, `ProductNotFound`, `SkipMessage` for idempotent skips). Pitfalls: use the same UoW as the use case; keep business logic out of preconditions. If a rule can be tested in the domain model, test it there.
  - **Pragmatics**: response in context. Belongs in the domain model.
- Recap: Q30 [quotation withheld]. Q31 [quotation withheld]
- The message bus is presented as a place for cross-cutting validation. **Tolerant Reader**: validate as little as possible, read only the fields you need, don't share message definitions between systems. The book limits Postel's law to integration between services you control.

**Business-rule guards.**
- (P) In the domain: `Batch.can_allocate()`, `Product.allocate()` raising `OutOfStock`, and the invariants of Ch. 7.
- In the service layer: precondition checks such as `is_valid_sku` / `InvalidSku` (Ch. 4 `#_a_typical_service_function`), later "Ensure" preconditions (App. E).
- The Epilogue use-case recipe includes "Check any preconditions (see the Ensure pattern…)".

**Domain exceptions / errors.**
- Ch. 1 `#_exceptions_can_express_domain_concepts_too` (P): exceptions can express domain concepts. Q32: [quotation withheld]. Example: `OutOfStock(Exception)`.
- Ch. 4 suggests `domain/exceptions.py` for domain-layer exceptions and service-layer exceptions inside the service layer (`InvalidSku`).
- **Ch. 8 reverses this for out-of-stock:** `OutOfStock` becomes an event, and the book calls the earlier use "exceptions for control flow", a code smell. Q33: [quotation withheld] (`#_the_model_raises_events`).
- Ch. 10: command errors propagate ("fail noisily"); event-handler errors are caught and logged.

**Immutability.**
- (P) Value objects are frozen (Ch. 1). Configuration should be immutable and changed only through environment variables (App. B tip, quoted under Configuration below).
- Observation (P): the event and command listings in Ch. 8–10 use plain `@dataclass`, not `frozen=True`. The text says events "don't have any behavior".

**Commands and queries (CQRS)** (Ch. 10, Ch. 12).
- (P) Commands are imperative, sent to one recipient, fail noisily, and have exactly one handler. Events are past tense, broadcast to all listeners, and fail independently (Ch. 10 table `#_commands_and_events`). A command should change a single aggregate.
- Ch. 12 argues that domain models are for writing. Reads can be eventually consistent. Views live in `views.py`.
- Ch. 12 compares five read-side options: repositories; ORM queries; hand-rolled SQL; denormalized tables; a separate read store updated by event handlers, with Redis as the example.
- Ch. 9's "temporary ugly hack" (the bus returning a result) is fixed in Ch. 12 by separating the POST from a GET.
- Tip: splitting read-only views from handlers "is probably a good idea, even if you don't want to go to full-blown CQRS" (P, Ch. 12 `#hold-on-ch12`).

**The message bus** (Ch. 8–10, 13).
- (P) At first a dict mapping event types to handler lists, a simple publish-subscribe. Ch. 8 notes it gives no concurrency.
- Ch. 8 shows three ways to get events onto the bus; the book prefers the UoW collecting events from `repo.seen`.
- Ch. 9 makes the bus central: it pulls events from the UoW with `collect_new_events()` and processes a queue.
- Ch. 10 splits dispatch into `handle_event` and `handle_command`, adds retries with tenacity, and logs messages.
- Ch. 13 turns the bus into a class (`MessageBus`) that receives already-injected handlers. Footnote: the Ch. 9 module version was effectively a Singleton.
- The book contrasts it with Celery (Ch. 8 sidebar).
- Observation (P): the Ch. 8 recap box labels "Option 1" and "Option 2" the other way round from the body sections `#_option_1_…` and `#_option_2_…`.

**Domain events and handlers** (Ch. 8–9).
- Q34: [quotation withheld] (Ch. 8 `#_events_are_simple_dataclasses`).
- (P) Events are named in domain language and belong to the domain (`domain/events.py`). The model records them on `.events`. "When X, then Y" phrasing from domain experts signals an event.
- Handlers can call the model or external services. One event may have several handlers, and handlers may raise further events (Ch. 9 `#_what_have_we_achieved`).
- Ch. 9 also notes that events and model objects will duplicate fields, which has a maintenance cost.

**Integration / external events, Redis pub/sub, outbox** (Ch. 11; Epilogue `#footguns`).
- (P) Integration uses asynchronous messages through a **message broker**, with Redis pub/sub as the example. At MADE.com the authors use Event Store; Kafka and RabbitMQ are named as alternatives.
- The inbound adapter is called an **event consumer** (`redis_eventconsumer.py`), described as a thin adapter like Flask. The outbound adapter is an **event publisher** (`redis_eventpublisher.py`).
- Keep internal and external events distinct (`#_internal_versus_external_events`). Outbound events are a place to apply validation.
- **Outbox:** a single pointer in Footguns ("You might also look at the Outbox pattern"). Not explained.
- The Footguns section also warns: Redis pub/sub is not reliable messaging; idempotency is not discussed; event schemas will evolve, and the authors like JSON Schema plus Markdown for documenting them.

**Bounded contexts** (Ch. 7 sidebar "Aggregates, Bounded Contexts, and Microservices"; Epilogue).
- (P) A reaction against one model for a whole business. The same word (for example "customer" or "product") can mean different things in different contexts. Draw boundaries and translate explicitly between them.
- Example: allocation's `Product(sku, batches)` versus ecommerce's richer `Product`.
- Rule of thumb: models carry only the data their calculations need. Choosing aggregates goes together with choosing their context. The book defers depth to DDD books.

**DTOs / read models.**
- (P) The term "DTO" / "data transfer object" is **not found**.
- Nearby concepts:
  - commands and events as "dumb data structures" (Ch. 10);
  - primitives as the service-layer API (Ch. 5);
  - view functions returning dicts (Ch. 12);
  - **read model** / **view model**: denormalized tables or Redis, updated by event handlers (Ch. 12 `#_updating_a_read_model_table_using_an_event_handler`), rebuildable from write-side state;
  - **View Builder** and **view fetcher** objects returning "dumb read models" (Epilogue, tech-reviewer Q&A).

**Repositories and the Unit of Work** (Ch. 2, 6, 7).
- Repository (P): an abstraction over persistent storage that gives the illusion of an in-memory collection. Minimal interface is `add()` / `get()` (fn 6: list, delete and update are deliberately absent). `.commit()` stays outside the repository.
- Ch. 7 rule: Q35 [quotation withheld]
- Fakes are easy to build. Ch. 2 tip (P): if something is hard to fake, the abstraction is probably too complicated.
- The Ch. 2 sidebar on ABCs, duck typing and Protocols says the authors sometimes delete ABCs from production code and suggests PEP 544 protocols as an alternative. Ch. 8 suggests switching ABCs to `typing.Protocol` to avoid inheritance.
- UoW (P): an abstraction over atomic operations. It is a context manager, gives access to repositories (`uow.batches`, later `uow.products`), commits explicitly, and rolls back by default ("safe by default"). The book counts the UoW as part of the service layer (Ch. 6 intro).
- The UoW narrows SQLAlchemy's Session ("Don't mock what you don't own"). It later tracks seen aggregates for event collection.
- App. C swaps in CSV-backed `CsvRepository`/UoW implementations without changing the service layer.

**Mapping (classical / imperative ORM mapping; one-way vs two-way).**
- Ch. 2 `#_inverting_the_dependency_orm_depends_on_model` (P): SQLAlchemy "declarative" models make the model depend on the ORM. The book instead uses what it says SQLAlchemy calls a **classical mapping**: `Table` objects defined separately in `orm.py` and bound by `start_mappers()`. The ORM imports the domain model, not the reverse.
- The book does **not** use the terms "one-way" / "two-way" mapping. (P) Its nearest contrast is App. D (Django). Django has no classical mapper, so the ORM classes carry explicit translation methods in both directions (`to_domain`, `update_from_domain`). The Django UoW's `commit()` must walk every touched object and copy it back to the ORM.
- Ch. 2's trade-off table lists hand-maintained mappings as a cost.

**Project / package structure (App. B; Ch. 4).**
- (P) Ch. 4 introduces `domain/`, `service_layer/`, `adapters/`, `entrypoints/`, with `config.py` at the root and `tests/{unit,integration,e2e}`.
- App. B: `src/allocation/...` installed with `pip install -e` via a three-line `setup.py`, plus Dockerfile, docker-compose, Makefile, `mypy.ini`, and `tests/` with `conftest.py` and `pytest.ini`.
- Later chapters add `domain/commands.py`, `domain/events.py`, `service_layer/handlers.py`, `service_layer/messagebus.py`, `service_layer/unit_of_work.py`, `adapters/notifications.py`, `views.py` and `bootstrap.py`.
- Observation (P): App. B's prose says the package is "totally flat" and would grow `domain_model/`, `infrastructure/`, `services/` and `api/`. The tree printed beside that prose already shows `adapters/`, `domain/`, `entrypoints/` and `service_layer/`.

**Layering** (Introduction `#_layering`; Ch. 2; App. A).
- (P) The book starts from the three-layer architecture (presentation, business logic, database) and turns it "inside out" with DIP into the onion.
- Final layers (App. A): Domain; Service Layer (handlers, UoW, internal message bus); Adapters (Secondary); Entrypoints (Primary adapters).
- Dependency direction is shown in the Ch. 4 `#_the_dip_in_action` figures: the service layer depends on the domain and on AbstractRepository; adapters implement the abstraction.

**Dependency enforcement (e.g., import-linter).** **Not found.**
- No mention of import-linter or any tool that enforces layering. Searches for "import-linter", "import_linter" and "importlinter" returned nothing on any page.
- (P) Enforcement is by convention: the ORM imports the model; repositories return only aggregates ("Be wary of breaking it!", Ch. 7 note); the bootstrap is the only importer of config (App. B tip).
- Ch. 2 fn 7 recommends running pylint and mypy to get value from ABCs.

**Architecture tests.** **Not found.** (P) No tests that assert import or dependency structure. The test taxonomy covers unit, integration and e2e only.

**Configuration** (App. B `#_config_py`; Ch. 13).
- (P) `config.py` exposes functions, not import-time constants, so that callers can change `os.environ`. It has local-dev defaults (fn 4: you may prefer to fail hard on missing variables). The book points to environ-config and 12-factor environment variables.
- Q36: [quotation withheld] Q37: [quotation withheld] (App. B tip, said of the bootstrap script).

**Bootstrapping and the composition root** (Ch. 13).
- Q38: [quotation withheld] (`#_arent_explicit_dependencies_totally_weird_and_java_y`).
- (P) `bootstrap.py` declares default dependencies that can be overridden, does one-time initialisation (`orm.start_mappers()`, logging), injects dependencies into handlers, and returns the message bus.
- Manual DI ("Pure DI", per Mark Seemann, fn 2) is shown three ways: closures/lambdas, `functools.partial`, and callable classes. Note: closures bind late, which can confuse when dependencies are mutable.
- Harry's version inspects handler signatures (`inject_dependencies`). Bob's even-more-manual version writes the partials inline. Both are said to work because DI happens in one place only, the handlers.
- DI frameworks (Inject, Punq, Dependencies) are suggested only for DI at several levels or chained dependencies.
- Ch. 13 recap recipe for a proper adapter: define the API with an ABC; implement the real thing; build a fake for unit, service-layer and handler tests; find a less-fake version for the Docker environment (MailHog); test the less-fake real thing.

**Testing.**
- **Test pyramid** (Ch. 5 `#_how_is_our_test_pyramid_looking`, `#_wrap_up`). Recap rules of thumb (P):
  - one e2e test per feature;
  - most tests against the service layer;
  - a small core of domain-model tests, which may be deleted once the service layer covers them;
  - error handling counts as a feature (one e2e test for all unhappy paths);
  - express the service layer in primitives.
- **High gear / low gear** (Ch. 5 `#_high_and_low_gear`): (P) test against services when adding features or fixing bugs (lower coupling); drop to domain-model tests for new projects or hard problems (better design feedback). Bicycle-gear metaphor. Fn 1 there warns about combinatorial explosion in high-level tests.
- **Edge-to-edge tests** (Ch. 3 `#_testing_edge_to_edge_with_fakes_and_dependency_injection`): (P) invoke the whole system with I/O faked through DI. The book credits the name to Bob. Downside cited: DHH's "test-induced design damage".
- **Fakes vs mocks** (Ch. 3 `#_why_not_just_patch_it_out`):
  - Q39: [quotation withheld]
  - Q40: [quotation withheld]
  - (P) Reasons: patching doesn't improve design; it couples tests to implementation; it produces confusing suites.
  - The book places itself in the classicist (state-based) TDD camp, not London school. Fakes are "working implementations… designed for use only in tests"; mocks verify interactions. A fake that records actions is "both a 'fake' and a 'spy'". `unittest.mock` is mentioned only to say MagicMocks are really spies or stubs.
  - Ch. 8 uses `mock.patch` once; Ch. 13 replaces it with DI.
  - The Epilogue's view-builder Q&A mentions testing with "mocked data (e.g., a list of dicts)".
- **Fake message bus** (Ch. 9 `#fake_message_bus`): (P) optional, for isolating handlers. "Start out with edge-to-edge testing, and resort to this only if necessary."

**External contracts: sync vs event-driven integration; orchestration vs choreography.**
- (P) Ch. 11 argues against noun-based, HTTP/RPC-coupled microservices (temporal coupling, the "distributed ball of mud"). It recommends asynchronous messaging, "verbs, not nouns", and accepting eventual consistency between services.
- Ch. 11 `#_the_alternative_temporal_decoupling_using_asynchronous_messaging`: "Like aggregates, microservices should be consistency boundaries." (Not counted as a numbered quotation; under 10 words.)
- Orchestration vs choreography appears only in **Ch. 8 fn 2**. (P) A tech reviewer's remark that moving from imperative to event-based flow control turns orchestration into choreography.
- The book uses "orchestration" heavily for the service layer's job (Ch. 4). It does not develop choreography as a design topic beyond this footnote. Ch. 11 closes by quoting Martin Fowler on how event-notification flows become hard to see.
- The trade-off tables list at-least-once vs at-most-once delivery as a thing to think through.

### Transforming existing code: the Epilogue compared with the operator's five steps

**What the Epilogue prescribes, in order (P):**
1. Name the problem you are solving, and tie the clean-up to feature work ("architecture tax").
2. **Separate entangled responsibilities by building a service layer first** (`#_separating_entangled_responsibilities`). List the use cases and give each an imperative name. Write one function or class per use case that starts a transaction, fetches data, checks preconditions, updates the model and persists. Pull data-access, orchestration and I/O code out of the domain model and into these handlers. Duplication is acceptable; "Just copy and paste" the tangled code into the new place, tidy it, redirect callers, delete the old code (tech-reviewer Q&A). Feathers' *Working Effectively with Legacy Code* is recommended.
3. **Identify aggregates and bounded contexts** (`#_identifying_aggregates_and_bounded_contexts`). Break the connected object graph, replace direct references with identifiers, change one aggregate per use case, move heavy reads to plain SQL or read models, and introduce a message bus that raises one command per affected aggregate.
4. **Strangler fig via event interception** (`#_an_event_driven_approach_to_go_to_microservices_via_strangler_pattern`). (P) Three steps: raise events representing changes in the system to be replaced; build a second system that consumes them into its own model; replace the old system. Start with a "walking skeleton" that only logs its input.
5. **Domain modeling to convince stakeholders** (`#_convincing_your_stakeholders_to_try_something_new`). "We recommend domain modeling as a first step" for carving out a new system. The goal is a shared ubiquitous language. Event storming, CRC and event modeling are named; treat domain problems as TDD kata.

| Operator's step | Closest Epilogue (and book) counterpart | Match? (P) |
|---|---|---|
| 1. Extract domain logic and ubiquitous language | Epilogue "Convincing Your Stakeholders": domain modeling as a first step; ubiquitous language; event storming. Ch. 1 `#_exploring_the_domain_language`. | **Partial, and in a different order.** The book places domain modeling first for *carving out a new system*. For *improving an existing mud ball* its first concrete step is the service layer (Q&A: build a service layer first, then "it's much easier to push logic into the model"). |
| 2. Define ports in domain language | No dedicated step. Ch. 2–3 and Ch. 13 recap: "Define your API using an ABC". Events and commands are named in domain language (Ch. 8, 10). | **Not a named step.** The book's abstractions are named for persistence and I/O roles (`AbstractRepository`, `AbstractUnitOfWork`, `AbstractNotifications`). Domain language governs names of events, commands, exceptions and handlers. The book does not say ports must be phrased in domain language. Ch. 3 heuristics ("Separate the what from the how…") are the nearest guidance. |
| 3. Facade existing code behind ports | No Epilogue step by this name. Nearest: "Don't mock what you don't own" (Ch. 6) wraps a messy subsystem (SQLAlchemy Session) in a simpler abstraction. Ch. 3 wraps the filesystem. The tech-reviewer Q&A says to keep a service layer even over a messy Django ORM. App. D's `logic.py` stepping stone. | **Partial.** The idea of a narrowing abstraction over existing infrastructure is present. Fronting *existing application code* with a port as a migration step is not described. The book's migration route copies code into use-case handlers instead. |
| 4. Refactor into handlers | Epilogue step 2 (service layer / command handlers). Ch. 9 refactors services into handlers. | **Strong match**, but it is the book's **first** remediation step, not its fourth. |
| 5. Swap facades for real adapters | Strangler fig / event interception (Epilogue). Ch. 13 adapter recipe (fake, then real, then less-fake integration test). App. C (swap the whole infrastructure for CSVs). | **Partial.** The book swaps *fakes* for real adapters, and *systems* for new systems. It has no "facade, then real adapter" sequence for legacy code. |

---

## 5. Where the book's examples depend on Flask, SQLAlchemy, pytest, Redis and others

| Technology | Where it carries weight | What gzkit would need to translate (P, descriptive only) |
|---|---|---|
| **pytest** | Throughout. Ch. 2 explains fixtures (the `session` fixture). `conftest.py`, `pytest.ini`, the `add_stock` fixture (Ch. 4). `@pytest.skip` (Ch. 7 exercise). `pytest-django` and `mark.django_db` (App. D). App. B points to the pytest docs on layout. | Fixtures become `unittest` `setUp` and helpers. The book's fake-based, state-asserting style needs no pytest-specific feature. |
| **unittest.mock** | Ch. 3 (definition only) and Ch. 8 (`mock.patch` of email), later removed in Ch. 13. | Already stdlib. The book recommends avoiding it. |
| **SQLAlchemy** (+ Alembic) | Ch. 2 classical mapping (`orm.py`, `start_mappers`). Ch. 6 `SqlAlchemyUnitOfWork` and session factory. Ch. 7 isolation levels and `with_for_update`. Ch. 12 ORM-based views and SELECT N+1. Ch. 2 fn 4 mentions Alembic. | The UoW and repository ports are ORM-free. The mapping, session, transaction and locking material is SQLAlchemy- or Postgres-specific. App. C shows a non-ORM (CSV) repository and UoW. The Ch. 2 exercise invites an ORM-free repository. |
| **Postgres / SQLite** | Ch. 6 (SQLite swapped in for tests), Ch. 7 (REPEATABLE READ, SERIALIZABLE, SELECT FOR UPDATE; fn 3 database differences), Ch. 12 (raw SQL views, denormalized table). | Concurrency control is database-specific. Ch. 7 says not to copy and paste it. |
| **Flask** | Primary adapter in Ch. 4–13 (`flask_app.py`). Ch. 13 fn 3 on module-global bus and app factories. App. E validation errors. | Primary adapter only. The book stresses that the framework is a minor detail. App. C (CLI) and App. D (Django views) are alternative primary adapters. |
| **Redis** | Ch. 11 pub/sub event consumer and publisher. Ch. 12 Redis read model. Epilogue Footguns: Redis pub/sub is not reliable. | An external message bus and read store. Both are secondary or primary adapters. |
| **Docker / docker-compose / Makefile / MailHog** | App. B (containers, config, env), Ch. 13 (MailHog for email integration test). | Environment and integration-test infrastructure. |
| **tenacity** | Ch. 10 (retry in message bus), Ch. 11 (retry loop in e2e test). | Third-party retry helper. |
| **schema** library | App. E (syntax validation on message classes, `ignore_extra_keys=True`). | Third-party validation. |
| **requests / duckduckgo / attrs / environ-config / Inject / Punq / Dependencies / Celery / Event Store / Kafka / RabbitMQ** | Mentioned as examples or alternatives (Introduction, Ch. 1 fn 2, App. B, Ch. 13, Ch. 8, Ch. 11, Epilogue). | Not load-bearing for the patterns. |
| **Stdlib features the patterns rely on** | `dataclasses` (including `frozen=True`, `make_dataclass`), `typing.NamedTuple`, `collections.namedtuple`, `typing.NewType`, `typing.Protocol` (suggested), `abc.ABC` / `abc.abstractmethod`, context managers / `contextlib.contextmanager` (Ch. 6 exercise), `functools.partial`, `inspect` (Ch. 13), `logging`, `os.environ`, `hashlib` / `shutil` / `pathlib` (Ch. 3). | All stdlib. |

---

## 6. Coverage limits

1. **Table of contents URL failed.** `https://www.cosmicpython.com/book/` (and `/book/index.html`) returned **HTTP 404** on 2026-11-08. The chapter list was taken from the table of contents embedded in the Preface page and from links on `https://www.cosmicpython.com/`. All 23 listed pages returned HTTP 200.
2. **Fetch method.** Pages were fetched with `curl` and converted to text locally. Prose, headings, callouts, sidebars, tables and footnotes were read in full. **Code listings and ASCII/PlantUML figure sources were skipped while reading prose.** They were consulted only by targeted search for specific identifiers: `frozen=True`, `NamedTuple`, `namedtuple`, `@dataclass` on events and commands, exception and ABC class names, Django mapping method names, and the project trees. Statements about code are therefore limited to those identifiers.
3. **Images.** Figures rendered as images (component diagrams, the onion diagram, the Epilogue's high-resolution diagrams) were seen only through their captions.
4. **Absence findings.** "Not found" results (input/output port, always-valid, DTO, import-linter, architecture tests, one-way/two-way mapping, completeness as a principle) rest on reading the prose plus whole-HTML regular-expression searches across all 23 pages. Disqus comments were not loaded (JavaScript) and were not read.
5. **Typography.** In the quotations, curly apostrophes and quotation marks were normalised to ASCII. Wording is otherwise verbatim.
6. **Edition.** Online edition stamped "Last updated 2023-11-24". The print edition (O'Reilly, differently licensed) was not consulted and may differ.
7. **Quotation count.** 40 numbered quotations (Q1–Q40), each under 25 words. One further short phrase in § 4 (external contracts) is marked as such. A few other two-to-five-word phrases appear in quotation marks within paraphrase as identifiers of the book's terms.
