---
name: gz-health-audit
persona: spec-reviewer
description: Namespace router → the four-axis health and integrity audit, read through four dimensions of agent movement (change point, jurisdiction, invariant, escalation). Use when the operator reports that gzkit feels "wobbly", misaligned, or that governance is not holding — or before a release, to check that declared mechanisms still fire. Routes to the concrete axis surfaces in a fixed cheapest-first order; owns the ordering rationale, the reading frame and the budget rule, not the analyses themselves.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-12
metadata:
  skill-version: "1.1.0"
model: sonnet
---

# gz-health-audit

Four axes, in this order. **The order is the method** — running them out of
order wastes the expensive one.

| # | Axis | Question | Surface | Cost |
|---|---|---|---|---|
| 0+1a | Conformance + validator reachability | Does the system pass its own checks, and does each check actually run? | `control-surface-validator-reachability` chore | mechanical |
| 1b+1c | Ledger vocabulary inertness | Does each declared event type ever fire? | `ledger-vocabulary-inertness` chore | mechanical |
| 3 | Doctrine coherence | Do two rules mandate opposite actions? | `control-surface-rule-conflicts` chore | medium |
| 2 | Intent trace | Does the shipped surface fulfil its ADR's declared intent? | `gz-intent-trace` skill | deep, human |

Invoke the matched surface directly. Axis 2 runs **last** despite its number.

## The diagnosis this method is built on

gzkit's ~100 validator scopes audit exactly one layer: **conformance to declared
invariants**. Essentially none audit either of:

- whether a declared mechanism **ever fires**, or
- whether the invariants are still **coherent with original intent**.

A system can therefore pass every check it knows how to make and still be
misaligned — which is the observed state that produced this method. The 2026-08-15
run found the repo green on nearly every scope while three scopes failed
*outside* the gated tier, two of them regressions introduced by the fix for the
previous defect.

The structural generator is a **surface inversion**: the governance surface is
larger than the surface it governs. Measure it before reasoning about it — do not
trust a figure transcribed into prose:

```bash
ls docs/design/adr/foundation docs/design/adr/pre-release | wc -l
find docs -name 'OBPI-*.md' | wc -l
uv run gz validate --help | grep -coE '^\s+--[a-z-]+'
find src -name '*.py' | wc -l
```

Every added rule multiplies the pairwise contradiction surface. There is already
a documented instance: `.claude/rules/governance-core.md` `0.9.0` exists because
two binding rules mandated opposite actions for the two most common session
decisions in the repo.

## The reading frame — four dimensions of an agent's movement into the codespace

The axes above produce **inventory**. This frame is how the inventory is
**read** and how axis 2's sample is **chosen**. It was ratified by the operator
on 2026-09-12 from a 2026-09-11 conversation on why bounded OBPIs had grown from
under an hour to multiple days; the operator's instruction was verbatim *"Pull
the four as-is. Keep them bare deliverables."* The worked example is
`docs/governance/capability-control-review-2026-09-12.md`.

The four are lenses, not features. Task size and jurisdiction are not the same
thing: a tiny task can carry a large blast radius. The conversation proposed a
boundary below the existing hierarchy — **OBPI → requirement → task →
authorized change surface** — and whether that boundary is missing is a
question the lenses investigate, not a settled fact. The lenses apply to ADRs,
validators, workflows, rules and prompts, not only code.

| Dimension | Governing question | Concept behind it | Focal anchors |
|---|---|---|---|
| **Change point** | For this change, what is the narrowest seam where behavior may legitimately change, and can the change be localized behind the existing contract? | seams and safe change | Feathers, *Working Effectively with Legacy Code*; Fowler, refactoring; Hunt and Thomas, *The Pragmatic Programmer* (tracer bullets) — practitioner |
| **Jurisdiction** | Which design decisions and artifacts may this agent disturb, and what must remain invariant? Did it cross an information-hiding boundary, not merely a file count? | information hiding and least privilege | Parnas, "On the Criteria to be Used in Decomposing Systems into Modules" (1972) — scholarly; least privilege and capability-based security; Evans, *Domain-Driven Design* (bounded contexts); Skelton and Pais, *Team Topologies* (cognitive load, ownership boundaries) — practitioner |
| **Invariant** | Which contracts must this change preserve, and do ADRs, validators, workflows, rules and code still tell the same story afterwards? | design by contract | Meyer, *Object-Oriented Software Construction* — scholarly; Brooks, conceptual integrity |
| **Escalation** | When the task must cross its authorized surface, does the agent stop with an impact argument — *"I was authorized here; here's why that isn't enough; here's the dependency and likely surface"* — and does the stop land on Layer-2? | change-impact analysis and controlled handoffs | Arnold and Bohner, *Software Change Impact Analysis* — scholarly |

