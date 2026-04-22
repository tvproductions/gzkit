# /gz-justify

Pre-execution reasoning walkthrough for GHIs, OBPIs, and drafts. Invoke before implementation when confidence is <90%, when a gz-adr-evaluate score lands below 3.0, or when scope boundaries feel ambiguous. The CLI renders an 8-section markdown scaffold pre-populated with anchor evidence; you fill each `_[To be filled]_` block with grounded reasoning cited from the gathered evidence, then commit or attach the filled artifact to downstream governance.

---

## Purpose

`/gz-justify` exposes the canonical gz-justify workflow for operator invocation. It is the operator-facing ritual for Prime Directive invariant 11: when self-reported confidence in a planned change is below 90%, the walkthrough turns "I should think about this more" into an artifact that can be cited, reviewed, and validated.

## When to Use

Invoke this skill when your self-reported confidence in a planned implementation is <90%, after a `gz-adr-evaluate` run scores below 3.0 on an ADR with a tracking GHI or OBPI, before promoting a pool ADR into active work, or mid-pipeline when scope feels ambiguous. The `gz-adr-evaluate` skill's Low-Score Footer Guidance and the `gz-obpi-pipeline` skill's Stage 1→2 Confidence Gate both route operators here automatically.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-justify/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, scaffold filling rules, and round-trip validation procedure.

## Invocation

```text
/gz-justify
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `<anchor>` | Yes (or `--draft`) | GHI / OBPI identifier to reason about |
| `--save` | No | Persist to `artifacts/justify/<slug>-<timestamp>.md` |
| `--output <path>` | No | Persist to an explicit path |
| `--draft <text>` / `--draft-slug <slug>` | No | Literal draft passthrough |
| *(see SKILL.md)* | — | Full flag set is defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-justify/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-justify/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-justify/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-justify/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-adr-evaluate`](gz-adr-evaluate.md) | Low-score footer routes to `gz-justify` |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Stage 1→2 Confidence Gate routes to `gz-justify` |
| [`/gz-plan-audit`](gz-plan-audit.md) | Downstream consumer — filled walkthrough is plan-receipt evidence |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
