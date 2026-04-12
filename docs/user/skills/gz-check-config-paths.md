# /gz-check-config-paths

Validate configured and manifest path coherence. Use when diagnosing control-surface or path drift.

---

## Purpose

`/gz-check-config-paths` exposes the canonical gz-check-config-paths workflow for operator invocation. Operate the gz check-config-paths command surface as a reusable governance workflow.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-check-config-paths/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-check-config-paths
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-check-config-paths/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-check-config-paths/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-check-config-paths/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-check-config-paths/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
