---
name: gz-adr-evaluate
persona: pipeline-orchestrator
description: Post-authoring quality evaluation for ADRs and OBPIs. Scores ADRs on 8 weighted dimensions, OBPIs on 5 dimensions, and can run 10 structured red-team challenges before proposal/defense.
category: adr-lifecycle
compatibility: GovZero v6 framework; adapted from AirlineOps for gzkit ADR package layouts
metadata:
  skill-version: "6.7.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "lifecycle (pre-proposal QC), quality rubric, OBPI decomposition"
  govzero_layer: "Layer 1 - Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-21
model: sonnet
---

# gz-adr-evaluate

## Purpose

Structured quality evaluation for ADRs and their OBPI decompositions. This
skill provides rubrics, challenge protocols, and a red-team prompt that form a
blocking QC step between ADR authoring and human proposal/defense review.

It can be invoked for newly authored ADRs or for retroactive evaluation of an
existing ADR package.

### Common Rationalizations

| Thought | Reality |
|---------|---------|
| "The ADR looks comprehensive, it'll score well" | Comprehensiveness does not equal quality. The rubric measures decision justification, not document length. |
| "The CLI gave a high score, no need for manual review" | The CLI uses heuristics that produce false negatives. Manual review supersedes CLI pre-screen. |
| "This is a retroactive evaluation, I'll be lenient" | The rubric is the rubric. Retroactive evaluation with relaxed standards produces misleading scorecards. |
| "The red-team challenges don't apply to this simple ADR" | Every challenge must be engaged. N/A is not acceptable. Simple ADRs often have unexamined assumptions. |
| "One dimension scored 1, but the overall weighted score is above 3.0" | Any dimension scoring 1 must be revised regardless of the weighted total. |
| "I'll skip the OBPI scoring since the ADR scored well" | ADR quality and OBPI quality are independent assessments. Both are required. |

### Red Flags

