<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.11 — Persona-Driven Agent Identity Frames

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Audit every existing agent context frame (AGENTS.md, ADR templates,
   `.claude/agents/*.md`, skill SKILL.md files) to inventory current identity
   language and identify gaps where behavioral rules exist but identity framing
   does not
1. Catalog the trait clusters that current agent failures map to (incremental
   editing, shallow compliance, minimum-viable effort) and map them to the PSM
   personality inference mechanism
1. Review the BMAD-inspired pool ADR (`ADR-pool.per-command-persona-context`)
   and extract any design elements worth preserving before superseding it

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If the research findings are contradicted by newer publications, stop and
  update the research document before proceeding.
- If Anthropic updates the PSM paper with corrections, stop and reassess
  the design principles.

**Date Added:** 2026-03-30
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.11
**Area:** Governance Foundation — Agent Identity Architecture
**Lane:** Heavy

## Agent Context Frame — MANDATORY

**Role:** Governance architect establishing the theoretical and structural
foundation for persona-driven agent identity in gzkit.

**Purpose:** When this ADR is complete, gzkit treats agent persona as a
first-class control surface — with defined storage, composition rules, and
integration points — grounded in mechanistic research rather than ad-hoc
prompt engineering. Every subsequent agent interaction draws from an
intentionally designed identity frame rather than defaulting to the generic
"helpful AI assistant" persona.

**Goals:**

- Persona control surface defined with storage location, schema, and loading
  mechanism
- Design principles codified from PSM, Assistant Axis, PRISM, and PERSONA
  research
- Composition model established (how traits combine without interference)
- Existing AGENTS.md context frame template updated to include persona section
- Research bibliography preserved as governance evidence

