# Architectural Enforcement Protocol

**Purpose:** Mechanisms to ensure agents follow architecture, not just read it.
**Status:** Proposed
**Last reviewed:** 2026-11-14 (rewritten to the carried practice; operator, verbatim: *"Rewrite to practice"*)

---

## Problem Statement

Documentation makes the right answer *findable*. It doesn't make it *unavoidable*.

The failure that prompted this protocol: a brief said "delegate to the existing module", the agent wrote a
standalone implementation anyway, and the tests passed while the architecture was violated.

---

## Where the practice comes from

This protocol began in AirlineOps, where it named that project's six data-warehouse contexts, its data
contracts and its dataset formats. Those are AirlineOps's domain, not gzkit's. The R&D run
[`hexagonal-specification`](https://github.com/tvproductions/gzkit/blob/main/docs/rnd/hexagonal-specification.md) ruled what carries forward (decision
*the AirlineOps context practice is carried; its six names are not*; operator, verbatim: *"A: carry
practice"*, *"a + b is really best"*): the practice, not the names.

gzkit's contexts are not listed here, because none is designed yet. They are derived, not prescribed: REQs
are admitted first, subdomains are discovered in them, and bounded contexts are designed over the subdomains
(decision *the order things derive in*; operator, verbatim: *"A: rule the order"*;
[`hexagonal-architecture.md` § Domain-driven design](../hexagonal-architecture.md#domain-driven-design)).
Earlier context lists, the AirlineOps six among them, are evidence for that design, not canon.

---

## The practice

Inside each context, once designed:

1. **Name the context before coding.**
2. **State what it owns and what it does not own.**
3. **Stop when no context fits**, and emit BLOCKERS rather than invent one.
4. **Let the dependency checker audit imports that cross contexts.**

Until contexts are designed, an author names the hexagon region the work sits in (domain, ports, handlers,
an adapter, the configurator; [`hexagonal-architecture.md` § The packages](../hexagonal-architecture.md#the-packages))
and writes "none designed yet" for the context.

---

## Three Enforcement Layers

| Layer | gzkit mechanism today | What it catches | Automated? |
|---|---|---|---|
| 1. Code-level validation | `uv run gz validate --hexagon-dependencies`, reading the package map in `pyproject.toml`; `uv run gz validate --hexagon-tests` | An import outside a region's row of the dependency table; a hexagon test that mocks, lacks its labels or names no REQ | Yes, on every per-change `gz check` |
| 2. Agent checkpoint | The OBPI template's § Architectural Checkpoint (`.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md`) | Work started without naming its context, or reaching into one it does not own | No (human review) |
| 3. Compliance in the gate | The two scopes above, in the default tier of `uv run gz check`, today's findings held in shrink-only baselines | A new violation of the dependency table or the test discipline | Yes |

**Not built:** the cross-context arm of layer 1. The dependency checker audits regions today; it audits
contexts once they are designed and the package map names them (point 4 of the practice).

---

## Integration with OBPI Workflow

### Before Implementation

1. Agent completes the **Architectural Checkpoint** in the brief.
2. Human reviews the checkpoint before approving implementation.

### During and After Implementation

1. `uv run gz check` runs the hexagon scopes on every change; violations fail at full strength.
2. Human attestation includes architectural compliance.

---

## See Also

- [`hexagonal-architecture.md`](../hexagonal-architecture.md) — gzkit's hexagonal specification, its packages and
  its dependency table
- [`hexagonal-specification.md`](https://github.com/tvproductions/gzkit/blob/main/docs/rnd/hexagonal-specification.md) — the R&D run and its rulings on the practice
- `.gzkit/rules/hexagonal-architecture.md` — the binding rule and its § Verify
- [OBPI Template](https://github.com/tvproductions/gzkit/blob/main/.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md) — the checkpoint
