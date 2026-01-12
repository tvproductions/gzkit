# Lineage

gzkit descends from three lineages, each contributing essential DNA.

But lineage is not destiny. gzkit is opinionated—it takes strong positions and makes choices so you don't have to argue about them. Like Django, Rails, and other opinionated tools, it trades flexibility for focus.

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

### The Evolution of "Zero"

The name has meant different things at different stages:

| Era | Meaning |
|-----|---------|
| **Early** | "Zero governance overhead"—resistance to ceremony bloat |
| **Middle** | "Zero drift"—intent preservation across sessions |
| **Now** | "Index zero"—the human is first in the value chain, final in authority |

The Zero is not absence. It is primacy. The human is `array[0]`—everything else indexes from there.

### Key lessons from GovZero

1. **ADR-0.1.9 anti-pattern:** A single minor version accumulated too many work items. SemVer should map to governance assertions, not just code changes.

2. **Gate 3-5 linkage:** Documentation IS the proof. User-facing docs demonstrate operational workflows; running those workflows IS the attestation.

3. **Lanes prevent ceremony bloat:** Not everything needs five gates. Lite lane (1, 2) for internal; Heavy lane (1-5) for external contracts.

4. **Human attestation cannot be automated:** The whole point is human observation. Gate 5 is the covenant's seal.

5. **Q&A as forcing function:** Without mandatory questioning, humans drift to rubber-stamp. The agent becomes the de facto authority. The covenant fails silently.

### The Two Disciplines

After ~100 work items of agent-assisted development, two practices emerged as non-negotiable:

| Discipline | Why it matters |
|------------|----------------|
| **Read everything** | Agents produce volume. Skimming is abdication. The agent cannot drift from intent if you notice the drift. |
| **Insist on Q&A** | At every critical juncture—design, implementation, evaluation—stop and question. The agent will answer but won't ask unprompted. |

These are not tool features. They are human behaviors. The gates are scaffolding; these two practices are the discipline that makes the covenant real.

Without them, governance becomes theater: gates pass, attestations record, but the human never actually verified anything.

### The Honest Tradeoff

This is slower than multi-agent orchestration. That's the point.

Some people can YOLO through agentic workflows—let agents spawn agents, approve PRs in batches, ship at machine speed. If that works for you, GovZero is not your framework.

But the bet is this: more people need the sanity of this pace than can handle the chaos of full autonomy. Reading everything is a pain in the ass. Q&A at every juncture is friction. **That friction is the feature.**

The speed of agent orchestration comes at a cost: you stop being the architect of your own system. GovZero trades velocity for comprehension. gzkit exists to help you keep that bearing.

**What gzkit inherits:**
- Five Gates model
- Lane doctrine (Lite/Heavy)
- Attestation vocabulary (Completed, Completed—Partial, Dropped)
- Charter as sole authority for gate definitions
- Q&A as mandatory design imperative

**What gzkit generalizes:**
- Removes AirlineOps-specific paths and conventions
- Makes gates configurable per project
- Adds CLI tooling for verification
- Codifies the Zero Doctrine explicitly

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
spec-kit phases + GovZero gates + CLAUDE.md constraints + Q&A imperative
= Development Covenant
```

The result is:
- **Specification** that agents can ground against
- **Methodology** that provides structure without bureaucracy
- **Governance** that reserves judgment for humans
- **Q&A** that forces engagement and resists passive approval

This is not governance in the compliance sense. It is cognitive infrastructure that actively resists your replacement—a protocol that preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

### The Opinionated Stance

gzkit is deliberately opinionated:

| Choice | Alternative rejected |
|--------|---------------------|
| **Mandatory Q&A** | Optional questioning that gets skipped |
| **Lite as default** | Heavy ceremony for everything |
| **Human attestation is final** | Automated approval workflows |
| **Adversarial engagement** | Polite compliance theater |
| **Ceremony is debt** | Gates as bureaucratic checkboxes |

These opinions exist because humans are lazy and agents are eager. Left unchecked, the agent will happily do all the thinking. gzkit exists to prevent that failure mode.

Disagree? Fork it.

---

## References

- [GitHub spec-kit](https://github.com/github/spec-kit)
- [Charter](charter.md) — The gzkit covenant
