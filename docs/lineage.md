# Lineage

gzkit descends from three lineages, each contributing essential DNA.

---

## GitHub spec-kit

**Source:** [github/spec-kit](https://github.com/github/spec-kit)

spec-kit provides the **phase model**:

```
constitute → specify → plan → implement → analyze
```

| Phase | spec-kit | gzkit |
|-------|----------|-------|
| Constitute | Define product principles | Define canon/constitutions |
| Specify | Write specifications | Create briefs with acceptance criteria |
| Plan | Track implementation | Manage ADRs and linkage |
| Implement | Build features | Verify gates (TDD, Docs, BDD) |
| Analyze | Review outcomes | Audit and human attestation |

**What gzkit inherits:**
- Phase sequencing as cognitive scaffold
- Specifications as first-class artifacts
- The idea that governance can be executable

**What gzkit extends:**
- Explicit agent/human authority boundaries
- Five Gates model for verification
- Lite/Heavy lane doctrine

---

## GovZero (AirlineOps)

**Source:** Internal framework evolved through AirlineOps development

GovZero emerged from ~100 work items of iterative learning. It codified patterns that prevented drift and preserved intent across extended AI-assisted development.

**Key lessons from GovZero:**

1. **ADR-0.1.9 anti-pattern:** A single minor version accumulated too many work items. SemVer should map to governance assertions, not just code changes.

2. **Gate 3-5 linkage:** Documentation IS the proof. User-facing docs demonstrate operational workflows; running those workflows IS the attestation.

3. **Lanes prevent ceremony bloat:** Not everything needs five gates. Lite lane (1, 2) for internal; Heavy lane (1-5) for external contracts.

4. **Human attestation cannot be automated:** The whole point is human observation. Gate 5 is the covenant's seal.

**What gzkit inherits:**
- Five Gates model
- Lane doctrine (Lite/Heavy)
- Attestation vocabulary (Completed, Completed—Partial, Dropped)
- Charter as sole authority for gate definitions

**What gzkit generalizes:**
- Removes AirlineOps-specific paths and conventions
- Makes gates configurable per project
- Adds CLI tooling for verification

---

## Claude Code Conventions

**Source:** CLAUDE.md patterns from Claude Code projects

Claude Code projects use CLAUDE.md as an agent contract—a document that provides constraints, conventions, and context for AI-assisted development.

**Patterns that work:**

| Pattern | Why it works |
|---------|--------------|
| Explicit constraints | "NEVER use pytest" is a hard boundary; "prefer unittest" drifts |
| Declarative intent | "Ensure determinism" lets agent reason about goals |
| Constraint-forward rules | NEVER/ALWAYS beat SHOULD/CONSIDER |
| Immutable reference docs | Canon prevents drift across sessions |
| Role clarity | Agent vs. human authority is explicit |

**What gzkit inherits:**
- Constraint-forward design philosophy
- The three concerns model (specification, methodology, governance)
- Understanding that agents need cognitive scaffolding

---

## The Synthesis

gzkit combines these lineages:

```
spec-kit phases + GovZero gates + CLAUDE.md constraints
= Development Covenant
```

The result is:
- **Specification** that agents can ground against
- **Methodology** that provides structure without bureaucracy
- **Governance** that reserves judgment for humans

This is not governance in the compliance sense. It is cognitive infrastructure for extended human-AI collaboration—a protocol that preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

---

## References

- [GitHub spec-kit](https://github.com/github/spec-kit)
- [Charter](charter.md) — The gzkit covenant
- [README](../README.md) — Project overview
