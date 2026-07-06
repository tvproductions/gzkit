# /gz-ontology

Image the governance shape with the read-only ontology sonar. Use to sweep the current structural shape, trace a node's lineage, diff versus the last sweep (the airlock re-sense gate), or read a node's downstream blast-radius before reasoning about lineage.

---

## Purpose

`/gz-ontology` exposes the canonical gz-ontology workflow for operator invocation. Wield the `gz ontology` read-only sonar (ADR-0.32.0) — a Tier-B derived projection, never authority — to image the actual shape of governance lineage instead of reasoning from stale docs.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-ontology/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-ontology
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-ontology/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-ontology/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-ontology/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-ontology/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [`gz ontology` manpage](../manpages/ontology.md) | Command reference |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