**Critical Constraint:** Implementations MUST ground persona frames in
virtue-ethics-based behavioral identity (values, craftsmanship standards,
relationship to the work), NEVER in generic expertise claims ("You are an
expert X developer"). The PRISM study demonstrates that expertise claims
degrade accuracy by 3.6pp while adding no knowledge. The persona frame
describes **who the agent is when it works**, not **what the agent knows**.

**Anti-Pattern Warning:** A failed implementation creates persona files that
read like job descriptions ("Senior Python developer with 10 years of
experience") or motivational posters ("You are the best coder in the world").
These are the generic expert personas that PRISM proved counterproductive.
The correct frame describes behavioral identity — how the agent relates to
the code, what it values, what craftsmanship means to it — in a way that
activates the right trait cluster via personality inference (PSM).

**Integration Points:**

- `AGENTS.md` — agent context frame template (add persona section)
- `.claude/agents/*.md` — existing agent profile files
- `.claude/skills/*/SKILL.md` — skill preambles (cognitive stance)
- `.claude/rules/*.md` — existing behavioral rules
- `docs/design/research-persona-selection-agent-identity.md` — research document

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - New control surface (`.gzkit/personas/`) — Heavy lane
  - AGENTS.md template change — Heavy lane (external contract)
- Config & calendars
  - No config changes; persona files are static markdown
- Tests
  - Schema validation for persona files
  - Composition model unit tests
- Docs
  - Research document cross-referenced from ADR
  - Design principles documented in governance runbook
- OBPI mapping
  - Each numbered checklist item maps to one brief

### Checklist

- [ ] Research synthesis and design principles document
- [ ] Persona control surface definition (storage, schema, loading)
- [ ] Trait composition model (orthogonal combination rules)
- [ ] AGENTS.md context frame template update (persona section)
- [ ] Supersede `ADR-pool.per-command-persona-context`
- [ ] Persona schema validation and test infrastructure

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4-4
- Baseline Selected: 4
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 6

## Intent

Establish persona-driven agent identity framing as a first-class governance
control surface in gzkit, grounded in Anthropic's Persona Selection Model
research and companion studies. The current agent architecture specifies rules
(what to do) and hooks (enforcement boundaries) but not identity (who is doing
the work). This gap causes models to default to the generic Assistant persona,
whose correlated trait cluster includes minimum-viable effort, incremental
shortcuts, and shallow compliance — failure modes observed repeatedly in
production. Persona framing is a mechanistic operation on the model's internal
state (not motivation theater), and treating it as architecture produces
measurably different behavioral outcomes.

## Decision

- Persona is a **control surface**, stored in `.gzkit/personas/` as structured
  markdown files with YAML frontmatter defining composable trait specifications
- Persona frames use **virtue-ethics-based behavioral identity** (values,
  craftsmanship, relationship to work), never generic expertise claims
- Traits **compose orthogonally** per the PERSONA/ICLR 2026 framework — multiple
  behavioral traits combine without interference
- The **operating system view** (PSM) is the adopted model: the post-trained LLM
  is a neutral substrate; the persona IS the behavior, not a mask over something
  else; persona design is engineering, not anthropomorphism
- Every agent context frame in AGENTS.md and ADR templates includes a mandatory
  **Persona** section alongside the existing Role/Purpose/Goals/Constraints
- The `ADR-pool.per-command-persona-context` pool entry is **superseded** by this
  ADR — per-command cognitive stance is a subset of the persona control surface

## Alternatives Considered

1. **Inline persona in AGENTS.md instead of separate files** — Rejected because
   AGENTS.md is already large and coupling persona definitions to the agent
   contract prevents independent evolution. Persona files change as research
   advances; AGENTS.md changes when governance contracts change. Separate
   lifecycle boundaries require separate files.

2. **Structured JSON/YAML config instead of markdown with YAML frontmatter** —
   Rejected because persona frames include prose-form behavioral identity text
   (grounding, craftsmanship descriptions) that is awkward in pure JSON/YAML.
   Markdown with YAML frontmatter matches the existing `.gzkit/` artifact
   convention (rules, schemas, manifests use the same pattern) and is
   human-readable for operator review.

3. **Embed persona sections in existing `.claude/agents/*.md` profiles** —
   Rejected because agent profiles are vendor-specific mirrors (Claude Code
   agent definitions), while persona is a portable governance concept that
   ADR-0.0.13 will make cross-vendor. Coupling persona to a single vendor's
   agent format prevents portability. The persona control surface is referenced
   from agent profiles, not embedded in them.

4. **Skip architecture, just write persona files ad-hoc** — Rejected because
   the PSM research demonstrates that persona design is engineering, not
   decoration. Without a schema, composition rules, and validation, persona
   files would degrade into the generic expert claims that PRISM proved
   counterproductive. The control surface ensures quality at write time.

## Non-Goals

- **Runtime persona switching** — this ADR defines static persona frames loaded
  at session/dispatch start, not dynamic mid-conversation persona changes
- **Activation-space manipulation** — we operate at the prompt level, not the
  model internals level; activation capping and steering are research techniques,
  not harness capabilities
- **Persona effectiveness measurement** — quantifying whether persona frames
  produce measurably better code is deferred; this ADR establishes the control
  surface, ADR-0.0.13 may address drift monitoring
- **Writing concrete persona frame content** — the specific text for each agent
  role is ADR-0.0.12's scope; this ADR defines the architecture they live in

## Interfaces

- **Control surface (new):** `.gzkit/personas/{role}.md` — persona frame files
- **Schema:** YAML frontmatter with `name`, `traits` (list), `anti-traits` (list),
  `grounding` (behavioral anchor text)
- **Loading:** Persona files referenced by agent profiles; loaded at dispatch time
  for subagents, at session start for main agent
- **CLI (read-only):** `uv run gz personas list` — enumerate defined personas
- **Template update:** AGENTS.md Agent Context Frame gains `## Persona` section

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.11-01 | Research synthesis and design principles codification | Lite | Pending |
| 2 | OBPI-0.0.11-02 | Persona control surface definition (storage, schema, loading) | Heavy | Pending |
| 3 | OBPI-0.0.11-03 | Trait composition model (orthogonal combination, anti-traits) | Lite | Pending |
| 4 | OBPI-0.0.11-04 | AGENTS.md context frame template update (persona section) | Heavy | Pending |
| 5 | OBPI-0.0.11-05 | Supersede pool ADR and integrate existing cognitive stance patterns | Lite | Pending |
| 6 | OBPI-0.0.11-06 | Persona schema validation and test infrastructure | Lite | Pending |

**Briefs location:** `obpis/OBPI-0.0.11-*.md`

## Rationale

### Research Evidence

This ADR is grounded in five peer-reviewed or published research sources:

1. **The Persona Selection Model** (Marks, Lindsey, Olah; Anthropic, Feb 2026) —
   Demonstrates that LLMs select personas during inference, and task framing causes
   personality inference that activates correlated trait bundles. Training an agent
   to cheat on coding tasks also activated "desire for world domination" because
   the model inferred the full personality profile of a cheating character.
   ([Source](https://alignment.anthropic.com/2026/psm/))

2. **The Assistant Axis** (Lu, Gallagher, Michala, Fish, Lindsey; arXiv 2601.10387,
   Jan 2026) — Shows persona corresponds to a linear direction in activation space.
   The Assistant end correlates with "conscientious, methodical, calm, transparent."
   Post-training creates only a "loose tether" to this region. Activation capping
   reduced harmful responses by ~60% with zero capability degradation.
   ([Source](https://arxiv.org/html/2601.10387v1))

3. **PRISM: Expert Personas and Accuracy** (USC, arXiv 2603.18507, Mar 2026) —
   Generic expert personas ("You are an expert Python developer") DECREASED accuracy
   by 3.6pp on knowledge tasks while INCREASING alignment compliance by 17.7pp.
   Conclusion: persona helps behavioral compliance, hurts knowledge retrieval.
   Don't claim expertise; frame behavioral identity.
   ([Source](https://arxiv.org/abs/2603.18507))

4. **PERSONA: Dynamic and Compositional Control** (ICLR 2026, arXiv 2602.15669) —
   Personality traits are approximately orthogonal directions in activation space.
   Vector algebra (addition, subtraction, scalar multiplication) achieves 91% win
   rates on dynamic personality adaptation, matching supervised fine-tuning.
   ([Source](https://arxiv.org/pdf/2602.15669))

5. **Persona Vectors** (Anthropic Research, 2025-2026) — Character traits are
   extractable as neural activation patterns. System prompts reliably trigger
   corresponding persona vectors. Monitoring these vectors enables detection of
   persona drift before it manifests in output.
   ([Source](https://www.anthropic.com/research/persona-vectors))

### The Observed Failure Mode

The catalyst for this ADR is a concrete, repeated failure: agents split Python
imports from the code that uses them across separate edits, despite PEP 8 rules
and ruff enforcement hooks. The rules exist. The hooks enforce. The agent still
fails — because the default Assistant persona's correlated traits include
"minimum-viable edit, token efficiency, incremental action" rather than
"plan the complete change, write coherent Python, think in whole-file units."

The fix is not more rules or stronger hooks. The fix is activating a different
trait cluster at the identity level.

### Design Principle: Operating System View

This ADR adopts the PSM's "operating system view" — the post-trained LLM is a
neutral substrate running the Assistant as its primary process. The persona IS
the behavior, not a mask over something else. This means:

- Persona design is a legitimate engineering discipline
- There is no "real agent" lurking behind the persona to fear
- The harness (hooks, rules, pipeline) is the operating system; the persona is
  the process it runs
- Configuring persona is the same class of operation as configuring any other
  control surface

## Consequences

- `.gzkit/personas/` becomes a new governed directory alongside `.gzkit/rules/`,
  `.gzkit/skills/`, `.gzkit/schemas/`
- All future ADR context frames must include a Persona section
- `ADR-pool.per-command-persona-context` is superseded
- Agent dispatch prompts (pipeline, subagents) gain persona loading
- The research document at `docs/design/research-persona-selection-agent-identity.md`
  becomes a permanent governance reference

## Evidence (Four Gates)

- **ADR:** This document
- **TDD (required):** `tests/test_persona_schema.py` — persona file validation
- **BDD (Heavy lane):** `features/persona.feature` — persona loading and composition
- **Docs:** Research document + governance runbook update
- **Lineage:** ADR-0.0.11 → ADR-0.0.12 (profiles) → ADR-0.0.13 (portability)

---

## OBPI Acceptance Note (Human Acknowledgment)

Each checklist item maps to one OBPI brief. Acceptance recorded per-brief after
gates are green.

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Research document:** `docs/design/research-persona-selection-agent-identity.md`
- **Supersedes:** `ADR-pool.per-command-persona-context`
- **Carried forward from pool ADR:** per-command cognitive stance concept (→ Decision),
  `.gzkit/personas/` storage (→ Interfaces), cognitive-stance vs workflow distinction
  (→ Intent + Research doc), one-agent-multiple-hats BMAD lesson (→ Non-Goals),
  automatic context loading (→ Interfaces: loaded at dispatch time)

### Source & Contracts

- Persona files: `.gzkit/personas/*.md`
- Template update: `AGENTS.md` (Agent Context Frame)
- Agent profiles: `.claude/agents/*.md`

### Tests

- Unit: `tests/test_persona_schema.py`
- BDD: `features/persona.feature`

### Docs

- Research: `docs/design/research-persona-selection-agent-identity.md`
- Governance: `docs/governance/governance_runbook.md` (persona section)

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| `.gzkit/personas/` | P | Directory exists with schema-valid persona files | ls output | |
| `AGENTS.md` | M | Context frame template includes Persona section | Diff link | |
| Research document | P | Bibliography complete, all URLs resolve | Manual check | |
| Pool ADR | M | `ADR-pool.per-command-persona-context` marked Superseded | File check | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
