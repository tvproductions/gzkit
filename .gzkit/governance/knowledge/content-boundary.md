---
type: doctrine
title: .gzkit/ vs docs/ Content Boundary
description: >
  The boundary between gzkit-core knowledge and adopter-authored project content.
  gzkit-core canon lives under .gzkit/; docs/ is reserved for adopter-authored
  project content; OKF bundles are domain-named.
tags:
  - governance
  - content-boundary
  - knowledge-structure
---

# .gzkit/ vs docs/ Content Boundary

**Status:** Doctrine (authored under ADR-0.30.0, OBPI-0.30.0-06)

## The Boundary

gzkit draws a strict content boundary between two directory roots:

| Root | Owner | Content |
|------|-------|---------|
| `.gzkit/` | gzkit-core | gzkit's binding canon of documentation — why gzkit exists, what its bounds are, governance doctrine, generated OKF bundles, skills, rules, personas, invariants, ledger, and all control surfaces |
| `docs/` | adopter | Adopter-authored project content — project-specific runbooks, concepts, design docs, and any other documentation the adopting project creates |

**Three rules that follow from this boundary:**

1. **gzkit-core knowledge homes under `.gzkit/`.** Any documentation that describes how gzkit functions, why it makes the decisions it does, or what its governance constraints are belongs under `.gzkit/` — not `docs/`. This keeps the `.gzkit/` surface self-contained and correctly separated from adopter-authored content.

2. **`docs/` is reserved for adopter-authored project content.** When an implementing project authors `docs/`, they are writing about their own project, not about gzkit itself. gzkit's core canon does not belong in `docs/`; placing it there makes the adopter's `docs/` surface unclear and forces adopters to filter gzkit-internal documentation from their own.

3. **OKF bundles are domain-named, not format-named.** The OKF knowledge bundle that gzkit emits is homed at `.gzkit/governance/knowledge/` (domain name: governance), not `docs/okf/` or any `okf/`-named namespace. OKF-conformance is a property of the markdown files (`type` frontmatter + reserved `index.md`/`log.md` structure), not a folder name.

## Phased Relocation Declaration

**The consequence of this boundary is real:** much of gzkit's existing core canon (doctrine docs, rationale, governance runbooks) currently lives under `docs/governance/` and `docs/user/` — adopter space, not gzkit-core space.

**The docs/→`.gzkit/` relocation is a PHASED, forced subsequent decision** declared here and deliberately NOT performed under ADR-0.30.0. The migration is delicate: relocating existing `docs/` core canon requires updating all cross-references, validating the `gz validate --documents` surface, and ensuring no adopter-facing content is disrupted. A mass move inside a tracer bullet would be the scope-creep failure the tracer-bullet discipline exists to prevent.

**This OBPI (OBPI-0.30.0-06) establishes the boundary as written doctrine. It does NOT relocate, move, or delete any existing `docs/` document.** The wholesale `docs/`→`.gzkit/` migration of gzkit's existing core canon is tracked as a forced subsequent decision, likely its own future ADR phase. Until that migration lands, gzkit's existing `docs/` canon is a known doctrine-vs-state gap — intentional, tracked, not silently tolerated.

## Why This Boundary Matters

The operator's framing (verbatim, 2026-06-28):

- *"`.gzkit/` should be things about gzkit's core function; `docs/` is about the adopting project"*
- *"gzkit's binding canon of documentation — why it exists, what are its bounds — should live in `.gzkit/`"*
- *"much of what we place into `/docs` really belongs in `.gzkit/`. This keeps it clean for implementing projects"*
- *"This is a delicate matter."*

The boundary matters because `docs/` is the surface an implementing project authors. When gzkit places its own core canon in `docs/`, it occupies adopter space and forces every consuming project to navigate around gzkit-internal documentation in what should be their own space.

## Parent ADR

This doctrine is authored under **ADR-0.30.0-okf-documentation-knowledge-structure** (Boundary Invariant 4):

> *The `.gzkit/` vs `docs/` content boundary holds: gzkit-core canon lives under `.gzkit/`; `docs/` is adopter space. [...] The wholesale relocation of gzkit's existing `docs/` core canon into `.gzkit/` is a phased consequence declared by this ADR, NOT performed within it.*
