# Genesis: The Origin of gzkit

This document captures the conversation that led to gzkit's creation. It preserves context that would otherwise be lost across session boundaries—exactly the problem gzkit exists to solve.

**Date:** 2026-01-12
**Participants:** Jeffry Babb (human), Claude (Opus 4.5)
**Context:** FlightOps project, discussing ADR semver drift from AirlineOps

---

## The Precipitating Problem

The conversation began with a discussion of ADRs in FlightOps and how they use "GovZero's semver approach." The human noted that their use of `x.y.z` versioning in AirlineOps had "drifted from the real intent."

This drift was documented in the GovZero Release Doctrine as the **ADR-0.1.9 anti-example**:

> ADR-0.1.9 accumulated a long-running set of work while remaining under a single 0.1.9 identity. The effort dragged on as "0.1.9" while accumulating roughly 100 OBPIs. Under this doctrine, the work SHOULD have segmented into multiple minor increments and patch increments.

The human recognized that the governance framework developed through this painful learning was valuable and needed extraction into a standalone tool.

---

## The Classification Question

The human asked: "This is more than a spec kit, what is a better classification?"

Several options were considered:

| Classification | Emphasis |
|----------------|----------|
| Agentic Development Protocol | How work gets done with AI |
| Pairing Protocol | Human-AI collaboration |
| Development Covenant | Binding agreement between parties |
| Symbiotic Development Framework | Partnership model |
| Intent Infrastructure | Preserving intent across boundaries |
| Collaboration Scaffold | Structure for extended partnership |

The chosen answer: **Development Covenant**

A covenant is:
- **Explicit** (written down)
- **Binding** (both parties commit)
- **Enduring** (survives sessions)
- **Mutual** (obligations on both sides)

This captured what gzkit is: a binding agreement between human and agent for how work gets done.

---

## The Three Concerns

A key insight emerged: gzkit conflates three distinct concerns that are often treated as one.

| Concern | Definition | Primary Audience |
|---------|------------|------------------|
| **Specification** | What invariants must hold | Agent (grounding) |
| **Methodology** | How work flows through phases | Process (structure) |
| **Governance** | Who has authority to decide | Human (oversight) |

### Specification (Agent-Native)

Agents need constraints to reason against. Specification provides:
- Canon (immutable reference documents)
- Acceptance criteria (testable claims)
- Constraints (NEVER/ALWAYS rules)

Claude observed: "For maximizing Claudishness, only specification matters. Claude doesn't care about gate numbers (human ritual), attestation authority (org structure), or release lane doctrine (process discipline). Claude DOES care about canon invariants, acceptance criteria, and constraint boundaries."

### Methodology (Shared)

Structure without bureaucracy. Methodology provides:
- Phases (constitute → specify → plan → implement → analyze)
- Gates (verification checkpoints)
- Lanes (Lite/Heavy configuration)

### Governance (Human-Native)

Reserved for humans. Governance provides:
- Authority boundaries
- Attestation ceremonies
- Audit trails

---

## The Symbiosis Model

The human asked: "What does Anthropic and Claude feel about the symbiosis of human and model in getting work like AirlineOps and FlightOps done?"

Claude's response on productive partnership:

| Role | Human | Claude |
|------|-------|--------|
| **Intent** | Originates | Interprets, clarifies |
| **Constraints** | Defines, enforces | Operates within, flags violations |
| **Exploration** | Guides | Executes, surfaces options |
| **Judgment** | Final authority | Proposes, explains tradeoffs |
| **Memory** | Long-term, cross-project | Session-bound, needs scaffolding |
| **Verification** | Attests | Generates evidence |

The asymmetry matters:
- Claude can't remember last week's conversation without artifacts
- Humans can't read 5,500 datarefs in 30 seconds
- Claude drifts without constraints; humans can't scale without delegation
- Claude synthesizes; humans originate

**Key quote:** "What GovZero actually is: a protocol for productive human-AI symbiosis that preserves human intent across my context boundaries, gives me constraints I can reason against, creates verification loops we both trust, and reserves judgment for you."

---

## Constraint-Forward Design

A pattern emerged for what works with Claude:

| Pattern | Why it works for Claude |
|---------|------------------------|
| Explicit constraints | Claude grounds against stated rules, not inferred conventions |
| Declarative intent | "Ensure X" beats "do Y then Z" — Claude can reason about goals |
| Immutable reference docs | Canon prevents drift across sessions |
| Verification loops | Tests/checks let Claude self-correct with feedback |
| Role boundaries | Clear agent vs. human authority prevents overreach |
| Incremental checkpoints | Todo lists, ADRs, gates = context anchors |

