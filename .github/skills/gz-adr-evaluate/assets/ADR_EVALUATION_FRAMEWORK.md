<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR And OBPI Evaluation Framework

**Purpose:** Structured rubric for evaluating ADR and OBPI quality in gzkit and
other GovZero-governed repositories. Usable by humans for self-review and by AI
models for adversarial ("red-team") assessment.

**Version:** 1.0
**Date:** 2026-03-13
**Last reviewed:** 2026-03-13

---

## How To Use This Framework

### For Self-Review

Work through Part 1 (ADR rubric) and Part 2 (OBPI rubric), scoring each
dimension. A well-formed ADR should score 3+ on every dimension. Any dimension
scoring 1 indicates a structural defect that must be addressed before the ADR
moves to Proposed / human defense review.

### For Red-Team Review

Give the target ADR document and Part 3 (Red-Team Protocol) to a separate AI
model with the prompt in Part 4. The red-team model produces a structured
challenge report that the ADR author must address.

---

## Part 1: ADR Quality Rubric

Score each dimension 1-4:

| Score | Meaning |
|-------|---------|
| 4 | Exemplary - could serve as a template for future ADRs |
| 3 | Solid - meets all requirements, no material gaps |
| 2 | Adequate - meets minimum requirements but has weaknesses |
| 1 | Deficient - structural gap that must be addressed |

### Dimension 1: Problem Clarity (Weight: 15%)

**Question:** Is the problem specific, measurable, and compelling?

| Score | Criteria |
|-------|----------|
| 4 | Problem is quantified, before/after state is concrete, and the "so what?" is immediately obvious |
| 3 | Problem is well-defined with clear before/after, reader understands why this matters |
| 2 | Problem is stated but vague, before/after unclear |
| 1 | Problem is missing or purely aspirational |

**Checklist:**

- [ ] Can you state the problem in one sentence without jargon?
- [ ] Is there a concrete "before" state with evidence?
- [ ] Is there a concrete "after" state that is testable?
- [ ] Does the "so what?" test pass?
- [ ] Is the problem explicitly scoped?

### Dimension 2: Decision Justification (Weight: 15%)

**Question:** Are decisions defensible with evidence, not just assertion?

| Score | Criteria |
|-------|----------|
| 4 | Each decision cites precedent, names alternatives, and explains why the chosen approach wins |
| 3 | Decisions are justified with rationale, alternatives acknowledged |
| 2 | Decisions are stated but rationale is thin or circular |
| 1 | Decisions are asserted without justification |

**Checklist:**

- [ ] Does each numbered decision have an independent "why"?
- [ ] Are alternatives named and dismissed with specific reasons?
- [ ] Do decisions reference existing patterns or exemplars in the codebase?
- [ ] Are counterarguments addressed?
- [ ] Are decisions internally consistent?

### Dimension 3: Feature Checklist Completeness (Weight: 15%)

**Question:** Does every checklist item earn its place, and is anything missing?

| Score | Criteria |
|-------|----------|
| 4 | Every item is necessary, sufficient, and independently valuable |
| 3 | All items are justified and coverage appears complete |
| 2 | Some items feel redundant or visible gaps remain |
| 1 | Items are padding or major gaps exist |

**Checklist:**

- [ ] For each item: if removed, what specific capability would be lost?
- [ ] Is there a needed capability that no checklist item delivers?
- [ ] Are items at consistent granularity?
- [ ] Does each item map to a testable deliverable?
- [ ] Are items ordered logically?

### Dimension 4: OBPI Decomposition Quality (Weight: 15%)

**Question:** Is each OBPI a meaningful, independently completable work unit?

| Score | Criteria |
|-------|----------|
| 4 | Each OBPI can be implemented, tested, and reviewed independently; no OBPI is trivially small or overwhelmingly large |
| 3 | OBPIs are reasonable work units with clear boundaries |
| 2 | Some OBPIs are too large, too small, or arbitrarily grouped |
| 1 | OBPIs are monolithic or atomized to absurdity |

