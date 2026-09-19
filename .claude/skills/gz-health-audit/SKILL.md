---
name: gz-health-audit
persona: spec-reviewer
description: Namespace router → the four-axis health and integrity audit, read through four dimensions of agent movement (change point, jurisdiction, invariant, escalation). Use when the operator reports that gzkit feels "wobbly", misaligned, or that governance is not holding — or before a release, to check that declared mechanisms still fire. Routes to the concrete axis surfaces in a fixed cheapest-first order; owns the ordering rationale, the reading frame and the budget rule, not the analyses themselves.
category: governance-infrastructure
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-09-19
metadata:
  skill-version: "1.4.0"
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

The 2026-08-15 diagnosis found that conformance checks dominated the audit,
leaving two questions insufficiently examined:

- whether a declared mechanism **ever fires**, or
- whether the invariants are still **coherent with original intent**.

A system can therefore pass every check it knows how to make and still be
misaligned — which is the observed state that produced this method. The 2026-08-15
run found the repo green on nearly every scope while three scopes failed
*outside* the gated tier, two of them regressions introduced by the fix for the
previous defect.

That diagnosis raised **surface inversion** — governance larger than the surface
it governs — as a possible contributor. Counts alone establish neither causation
nor a reason to retire a control. Use the routed chores' current measurements;
the historical result is a sampling lead, not evidence of today's state.

Added rules introduce possible interactions to inspect. A documented historical
instance: `governance-core.md` `0.9.0` (a rule since folded into root `AGENTS.md`) exists because
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
| **Jurisdiction** | Which design decisions and artifacts may this agent disturb, and what must remain invariant? Did it cross an information-hiding boundary, not merely a file count? | information hiding and least privilege | Parnas, "On the Criteria to be Used in Decomposing Systems into Modules" (1972); Saltzer and Schroeder, ["The Protection of Information in Computer Systems" (1975)](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html), § I.A.3(f), least privilege — scholarly; capability-based security; Evans, *Domain-Driven Design* (bounded contexts); Skelton and Pais, *Team Topologies* (cognitive load, ownership boundaries) — practitioner |
| **Invariant** | Which contracts must this change preserve, and do ADRs, validators, workflows, rules and code still tell the same story afterwards? | design by contract | Meyer, *Object-Oriented Software Construction* — scholarly; Brooks, conceptual integrity |
| **Escalation** | When the task must cross its authorized surface, does the agent stop with an impact argument — *"I was authorized here; here's why that isn't enough; here's the dependency and likely surface"* — and preserve it through the applicable record or exchange procedure? | change-impact analysis and controlled handoffs | Arnold and Bohner, *Software Change Impact Analysis* — scholarly |

The four were reduced from six bodies of work the conversation listed:
modularity and information hiding plus DDD bounded contexts; change impact
analysis; design by contract and invariants; least privilege and
capability-based security; Feathers' seams and safe change; cognitive load and
ownership boundaries. The conversation elaborated one constellation, the
jurisdiction cluster around Parnas; the other three were mapped by the agent on
operator direction on 2026-09-12 and are marked so below.

### The four constellations

Where each dimension's thinking lives — the sources the conversation named, the
operator's addition and the agent's proposals, and the boundary each cluster
crosses into the next — is mapped in [`references/constellations.md`](references/constellations.md).
Read it before citing a source in an audit finding.

The conversation's caution binds every cluster: mix in control theory, safety
engineering and socio-technical systems to test whether the older frames still
hold, and never force a new agentic control problem into a 1970s module frame.
Naur, "Programming as Theory Building", frames a cross-cutting question: where
does implementation understanding reside, and how does the next session recover
it? The conversation distinguishes the operator's intentional theory from an
implementation understanding that may be dispersed across agent decisions.
Inspect that reconstruction; contracts and handoffs do not prove it by existing.

**Per dimension, one skeleton, no field skipped:** concern, governing question,
intellectual lineage, current gzkit mechanisms, evidence to inspect, failure
signatures, boundaries.

**The pass:** inventory → map evidence to lenses → mark gaps and overlaps → test
against failure patterns → decide. The signature catalog is not exhaustive:
an unmatched observation still warrants evaluation against the governing intent
and evidence, with uncertainty recorded.

The four axes collect evidence; the four dimensions interpret it across axes.
Do not run four additional audits or force a one-to-one axis/lens mapping. Select
the bounded intent-trace sample from earlier signals before reading it deeply.
For each finding report its surface, applicable lens or lenses, declared intent,
observed behavior, witness and limitations, and proposed disposition. Preserve
the seven-field skeleton above even when a field's honest answer is unknown.

**Cross-cutting question, asked of every dimension:** *"Is this explicit enough
that a fresh agent can reconstruct it without relying on tacit memory?"*

**Five checks per dimension, before any disposition:** health, opportunity,
strategic fit, tactical tweak, retirement — *"Has something outlived its
assumptions?"* Dispositions are the budget rule's: retain, clarify, reconnect an
existing control, repair an observed failure, investigate, or retire with
steering-failure evidence. Jurisdiction constrains mutation, not understanding:
read broadly, write narrowly. Don't add mechanisms first.

**Evidence discipline for the frame:** every lens's evidence names an
instrument where one exists — a chore script or a `gz` verb. Any necessary ad-hoc
measurement must disclose its method, inputs and limitations; it is raw evidence,
not automatically a new control requirement. The 2026-09-12 worked example carries three such
ad-hoc measurements (airlock decisions by seam-map emptiness, acceptance records
and distinct digests per brief, Feature Checklist score distribution) and says
so. Recheck its calibration-instrument gaps before treating them as current.
Distinguish an observation gap from a violated mechanism obligation: identify
the governing requirement and producer before assigning a failure signature.

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

**Budget the audit by steering need and evidenced decisions.** Root `AGENTS.md`
§ MAKE LLM STOCHASTIC VIBES INERT governs — lighter ceremony does not decide a choice, and the corpus keeps the ruling's original wording, "Volume follows steering need"; reduction alone is not success.
Retain, clarify, reconnect an existing control, repair an observed failure,
investigate, or retire. Retirement requires named evidence of degraded steering
or displaced assumptions, with the preserved obligation and replacement, if
needed, made explicit. Low invocation counts alone do not prove uselessness.

Report additions and removals with their steering rationale, without a net
reduction quota. A contradiction needs an authority-grounded disposition; an
inert declaration needs its trigger and producer inspected before choosing
repair or retirement. An unfinished OBPI needs its history read before any
withdrawal recommendation. Audit findings do not initiate OBPI work or authorize
canon removal; route actions through the existing operator and skill contracts.

## Two disciplines this method learned the hard way

**Use existing instruments before ad-hoc measurements.** The 2026-08-15 run
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
from the source — `AGENTS.md` § DO IT RIGHT #8 (6g), verbatim: *"Before recommending a
command, run it, observe it and paste what it printed."*

## Related

- `gz-tech-debt-review` — debt across probes; this method is about mechanisms firing, not debt
- `gz-foundation-triage` — ranks the foundation backlog; complementary, different question
- `docs/governance/state-doctrine.md` — Layer-3 views are never source-of-truth
- `docs/governance/advisory-rules-audit.md` — the Mechanical/Promotable/Judgment scorecard axis 3 feeds
- `docs/governance/capability-control-review-2026-09-12.md` — the reading frame's worked example and the provenance of the four dimensions
