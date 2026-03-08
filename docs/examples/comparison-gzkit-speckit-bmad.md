# Framework Comparison: GZKit vs. OpenSpec vs. Spec Kit vs. BMAD

## Four Approaches to AI-Assisted Development Governance

**Date:** 2026-03-08

---

## Overview

All four frameworks solve the same core problem: **how do you stay the
architect when an AI writes the code?** Each takes a different philosophical
approach.

| Framework | Creator | License | Type | GitHub Stars |
|-----------|---------|---------|------|-------------|
| **GZKit** | Jeff (AirlineOps) | MIT | Python CLI + methodology | — |
| **OpenSpec** | Fission AI (YC) | MIT | Node CLI + markdown | 27k+ |
| **Spec Kit** | GitHub | MIT | Python CLI + methodology | — |
| **BMAD** | BMad Code, LLC | MIT | Template set + methodology | 39k+ |

---

## Philosophy Comparison

### GZKit: "The human is index zero"

GZKit implements the **Zero Doctrine** — the human is first in priority and
final in authority. It uses formal quality gates and explicit attestation
ceremonies to ensure the human stays engaged. The friction is intentional:
gates interrupt flow to prevent rubber-stamping.

**Core belief:** Governance prevents the degradation from "I'm building this"
to "I'm approving this."

### OpenSpec: "Structure before code"

OpenSpec implements **Spec-Driven Development with change isolation** —
every proposed change lives in its own directory with a proposal, design,
specs, and task list. The current system state (specs/) is separated from
pending changes (changes/), and deltas merge only at completion. Designed
for brownfield work first.

**Core belief:** If you physically isolate what exists from what you're
changing, AI assistants won't lose context or drift.

### Spec Kit: "Specifications drive implementation"

Spec Kit implements **Spec-Driven Development (SDD)** — write the spec first,
then the AI implements from it. A "constitution" file defines immutable
project principles that all generated code must satisfy. The specification is
the single source of truth.

**Core belief:** If you define what you want precisely enough, the AI can
build it correctly.

### BMAD: "Specialized agents, structured artifacts"

BMAD implements **Agent-as-Code** — instead of one generic AI assistant, you
define multiple specialized personas (Product Manager, Architect, Developer,
QA) as markdown files. Each persona has defined expertise, responsibilities,
and constraints. Artifacts (PRD, architecture sketch, stories) travel with
the code.

**Core belief:** The right persona with the right context produces the right
output.

---

## Workflow Comparison

### GZKit Workflow

```text
gz init → gz prd → gz plan → [tasks/OBPIs] → implement → gz gates → gz closeout → gz attest
```

**Phases:** Initialize → Intent (PRD) → Design (ADR) → Decompose (tasks) →
Build → Verify (Gates) → Present (Closeout) → Sign-off (Attestation)

**Human checkpoints:** ADR defense (mandatory), task acceptance ceremony
(mandatory for Heavy lane), final attestation

### OpenSpec Workflow

```text
opsx:new → opsx:ff (propose) → opsx:apply → opsx:archive
```

**Phases:** Create change directory → Generate proposal + design + specs +
tasks → Implement sequentially → Merge deltas into source-of-truth specs

**Human checkpoints:** Review proposal before apply; review specs before
archive. No formal ceremony — it's fluid and iterative.

### Spec Kit Workflow

```text
specify init → /speckit.specify → /speckit.plan → /speckit.implement
```

**Phases:** Initialize → Specify (functional spec) → Plan (technical plan) →
Implement (task execution)

**Human checkpoints:** Optional clarification phase before planning;
constitutional check on output

### BMAD Workflow

```text
npx bmad-method install → Analysis → Planning → Solutioning → Implementation
```

**Phases:** Install personas → Analyze (PRD) → Plan (user stories) →
Solution (architecture) → Implement (iterative stories)

**Human checkpoints:** PR review loops; acceptance criteria on stories

---

## Feature-by-Feature Comparison

