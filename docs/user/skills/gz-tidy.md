# /gz-tidy

Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations.

---

## Purpose

`/gz-tidy` exposes the canonical gz-tidy workflow for operator invocation. It runs the read-only `gz tidy` report (validation issues, orphaned OBPIs, settings vault, ADRs pending attestation), routes each finding to its repair or to the operator, regenerates control surfaces with `--fix`, and in Claude Code checks hooks, the instructions budget and skill mirror parity.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-tidy/SKILL.md` (mirrored into `.claude/skills/` and `.agents/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-tidy
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-tidy/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-tidy/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-tidy/SKILL.md` | Codex mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
