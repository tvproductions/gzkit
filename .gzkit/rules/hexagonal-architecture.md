---
id: hexagonal-architecture
paths:
  - "**/*.py"
description: Ports & adapters as gzkit's primary code architecture directive
---

<!-- rule-version: 0.2.0 -->

# Hexagonal Architecture (Ports & Adapters) — Primary Code Directive

> **Rule version:** `0.2.0` — seats HA inside the DDD → HA → BDD → TDD spine and
> adds the binding cohesion doctrine (domain modeled as the ontology, not a folder
> tree; `core/` stays; subsumption over parallel models; "why is this here?" is a
> required answer). `0.1.0` enshrined Cockburn Ports & Adapters as the primary
> code-architecture directive (deps behind adapters, stdlib + Pydantic core,
> parameterize every external dependency).

> Ports & adapters is gzkit's **primary code-architecture directive**. Every
> external dependency is confined to an **adapter** behind a **port**; the inner
> world stays **stdlib**. Pydantic is the single ratified exception.
> Canon: [`docs/governance/hexagonal-architecture.md`](../../docs/governance/hexagonal-architecture.md).

## The Cockburn demand (verbatim)

Ports & Adapters (2005) requires code that runs *"without either a UI or a
database"* so you can regression-test it, swap connected technologies, and
survive a dependency going away. Its most surprising requirement — the
mechanism this whole rule enforces:

> "Never explicitly name any external object or technology. Always take a
> parameter for any external object or technology you wish to access."
> — Alistair Cockburn, *Hexagonal Architecture* § 1.1

## The strong form

A full ("strong") Ports & Adapters implementation requires: **"The app cannot
know anything about the external technology."** (Cockburn). The core is not
merely decoupled — it is *ignorant* of what sits behind the port. That is the
bar rules 3, 4, and 6 enforce: if a core module can name the technology, it is
not strong-form.

## Operative rules (binding)

1. **Dependencies live in adapters, never in the core.** Any third-party import
   (networkx, tree-sitter, future deps) is confined to an adapter module behind
   a port. Core domain logic imports **stdlib + Pydantic ONLY**.
2. **Pydantic is the one ratified exception** admitted to the inner world
   (validation semantics stdlib cannot supply). Every other third-party surface
   stays outside a port boundary. STDLIB-FIRST governs the interior.
3. **Ports are domain-typed contracts.** A port's methods accept/return domain
   types (Pydantic models, stdlib types) — NEVER a library's native type. No
   `nx.Graph`, `ast.AST`, or tree-sitter node crosses a port. Exemplar:
   `OntologyGraph.reachable_from` returns `set[str]`, not an `nx` view.
4. **Never name the technology in the core; take it as a parameter** (Cockburn).
   Port shape via `typing.Protocol`, not `ABC`; inject adapters by composition,
   not inheritance.
5. **Encapsulate first; formalize the port when the SECOND adapter is real.**
   Confining a dep to one adapter IS the swappability. Design the method shape
   now; extract the `Protocol` + injection when a second implementation lands.
   One adapter → no formal port yet (a port ABC over a single impl is
   speculative generality).
6. **The core is testable without any adapter.** If a domain function cannot be
   exercised without importing networkx/tree-sitter/etc., the dependency has
   leaked inward — the defect this rule exists to catch (Cockburn's *"run
   automated regression-tests against it"*).

## The cascade & domain cohesion (binding)

Hexagonal is the **second stage** of gzkit's architectural spine, not a standalone
rule. The order is load-bearing for gzkit and every adopter project:

1. **DDD** — model the domain in governance's ubiquitous language (ADR, OBPI, REQ,
   GHI, gate, receipt, ledger), never framework-generic nouns. gzkit's domain is
   **modeled as the ontology** (typed Objects/Links, ADR-0.32.0) — *not* a folder tree.
2. **HA** — protect that domain behind parameter-injected seams (rules 1–6 above);
   stdlib + Pydantic core, every external technology in an adapter.
3. **BDD** — prove operator-visible covenant behavior (`features/`, Gate 4).
4. **TDD** — harden REQ-derived increments (`unittest` + `@covers`, Gate 2).

**Domain cohesion lives in the type system, not the folder tree.** gzkit grew ad hoc
as a command catalog; its domain was never modeled as one thing (scattered across
ledger event types, `triangle.py`, `schemas/`, ~50 top-level modules, with domain
types split between `core/models.py` and `models/`). The correction is **subsumption
into one typed model, never a folder restructure** — binding consequences:

7. **`core/` stays; do NOT add `domain/`/`application/`/`adapters/`/`contexts/`
   folder partitions to "do DDD."** Hexagonal governs the boundary, not internal
   layout (*"how the app is structured internally is not part of the pattern"* —
   Cockburn §2.4). Bounded contexts are **subgraphs of the ontology** (corpus /
   work / source), not directories.
8. **Prefer subsumption to a parallel model.** A new domain type joins the ontology's
   `OntologyNode`/`OntologyEdge` type system; never stand up a second, differently-typed
   representation of the same objects (differing-semantics-under-a-shared-name is the
   drift the ontology exists to kill).
9. **"Why is this here?" is a required answer.** Every new module, object, and seam
   earns its place by imaging the *actual* shape, never a convenient one (ADR-0.32.0
   persona). Name which cascade stage a new surface serves before adding it.

## Why — tracer bullets + seam accountability

Hexagonal **reinforces tracer-bullet development** (KEEL/ADR-0.31.0): a thin
port lets a tracer run end-to-end against a **stub adapter** before the real one
exists. It also **creates accountability for seams**: a port IS a seam made
explicit and owned — an unbounded dependency reaching into the core is a seam
let out of hand. Ports keep the seam-map finite and reviewable.

## Do Not

- Import a third-party library in a core/domain module (put it behind a port).
- Return a library-native type across a port boundary.
- Build a port `ABC` + injection wiring with only one adapter (speculative).
- Use inheritance to swap implementations — use composition + `Protocol`.

## Verify

```bash
uv run gz lint
uv run gz typecheck
```

- Core/domain modules import only stdlib + Pydantic (third-party imports live in
  adapter packages).
- Port method signatures name only domain types, never a library-native type.

## Related

- [`docs/governance/hexagonal-architecture.md`](../../docs/governance/hexagonal-architecture.md) — canon; conceptual origin + the Cockburn source
- [`.gzkit/rules/pythonic.md`](pythonic.md) — idiomatic-code contract (Protocol/DI)
- `AGENTS.md` § STDLIB-FIRST DOCTRINE — the interior default this rule enforces
