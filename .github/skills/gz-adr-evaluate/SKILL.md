---
name: gz-adr-evaluate
description: Post-authoring quality evaluation for ADRs and OBPIs. Scores ADRs on 8 weighted dimensions, OBPIs on 5 dimensions, and can run 10 structured red-team challenges before proposal/defense.
category: adr-lifecycle
compatibility: GovZero v6 framework; adapted from AirlineOps for gzkit ADR package layouts
metadata:
  skill-version: "6.1.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "lifecycle (pre-proposal QC), quality rubric, OBPI decomposition"
  govzero_layer: "Layer 1 - Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-13
---

# gz-adr-evaluate (v6.0.0)

## Purpose

Structured quality evaluation for ADRs and their OBPI decompositions. This
skill provides rubrics, challenge protocols, and a red-team prompt that form a
blocking QC step between ADR authoring and human proposal/defense review.

It can be invoked for newly authored ADRs or for retroactive evaluation of an
existing ADR package.

---

## Trust Model

**Layer 1 - Evidence Gathering.** This tool reads ADR documents and produces
evaluation scorecards. It does not modify ADR or brief content.

- **Reads:** ADR document, OBPI briefs, evaluation framework template
- **Writes:** `EVALUATION_SCORECARD.md` in the ADR directory
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

### Step 5: Determine Verdict

Apply the framework thresholds:

| ADR Weighted Total | Verdict |
|--------------------|---------|
| >= 3.0 | **GO** - Ready for proposal/defense review |
| 2.5 - 3.0 | **CONDITIONAL GO** - Address weaknesses, then re-evaluate |
| < 2.5 | **NO GO** - Structural revision required |

**OBPI threshold:** Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.

**Red-team threshold:** <= 2 failures = GO, 3-4 = CONDITIONAL GO, >= 5 = NO GO.

### Step 6: Record Scorecard

Write `EVALUATION_SCORECARD.md` in the ADR directory using the summary template
from the framework. This scorecard supersedes the CLI-generated pre-screen.
Include:

- CLI pre-screen verdict and weighted total (for traceability)
- All ADR dimension scores with weighted totals and rationale — when the
  manual score differs from the CLI score, state the CLI score, the manual
  score, and the specific heuristic mismatch that caused the divergence
- All OBPI dimension scores with averages
- Red-team challenge results when run
- Overall verdict (GO / CONDITIONAL GO / NO GO)
- Action items for any deficiencies

### Step 7: Gate Decision

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
- `EVALUATION_SCORECARD.md` is written to the ADR directory
- Verdict follows the threshold rules with no manual override
- `NO GO` blocks progression to human proposal/defense

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Authoring workflow that should invoke evaluation before proposal |
| `gz-adr-manager` | Compatibility alias that inherits `gz-adr-create` behavior |
| `gz-adr-check` | Evidence/coverage checks; different concern |
| `gz-adr-audit` | Post-completion audit; downstream phase |
| `gz-adr-closeout-ceremony` | Closeout occurs after implementation, not authoring |

---

## References

- Evaluation framework: `assets/ADR_EVALUATION_FRAMEWORK.md`
- ADR lifecycle: `docs/governance/GovZero/adr-lifecycle.md`
- GovZero charter: `docs/governance/GovZero/charter.md`
- Parity origin: `../airlineops/.github/skills/gz-adr-evaluate/SKILL.md`
