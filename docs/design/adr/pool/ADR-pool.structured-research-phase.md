# ADR-pool.structured-research-phase

- **Status:** Pool
- **Lane:** Lite
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — research agent adaptation

## Intent

Add an explicit research phase between ADR planning and OBPI specification. Currently
`gz plan` produces an ADR (intent + decision), and `gz specify` decomposes it into
OBPI briefs. The gap: no structured step investigates ecosystem patterns, library
choices, API constraints, or known pitfalls before the decision is committed to OBPIs.
Research happens informally (the agent reads code, the human has background knowledge)
but it isn't captured as an artifact. When research is missing, OBPIs are specified
against assumptions that could have been validated — leading to mid-implementation
pivots that waste OBPI cycles.

## Target Scope

### Research Command

`gz research --adr ADR-X.Y.Z` runs a structured investigation and produces a
research artifact:

- **Investigation areas (templated, ADR-specific):**
  - **Ecosystem scan:** Libraries, frameworks, and tools relevant to the ADR's decision.
    What exists? What's maintained? What are the known failure modes?
  - **Pattern analysis:** How do similar systems solve this problem? What are the
    established patterns in the codebase for this kind of change?
  - **Constraint discovery:** API limits, platform restrictions, performance
    characteristics, licensing concerns that affect the decision.
  - **Pitfall catalog:** Known failure modes, anti-patterns, and "things that seem
    like a good idea but aren't" for this problem domain.
  - **Prior art in project:** Previous ADRs or OBPIs that touched similar areas.
    What worked? What was revised?
- **Output:** `{ADR-dir}/research/RESEARCH-ADR-X.Y.Z.md` — structured markdown
  with findings per investigation area, sources cited, and a "implications for OBPIs"
  section that directly informs specification.

### Integration Points

- `gz plan --research` runs research inline after ADR creation, before OBPI specification
- `gz specify` reads the research artifact (if present) and surfaces relevant findings
  during OBPI authoring
- Research findings are referenced in OBPI briefs' rationale sections
- The research artifact is a permanent part of the ADR package — not consumed and discarded

### Research Modes

- **Agent-driven (default):** Agent performs the investigation using available tools
  (codebase search, web search, documentation reading) and produces the artifact.
  Human reviews findings before proceeding to specification.
- **Human-seeded:** Human provides initial research (links, notes, prior knowledge)
  via `gz research --seed <notes-file>`. Agent expands and structures the input
  into the full research artifact format.
- **Targeted:** `gz research --adr ADR-X.Y.Z --focus "performance implications"`
  narrows the investigation to specific concerns rather than running the full template.

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- Research does not make decisions — it surfaces information for the ADR decision
  and OBPI specification to consume.
- No mandatory research phase — experienced operators with domain knowledge can
  skip directly to specification.
- No ongoing research tracking — this is a point-in-time investigation, not a
  living document. If the ecosystem changes, run `gz research` again.

## Dependencies

- **Blocks on:** None
- **Blocked by:** None
- **Complements:** ADR-pool.pre-planning-interview (interview surfaces unknowns;
  research investigates them)
- **Complements:** ADR-pool.universal-agent-onboarding (bootstrap chain could include
  an optional research step between plan and specify)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Research artifact template and storage location are accepted.
3. Investigation area template is validated against at least 3 real ADRs — confirm
   the template surfaces useful findings without being busywork.
4. Integration with `gz specify` is designed — how does the research artifact inform
   OBPI authoring without becoming a mandatory gate?

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-plan-phase` research step — spawns a dedicated Researcher agent that investigates implementation patterns guided by the phase context. Creates `{N}-RESEARCH.md` as input to plan creation. Research is optional but recommended.
- Amazon's "Working Backwards" process — research and discovery happen before the
  specification is written, not after implementation starts.

## Notes

- The gz-adr-create interview (v6) already includes "constraint archaeology" and
  "assumption surfacing" questions. Research is the natural extension — the interview
  identifies what to investigate, research does the investigation.
- Risk: research can become an infinite time sink. The templated investigation areas
  and targeted mode (`--focus`) are the primary scope controls.
- Consider: research artifacts as input to the gz-adr-evaluate scoring framework.
  An ADR with research backing scores higher on "Alternatives Considered" and
  "Consequences Analysis" dimensions.
- The research artifact's "implications for OBPIs" section is the key value —
  it directly shapes specification quality. Without it, research is just homework.
- GSD's Researcher is a distinct agent persona. In gzkit, research could be a
  persona-tagged activity (research persona) or simply a skill with investigative
  prompting — design decision for promotion time.
