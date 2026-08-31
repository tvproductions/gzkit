# /gz-context-diet

Trim per-turn agent context weight by lifting pedagogical narrative from AGENTS.md, CLAUDE.md, and .claude/rules/** to docs/governance/, leaving binding bullets and one-line pointers behind.

---

## Purpose

`/gz-context-diet` is the trigger-discovery wrapper for the `instructions-files-diet` chore. The chore (`src/gzkit/chores/instructions-files-diet/CHORE.md`) is the source of truth for the procedure, acceptance criteria, and common rationalizations; this skill exists so the skill catalogue pattern-matches on operator language ("diet," "progressive disclosure," "trim contract weight") that the generic `gz-chore-runner` description does not surface.

## When to Use

Invoke this skill when the per-turn contract surface (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, skill bodies) has accreted multi-paragraph rationale and "Why this is canon" codas that the agent does not need on every turn, or when the advisory scorecard surfaces Judgment-class duplicates that can be folded into Mechanical neighbors. The lift target is `docs/governance/`; the per-turn surface keeps binding bullets plus one-line pointers.

This is **not** a substitute for reading the chore. The agent must read `CHORE.md` before acting; the skill body below only routes there.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-context-diet/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-context-diet
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-context-diet/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-context-diet/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-context-diet/SKILL.md` | Codex mirror | Read |
| `src/gzkit/chores/instructions-files-diet/CHORE.md` | Underlying chore procedure | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [`/gz-chore-runner`](gz-chore-runner.md) | Generic chore execution surface |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
