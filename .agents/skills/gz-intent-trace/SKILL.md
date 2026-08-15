---
name: gz-intent-trace
persona: spec-reviewer
description: Trace a sampled set of ADRs from declared intent to shipped surface, and route every gap as a correction under its owning ADR. Use when asking whether what shipped actually fulfils what was decided — after an inertness audit surfaces candidates, before a release, or when the operator reports that a capability "exists but doesn't really work". Diagnosis and routing only; never authors a new ADR and never widens scope beyond the sampled set.
category: adr-audit
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-15
metadata:
  skill-version: "1.0.0"
model: sonnet
---

# gz-intent-trace

Read an ADR's declared **Decision** and **Acceptance Criteria**, read the surface
that actually shipped, and answer one question per ADR:

> Does the shipped surface fulfil its original declared intent?

Every `no` is a **correction routed under the owning ADR** — never a fresh pool
ADR, never new-design ceremony, and never an "enhancement". That routing is
operator canon, verbatim:

> *"discovering that more is needed to fulfil the intent of a feature is not an
> enhancement, it is a correction."*

Enhancement means the surface works as designed and could merely be tighter.
"Capability not yet built" is never an enhancement.

## Why this is a skill and not a chore

Chores are **recurring maintenance** with a definite disposition per finding.
This is not that. It is an **on-demand deep procedure** producing judgments that
route to corrective work — the same shape as `gz-tech-debt-review` and
`gz-foundation-triage`. There is no per-run tidying it generates and no ratchet
it holds; forcing it into a chore would label design work as maintenance.

## Position in the health-audit method

The fourth and most expensive axis. Run it **after** the mechanical axes, never
before — they exist to aim it. See `gz-health-audit` for the ordering and why it
is load-bearing.

| Axis | Surface | Cost |
|---|---|---|
| Conformance + validator reachability | `control-surface-validator-reachability` chore | mechanical |
| Ledger vocabulary inertness | `ledger-vocabulary-inertness` chore | mechanical |
| Doctrine coherence | `control-surface-rule-conflicts` chore | medium |
| **Intent trace** | **this skill** | **deep, sampled, human judgment** |

## Do not trace the whole corpus

The ADR corpus is large enough that an exhaustive pass is not a budget anyone
will spend twice, and an unaimed pass spends it on whichever ADR happened to be
open. **Sample by risk signal**, drawn from the mechanical axes:

| Signal | Source | Why it predicts intent drift |
|---|---|---|
| Parked / withdrawn / repudiated / uncovered-accepted OBPIs | `uv run gz adr status <ADR-ID>` | a decomposition that did not complete is where declared intent most often outran delivery |
| A declared mechanism measured inert | Pass D and the ledger-inertness chore | the ADR shipped a surface; nothing exercises it |
| Heavily cited foundation ADRs | `rg` across `.gzkit/rules/**`, `docs/governance/**` | drift here propagates to everything citing it |
| Failing `gz validate --evaluation-justify-binding` | that scope | the ADR's own scorecard already says a dimension is below threshold |

Take the intersection first — an ADR carrying two or more signals is the
highest-yield trace in the corpus.

## Procedure

### 1. Build the sample

Gather candidates from the signals above. Record the sample and the signal that
selected each ADR **before** reading any of them — a sample chosen after reading
is not a sample, it is a conclusion.

### 2. Read the ADR's declared intent

For each ADR, read `## Decision` and `## Acceptance Criteria` (or its Feature
Checklist). Extract the intent as a list of claims about what will exist and
what it will do. Do not read the implementation yet.

```bash
uv run gz context <ADR-ID>          # body + OBPI briefs + covering tests + rules
uv run gz adr status <ADR-ID>       # Layer-2 lifecycle and landed count
```

### 3. Read what shipped

Read the actual surface — the code, the CLI output, the validator, the rule
file. **Run it.** DO IT RIGHT #4 and Invariant 6g both bind: verify observed
behaviour, not assumed behaviour; paste real output.

The most common false pass at this step is reading a *test* and concluding the
behaviour exists. A test that runs against a fixture proves the fixture, not the
repository — a failure mode this repo has already shipped (see Pass D's
§ Background, where three validators failed the live tree while their tests were
green).

### 4. Apply the intent test, claim by claim

For each extracted claim: does the shipped surface fulfil it?

| Verdict | Meaning | Route |
|---|---|---|
| **Fulfilled** | the claim is met, observed | nothing |
| **Correction** | the surface exists but does not fulfil the declared intent | corrective work **under the owning ADR** |
| **Enhancement** | the surface fulfils the intent and could merely be tighter | out of scope for this skill |

When uncertain between correction and enhancement, it is a **correction** — the
default the operator's canon sets, precisely because the opposite default is how
unfinished work gets relabelled as satisfactory.

### 5. Route

- **Correction, and it fits `AGENTS.md` § Defect-fix routing thresholds** —
  direct fix, `fix(<scope>): … (GHI #N)`, citing the owning ADR.
- **Correction, larger than the thresholds** — file through `/ghi-author`
  (never `gh issue create`), body naming the ADR, the declared claim verbatim,
  and the observed surface.
- **Never** author a new ADR from a trace finding. The owning ADR already exists;
  that is what makes the gap a correction.

## Boundaries

- **Diagnosis and routing only.** This skill does not implement the corrections
  it finds.
- **Never widens the sample mid-run.** A signal discovered while tracing goes on
  the next run's candidate list, not this one's. Widening mid-run is how a
  sampled audit becomes an unbounded one and stops finishing.
- **Never authors a new ADR, pool or otherwise.**
- **Quote the declared claim verbatim.** Invariant 6h — a narrative
  reconstruction of what an ADR "basically said" is exactly the drift this skill
  exists to detect, reproduced by the detector.

## Sequencing caution

A trace run is deliverable-bearing work and will compete with the active
campaign, which is Magna Carta (`AGENTS.md` § Operator Doctrine). The sample's
top entries are frequently the ADRs the campaign is already sequenced around.
**Surface the collision to the operator and get a ruling before running** — do
not resolve it unilaterally (Behavior Rule 9).

## Related

- `gz-health-audit` — the router that owns the ordering and the budget rule
- `gz-adr-audit` — Gate-5 audit of one ADR's own evidence chain (different question: does the evidence support closeout, not does the surface fulfil intent)
- `gz-tech-debt-review` — debt across probes; this skill is intent, not debt
- `AGENTS.md` § Operator Doctrine — correction vs enhancement, verbatim