| Feature | GZKit | OpenSpec | Spec Kit | BMAD |
|---------|-------|---------|----------|------|
| **Installation** | `uv tool install gzkit` | `npx openspec init` | `npx specify init` | `npx bmad-method install` |
| **Language** | Python | Node/npm | Python | JavaScript/Node |
| **PRD support** | Yes (`gz prd`) | Proposal.md per change | Yes (spec document) | Yes (one-page PRD) |
| **Architecture decisions** | Formal ADRs with lifecycle | Design.md per change | Implicit in plan | Architecture sketch |
| **Work decomposition** | Tasks / OBPI briefs | Tasks.md checklist | Tasks from plan | User stories |
| **Change isolation** | Branch-per-ADR (convention) | Filesystem-level (changes/) | None explicit | None explicit |
| **Quality gates** | 5 formal gates | None formal — fluid | Constitution check | Acceptance criteria |
| **Human attestation** | Explicit ceremony | Not formalized | Not formalized | PR review loops |
| **Audit trail** | JSONL ledger (append-only) | Git history of specs/ | None | Artifacts in repo |
| **Brownfield support** | Yes (ADRs apply to any codebase) | Primary design goal | Greenfield-oriented | Greenfield-oriented |
| **AI agent model** | Single agent with binding rules | Single agent, slash commands | Single agent from spec | Multiple specialized personas |
| **Scaling system** | Lite (2 gates) vs Heavy (5 gates) | Fluid (no phases) | Single workflow | Scale-adaptive |
| **Tool support** | Claude Code, Codex | 20+ AI assistants | Claude, Copilot, Cursor, Gemini | Tool-agnostic |
| **Dogfooding** | Yes (governs itself, 9 ADRs) | Not documented | Not documented | Not documented |
| **Maturity** | v0.8.0 | v1.x (27k stars) | Recently released | v6.0.4 (39k stars) |

---

## Governance Depth Spectrum

```text
Lighter ◄────────────────────────────────────────────────────► Heavier

  BMAD       OpenSpec      Spec Kit      GZKit (Lite)     GZKit (Heavy)
  │            │              │                │                │
  Stories +    Proposal +     Constitution +   ADR +            ADR +
  PR review    design +       spec check       unit tests       5 gates +
               fluid specs                                      attestation +
                                                                audit ledger
```

---

## What Each Cares About Most

| Framework | Primary Question | What It Produces |
|-----------|-----------------|-----------------|
| **GZKit** | **Why** did we decide this? | ADRs (decision records) + audit trail |
| **OpenSpec** | **What** changed and how does it affect the system? | Spec deltas (before/after) |
| **Spec Kit** | **What** should we build? | Specifications + plans |
| **BMAD** | **Who** should handle each concern? | Persona-driven artifacts |

This is the key differentiator. GZKit forces students to articulate
rationale. OpenSpec forces them to describe system state. Spec Kit forces
them to define requirements. BMAD forces them to think about roles.

---

## Strengths and Weaknesses

### GZKit

**Strengths:**

- Strongest governance: formal gates, attestation, audit trail
- Proven by self-governance (9 ADRs, 305 tests)
- Lane system supports progressive adoption (Lite → Heavy)
- Philosophy is well-articulated and compelling
- Rich documentation and concept library

**Weaknesses:**

- Steepest learning curve of the four
- No beginner examples outside its own domain
- Ceremony can feel heavy for small projects
- Python-only (limits adoption in JS-heavy classrooms)
- Not yet tested on greenfield projects outside AirlineOps

### OpenSpec

**Strengths:**

- Lightest ceremony — fluid, not rigid; iterate freely
- Change isolation in the filesystem prevents context drift
- Brownfield-first — designed for real-world codebases, not just greenfield
- Massive community (27k+ stars, YC-backed)
- Works with 20+ AI tools — no vendor lock-in
- Spec deltas (ADDED/MODIFIED/REMOVED) are readable and reviewable
- GIVEN/WHEN/THEN specs are inherently testable

**Weaknesses:**

- No formal quality gates — discipline is left to the user
- No audit trail beyond git history
- No human attestation or sign-off ceremony
- Architecture decisions are per-change (design.md), not project-level ADRs
- No lane or scaling system — same ceremony for a typo fix and a rewrite
- JavaScript/Node ecosystem (not Python-native)
- Spec maintenance burden grows as changes accumulate

### Spec Kit

**Strengths:**

