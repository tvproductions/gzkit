# /gz-adr-evaluate

Post-authoring quality evaluation for ADRs and OBPIs. Scores ADRs on 8 weighted dimensions, OBPIs on 5 dimensions, and can run 10 structured red-team challenges before proposal/defense.

---

## Purpose

`/gz-adr-evaluate` exposes the canonical gz-adr-evaluate workflow for operator invocation. Structured quality evaluation for ADRs and their OBPI decompositions. This skill provides rubrics, challenge protocols, and a red-team prompt that form a blocking QC step between ADR authoring and human proposal/defense review.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-evaluate/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-evaluate
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-evaluate/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-evaluate/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-evaluate/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-evaluate/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
