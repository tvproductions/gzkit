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
last_reviewed: 2026-04-04
---

# gz-adr-evaluate (v6.1.0)

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

The CLI and the agent have different jobs. The CLI is a deterministic tool —
it applies structural checks and does not drift. The agent reasons — it reads
the ADR as a whole, connects evidence across documents, catches what a parser
cannot, and produces prose analysis that a downstream agent can act on.

The CLI provides the scores. The agent provides the understanding.

### Step 1: CLI Deterministic Scoring

```bash
uv run gz adr evaluate ADR-X.Y.Z
```

This scores all 8 ADR dimensions and all OBPI dimensions, writes
`EVALUATION_SCORECARD.md`, and emits a verdict (GO / CONDITIONAL GO / NO GO).

### Step 2: Read the ADR Package and Annotate Every Dimension

Read the full ADR, all OBPI briefs, and the evaluation framework. Then
annotate every CLI dimension score — not to re-score, but to provide the
prose analysis and evidence references that a structural parser cannot.

For each dimension, the agent writes:

- **Analytical reasoning**: Why this score is correct (or why it should be
  overridden). This is the primary value — the agent's prose analysis of how
  the ADR's content earns or fails to earn the score. Connect evidence across
  the ADR, briefs, and codebase. Name what is strong, what is weak, and why.
- **Evidence references**: File paths, line numbers, and section headings that
  support the analysis. These are receipts — they let a downstream agent
  locate the source material. They serve the analysis, not the other way
  around.
- **Overrides**: When the agent's reasoning contradicts the CLI score, record
  the override with the analytical justification and the evidence the CLI's
  parser missed.

The CLI will not drift — trust its structural checks. The agent can reason —
use that to catch what structure alone misses. If annotation reveals that a
CLI score is wrong, override it. If annotation confirms the CLI, say why
the score holds and what specifically in the ADR earns it.

**On CONDITIONAL GO / NO GO**: The same annotation process applies, but the
agent pays special attention to the flagged dimensions. On NO GO, fall back
to the full scoring rubric (Parts 1 and 2 of the framework) for a complete
manual assessment.

### Step 3: Exemplar Comparison (Mandatory)

Select the strongest validated ADR in the same track (foundation or feature).
Prefer an ADR in the same domain lineage when one exists.

Read the exemplar ADR. Produce a structural comparison:

1. **What the exemplar has that the target lacks** — name specific structural
   elements (evidence ledger, failure narrative, supersession tracking, etc.),
   not subjective quality differences.
2. **What the target improves over the exemplar** — name specific structural
   elements.
3. **Structural verdict** — one sentence: does the target meet, exceed, or fall
   short of the exemplar's template discipline?

This comparison must reference concrete sections, not hand-wave. If you cannot
name specific elements, you have not read the exemplar.

### Step 4: Red-Team Challenges (When Requested)

Run all 10 structured challenges from Part 3 of the framework.

Every challenge must be engaged. `N/A` is not acceptable.

### Step 5: Record Scorecard

Write `EVALUATION_SCORECARD.md` in the ADR directory.

**Richness mandate:** The scorecard is a knowledge artifact for downstream
agents. The evaluating agent has full context loaded — ADR, OBPIs, exemplar,
codebase, framework — and MUST capture that context exhaustively so no
downstream agent needs to re-read the source material.

Richness lives in two layers:

1. **Prose analysis** — the agent's reasoning about what the ADR does well,
   where it is weak, how its pieces connect, and why scores are earned. This
   is the primary value. A downstream agent reads the analysis to understand
   the ADR's quality and make decisions. The prose should be substantive —
   it explains, connects, and concludes.

2. **Evidence references** — file paths, line numbers, section headings,
   cross-references between documents. These are receipts. They let a
   downstream agent verify claims and locate source material. They support
   the prose analysis; they do not replace it.

Both layers must be present for every dimension, every OBPI, every
comparison, and every advisory item. Prose without references is
unverifiable. References without prose is a database dump. The scorecard
needs both.

A downstream agent reading only the scorecard should be able to:

- Understand every score through the evaluator's analytical reasoning
- Locate every claim in source material by file path and line number
- Understand the dependency graph between OBPIs with file-path evidence
- Know which codebase paths each OBPI will touch and whether they exist
- Understand how the ADR compares to the exemplar at the section level
- Act on advisory items without further investigation

The scorecard has 4 sections regardless of CLI verdict:

**Section 1 — Header & CLI Scores with Analytical Annotation**

Record the CLI verdict, weighted total, and per-dimension scores. For EVERY
dimension, provide both layers:

- **Prose analysis** (primary): Why this score is earned. What in the ADR
  is strong, what connects across documents, what a downstream agent needs
  to understand about this dimension's quality. For overrides: the
  analytical reasoning for why the CLI was wrong — what it missed and why
  the agent's reading reaches a different conclusion.
- **Evidence references** (receipt): ADR section headings + line ranges,
  OBPI brief cross-references with file paths, codebase files that confirm
  architectural claims. These let a downstream agent verify the analysis.

**Section 2 — OBPI Evidence Map**

For EVERY OBPI, record exhaustively:

- Brief file path
- Lane and justification (from brief, with line reference)
- Declared dependencies (with OBPI file paths and the STOP-on-BLOCKERS
  line reference for each dep)
- Parent ADR checklist item (exact text + line number)
- All acceptance criteria (REQ IDs, brief line range)
- All verification commands (from brief, with line range)
- All allowed paths (from brief, with line range) with confirmation that
  those paths exist in the codebase or are expected-new
- All denied paths (from brief, with line range)
- Key requirements (MUST/NEVER/ALWAYS rules with brief line references)
- Pattern-to-follow references (from brief Discovery Checklist)
- Heavy lane gate obligations (Gate 3/4/5 sections with line refs)
- Cross-references to ADR Rationale sections that inform the OBPI's
  design (ADR heading + line range)
- Cross-references to related OBPIs (file paths)

**Section 3 — Exemplar Comparison**

From Step 3. Every structural element named must include file path and
section heading from both the exemplar and target ADR. Name specific line
ranges, not just section names. Explain WHY each difference matters for
a downstream agent or reviewer.

**Section 4 — Verdict & Advisory Items**

Final verdict with adjusted weighted total if overrides exist. Advisory
items with specific file:line references, recommended actions, and which
downstream agent or workflow the advisory applies to (implementer,
reviewer, closeout ceremony, etc.).

### Step 6: Gate Decision

| Verdict | Action |
|---------|--------|
| **GO** | Proceed to human proposal/defense review |
| **CONDITIONAL GO** | Revise flagged items, then re-run evaluation |
| **NO GO** | Return to authoring; do not proceed to proposal/defense |

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

- CLI deterministic scoring runs first and is authoritative unless overridden
- Manual assessment is scoped to CLI-flagged dimensions, not a full re-score
- Exemplar comparison names concrete structural elements from the exemplar ADR
- `EVALUATION_SCORECARD.md` is written to the ADR directory
- Scorecard is exhaustive regardless of CLI verdict (richness mandate)
- Verdict follows threshold rules; manual overrides require one-line justification
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