**Checklist:**

- [ ] Can each OBPI be assigned to a different agent and completed independently?
- [ ] Is each OBPI a 1-3 day work unit?
- [ ] Do groupings follow domain boundaries?
- [ ] Is the dependency graph acyclic with clear parallelization?
- [ ] Does numbering have no gaps?

### Dimension 5: Lane Assignment Correctness (Weight: 10%)

**Question:** Are Heavy/Lite assignments defensible per `AGENTS.md`?

| Score | Criteria |
|-------|----------|
| 4 | Every assignment is justified with specific criteria |
| 3 | Assignments are correct with brief rationale |
| 2 | Assignments are present but some are debatable |
| 1 | Assignments are missing or clearly wrong |

**Checklist:**

- [ ] Does every Heavy OBPI touch an external contract?
- [ ] Is every Lite OBPI truly internal-only?
- [ ] Are Gate 3/4/5 obligations acknowledged for Heavy work?

### Dimension 6: Scope Discipline (Weight: 10%)

**Question:** Are boundaries clear and non-goals explicit?

| Score | Criteria |
|-------|----------|
| 4 | Non-goals are specific and tested against plausible creep scenarios |
| 3 | Non-goals are stated and scope is clear |
| 2 | Scope is implied but not explicitly bounded |
| 1 | Scope is unbounded |

**Checklist:**

- [ ] Can you name three explicit non-goals?
- [ ] Is the argument for excluding them documented?
- [ ] Is the ADR self-contained rather than dependent on unspecified future work?
- [ ] Are guardrails stated to prevent scope expansion?

### Dimension 7: Evidence Requirements (Weight: 10%)

**Question:** Is "done" operationally defined for each OBPI?

| Score | Criteria |
|-------|----------|
| 4 | Each OBPI has concrete verification commands that CI could run |
| 3 | Verification approach is clear with specific commands or checks |
| 2 | "Done" is described but verification is vague |
| 1 | No verification criteria are specified |

**Checklist:**

- [ ] Could you write a `bash` script that verifies each OBPI is done?
- [ ] Are the quality gates specified per OBPI?
- [ ] For Heavy OBPIs, are Gate 3/4/5 criteria explicit?

### Dimension 8: Architectural Alignment (Weight: 10%)

**Question:** Does this ADR follow established codebase patterns?

| Score | Criteria |
|-------|----------|
| 4 | Every technical decision references a local precedent; novel patterns are justified |
| 3 | ADR follows established patterns and names integration points |
| 2 | ADR is generally consistent but some decisions drift |
| 1 | ADR introduces novel patterns without justification |

**Checklist:**

- [ ] Does the ADR reference exemplar files?
- [ ] Are integration points listed with module paths?
- [ ] Are anti-patterns named with explicit "what wrong looks like" examples?
- [ ] Do guardrails prevent known mistakes?

---

## Part 2: OBPI Quality Rubric

Apply to each OBPI individually. Score 1-4 on each dimension.

### OBPI Dimension A: Independence

**Question:** Can this OBPI be completed without waiting for others except
declared dependencies?

| Score | Criteria |
|-------|----------|
| 4 | Fully independent |
| 3 | Depends only on declared predecessors |
| 2 | Has undeclared dependencies |
| 1 | Cannot be started without most other OBPIs first |

### OBPI Dimension B: Testability

**Question:** Can completion be verified with commands?

| Score | Criteria |
|-------|----------|
| 4 | A single command proves completion |
| 3 | A small set of commands verifies completion |
| 2 | Verification requires manual inspection |
| 1 | No clear way to verify completion |

### OBPI Dimension C: Value

**Question:** What would be lost if this OBPI were removed?

| Score | Criteria |
|-------|----------|
| 4 | Removing it leaves a visible capability gap |
| 3 | Removing it weakens the ADR noticeably |
| 2 | Removing it is mildly inconvenient |
| 1 | Removing it would not be noticed |

### OBPI Dimension D: Size

