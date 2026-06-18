# gz adr evaluate

Evaluate ADR and OBPI quality using deterministic scoring across 8 ADR dimensions and 5 OBPI dimensions. Produces an `EVALUATION_SCORECARD.md` in the ADR directory with a GO / CONDITIONAL GO / NO GO verdict.

---

## Usage

```bash
gz adr evaluate <adr_id> [--json] [--no-scorecard]
```

---

## What It Evaluates

### ADR Quality (8 weighted dimensions)

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

#### Substance grading, not shape (dim-1 / dim-2)

Problem Clarity and Decision Justification grade decision **substance**, never prose
shape or keyword presence (ADR-0.0.73, GHI #624). A score is never satisfiable by
keyword or format presence alone, and rigorous prose phrased without the conventional
keywords is not floored:

- **Problem Clarity** rewards an Intent with substantive depth, concrete grounding
  (code spans, file paths, `GHI #`/`ADR-`/`OBPI-` references), and an articulated
  problem-and-outcome contrast — not the literal words "before"/"after".
- **Decision Justification** rewards a Decision with substantive depth, explicitly
  **weighed-and-rejected** alternatives, and **honest negative consequences** — not a
  markdown numbered list or the literal word "because".

A facade ADR that stuffs the old keywords no longer scores high; a rigorous ADR phrased
differently no longer scores 1.

### OBPI Quality (5 dimensions per brief)

| Dimension | Question |
|-----------|----------|
| Independence | Can this OBPI be completed without waiting for others? |
| Testability | Can completion be verified with commands? |
| Value | What concrete capability would be lost if removed? |
| Size | Is this a 1-3 day work unit? |
| Clarity | Could a different agent implement this without ambiguity? |

### Scaffold Detection

Briefs containing template placeholders (`src/module/`, `First constraint`, etc.) are flagged and scored low on the value dimension. This catches auto-generated stubs that were never authored.

---

## Verdict Thresholds

| ADR Weighted Total | Verdict |
|--------------------|---------|
| >= 3.0 | **GO** — Ready for proposal/defense review |
| 2.5 - 3.0 | **CONDITIONAL GO** — Address weaknesses, then re-evaluate |
| < 2.5 | **NO GO** — Structural revision required |

**OBPI threshold:** Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

---

## When to Use

- After drafting a new ADR and its OBPIs — quality gate before proposal
- Before moving a Draft ADR to Proposed / human defense review
- When benchmarking the quality of an existing ADR package
- After populating OBPI briefs — verify scaffold is cleared

---

## Examples

```bash
# Evaluate a specific ADR
uv run gz adr evaluate ADR-0.3.0

# Machine-readable output
uv run gz adr evaluate ADR-0.3.0 --json

# Skip writing the scorecard file
uv run gz adr evaluate ADR-0.3.0 --no-scorecard
```

---

## Options

| Option | Description |
|--------|-------------|
| `adr_id` | ADR identifier (e.g., `ADR-0.3.0`) |
| `--json` | Emit machine-readable output |
| `--no-scorecard` | Skip writing `EVALUATION_SCORECARD.md` to the ADR directory |

---

## Output

Writes `EVALUATION_SCORECARD.md` in the ADR package directory containing:

- All ADR dimension scores with weighted totals
- All OBPI dimension scores with averages
- Overall verdict (GO / CONDITIONAL GO / NO GO)
- Action items for any deficiencies

---

## Pipeline Enforcement

When a scorecard exists with a **NO GO** verdict, `gz obpi pipeline` Stage 1 treats it as a blocker and aborts. This makes the evaluation a blocking gate for pipeline execution — run `gz adr evaluate` before starting OBPI work, and address NO GO action items before invoking the pipeline.

GO and CONDITIONAL GO verdicts do not block. Missing scorecards do not block (evaluation is optional until run).

---

## QC-Step Registration

`gz adr evaluate` self-registers as a QC step classified **`advisory`** (ADR-0.0.73,
GHI #624). It grades quality; it does **not** gate `gz check`'s exit code. Registering
it means the verification-layer mechanism this project introduces governs the evaluator
itself: `gz validate --qc-binding` classifies and audits it like any other QC step, so a
shape-graded score presented as authoritative truth is a binding-mismatch finding, never
a silent pass. The advisory classification is why the evaluator is not required to fail a
negative-control fixture — only `bound` steps carry that obligation.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| `gz adr audit-check` | Post-implementation evidence verification (downstream) |
| `gz obpi validate` | Single-brief or batch authored/completion readiness check |
| `gz obpi validate --adr` | Batch-validate all briefs under an ADR |
| `gz adr report` | Status view without scoring |
