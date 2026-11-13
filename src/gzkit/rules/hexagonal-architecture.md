---
id: hexagonal-architecture
paths:
  - "**/*.py"
description: Ports & adapters as gzkit's primary code architecture directive
---

<!-- rule-version: 0.6.2 -->

# Hexagonal Architecture (Ports & Adapters) — Primary Code Directive

> **Rule version:** `0.6.2` — § Verify says what the checker refuses and what it does not: an unmapped module's imports are unjudged and growth inside a held package adds no finding (the RP-15 tranche 6 review); binding rules unchanged; version narrative in [Rule Version History](../../docs/governance/rule-version-history.md#hexagonal-architecturemd).

> Ports & adapters is gzkit's **primary code-architecture directive**. Every
> external dependency is confined to an **adapter** behind a **port**; the inner
> world stays **stdlib**. Pydantic is the single ratified exception.
> The specification (parts, packages, dependency table, testing) is
> [`docs/governance/hexagonal-architecture.md`](../../docs/governance/hexagonal-architecture.md);
> gzkit's code does not yet conform to it, and its § Present state lists the tracked gaps.

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
5. *Retired 2026-11-12.* The second-adapter threshold is gone: every driven port
   has a hand-written fake from its first test, so its second adapter is never
   speculative (specification § Testing).
6. **The core is testable without any adapter.** If a domain function cannot be
   exercised without importing networkx/tree-sitter/etc., the dependency has
   leaked inward — the defect this rule exists to catch (Cockburn's *"run
   automated regression-tests against it"*).

## The cascade & domain cohesion (binding)

Hexagonal is the **second stage** of gzkit's architectural spine, not a standalone
rule. The order is load-bearing for gzkit and every adopter project:

1. **DDD** — model the domain in governance's ubiquitous language (the drydock's
   ruled record names), never framework-generic nouns. Subdomains are discovered in
   admitted REQs and bounded contexts designed over them; **the ontology depicts that
   model, it does not define it**.
2. **HA** — protect that domain behind parameter-injected seams (rules 1–6 above);
   stdlib + Pydantic core, every external technology in an adapter.
3. **BDD** — prove operator-visible covenant behavior (`features/`, Gate 4).
4. **TDD** — harden REQ-derived increments (`unittest` + `@covers`, Gate 2).

**Domain cohesion lives in one typed model inside one package design.** gzkit grew ad hoc
as a command catalog; its domain was never modeled as one thing (scattered across
ledger event types, `triangle.py`, `schemas/`, 128 top-level modules (counted 2026-11-08), with domain
types split between `core/models.py` and `models/`). Binding consequences:

7. **`core/` is the hexagon; each adapter is a sibling package of `core/`.** `core/`
   holds `domain/`, `ports/driving/`, `ports/driven/` and `handlers/`; one
   `configurator` module wires them; the hexagonal architecture system package map in
   `pyproject.toml` `[tool.py-gzkit]` names each top-level package's part, and the
   dependency rules are read from it. New code goes where the map places it.
8. **Prefer subsumption to a parallel model.** One typed representation per domain
   object, built on the kernel's bases; never stand up a second, differently-typed
   representation of the same objects (differing-semantics-under-a-shared-name is the
   drift). The ontology is a projection of that model, not a second one.
9. **"Why is this here?" is a required answer.** Every new module, object, and seam
   earns its place by imaging the *actual* shape, never a convenient one (ADR-0.32.0
   persona). Name which cascade stage a new surface serves before adding it.

## Configuration (binding)

10. **Configuration is read once, by the configurator.** At start-up one config
    adapter merges gzkit's defaults with the adopter's overrides (`.gzkit.json` and
    `manifest.json`) and validates them into frozen settings; the configurator passes
    each part as values to what needs it. No handler, domain code or other adapter
    reads a configuration file. Existing loaders (50 modules call `load_config` or
    `GzkitConfig.load` and 35 read `manifest.json`, measured 2026-11-09) move under the
    specification run's row 5 programme; new code takes settings as parameters and
    adds no loader call.

## Why — tracer bullets + seam accountability

Hexagonal **reinforces tracer-bullet development** (KEEL/ADR-0.31.0): a thin
port lets a tracer run end-to-end against a **stub adapter** before the real one
exists. It also **creates accountability for seams**: a port IS a seam made
explicit and owned — an unbounded dependency reaching into the core is a seam
let out of hand. Ports keep the seam-map finite and reviewable.

## Do Not

- Import a third-party library in a core/domain module (put it behind a port).
- Return a library-native type across a port boundary.
- Define a port as an `ABC`; ports are `typing.Protocol`.
- Use inheritance to swap implementations — use composition + `Protocol`.

## Verify

```bash
uv run gz validate --hexagon-dependencies
uv run -m unittest tests.policy.test_import_boundaries
```

Neither `gz lint` nor `gz typecheck` checks an import boundary. The witness is the kernel's dependency checker (`gzkit.kernel.dependency_checker`), which reads the package map and refuses, over the whole package, a new unmapped package or loose module, an import outside a mapped module's region row, a kernel base subclassed outside its region (directly or through another class), a misnamed handler, and a map whose package is not on disk. It does not judge the imports of an unmapped module, and a module added inside an already-unmapped package adds no finding: until gzkit's code is mapped, `core/`'s dependency on the command layer (#1267) is unwitnessed by it. It runs in every per-change `gz check` as `gz validate --hexagon-dependencies` and in `tests/policy/test_import_boundaries.py`, which also keeps the older `core/`-only allowlist. gzkit's code has not migrated, so today's findings sit in the shrink-only `data/hexagon_dependency_baseline.json`: rule 7 is enforced in place and only shrinking, not at zero.

- Core/domain modules import only stdlib + Pydantic (third-party imports live in
  adapter packages).
- Port method signatures name only domain types, never a library-native type.

## Related

- [`docs/governance/hexagonal-architecture.md`](../../docs/governance/hexagonal-architecture.md) — the specification; its rulings are in `docs/rnd/hexagonal-specification.md`
- [`.gzkit/rules/pythonic.md`](pythonic.md) — idiomatic-code contract
- `AGENTS.md` § STDLIB-FIRST DOCTRINE — the interior default this rule enforces
