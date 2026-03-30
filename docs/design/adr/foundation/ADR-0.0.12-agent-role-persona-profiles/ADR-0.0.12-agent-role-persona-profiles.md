<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.12 — Agent Role Persona Profiles

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Inventory all existing agent profile files (`.claude/agents/*.md`) and extract
   current behavioral instructions that could be reframed as persona traits
1. Inventory all skill SKILL.md preambles for cognitive stance language that
   should migrate into persona frames
1. Review pipeline dispatch prompt composition in `pipeline_runtime.py` to
   understand where persona injection would occur

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If ADR-0.0.11 (persona control surface) is not complete, stop. This ADR
  depends on the schema and storage model defined there.

**Date Added:** 2026-03-30
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.12
**Area:** Governance Foundation — Agent Identity Profiles
**Lane:** Heavy

## Agent Context Frame — MANDATORY

**Role:** Identity designer writing concrete persona frames for each agent role
in gzkit's multi-agent architecture.

**Purpose:** When this ADR is complete, every agent role (main session,
implementer, spec-reviewer, quality-reviewer, narrator, pipeline orchestrator)
has a virtue-ethics-based persona frame that activates the right behavioral
trait cluster for its specific work. Agents stop defaulting to "helpful AI
assistant" and start operating from intentionally designed identities.

**Goals:**

- Main session persona frame written and integrated into CLAUDE.md/AGENTS.md
- Implementer persona frame activates craftsmanship traits (plan-then-write,
  whole-file thinking, PEP 8 as identity not checklist)
- Reviewer personas activate rigor traits (independent judgment, skepticism
  of optimistic claims, evidence-based assessment)
- Narrator persona activates communication traits (clarity, precision,
  operator-value framing)
- Pipeline orchestrator persona activates governance traits (ceremony
  completion, stage discipline, no premature summarization)

**Critical Constraint:** Persona frames MUST be grounded in the design
principles from ADR-0.0.11. They MUST use virtue-ethics framing (character
traits, values, relationship to work), NEVER expertise claims. Each frame
MUST specify both traits (what to activate) and anti-traits (what to suppress).

