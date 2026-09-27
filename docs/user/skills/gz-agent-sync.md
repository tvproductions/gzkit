# /gz-agent-sync

Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates.

---

## Purpose

`/gz-agent-sync` exposes the canonical gz-agent-sync workflow for operator invocation. It runs `gz agent sync control-surfaces`, which regenerates every derived control surface (vendor skill, rule and persona mirrors, AGENTS.md, CLAUDE.md, settings, manifest, Codex files) from `.gzkit/` canon, refusing when canonical skills fail its preflight.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-agent-sync/SKILL.md` (mirrored into `.claude/skills/` and `.agents/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-agent-sync
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-agent-sync/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-agent-sync/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-agent-sync/SKILL.md` | Codex mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
