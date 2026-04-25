# CHORE: Skill & Command Documentation Parity

**Version:** 1.0.0
**Lane:** Heavy
**Slug:** `skill-command-doc-parity`

---

## Overview

Audit every `gz-*` skill and `gz` CLI command for documentation coverage parity. Ensure each skill has a clear, regulated purpose statement and each command has a matching `docs/user/commands/` page. Detect undocumented commands, orphaned skill files, stale descriptions, and purpose drift between skill SKILL.md content and command doc contracts.

## Policy and Guardrails

- **Lane:** Heavy — documentation is an external contract (Gate 5 Runbook-Code Covenant)
- Audit only; classify findings before remediation
- Every `gz` CLI subcommand must have a `docs/user/commands/<name>.md` page
- Every `gz-*` skill must have a SKILL.md with a clear, non-overlapping purpose
- Skills that wrap the same command must cross-reference, not duplicate
- Runbooks (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`) must reference all commands they exercise

## Workflow

### 1. Inventory

Enumerate all surfaces:

```bash
uv run gz --help
uv run gz skill audit
uv run gz cli audit
```

Cross-reference:
- `.claude/skills/gz-*/SKILL.md` — all skill files
- `docs/user/commands/*.md` — all command docs
- `docs/user/commands/index.md` — command index entries

### 2. Gap Analysis

For each command from `gz --help`, check:
- [ ] `docs/user/commands/<name>.md` exists
- [ ] Command appears in `docs/user/commands/index.md`
- [ ] At least one runbook references the command

For each `gz-*` skill, check:
- [ ] SKILL.md has a clear, non-overlapping purpose statement
- [ ] If the skill wraps a CLI command, the command doc exists
- [ ] No two skills describe the same purpose without explicit alias/compatibility note

### 3. Classify Findings

| Severity | Description |
|----------|-------------|
| **Missing** | Command exists but has no documentation page |
| **Orphaned** | Documentation page exists but command was removed |
| **Drift** | Skill purpose and command doc describe different behavior |
| **Overlap** | Two or more skills describe the same purpose without aliasing |
| **Index gap** | Command documented but missing from index.md |
| **Runbook gap** | Command undocumented in either operator or governance runbook |

### 4. Remediate

- Create missing command docs following the existing template (Usage, Options, What It Does, Examples)
- Update index.md with new entries
- Resolve drift by aligning skill SKILL.md with command doc
- Remove orphaned docs or mark as deprecated
- Add runbook references for commands used in workflows

### 5. Validate

```bash
uv run gz cli audit
uv run gz validate --documents --surfaces
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz cli audit` | 0 |
| exitCodeEquals | `uv run gz validate --documents --surfaces` | 0 |
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run gz cli audit > ops/chores/skill-command-doc-parity/proofs/cli-audit.txt
uv run gz skill audit > ops/chores/skill-command-doc-parity/proofs/skill-audit.txt
uv run gz validate --documents --surfaces > ops/chores/skill-command-doc-parity/proofs/validate.txt
```

## Known Gaps (Baseline 2026-03-21)

Commands missing `docs/user/commands/` pages:
- `gz lint`, `gz format`, `gz test`, `gz typecheck`, `gz check`
- `gz validate`, `gz tidy`, `gz superbook`, `gz interview`
- `gz chores show`, `gz chores advise`
- `gz skill new`, `gz skill list`

Structural gaps:
- `docs/user/manpages/` directory not populated
- No operator-facing skill reference alongside command reference

---

**End of CHORE: Skill & Command Documentation Parity**
