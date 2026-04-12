# /gz-obpi-simplify

OBPI-scoped code review for reuse, quality, and efficiency. Resolves scope from the brief's Allowed Paths, reviews across three dimensions, and applies fixes. Use after implementation, before reconcile.

---

## Purpose

`/gz-obpi-simplify` exposes the canonical gz-obpi-simplify workflow for operator invocation. OBPI-scoped code review: resolve scope from the brief, review across three dimensions (reuse, quality, efficiency), fix issues found.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-obpi-simplify/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-obpi-simplify
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-obpi-simplify/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-obpi-simplify/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-obpi-simplify/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-obpi-simplify/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
