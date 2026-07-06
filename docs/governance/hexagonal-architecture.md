# Hexagonal Architecture (Ports and Adapters) — Influence on gzkit

> **Influence, not wholesale adoption.** gzkit borrows Cockburn's vocabulary
> (port, adapter) and the topological intuition (invariant boundaries are
> ports; concrete implementations are adapters), then maps it onto gzkit's
> own ADR-kind taxonomy. This document is the canonical reference for that
> mapping.

## Source

Alistair Cockburn, **Hexagonal Architecture** (2005), originally subtitled
*"or, Ports and Adapters"*. Source: <https://alistair.cockburn.us/hexagonal-architecture/>.

Book-length treatment (figures + the "copy this code" formulation), enshrined as
gzkit's hexagonal canon: <https://alistaircockburn.com/figs%20hexarch%20book.pdf>.
Its § 1.1 states the load-bearing requirement verbatim: *"Never explicitly name
any external object or technology. Always take a parameter for any external
object or technology you wish to access."*

The pattern names two roles:

- **Port** — an abstract contract every implementation must honor. Defined by
  the application's invariants, not by any specific implementation.
- **Adapter** — a concrete implementation behind a port. Adapts the port's
  abstract contract to one specific outside world (database, framework, CLI,
  test fixture, etc.).

Cockburn's original framing: ports point inward to invariance; adapters point
outward to concrete dependencies. The hexagon is the application core
surrounded by adapters on every side.

## Hexagonal as gzkit's primary code-architecture directive

Beyond the ADR-taxonomy mapping below, hexagonal is gzkit's **primary code
architecture directive** (operator ruling, 2026-07-06 — mid-course reflection on
ADR-0.32.0). The binding per-turn form lives in
[`.gzkit/rules/hexagonal-architecture.md`](../../.gzkit/rules/hexagonal-architecture.md);
this section enshrines the full Cockburn reference (§1–§2.3) and maps every
element to gzkit's actual structure.

### The demand, and the strong form

> "Never explicitly name any external object or technology. Always take a
> parameter for any external object or technology you wish to access." (§1.1)

The full ("strong") implementation: **"The app cannot know anything about the
external technology."** The core is not merely decoupled — it is *ignorant* of
what sits behind the port, so it can be regression-tested with no production
connection, swap technologies, and survive a dependency going away.

### The five elements (four in the pattern + the configurator)

| # | Cockburn element | What it is | gzkit realization |
|---|---|---|---|
| 1 | **App / System / Hexagon / Core** | All business logic, technology-agnostic — no reference to DB / network / UI | Domain layer: `src/gzkit/ontology/` (graph, model, purity), `src/gzkit/core/`, pure `governance/*` logic. Stdlib + Pydantic only. |
| 2 | **Ports** | The app's true boundary; each is a set of interactions with one *intention*, named "For &lt;verb&gt;-ing" | Driving (provided/API): the `gz` verb contracts. Driven (required/SPI): the `Ledger`, filesystem, git, config contracts. In Python ports aren't declared — a port is "all the calls the app makes" at that seam. |
| 3 | **Actors (driving / driven)** | Driving (primary) kicks the app into action; driven (secondary) is called by the app | Driving: the operator, `gz` invocations, test cases. Driven: `.gzkit/ledger.jsonl`, filesystem, git, GitHub. |
| 4 | **Adapters** | Code that fits an actor's interface to a port; lives *outside* the app | Driving: the argparse CLI (`commands/*`, `cli/*`). Driven: `Ledger(path)`, `FileConfigStore`, git/subprocess runners. **Test doubles are adapters too** (`tests/fakes/`). |
| 5 | **Configurator** (5th, officially outside) | Instantiates driven adapters, instantiates the app injecting them, then instantiates driving adapters passing the app (Fig 2.1) | gzkit's **command layer**: `get_project_root()` resolves once at the edge (`commands/common.py`) and threads `project_root: Path` / `Ledger` inward as parameters. Plain constructor/parameter injection — **no DI framework** ("like Spring" is deliberately not adopted; stdlib-first). |

### Ports: provided vs required (API vs SPI), and the who-knows-whom asymmetry

- **Provided interface** (driving / primary / inbound / API) — the services the app offers.
- **Required interface** (driven / secondary / outbound / SPI) — "all the calls the app will make" at that port. *The surprising, powerful half:* the app says "I will only talk to you in my language," defines that language, and the technology behind it becomes swappable at configuration time.
- **Asymmetry:** the app does not know *who* calls its provided interface, but it *does* hold the handle for its driven actors — which is exactly why driven dependencies must be **injected** (the parameterize-everything rule).

### How the configurator wires it (Fig 2.1) — and the testing payoff

