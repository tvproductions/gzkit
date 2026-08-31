# /gz-deps-upgrade

Refresh global uv tools, Python 3.13.x runtime, `pyproject.toml` pins/floors, and `uv.lock` to current PyPI latest in one disciplined pass.

---

## Purpose

`/gz-deps-upgrade` exposes the canonical gz-deps-upgrade workflow for operator invocation. Performs a mechanical end-to-end refresh of the project's Python dependency surface — global uv tools, the 3.13.x runtime, pinned (`==`) dependencies, `>=` floors, and the lock file — then verifies via `gz check` and emits a canonical ARB unittest receipt as evidence per AGENTS.md § Attestation.

Trigger phrases: "update deps", "upgrade dependencies", "refresh uv.lock", "bump python", "deps to latest", "update pyproject".

## When to Use

Invoke this skill when the operator asks for any form of dependency-surface refresh — even when they don't name `uv` or `pyproject.toml` explicitly. Default tool when "update" / "upgrade" lands on Python tooling for this repo. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

Do not use for adding a new dependency — that requires a foundation-attested ADR per AGENTS.md § STDLIB-FIRST DOCTRINE.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-deps-upgrade/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-deps-upgrade
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-deps-upgrade/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-deps-upgrade/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-deps-upgrade/SKILL.md` | Codex mirror | Read |
| `pyproject.toml` | Pin/floor source of truth | Read/Write |
| `uv.lock` | Resolution snapshot | Read/Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [`/gz-check`](gz-check.md) | Quality gate invoked by step 8 of the upgrade |
| [`/gz-arb`](gz-arb.md) | Canonical receipt emission for the unittest evidence |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
