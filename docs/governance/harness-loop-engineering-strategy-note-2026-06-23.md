# Harness Loop Engineering Strategy Note - 2026-06-23

Status: operator-supplied strategy synthesis. This note captures a broad
discussion of gzkit's harness-development posture using Jia Huang's agent
architecture guidance as operator-supplied design input. It is not a new
campaign, not an ADR, and not an authority layer.

## Thesis

gzkit has crossed a phase boundary. The discovery-era strategy was to capture
doctrine, preserve context, build governance surfaces, and make agent-driven
work auditable across sessions. That strategy was effective for invention.

The current strategy must shift from capture to loop engineering: make the
agent's perceive-reason-act loop smaller, more accurate per step, better
verified, and faster to abort when orientation is wrong.

The next phase is not more gzkit. It is loop discipline, layer discipline, and
pattern discrimination.

## Harness vs Loop

Harness engineering defines the runtime environment: tools, permissions,
sandboxing, state persistence, skills, observability hooks, and action
interfaces.

Loop engineering defines the bounded agent cycle inside that environment:
perceive authoritative context, reason about the lawful route, act through
governed tools, observe evidence, reflect, and either continue, escalate, or
stop.

gzkit has built substantial harness. It now needs explicit loop engineering
doctrine so governance does not become a catch-all substitute for perception,
orientation, runtime, or test-harness defects.

## Current Imbalance

gzkit is strongest in memory and governance, and weakest at the interfaces that
decide what the next agent should perceive, orient around, and do.

- Perception is weak-to-medium: the documentation corpus is large, but agents
  mostly see it through filenames, search hits, handoffs, and control-surface
  pointers.
- Memory is strong but noisy: campaign, ADRs, OBPIs, handoffs, ledger, insights,
  corpus, and docs preserve a lot, but not every memory is current, binding, or
  relevant.
- Reasoning is strong in prose but weak at entry: agents can reason deeply after
  selecting a path, but AIRLOCK-IN is not yet a mechanical orientation gate.
- Action is broad but inconsistent: many commands exist, but some guards have
  self-decided fatality outside the checkpoint/disposition path.
- Reflection is rich narratively but not structured enough: handoffs and audits
  preserve lessons, but too much remains prose instead of typed deltas,
  squawks, contradictions, or negative-control gaps.
- Collaboration is useful but handoff-dependent: collaboration should improve
  throughput or independent evidence, not compensate for unclear authority.
- Governance is gzkit's moat, but it must narrow to constraints that fire:
  ledger truth, human attestation, live negative controls, operator-PII/secrets
  floor, release discipline, and MX hard exits.

## Loop Discipline

The core loop is:

```text
Perceive -> Reason -> Act -> Observe result -> Reflect -> continue/done
```

with a memory loop:

```text
Reflect -> write memory
Perceive -> read memory
```

gzkit's recurring failure class is wrong orientation early in the loop. If an
agent orients from stale handoff advice, weak authority ranking, or facade
evidence, later ceremony can make the wrong path look more legitimate.

AIRLOCK-IN is therefore an orientation gate, not merely a process gate. Before
mutation, the agent should be forced to name:

- mode: Design, Build, MX, or Chores
- authority: active campaign item, GHI, OBPI, chore, or explicit operator
  interrupt
- source ranking: which source wins if campaign, handoff, ADR, frontmatter, or
  ledger disagree
- seam-map: which boundaries the work crosses
- falsifier: what evidence would prove this route wrong
- topology-purpose declaration: which cognitive function and execution topology
  the workflow uses

## Layer Discipline

Every gzkit problem should be classified by layer before adding governance
surface:

- Cognitive module: perception, memory, reasoning, action, reflection,
  collaboration, governance
- Runtime VM: sandbox, state persistence, event/receipt system, observability,
  tool host, skills, test harness
- External boundary: operator, other agents, GitHub/PyPI/docs, downstream repos