The four were reduced from six bodies of work the conversation listed:
modularity and information hiding plus DDD bounded contexts; change impact
analysis; design by contract and invariants; least privilege and
capability-based security; Feathers' seams and safe change; cognitive load and
ownership boundaries. Only the jurisdiction constellation was elaborated in the
conversation — Parnas inside a modularity cluster with Dijkstra (separation of
concerns), Wirth (stepwise refinement), Myers and Constantine (cohesion and
coupling), Brooks (conceptual integrity). The other three dimensions carry
their named anchors; their constellations are not yet mapped, and mapping them
is part of the pass, not a prerequisite for it. Naur, "Programming as Theory
Building", frames the whole: the operator holds the intentional theory; the
implementation theory is distributed across thousands of agent decisions and is
partially reconstructed each session, which is why contracts, invariants and
jurisdiction boundaries matter more as the system ages. The conversation also
warned against forcing a new agentic control problem into a 1970s module frame:
test the old frames against control theory, safety engineering and
socio-technical systems before trusting them.

**Per dimension, one skeleton, no field skipped:** concern, governing question,
intellectual lineage, current gzkit mechanisms, evidence to inspect, failure
signatures, boundaries.

**The pass:** inventory → map evidence to lenses → mark gaps and overlaps → test
against failure patterns → decide. A finding that matches no recorded failure
signature is either a new signature or not a finding.

**Cross-cutting question, asked of every dimension:** *"Is this explicit enough
that a fresh agent can reconstruct it without relying on tacit memory?"*

**Five checks per dimension, before any disposition:** health, opportunity,
strategic fit, tactical tweak, retirement — *"Has something outlived its
assumptions?"* Dispositions are the budget rule's: retain, clarify, reconnect an
existing control, repair an observed failure, investigate, or retire with
steering-failure evidence. Jurisdiction constrains mutation, not understanding:
read broadly, write narrowly. Don't add mechanisms first.

**Evidence discipline for the frame:** every lens's evidence names an
instrument — a chore script or a `gz` verb — and an ad-hoc measurement is
disclosed as ad hoc, is never a finding's sole witness, and is a candidate for
an instrument, not a result. The 2026-09-12 worked example carries three such
ad-hoc measurements (airlock decisions by seam-map emptiness, acceptance records
and distinct digests per brief, Feature Checklist score distribution) and says
so; the calibration signals the decomposition matrix names — rework rate, failed
gates, attestation churn, delivery predictability — have no instrument today,
which is itself a doctrine-declared-without-mechanism finding.

## Why cheapest-first is load-bearing

The mechanical axes exist to **aim** the expensive one. Run in the other order,
the deep-read budget goes to whichever ADR happened to be open, and the trace
produces judgments nothing selected. Axes 0/1 cost roughly a session each and are
fully reproducible; axis 2 is human judgment that does not scale and cannot be
re-run cheaply to check itself.

Each mechanical axis also emits the **risk signals axis 2 samples on** — parked
and uncovered OBPIs, measured-inert mechanisms, ADRs already below threshold. Run
axis 2 first and those signals do not exist yet.

## The budget rule (binding on any run of this method)

**Budget the audit by net surface reduction, not by findings count.**

If a run produces forty new GHIs and three new ADRs, it has made the inversion
worse and the next run will find *more* wobble. Given the diagnosis, the primary
output verb is **retirement**:

| Finding | Primary verb |
|---|---|
| inert mechanism | delete, or promote to mechanical |
| contradictory rule pair | resolve to one |
| phantom / never-completing OBPI | withdraw |
| unrowed clause with a real check | score it |
| declared-but-unproduced event type | wire the producer or retire the declaration |

A run that adds more governance surface than it retires should say so explicitly
in its own report. That is the honest failure mode of an audit, and naming it is
cheaper than discovering it two runs later.

## Two disciplines this method learned the hard way

**Measure with the instruments, never with ad-hoc pipelines.** The 2026-08-15 run
reported validator tier counts from a throwaway shell pipeline that missed a
pre-commit line gating three scopes at once, and the wrong figures were relayed
twice before the chore's own script corrected them. The chores exist partly
because their measurements are reproducible and self-tested; a one-off `rg`
pipeline is neither.

**Report the count; read the producer before telling the story.** The same run
read a correct `obpi_parked`/`obpi_unparked` ratio as an operator "abandonment
channel" and named a
<!-- gz-validate-skip: command-shape -->
`gz obpi park` verb **that does not exist**. Parking is
emitted by an ADR-demotion migration, and that module states parking "is
reversible on re-promotion and is not a negation of completed work." The counts
were right; the explanation was invented from training memory rather than read
from the source — DO IT RIGHT Invariant 6g, verbatim: *verify the runtime surface
before recommending an incantation.*

## Related

- `gz-tech-debt-review` — debt across probes; this method is about mechanisms firing, not debt
- `gz-foundation-triage` — ranks the foundation backlog; complementary, different question
- `docs/governance/state-doctrine.md` — Layer-3 views are never source-of-truth
- `docs/governance/advisory-rules-audit.md` — the Mechanical/Promotable/Judgment scorecard axis 3 feeds
- `docs/governance/capability-control-review-2026-09-12.md` — the reading frame's worked example and the provenance of the four dimensions
