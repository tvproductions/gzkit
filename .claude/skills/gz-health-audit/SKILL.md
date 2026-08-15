---
name: gz-health-audit
persona: spec-reviewer
description: Namespace router → the four-axis health and integrity audit. Use when the operator reports that gzkit feels "wobbly", misaligned, or that governance is not holding — or before a release, to check that declared mechanisms still fire. Routes to the concrete axis surfaces in a fixed cheapest-first order; owns the ordering rationale and the budget rule, not the analyses themselves.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-15
metadata:
  skill-version: "1.0.0"
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
