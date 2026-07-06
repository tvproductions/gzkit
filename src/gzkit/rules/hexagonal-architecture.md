---
id: hexagonal-architecture
paths:
  - "**/*.py"
description: Ports & adapters as gzkit's primary code architecture directive
---

<!-- rule-version: 0.1.0 -->

# Hexagonal Architecture (Ports & Adapters) — Primary Code Directive

> **Rule version:** `0.1.0` — initial authoring; enshrines Cockburn Ports &
> Adapters as gzkit's primary code-architecture directive (deps behind adapters,
> stdlib + Pydantic core, parameterize every external dependency).

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