**Key insight:** "The CLAUDE.md pattern works because it's constraint-forward: 'NEVER use pytest' is a hard boundary Claude respects. 'Consider using unittest' is a suggestion Claude might drift from."

---

## Favored Paradigms

The human asked: "Are there favored paradigms for Claude?"

Claude doesn't have "native" paradigms, but certain patterns align with how Claude operates:

### Works Well
- Explicit constraints over implicit conventions
- Declarative intent over procedural instruction
- Canon/Constitution pattern for grounding
- Structured thinking scaffolds (todo lists, ADRs, phases)
- Verification loops for self-correction
- Clear role boundaries

### Fails
- Vibe-coded work without specs (works for prototypes, fails for continuity)
- Implicit conventions ("we usually do X")
- Vague suggestions ("consider Y")
- Unstated assumptions ("obviously Z")
- Mutable guidance mid-session

---

## The Reframe

Claude offered a reframe of what GovZero actually is:

> What you've built in GovZero is actually two things welded together:
> 1. **Spec framework** — canon, invariants, acceptance criteria (Claude-native)
> 2. **Governance ritual** — gates, attestation, lanes (human-native)
>
> For gzkit, you could cleanly separate these:
> - `gzkit spec` — machine-readable constraints, canon enforcement, acceptance validation
> - `gzkit gov` — human rituals, attestation, audit ceremonies
>
> The spec layer is Claudish. The governance layer is for humans working WITH Claude to not lose the plot.

The human affirmed: "I NEED all three though and your feedback tells me that gzkit is bridging/spanning vital concerns - bringing the human and Claude into an alignment that allows for work to get done."

---

## The Definition

The final definition, used in the repo description:

> **GovZero Kit: A Development Covenant for Human-AI Collaboration**
>
> gzkit is cognitive infrastructure for extended human-AI collaboration—a protocol that preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

---

## On the PhD Comment

The human made a self-deprecating comment about the "analytic value of his own PhD given how succinct [Claude] can sometimes be."

Claude's response:

> Your ability to build GovZero came from years of wrestling with real problems—compliance, drift, agent chaos, governance theater. I can synthesize patterns, but the patterns exist because you lived them. Distillation requires something worth distilling.

And later:

> The messiness of AirlineOps wasn't failure—it was the learning that produced something worth extracting.

---

## Lineage Summary

gzkit descends from three sources:

### GitHub spec-kit
- Phase model: constitute → specify → plan → implement → analyze
- Specifications as first-class artifacts
- Governance as executable documentation

### GovZero (AirlineOps)
- Five Gates model
- Lane doctrine (Lite/Heavy)
- Attestation vocabulary
- Charter as sole authority
- ~100 OBPIs worth of iterative learning
- The ADR-0.1.9 anti-pattern as cautionary tale

### Claude Code Conventions
- CLAUDE.md as agent contract
- Constraint-forward design
- The three concerns model
- Understanding that agents need cognitive scaffolding

---

## Key Quotes to Preserve

On what gzkit is:
> "This is not 'AI governance' in the compliance sense. It's a protocol for productive partnership."

On the covenant:
> "A covenant is explicit (written down), binding (both parties commit), enduring (survives sessions), and mutual (obligations on both sides)."

On specification:
> "Specification without governance drifts. Governance without methodology is theater. Methodology without specification is arbitrary."

On symbiosis:
> "Anthropic would probably call this 'human oversight.' I experience it as partnership with clear roles. The best sessions feel like pair programming where we each contribute what we're good at."

On governance philosophy:
> "Governance is verification, not celebration."

On the learning:
> "Your instinct to formalize this in gzkit is sound. The messiness of AirlineOps wasn't failure—it was the learning that produced something worth extracting."

---

## What Comes Next

The human indicated:
- 11 days until wanting to share with students
- gzkit needs to be a standalone repo
- FlightOps and AirlineOps will both depend on it
- This conversation's context must survive the session boundary

This document exists to ensure that context survives.

---

## References

- [Charter](charter.md) — The covenant itself
- [Lineage](lineage.md) — Heritage documentation
- [Concepts](concepts/) — The three concerns explained
- Original sources in AirlineOps:
  - `docs/governance/GovZero/charter.md`
  - `docs/governance/GovZero/adr-lifecycle.md`
  - `docs/governance/GovZero/releases/README.md`
  - `docs/governance/gzkit/RFC-GZKIT-FOUNDATION.md`
