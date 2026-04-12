# /gz-adr-closeout-ceremony

Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.

---

## Purpose

`/gz-adr-closeout-ceremony` exposes the canonical gz-adr-closeout-ceremony workflow for operator invocation. Execute the ADR closeout ceremony by driving the CLI state machine.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-closeout-ceremony
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-closeout-ceremony/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-closeout-ceremony/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-closeout-ceremony/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
