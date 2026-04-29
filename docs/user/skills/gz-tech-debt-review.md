# /gz-tech-debt-review

Survey the codebase for technical debt and recommend resolutions. Synthesizes signals from existing gzkit chores, audits, and complexity tools (xenon, radon, ruff, ty, gz cli audit, gz validate, gz-pythonic-pattern-detect, doc-coverage, dependency-currency) into a single prioritized debt report with file:line evidence and recommended fixes.

---

## Purpose

`/gz-tech-debt-review` exposes the canonical gz-tech-debt-review workflow for operator invocation. Distinct from `/gz-obpi-simplify` (which fixes craft inside an active OBPI scope) and `/gz-check` (which gates a single change) — this skill produces a *report* across many debt classes that the operator can route into GHIs, OBPIs, or chores.

## When to Use

Invoke this skill when the operator asks to "review code for tech debt", "find tech debt", "audit the codebase for debt", "what's rotting", "where is the debt", or wants a debt assessment for an ADR/OBPI scope or a touched-files set. Also use proactively when an operator asks "what should we clean up next" or "is there debt accumulating in X".

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-tech-debt-review/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-tech-debt-review
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-tech-debt-review/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-tech-debt-review/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-tech-debt-review/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-tech-debt-review/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-obpi-simplify`](gz-obpi-simplify.md) | OBPI-scoped craft review (fixes inside active scope) |
| [`/gz-check`](gz-check.md) | Single-change quality gate |
| [`/gz-pythonic-pattern-detect`](gz-pythonic-pattern-detect.md) | Pythonic-pattern refactor candidates |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
