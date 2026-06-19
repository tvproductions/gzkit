# gz adr evaluate

Lint an ADR/OBPI package for **structural completeness** across 8 ADR dimensions and 5 OBPI dimensions, and surface a separate **substance** channel. Produces an `EVALUATION_SCORECARD.md` in the ADR directory. The deterministic score is a structural-completeness summary, **not** an authoritative quality or substance verdict (ADR-0.0.73, GHI #624).

---

## Usage

```bash
gz adr evaluate <adr_id> [--json] [--no-scorecard]
```

---

## Two channels, never composited

`gz adr evaluate` reports two separate channels with distinct labels. They measure
different things and must not be composited or compared as if commensurable — doing so
is the facade ADR-0.0.73 exists to close (GHI #624).

- **Structural completeness (deterministic).** Section presence, depth, counts, and
  references. A high structural score means the package is *structurally complete* — it
  does **not** mean the problem is clearly understood or the decision well justified.
- **Substance (judge-graded).** Whether the decision is genuinely sound is a semantic
  judgment no regex or word-count can make. Substance is graded **only** by a recorded,
  disciplined judge verdict (the record-and-validate judge flow — no live LLM call) and
  is reported **`UNGRADED`** absent one. It is never derived from the structural scores.

---

## What It Evaluates

### Structural completeness — ADR (8 weighted dimensions)

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

Every dimension is a **structural-completeness signal** — section presence, depth,
references. The dimension names are historical labels; they are NOT substance claims.
For example, dim-1 "Problem Clarity" rewards an Intent that is present, deep, and
concretely referenced — it does **not** judge whether the problem is clearly understood.
That substance judgment lives in the Substance channel below, or is `UNGRADED`.

### Substance — ADR (judge-graded channel)

| Dimension | Grade source |
|-----------|--------------|
| Problem Substance | recorded judge verdict, or `UNGRADED` |
| Decision Substance | recorded judge verdict, or `UNGRADED` |

A grade exists only when a disciplined judge verdict has been recorded (an
explanation-first rationale of >= 50 characters plus an `arb-step-judge-*` receipt).
Absent that, the dimension is `UNGRADED` — the evaluator never fabricates a substance
grade from the prose.

> **Forced downstream:** the full judge governance (leakage / output-discipline /
> meta-eval validators — ADR-0.0.40) that *populates* this channel is not yet built;
> until it lands, the substance channel is honestly `UNGRADED`.

### Structural completeness — OBPI (5 dimensions per brief)

| Dimension | Question |
|-----------|----------|
| Independence | Are cross-OBPI dependencies declared (structural signal)? |
| Testability | Are verification commands present? |
| Value | Is the Objective non-placeholder and of real length? |
| Size | Is the allowed-path count in a sane band? |
| Clarity | Are the required sections present and filled? |

### Scaffold Detection

Briefs containing template placeholders (`src/module/`, `First constraint`, etc.) are flagged and scored low. This catches auto-generated stubs that were never authored.

---

## Structural-Completeness Summary

| ADR Weighted Total | Summary |
|--------------------|---------|
| >= 3.0 | **STRUCTURALLY COMPLETE** |
| 2.5 - 3.0 | **STRUCTURAL GAPS** — address the structural action items |
| < 2.5 | **STRUCTURALLY INCOMPLETE** |

**OBPI threshold:** Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

This summary is about structural completeness only. It is **not** a quality/substance GO,
and must not be read as one or composited with a human substance review.

---

## When to Use

- After drafting a new ADR and its OBPIs — a structural-completeness lint before review
- Before moving a Draft ADR to Proposed / human defense review (alongside substance judgment)
- When checking an existing ADR package for structural gaps
- After populating OBPI briefs — verify scaffold is cleared

---

## Examples

```bash
# Lint a specific ADR for structural completeness
uv run gz adr evaluate ADR-0.3.0

# Machine-readable output (structural scores + substance channel)
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

- All structural-completeness dimension scores with weighted totals
- The substance channel (judge-graded grades or `UNGRADED`)
- All OBPI structural-completeness scores with averages
- A structural-completeness summary (not a quality verdict)
- Structural action items for any gaps

---

## Pipeline Enforcement

When a scorecard exists with a **STRUCTURALLY INCOMPLETE** summary, `gz obpi pipeline` Stage 1 treats it as a blocker and aborts — a structurally incomplete package is not ready for implementation. STRUCTURALLY COMPLETE and STRUCTURAL GAPS do not block. Missing scorecards do not block (the lint is optional until run). The structural summary is a *completeness* gate, never a substitute for the substance judgment a human (or the judge channel) makes.

---

## QC-Step Registration

`gz adr evaluate` self-registers as a QC step classified **`advisory`** (ADR-0.0.73,
GHI #624). It lints structure; it does **not** gate `gz check`'s exit code. Registering
it means the verification-layer mechanism this project introduces governs the evaluator
itself: `gz validate --qc-binding` classifies and audits it, so any regression to
presenting a shape-derived score as authoritative substance is a binding-mismatch
finding, never a silent pass. The advisory classification is why the evaluator is not
required to fail a negative-control fixture — only `bound` steps carry that obligation.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| `gz adr audit-check` | Post-implementation evidence verification (downstream) |
| `gz obpi validate` | Single-brief or batch authored/completion readiness check |
| `gz obpi validate --adr` | Batch-validate all briefs under an ADR |
| `gz adr report` | Status view without scoring |