Order: (1) instantiate driven adapters → (2) instantiate the app, injecting the driven actors via its constructor → (3) instantiate driving adapters, passing them the app. Legend: I=implements, U=uses, K=knows-of, iN=instantiates.

- **In testing, the test case is BOTH the configurator and the driving actor** — it builds and connects the players, then drives the app. This is precisely gzkit's working test pattern: a test builds a temp-dir `Ledger`, injects it into `project_corpus(ledger)`, and drives it — no production connection (e.g. `tests/test_ontology_corpus.py`).
- **In production, `main` / the composition root is the configurator** — in gzkit, the `gz` command layer.

### Costs & benefits (§1.4)

Benefits: **(1) testing** — system-level tests with no production connection, purer/faster; **(2)** swap production ↔ test connections for any port without recompile; **(3) leakage protection** — a test wall catches business logic leaking into technology or vice versa; **(4)** large-system independent development; **(5)** long-running technology swap over years; **(6)** DDD focus once technology is outside the boundary. Cost: complexity, higher in type-declared languages (an instance variable per driven actor, or fetch-on-demand).

### Conformance checklist (§2.4) — the mechanical "are we actually hexagonal?" test

**Required by the pattern (all six MUST hold):**

1. The app defines a provided or required interface for **every** external interaction.
2. The app defines **driving ports** for provided interfaces, **driven ports** for required interfaces (implicit in Python — a port is "all the calls the app makes" there).
3. The app allows **driven actors to be configured at run time** (injection).
4. The app has **no source-code dependency on its primary or secondary actors**.
5. External actors interact **only through the defined ports** — never reach inside the hexagon directly.
6. Ports and interfaces are **technology-neutral and expressed in business terms**.

**Weak vs strong conformance (the quality gradient):** *Weak* (legal but leaky) — the driven port expresses e.g. SQL concepts without naming a specific database, still tying the system to SQL. *Strong* (the target) — **"the app cannot know anything about the external technology"**; the driven port is expressed purely in application-language concepts and can't even know a database exists.

**Not part of the pattern at all:** how the app is structured *internally* (DDD or not, function-vs-model or not). This is where hexagonal differs from Clean/Onion, which *do* legislate internal layering — hexagonal governs only the boundary.

**gzkit conformance (resolved 2026-07-06 — the injection seam IS the canonical hexagon):** gzkit satisfies the pattern **through parameter injection, and that is its blessed hexagon** (operator ruling, 2026-07-06). Rules 3/4 hold via `project_root: Path` (738 param sites) and path-injectable `Ledger(path)` / `load_config(path=)` threaded from the command layer — the **configurator** (Cockburn Fig 2.1: the composition root instantiates the driven adapter, injects it into the app, then hands the app to the driving adapter). Tests act as configurator + driving actor over temp worlds; `tests/policy/test_import_boundaries.py` is a real AST "test wall" enforcing **core purity** (rule 5); the `ontology/` package is the strong-conformance exemplar (pure core, single injectable seam).

**Retired facade (the resolution):** the former `src/gzkit/ports/` + `src/gzkit/adapters/` + `tests/fakes/` layer (FileStore/ProcessRunner/LedgerStore/ConfigStore Protocols, the in-memory fakes, and `FileConfigStore`) was built and conformance-tested but wired into **zero** production code and injected into **zero** domain tests — by Cockburn's own test, *"a nice drawing but not much more."* It was retired as a correction under ADR-0.0.3 (supersession callouts on OBPI-0.0.3-01/-04/-05/-09). A port ABC over a single/zero impl beside a working self-contained seam is exactly the speculative generality the [primary directive](../../.gzkit/rules/hexagonal-architecture.md) forbids (*"encapsulate first; formalize the port only when the second adapter is real"*).

**Adapters-outside-the-core is future ADR work — not adopted here.** Cockburn's folder-first discipline points toward real driven adapters living *outside* the core (candidate naming `*_adapter`/`*_helper`), the app being the core of logic/intention — the intended direction (operator, 2026-07-06). But gzkit **and adopter projects are not yet ready** to realize this: the full folder-structure realization (`domain`/`application`/`adapters`/`api` zoning enforced by import direction) is **dedicated ADR work, not undertaken in this correction.** What this retirement did is narrower — it removed the *wrong-shaped, dormant* facade (`src/gzkit/adapters/` happened to sit *inside* the app package); it neither relocates nor builds any adapter, and it enshrines no folder mandate.

### Relationship to DDD, bounded contexts, and ACLs (§5.6–§5.7)