- Backed by GitHub — strong ecosystem integration
- Clear, linear workflow (Specify → Plan → Implement)
- Constitution concept is intuitive and powerful
- Microsoft Learn training module available
- Multi-agent support (Claude, Copilot, Cursor, Gemini)

**Weaknesses:**

- Strictly linear phases — no iteration without restarting
- No formal ADR or decision-recording mechanism
- No audit trail or attestation ceremony
- Light on verification — constitution check is the main gate
- Large volumes of generated markdown can become noise
- No built-in iteration model (redo spec to change direction)

### BMAD

**Strengths:**

- Most approachable — familiar Agile vocabulary
- Persona system is creative and extensible
- Scale-adaptive — adjusts ceremony to project size
- Tool-agnostic (works with any AI assistant)
- Large community (39.6k GitHub stars)

**Weaknesses:**

- No formal quality gates — governance is cultural, not enforced
- No audit trail or ledger
- Architecture decisions are implicit, not recorded
- Persona proliferation can be confusing (12+ agent types)
- JavaScript/Node tooling limits adoption in Python shops

---

## Which Should Students Use?

| If the goal is... | Use |
|-------------------|-----|
| Learning governance fundamentals with real gates | GZKit (Lite lane) |
| Learning spec-driven change management | OpenSpec |
| Quick spec-to-code with minimal ceremony | Spec Kit |
| Exploring AI persona specialization | BMAD |
| A course project with instructor oversight | GZKit — gates map to grade checkpoints |
| A hackathon or prototype | OpenSpec or Spec Kit — lighter overhead |
| Understanding why decisions matter | GZKit — ADRs force articulation |
| Working with an existing codebase | OpenSpec — brownfield-native change isolation |

### For CIDM 6330/6395 Specifically

**Recommended: GZKit (Lite lane) with student guides.**

Rationale:

1. **ADRs teach architectural thinking** — the core learning objective.
   The other three frameworks either skip the "why did we decide this?"
   question entirely (OpenSpec, Spec Kit) or leave it implicit (BMAD).

2. **Gates map to course milestones** — Sprint 1 = PRD (Gate 1), Sprint 2 =
   implementation + tests (Gate 2), Sprint 3 = docs and demo (Gates 3-5).
   The other frameworks don't have this natural milestone structure.

3. **Attestation teaches professional accountability** — students present
   their work and an instructor (or peer) signs off. This mirrors
   professional code review and architectural review board processes.

4. **Python alignment** — CIDM courses use Python; GZKit is Python-native.

**OpenSpec as a complement:** For students working with existing codebases
(brownfield assignments), OpenSpec's change isolation model is worth teaching
alongside GZKit's ADR model. The two are not mutually exclusive — you could
use GZKit for project-level governance and OpenSpec's proposal/design/tasks
pattern for individual feature work.

The student guides and simplified templates in this directory bridge the
onboarding gap until GZKit adds native student-mode support.

---

## Can They Be Combined?

Yes, selectively:

| Combination | Value |
|-------------|-------|
| GZKit ADRs + OpenSpec change isolation | ADRs for decisions; OpenSpec's changes/ for implementation tracking |
| GZKit gates + Spec Kit constitution | Constitution for invariants; gates for verification checkpoints |
| GZKit gates + BMAD personas | Specialized agent prompts within GZKit's gate-enforced workflow |
| OpenSpec specs + GZKit attestation | Write specs for clarity; use `gz attest` for human sign-off |

In practice, mixing frameworks adds complexity. For classroom use, pick one
and use it consistently. For professional teams, evaluate which governance
gaps exist and borrow specific concepts (not entire frameworks) to fill them.

---

## Sources

- [GZKit documentation](../user/) and [philosophy](../user/why.md)
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) and
  [openspec.pro](https://openspec.pro/)
- [GitHub Spec Kit](https://github.com/github/spec-kit) and
  [speckit.org](https://speckit.org/)
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) and
  [docs.bmad-method.org](https://docs.bmad-method.org/)
- [SDD Tools Comparison (Hightower, 2026)](https://medium.com/@richardhightower/agentic-coding-gsd-vs-spec-kit-vs-openspec-vs-taskmaster-ai-where-sdd-tools-diverge-0414dcb97e46)
