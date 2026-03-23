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

## Related Commands

| Command | Relationship |
|---------|--------------|
| `gz adr audit-check` | Post-implementation evidence verification (downstream) |
| `gz obpi validate` | Single-brief or batch completion readiness check |
| `gz obpi validate --adr` | Batch-validate all briefs under an ADR |
| `gz adr report` | Status view without scoring |