- **DDD and Ports & Adapters are independent but compatible.** You can do either without the other; they work well together. P&A is a *precursor* that simplifies DDD — it puts all external technology outside the app, so the inside contains only domain concepts and you do domain-driven design without distraction.
- **A bounded context is not automatically a hexagon.** Hexagons *per se* don't exist — ports (provided/required interfaces) are what exist. A bounded context becomes a P&A component only when it has **ports AND tests at the boundary**; without tests, "you have a nice drawing but not much more."
- **Tests make the boundary real** (the load-bearing theme, Fig 5.10–5.11): *"You can draw a line around any part of your code and call it anything you like, but only when you have to maintain the tests do boundaries become real."* → gzkit's `tests/policy/test_import_boundaries.py` is exactly this AST test wall — it makes the **core-purity** boundary real (core imports no `cli`/`adapters`/`rich`/`argparse`), which is the boundary the retired facade only *drew*.
- **ACLs (anti-corruption layers) are broader than adapters.** An ACL translates between two modeling languages and can sit *partially inside and partially outside* the hexagon. Whether an ACL *is* an adapter is "maybe" — yes if the boundary has ports + tests (then it is a driven adapter), no if it is just internal translation.
- **P&A is a special case of Component + Strategy** — the protected boundary is where external technology connects to the app, or where a team's decision authority ends.

## Mapping to gzkit ADR taxonomy

gzkit's ADR-kind taxonomy maps directly onto Cockburn's pattern:

| Cockburn term | gzkit ADR kind | Semver | Examples |
|---|---|---|---|
| **Port** | `foundation` | `0.0.x` | ADR-0.0.50 (validation pipeline port + redteam-terminal doctrine), ADR-0.0.51 (milestone-maintenance port + `/goal`-first-class doctrine) |
| **Adapter** | `feature` | `0.y.z` | ADR-0.13.0 (OBPI pipeline runtime surface — adapter implementing ADR-0.0.14's deterministic-OBPI-command port), ADR-0.18.0 (subagent-driven pipeline execution — one execution-strategy adapter), ADR-0.12.0 (OBPI pipeline enforcement parity — one enforcement implementation) |
| **Pool** (gzkit-specific) | `pool` | none | Backlog: not yet classified as port or adapter |

Foundation ADRs (ports) define what every implementation MUST honor; feature
ADRs (adapters) plug into existing foundation ports with one specific
implementation.

## Why this mapping holds

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

## Worked examples

### Ports (foundation)

- **ADR-0.0.50 — validation pipeline + redteam-terminal doctrine.** The port
  specifies the multi-skill orchestrator contract (stage sequence, persona
  dispatch, receipt shape, redteam terminal, fail-closed gating) every
  validation-phase implementation must honor. `gz-adr-validation-pipeline` is
  the canonical adapter.
- **ADR-0.0.51 — milestone-maintenance pipeline + `/goal`-first-class doctrine.**
  The port specifies when the maintenance milestone fires, what must be
  checked, and how convergence is bounded.

### Adapters (feature)

- **ADR-0.13.0 — `gz obpi pipeline` runtime surface.** One specific runtime
  implementation of ADR-0.0.14's deterministic-OBPI-command port: it elevates
  the `gz-obpi-pipeline` workflow into a first-class command contract (launch,
  stage progression, resume, abort, sync). The port is the command contract;
  this adapter is the specific runtime surface behind it.
- **ADR-0.18.0 — subagent-driven pipeline execution.** One execution strategy
  for the pipeline runtime — subagent dispatch — behind the same OBPI-pipeline
  contract. Its `--no-subagents` fallback preserves inline execution, which is
  the adapter tell: it is *one way* of executing, not the invariant.
- **ADR-0.12.0 — OBPI pipeline enforcement parity.** One specific
  AirlineOps-style enforcement implementation behind the pipeline contract.
  Still an adapter; the enforcement invariants are what it conforms to.

### Pool ADRs are pre-classification

A pool ADR has not yet been classified as port or adapter. Promotion via
`gz adr promote --kind {foundation,feature}` is when the classification is
recorded. Pool ADRs may eventually promote to either kind based on the
invariance test outcome.

## Where this is cited

Operational guidance and the invariance test itself live in
[`docs/user/concepts/foundation-feature-invariance-test.md`](../user/concepts/foundation-feature-invariance-test.md).
That document is the canonical home for the *how do I choose* answer; this
document is the canonical home for the *what's the conceptual origin* answer.

The `gz-design` skill body cites both: the framing question presented to the
operator during ADR design is *"Is this ADR a port (an abstract contract every
implementation must honor) or an adapter (one implementation behind an
existing port)?"*

## Departures from Cockburn

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

## Why this codification exists

Before this document, gzkit's ADR scaffold and `gz-design` skill body used
the term *"plug"* in place of Cockburn's canonical *"adapter."* The
terminology drifted from the source and operators picked up the wrong term
through the template scaffold. GHI #489 (filed 2026-05-18) tracks the
mechanical fix; this canon document is the durable answer to *"where did
gzkit's port/adapter framing come from"* — and prevents the next drift by
naming the source explicitly.