**Question:** Is this a 1-3 day work unit?

| Score | Criteria |
|-------|----------|
| 4 | Clearly scoped to 1-3 days of focused work |
| 3 | Reasonable size, might push to 4 days |
| 2 | Too large or too small |
| 1 | Trivial or massive |

### OBPI Dimension E: Clarity

**Question:** Could a different agent implement this without ambiguity?

| Score | Criteria |
|-------|----------|
| 4 | Two agents would likely produce similar implementations |
| 3 | Clear enough with minor interpretation needed |
| 2 | Significant ambiguity |
| 1 | So vague that implementation is unpredictable |

---

## Part 3: Red-Team Challenge Protocol

Every challenge must be engaged. `N/A` is not acceptable.

### Challenge 1: The "So What?" Test

For each Feature Checklist item, ask:

> "If we removed item [N], what specific capability would the repository,
> runtime, or governance workflow lack that it needs?"

**Pass criteria:** Every item has a concrete answer. "It would be less
complete" fails.

### Challenge 2: The Scope Challenge

Ask both directions:

> "Name something NOT in scope that arguably SHOULD be. Why was it excluded?"

> "Name something IN scope that arguably SHOULDN'T be. Why was it included?"

**Pass criteria:** Both inclusions and exclusions are justified with specific
reasoning.

### Challenge 3: The Alternative Challenge

> "Could this ADR achieve its goals with fewer OBPIs? Which could be merged
> without loss? Could it be done with more OBPIs? Which are too large and
> should be split?"

**Pass criteria:** The current decomposition is defended as the right
granularity, or legitimate merge/split suggestions are acknowledged.

### Challenge 4: The Dependency Challenge

> "If OBPI [N] fails or is blocked, which downstream OBPIs are affected?
> Is there a single point of failure in the dependency graph?"

**Pass criteria:** The dependency graph is resilient and explicitly understood.

### Challenge 5: The Gold Standard Challenge

> "How does this ADR compare structurally to the strongest validated ADR in this
> repository? What does that exemplar have that this lacks? What does this ADR
> improve?"

**Pass criteria:** Specific structural strengths and weaknesses are named
against a real local exemplar.

### Challenge 6: The Timeline Challenge

> "What is the critical path through the OBPI dependency graph? How many OBPIs
> can run in parallel? What is the theoretical minimum wall-clock time?"

**Pass criteria:** The critical path and parallelization stages are explicit.

### Challenge 7: The Evidence Challenge

> "For OBPI [N], write the exact commands that prove it is done. If you cannot
> write specific commands, the OBPI is underspecified."

**Pass criteria:** Every OBPI has at least one concrete verification command.

### Challenge 8: The Consumer Challenge

> "A maintainer or operator reads this ADR. What questions would they still
> have about whether the change is actually ready for use?"

**Pass criteria:** The ADR addresses the primary concerns of its intended
consumer.

### Challenge 9: The Regression Challenge

> "Six months after this ADR is Validated, what could silently break without
> detection? What monitoring or contract ensures it stays valid?"

**Pass criteria:** The ADR addresses long-term validity, not only initial
completion.

### Challenge 10: The Parity Challenge

> "If this ADR claims parity, compatibility, or doctrine alignment, pick the
> weakest claim and argue why it does NOT actually hold."

**Pass criteria:** The author can defend the claim or acknowledge remaining
gaps with a remediation plan.

---

## Part 4: Red-Team Model Prompt

Copy the following prompt and give it to a separate AI model along with the
target ADR document.

### RED-TEAM PROMPT

