# /gz-patch-release

Orchestrate the GHI-driven patch release ceremony: draft narrative release notes, operator approval, RELEASE_NOTES update, git-sync, and GitHub release.

---

## Purpose

`/gz-patch-release` exposes the canonical gz-patch-release workflow for operator invocation. Orchestrate the GHI-driven patch release ceremony by drafting narrative release notes, presenting them to the operator for approval, and executing the release pipeline.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-patch-release/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-patch-release
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-patch-release/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-patch-release/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-patch-release/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-patch-release/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