- EVALUATION_SUBSTANCE.md written without reading the actual ADR document
- A judged scorecard hand-written into `EVALUATION_SCORECARD.md`, which
  `gz adr evaluate` regenerates and will destroy (GHI #769)
- CLI pre-screen score accepted without manual verification (Step 2 skipped)
- Manual score differs from CLI score but no explanation of the heuristic mismatch
- Red-team challenges marked N/A instead of engaged
- ADR proceeds to proposal/defense with a NO GO or CONDITIONAL GO verdict

---

## Persona

**Active driver:** `pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity before executing this skill. Evaluation is a sequenced ceremony (score dimensions → engage red-team → render verdict); step-discipline keeps the rubric honest. Evaluation is independent judgment, not confirmation. Score what you read, not what you hope.

## Persona Dispatch

Evaluation is the highest-risk read-only judgment ceremony — the rubric's 8 dimensions split cleanly along the persona functional boundaries, and a single driver scoring its own scoring is the precise optimistic-bias defect `spec-reviewer`'s anti-traits name. Dispatch the following personas to produce independent dimension scores the driver synthesizes:

| Persona | Function in this ceremony | Invoked at |
|---|---|---|
| `spec-reviewer` | Scores spec/requirement dimensions of the rubric: requirement clarity, target-scope falsifiability, OBPI decomposition coverage, REQ-trace integrity — anything that asks "is the spec honest, falsifiable, traceable?" | Step 2 (manual rubric scoring) |
| `quality-reviewer` | Scores architectural dimensions: decision justification, alternatives considered, SOLID-analogues for ADR design, single-responsibility per ADR, decision boundaries, maintainability of the proposed surface | Step 2 (manual rubric scoring) |
| `narrator` | Composes the operator-facing scorecard and frames red-team challenge findings — each challenge's finding rendered as evidence-to-decision, not as raw analysis | Step 3 (red-team challenges, if invoked) and final scorecard render |

Personas not dispatched: `implementer` (evaluation is pre-implementation review — no code exists to write or evaluate).

The mechanical attestation that these dispatches occurred was scoped by `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6. That ADR is **Superseded** (`absorbed_into: ADR-0.0.73`, itself Validated 9/9), so there is no promotion pending and nothing arrives from one — the absorption delivered an absorption-marker audit, and that ADR's own § Notes place the receipt machinery (ledger events, bail-to-inline gates, validator scopes) in "a future feature-kind ADR work surface" that is not yet authored (GHI #846). This ceremony **does** have a dispatch channel: `gzkit.adr_eval_dispatch` reports `NOT DISPATCHED` absent a receipt and never infers dispatch from the presence of scores (GHI #770). See § Degraded mode.

### Degraded mode — when dispatch cannot run (binding, GHI #770)

**Dispatch is sometimes genuinely unavailable** — a session that forbids subagents, a headless or cron run, a harness without the Agent tool. Until GHI #770 there was no compliant path for those runs and no way to mark the output, so the mandate was simply skipped: on 2026-08-07 an evaluation of `ADR-0.35.0` ran single-driver, produced 8 dimension scores and a GO verdict, and **nothing recorded that the mandated dispatch had not happened.** An un-compliable mandate gets worked around.

The degraded mode is therefore **declared and legitimate, never silent**:

1. **Running single-driver is permitted.** Do not fabricate a dispatch, and do not abandon the evaluation.
2. **The scorecard states it mechanically.** `render_scorecard_markdown` always emits a `--- Persona Dispatch ---` channel: one row per mandated persona, `NOT DISPATCHED / no dispatch receipt recorded` absent a receipt, plus a `DISPATCH MODE: SINGLE-DRIVER` verdict. This is not something you remember to write — the renderer emits it unconditionally, and `tests/test_adr_eval_dispatch.py` fails closed if a dispatched and an undispatched scorecard could ever render identically.
3. **A single-driver scorecard is not an independent review.** Say so when relaying the verdict; do not present it as one.

A dispatch is credited **only** from a recorded receipt (`gzkit.adr_eval_dispatch`), never inferred from the presence of scores — the same discipline the substance channel applies to judge verdicts (GHI #624). Nothing emits that receipt yet, so every scorecard truthfully reads SINGLE-DRIVER until the pool ADR's Target Scopes #5/#6 land; the channel populates then with no change here.

Persona doctrine reference: ADR-0.0.11-persona-driven-agent-identity-frames (Validated).

## Trust Model

**Layer 1 - Evidence Gathering.** This tool reads ADR documents and produces
evaluation scorecards. It does not modify ADR or brief content.

- **Reads:** ADR document, OBPI briefs, evaluation framework template
- **Writes:** `EVALUATION_SUBSTANCE.md` in the ADR directory (the judge's file;
  `EVALUATION_SCORECARD.md` is machine-owned and regenerated by the CLI)
- **Does NOT modify:** ADR content, brief content, registries, or ledgers

---

## Invocation

```text
/gz-adr-evaluate ADR-X.Y.Z             # evaluate a specific ADR
/gz-adr-evaluate ADR-X.Y.Z --red-team  # include the 10-challenge red-team protocol
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `adr_id` | Yes | ADR identifier (for example `ADR-0.13.0`) |
| `--red-team` | No | Include the 10-challenge adversarial review protocol |

---

## When to Use

- After drafting a new ADR and its OBPIs
- Before moving a Draft ADR to Proposed / human defense review
- When benchmarking the quality of an existing ADR package
- When you want a structured red-team pass against scope, evidence, and decomposition

---

## Procedure

### Step 1: Run CLI deterministic scoring (pre-screen)

```bash
uv run gz adr evaluate ADR-X.Y.Z
```

This produces structural quality scores (8 ADR dimensions, OBPI scores) and
writes an initial `EVALUATION_SCORECARD.md`.

**The CLI score is a pre-screen, never a gate.** The CLI uses pattern-matching
heuristics (keyword detection, section structure) that can under-score or
over-score dimensions when an ADR distributes content across non-standard
sections. Common false negatives:

- **Problem Clarity:** CLI looks for before/after language in Intent — misses
  ADRs that carry depth in Rationale or Agent Context Frame
- **Decision Justification:** CLI looks for numbered items in Decision — misses
  bullet-point decisions or justification distributed across Decision +
  Alternatives Considered

**Mandatory next step:** Always proceed to Step 2 regardless of CLI verdict.
The agent reads the ADR, analyzes every CLI dimension score for
false-positive and false-negative artifacts, and produces the authoritative
manual scorecard that supersedes the CLI pre-screen.

### Step 2: Locate the ADR and its OBPIs

1. Resolve the ADR document under `docs/design/adr/**/ADR-X.Y.Z-*/ADR-X.Y.Z-*.md`
2. List all OBPI briefs in `obpis/` (preferred) or `briefs/` (legacy)
3. Read the evaluation framework from `assets/ADR_EVALUATION_FRAMEWORK.md`
4. Read the CLI-generated `EVALUATION_SCORECARD.md` — note each dimension score
   and the CLI's stated findings for analysis in Step 3

### Step 3: Score ADR Quality (Part 1 - 8 Dimensions)

Read Part 1 of the framework and score the ADR on each dimension (1-4 scale):

| # | Dimension | Weight |
|---|-----------|--------|
| 1 | Problem Clarity | 15% |
| 2 | Decision Justification | 15% |
| 3 | Feature Checklist Completeness | 15% |
| 4 | OBPI Decomposition Quality | 15% |
| 5 | Lane Assignment Correctness | 10% |
| 6 | Scope Discipline | 10% |
| 7 | Evidence Requirements | 10% |
| 8 | Architectural Alignment | 10% |

For each dimension, work through the checklist items in the framework and score
based on how many checklist items pass with path-level evidence.

**CLI reconciliation (mandatory per dimension):** Compare the agent's manual
score against the CLI pre-screen score. When they differ, the scorecard MUST
document why — naming the specific CLI heuristic that misfired (false positive
or false negative) and the evidence that justifies the override. The manual
score is authoritative; the CLI score is recorded for traceability.

### Step 4: Score OBPI Quality (Part 2 - 5 Dimensions)

For each OBPI, score on 5 dimensions (1-4 scale):

| Dimension | Question |
|-----------|----------|
| Independence | Can this OBPI be completed without waiting for others? |
| Testability | Can completion be verified with commands? |
| Value | What concrete capability would be lost if this OBPI were removed? |
| Size | Is this a 1-3 day work unit? |
| Clarity | Could a different agent implement this without ambiguity? |

### Step 5: Run Red-Team Challenges (Optional - Part 3)

If `--red-team` is specified, or if the evaluator wants stronger adversarial
review, work through all 10 structured challenges from the framework.

Every challenge must be engaged. `N/A` is not acceptable.

### Step 6: Determine Verdict

Apply the framework thresholds:

| ADR Weighted Total | Verdict |
|--------------------|---------|
| >= 3.0 | **GO** - Ready for proposal/defense review |
| 2.5 - 3.0 | **CONDITIONAL GO** - Address weaknesses, then re-evaluate |
| < 2.5 | **NO GO** - Structural revision required |

**OBPI threshold:** Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.

**Red-team threshold:** <= 2 failures = GO, 3-4 = CONDITIONAL GO, >= 5 = NO GO.

### Step 7: Record Substance Scorecard

Write **`EVALUATION_SUBSTANCE.md`** in the ADR directory using the summary
template from the framework.

> **Never write `EVALUATION_SCORECARD.md` by hand (GHI #769).** That path is
> machine-owned: `gz adr evaluate` rewrites it wholesale on every run, so a
> judged scorecard authored there is destroyed by the next invocation. The two
> files measure different things and GHI #624 forbids compositing them — the
> split makes that separation structural instead of a warning banner the writer
> ignores. The closeout NO-GO gate reads this file first, so a recorded NO GO
> now survives regeneration.

Cite the CLI pre-screen for traceability rather than restating it as your own
finding. Include:

- CLI pre-screen verdict and weighted total (for traceability)
- All ADR dimension scores with weighted totals and rationale — when the
  manual score differs from the CLI score, state the CLI score, the manual
  score, and the specific heuristic mismatch that caused the divergence
- All OBPI dimension scores with averages
- Red-team challenge results when run
- Overall verdict (GO / CONDITIONAL GO / NO GO)
- Action items for any deficiencies

#### Low-Score Footer Guidance

When the ADR's weighted total is `< 3.0` AND the ADR has at least one tracking
anchor — a `GHI-<N>` parent, a tracking GHI referenced in frontmatter, or at
least one existing OBPI brief under the ADR — append a footer line to the
emitted scorecard:

```text
> Consider: uv run -m gzkit justify <parent-GHI-or-first-OBPI>
```

Substitute the concrete identifier. If both a tracking GHI and an OBPI exist,
prefer the GHI (the tracking conversation is broader than any single OBPI's
scope). If neither exists, do not append — the walkthrough requires a change
instance to resolve evidence against.

A weighted total below 3.0 is an invariant-11 trigger: the ADR's structural
weakness means implementing agents will land at <90% confidence on at least one
OBPI. The pre-execution walkthrough (`gz-justify` skill) surfaces the hidden
ambiguity before promotion. Skipping this footer on a `< 3.0` ADR is the
adjacent rationalization pattern the walkthrough exists to close.

### Step 8: Gate Decision

- **GO:** proceed to human proposal/defense review
- **CONDITIONAL GO:** revise the ADR or OBPIs, then re-run evaluation
- **NO GO:** return to authoring; do not proceed to proposal/defense

---

## External Red-Team Review

For adversarial review by a separate model:

1. Read the red-team model prompt from Part 4 of the framework
2. Copy the prompt and append the target ADR document
3. Send it to a separate model
4. Review the challenge report and address findings before proposal/defense

---

## Assets

- **Evaluation Framework:** `assets/ADR_EVALUATION_FRAMEWORK.md`
  - Part 1: ADR quality rubric (8 weighted dimensions)
  - Part 2: OBPI quality rubric (5 dimensions)
  - Part 3: Red-team challenge protocol (10 challenges)
  - Part 4: Red-team model prompt
  - Part 5: Scoring summary template

---

## Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Framework not found | `assets/ADR_EVALUATION_FRAMEWORK.md` missing | Repair skill directory structure |
| ADR not found | No ADR package matches the requested ID | Verify ADR exists and uses canonical naming |
| No OBPIs found | `obpis/` and `briefs/` are empty | ADR must have co-created OBPIs before evaluation |
| Scorecard not written | Path or permission error | Verify ADR directory is writable |
| NO GO verdict | ADR has structural deficiencies | Revise ADR and re-run evaluation before proposal/defense |

---

## Acceptance Rules

- All 8 ADR dimensions are scored with evidence-based rationale
- All OBPIs are scored on all 5 dimensions
- `EVALUATION_SUBSTANCE.md` is written to the ADR directory (never
  `EVALUATION_SCORECARD.md`, which the CLI regenerates — GHI #769)
- Verdict follows the threshold rules with no manual override
- `NO GO` blocks progression to human proposal/defense

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Authoring workflow that should invoke evaluation before proposal |
| `gz-adr-audit` | Post-completion audit; downstream phase |
| `gz-adr-closeout-ceremony` | Closeout occurs after implementation, not authoring |

---

## References

- Evaluation framework: `assets/ADR_EVALUATION_FRAMEWORK.md`
- ADR lifecycle: `docs/governance/GovZero/adr-lifecycle.md`
- GovZero charter: `docs/governance/GovZero/charter.md`
- Parity origin: `../airlineops/.github/skills/gz-adr-evaluate/SKILL.md`

---

## Related ADRs

- **ADR-0.0.19** — Pre-execution reasoning walkthrough. The Low-Score Footer
  Guidance section routes operators from a sub-3.0 evaluation into the
  `gz-justify` walkthrough so invariant 11 (<90% confidence → ask/justify) is
  surfaced before the ADR is promoted into active work.