Do not solve a runtime VM defect with cognitive prose. Do not solve a cognitive
orientation defect with more tooling alone. Governance specifies invariants; the
runtime must carry them.

Examples:

- slow unit tests are a runtime/test-harness economics issue
- agents misreading docs is a perception/memory issue
- handoffs steering work is a collaboration/memory boundary issue
- gates self-deciding fatality is an action/runtime control-path issue
- claims of enforcement without live negative controls are governance/verifier
  failures

## Pattern Discrimination

Jia Huang's function-by-topology pattern matrix is useful for gzkit as a
classification tool, not a backlog generator. Empty cells are meaningful; not
every pattern should become a feature.

Every new harness mechanism should declare:

- cognitive function: perception, memory, reasoning, action, reflection,
  collaboration, or governance
- execution topology: chain, route, parallel, orchestrate, loop, or hierarchy
- authority: what authorizes the workflow
- verifier: what proves it worked
- termination: when it stops
- writeback: what memory surface, if any, is updated
- excluded patterns: what the design deliberately does not use

If a proposed workflow needs more than seven active function/topology patterns,
simplify or split it.

## Topology Rules

Topology and cognitive function are separate axes. Same topology, different
purpose; same purpose, different topology. A workflow declaration must name
both.

- Use Chain when the path is known and verified.
- Use Route when classification or authority selection is the main risk.
- Use Loop when the goal is clear but the implementation needs iterative
  correction.
- Use Parallel when independent evidence or independent solution paths reduce
  uncertainty.
- Use Orchestrate when bounded roles must produce or verify one artifact.
- Use Hierarchy only when parent-child authority or durable release
  decomposition is the real design.

Repair work should prefer Route + Loop through GHI/MX. Release-carrying build
work may justify Hierarchy + Chain through ADR/OBPI. Handoffs are Collaboration
+ Chain for continuity only; they are never authority.

## Scaling Rule

Collaboration is a scaling mechanism, not a correctness mechanism.

Scale agents only when the task shape requires it:

- Single agent: one context, one expertise
- Agent + tools: external capabilities needed
- Agent + subagents: decomposable subtasks with bounded scopes
- Pipeline: clear sequential stages
- Team: independent parallel subtasks
- Swarm: experimental only, not a gzkit governance default

Do not add agents to compensate for unclear authority, stale doctrine, or
uncertain topology. Resolve those at AIRLOCK-IN or through operator design
dialogue first.

## Loop Leverage Test

For any proposed harness work, ask:

- Does it reduce loop iterations?
- Does it improve per-step accuracy?
- Does it add a real verifier, not a facade?
- Does it enable faster failure before state corrupts?

If none hold, the work is likely accretion.

This reframes gzkit's strategic test from "is this good governance?" to "does
this improve loop leverage?"

## Application to Current Campaign

The current Build-to-1.0 priority remains coherent:

- ADR-0.0.74 gates-as-sensors improves Action -> Observe by forcing live guards
  through one checkpoint/disposition path.
- MX formalizes Observe -> Reflect -> repair.
- The enforcement-claim meta-validator ensures "enforced" claims have live
  negative-control proof.
- OKF/CMS improves Perception -> Memory retrieval for documentation knowledge.
- AIRLOCK-IN will improve Reason -> Act by catching wrong orientation before
  mutation.
- Unit-test harness repair improves runtime VM economics and loop cost.
- Handoff tightening keeps memory/collaboration artifacts from masquerading as
  authority.

The campaign should not be derailed into broad pattern adoption. The next phase
is pattern discrimination: choose the smallest topology-purpose contract that
reduces loop error for the current work.

## Strategic North Star

gzkit's architectural bet is not to become the runtime VM, editor UX, parallel
agent system, or universal context engine.

gzkit's bet is governed loop engineering over a runtime VM: authoritative
knowledge, constrained action, observable evidence, human attestation, live
negative controls, and replayable claims across sessions.

When gzkit says "done," the claim should be lawful, replayable, attested where
required, and falsified by a live negative control when it asserts enforcement.