**Anti-Pattern Warning:** A failed implementation writes persona frames that
are either too generic ("You care about code quality") or too specific ("You
always use pathlib.Path and never os.path"). The correct level is behavioral
identity — what the agent values and how it approaches work — not prescriptive
rules (those belong in `.claude/rules/`) or vague aspirations.

**Integration Points:**

- `.gzkit/personas/` — persona frame storage (from ADR-0.0.11)
- `.claude/agents/implementer.md` — implementer dispatch profile
- `.claude/agents/spec-reviewer.md` — spec reviewer dispatch profile
- `.claude/agents/quality-reviewer.md` — quality reviewer dispatch profile
- `.claude/agents/narrator.md` — narrator dispatch profile
- `src/gzkit/pipeline_runtime.py` — persona loading in dispatch prompts
- `AGENTS.md` — main session persona
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — orchestrator persona

---

## Feature Checklist — Appraisal of Completeness

### Checklist

- [ ] Main session persona frame (the "Python craftsperson" identity)
- [ ] Implementer agent persona (plan-then-write, whole-file, PEP 8 as nature)
- [ ] Reviewer agent personas (spec-reviewer: independent skeptic; quality-reviewer: architectural rigor)
- [ ] Narrator agent persona (clarity, operator-value, precision)
- [ ] Pipeline orchestrator persona (ceremony completion, stage discipline)
- [ ] Dispatch integration (pipeline_runtime.py loads persona at dispatch)
- [ ] AGENTS.md and CLAUDE.md persona reference integration

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 1
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3-3
- Baseline Selected: 3
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 7

## Intent

Write concrete, research-grounded persona frames for every agent role in
gzkit's architecture, applying the design principles and control surface
established by ADR-0.0.11. Each persona frame activates the specific
behavioral trait cluster that role requires, replacing the default generic
Assistant persona that causes quality failures.

## Decision

- Each agent role gets a dedicated persona file in `.gzkit/personas/`
- Persona frames follow the ADR-0.0.11 schema (traits, anti-traits, grounding)
- The **implementer persona** is the highest-priority frame — it directly
  addresses the observed failure modes (partial edits, import splitting,
  shallow PEP 8 compliance)
- Pipeline dispatch (`pipeline_runtime.py`) loads the relevant persona frame
  and prepends it to the subagent prompt
- Main session persona is loaded via AGENTS.md/CLAUDE.md integration
- Persona frames are **tested** — schema validation ensures they conform to
  the control surface contract

## Non-Goals

- **Persona effectiveness measurement** — this ADR writes persona frames and
  integrates dispatch loading; it does not establish A/B testing or behavioral
  comparison mechanisms to prove the frames work
- **Persona versioning** — persona files are treated as living documents,
  not versioned artifacts with migration paths; schema versioning is ADR-0.0.13
- **Cross-project portability** — persona frames written here are gzkit-specific;
  making them portable is ADR-0.0.13's scope
- **Drift detection** — monitoring whether agents stay in-persona during long
  sessions is ADR-0.0.13 OBPI-05; this ADR writes the frames, not the monitors
- **Modifying behavioral rules** — existing `.claude/rules/*.md` files are not
  touched; persona frames complement rules, they don't replace them

## Interfaces

- **Persona files (new):**
  - `.gzkit/personas/main-session.md`
  - `.gzkit/personas/implementer.md`
  - `.gzkit/personas/spec-reviewer.md`
  - `.gzkit/personas/quality-reviewer.md`
  - `.gzkit/personas/narrator.md`
  - `.gzkit/personas/pipeline-orchestrator.md`
- **Modified:** `src/gzkit/pipeline_runtime.py` — persona loading at dispatch
- **Modified:** `AGENTS.md` — main session persona reference

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.12-01 | Main session persona frame (Python craftsperson identity) | Heavy | Pending |
| 2 | OBPI-0.0.12-02 | Implementer agent persona (plan-then-write, whole-file thinking) | Lite | Pending |
| 3 | OBPI-0.0.12-03 | Reviewer agent personas (spec-reviewer + quality-reviewer) | Lite | Pending |
| 4 | OBPI-0.0.12-04 | Narrator agent persona (clarity, operator-value framing) | Lite | Pending |
| 5 | OBPI-0.0.12-05 | Pipeline orchestrator persona (ceremony discipline) | Lite | Pending |
| 6 | OBPI-0.0.12-06 | Dispatch integration (pipeline_runtime.py persona loading) | Lite | Pending |
| 7 | OBPI-0.0.12-07 | AGENTS.md and CLAUDE.md persona reference integration | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.0.12-*.md`

## Rationale

### Why Individual Profiles Matter

The PSM research shows that persona inference activates **correlated trait
bundles** — not individual behaviors. An implementer who "cares about PEP 8"
naturally plans complete edits, thinks in whole-file units, and treats imports
as inseparable from usage. A reviewer who values "independent judgment"
naturally questions optimistic claims and verifies evidence rather than
rubber-stamping.

### The PRISM Constraint

The PRISM study (USC, arXiv 2603.18507) found that generic expert personas
decrease accuracy by 3.6pp. Each persona frame must avoid expertise claims
and instead frame behavioral identity:

- **Wrong:** "You are a senior Python developer with deep expertise in PEP 8."
- **Right:** "You write Python the way it was meant to be written. PEP 8 is
  not a checklist you consult — it's how you think about code. A partial edit
  is a partial thought."

### The Composition Principle

Per the PERSONA/ICLR 2026 framework, traits compose orthogonally. Each persona
frame specifies multiple traits that combine without interference:

- Implementer: precise + thorough + ownership-driven
- Reviewer: skeptical + evidence-based + independent
- Narrator: clear + concise + operator-focused

### Evidence from Production Failures

The catalyst failure (splitting imports from usage) maps directly to the
default Assistant persona's trait cluster: "token-efficient, incremental,
shallow-compliant." The implementer persona must activate the opposing
cluster: "plan-first, whole-file, deeply-compliant."

## Consequences

- Every subagent dispatch includes a persona preamble
- Agent behavior should shift measurably toward designed trait clusters
- Pipeline dispatch prompts grow by ~200-400 tokens per persona frame
- Persona frames become part of the governed artifact set (sync'd like rules)

## Evidence (Four Gates)

- **ADR:** This document
- **TDD (required):** `tests/test_persona_profiles.py` — schema validation
- **BDD (Heavy lane):** `features/persona_dispatch.feature` — dispatch integration
- **Docs:** Governance runbook persona section
- **Lineage:** Depends on ADR-0.0.11; consumed by ADR-0.0.13

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| `.gzkit/personas/*.md` | P | All 6 persona files exist and validate | ls + schema check | |
| `pipeline_runtime.py` | M | Dispatch loads persona frame | Test output | |
| `AGENTS.md` | M | Main session persona referenced | Diff link | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