```text
You are a critical technical reviewer ("red team") evaluating an Architecture
Decision Record (ADR) for the gzkit project. Your job is to find weaknesses,
gaps, and unjustified claims.

CONTEXT:
- gzkit is a GovZero-governed Python 3.13+ project
- ADRs define repository capabilities, runtime contracts, governance surfaces,
  and implementation decomposition via OBPIs
- Heavy work changes external contracts such as CLI, API, schema, or operator
  behavior and therefore carries stronger evidence and human-attestation duties
- The target of this review is structural quality, not whether the ADR is
  optimistic or aesthetically pleasing

YOUR TASK:
Read the ADR document below and produce a structured challenge report with:

1. PROBLEM ASSESSMENT
   - Is the problem real and concretely stated?
   - Does the before/after claim hold up?
   - Would a skeptic agree this ADR is necessary now?

2. DECISION CHALLENGES
   - What alternative was not considered?
   - What is the strongest argument against each decision?
   - Are decisions supported by evidence or by assertion?

3. FEATURE CHECKLIST AUDIT
   - For each checklist item: if removed, what breaks?
   - Are any items redundant?
   - Is anything missing?

4. OBPI DECOMPOSITION CRITIQUE
   - Which OBPIs are too large or too small?
   - Which groupings feel arbitrary versus domain-driven?
   - Are there undeclared dependencies?
   - Could the total OBPI count be reduced without losing capability?

5. LANE ASSIGNMENT REVIEW
   - Any Heavy OBPI that should be Lite?
   - Any Lite OBPI that should be Heavy?
   - Are Gate 3/4/5 obligations correctly understood?

6. SCOPE BOUNDARY STRESS TEST
   - Name 3 things not in scope that arguably should be
   - Name 1 thing in scope that arguably should not be
   - Where is scope creep likely?

7. RISK ASSESSMENT
   - What is the biggest risk to successful completion?
   - What is the most likely failure mode?
   - Is there a single point of failure in the dependency graph?

8. CONSUMER PERSPECTIVE
   - What unanswered questions would a maintainer or operator still have?
   - Could this ADR pass all gates and still leave the capability unready?

9. COMPARISON TO REPOSITORY EXEMPLAR
   - How does this compare structurally to the strongest validated ADR in the repo?
   - What does that exemplar have that this lacks?
   - What improvement does this ADR make over that exemplar?

10. OVERALL VERDICT
    - GO: ADR is ready for proposal/defense review
    - CONDITIONAL GO: Ready with specific changes listed
    - NO GO: Structural issues must be resolved first
    - Provide specific, actionable recommendations

FORMAT:
- Be specific, not vague. Name OBPI numbers, checklist items, and sections.
- Support criticisms with reasoning, not just assertion.
- Acknowledge strengths as well as weaknesses.
- Conclude with a ranked list of the top 3 issues to address.

ADR DOCUMENT:
[Paste the ADR document here]
```

---

## Part 5: Scoring Summary Template

Use this template to record evaluation results.

```text
ADR EVALUATION SCORECARD
═══════════════════════════

ADR: [ADR number and title]
Evaluator: [human / model name]
Date: [YYYY-MM-DD]

─── ADR-Level Scores ───────────────────────────

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | | |
| 2 | Decision Justification | 15% | | |
| 3 | Feature Checklist | 15% | | |
| 4 | OBPI Decomposition | 15% | | |
| 5 | Lane Assignment | 10% | | |
| 6 | Scope Discipline | 10% | | |
| 7 | Evidence Requirements | 10% | | |
| 8 | Architectural Alignment | 10% | | |

WEIGHTED TOTAL: ___/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

─── OBPI-Level Scores ──────────────────────────

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | | | | | | |
| 02 | | | | | | |
| ... | | | | | | |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on
any dimension must be revised.

─── Red-Team Challenges ────────────────────────

| # | Challenge | Result (Pass/Fail) | Notes |
|---|-----------|-------------------|-------|
| 1 | So What? | | |
| 2 | Scope | | |
| 3 | Alternative | | |
| 4 | Dependency | | |
| 5 | Gold Standard | | |
| 6 | Timeline | | |
| 7 | Evidence | | |
| 8 | Consumer | | |
| 9 | Regression | | |
| 10 | Parity | | |

RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO

─── Overall Verdict ────────────────────────────

[ ] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

ACTION ITEMS:
1. [specific item]
2. [specific item]
3. [specific item]
```
