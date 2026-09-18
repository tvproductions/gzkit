# CHORE: Skill & Command Documentation Parity

**Lane:** Heavy
**Slug:** `skill-command-doc-parity`

---

## Overview

Audit every `gz-*` skill and `gz` CLI command for documentation coverage parity. Ensure each skill has a clear, regulated purpose statement and each command has a matching `docs/user/manpages/` page. Detect undocumented commands, orphaned skill files, stale descriptions, and purpose drift between skill SKILL.md content and command doc contracts.

## Policy and Guardrails

- **Lane:** Heavy — documentation is an external contract (Gate 5 Runbook-Code Covenant)
- Classify findings before remediating; aligning a skill's purpose lands only in an operator-initiated run
- Every `gz` CLI subcommand must have a `docs/user/manpages/<name>.md` page
- Every `gz-*` skill must have a SKILL.md with a clear, non-overlapping purpose
- Skills that wrap the same command must cross-reference, not duplicate
- Runbooks (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`) must reference all commands they exercise

## Workflow

### 1. Inventory — observe

Enumerate all surfaces:

```bash
uv run gz --help
uv run gz skill audit
uv run gz cli audit
```

Cross-reference:
- `.claude/skills/gz-*/SKILL.md` — all skill files
- `docs/user/manpages/*.md` — all command docs
- `docs/user/manpages/index.md` — command index entries

### 2. Gap Analysis — observe

For each command from `gz --help`, check:
- [ ] `docs/user/manpages/<name>.md` exists
- [ ] Command appears in `docs/user/manpages/index.md`
- [ ] At least one runbook references the command

For each `gz-*` skill, check:
- [ ] SKILL.md has a clear, non-overlapping purpose statement
- [ ] If the skill wraps a CLI command, the command doc exists
- [ ] No two skills describe the same purpose without explicit alias/compatibility note

### 3. Classify Findings — propose

| Severity | Description |
|----------|-------------|
| **Missing** | Command exists but has no documentation page |
| **Orphaned** | Documentation page exists but command was removed |
| **Drift** | Skill purpose and command doc describe different behavior |
| **Overlap** | Two or more skills describe the same purpose without aliasing |
| **Index gap** | Command documented but missing from index.md |
| **Runbook gap** | Command undocumented in either operator or governance runbook |

### 4. Remediate documentation — repair

- Create missing command docs following the existing template (Usage, Options, What It Does, Examples)
- Update index.md with new entries
- Remove orphaned docs or mark as deprecated
- Add runbook references for commands used in workflows

### 5. Align skill purpose (operator-initiated) — operator-only-repair

Only in a run the operator started: resolve **Drift** and **Overlap** findings by aligning the skill's SKILL.md with its command doc in `.gzkit/skills/`, then run `uv run gz agent sync control-surfaces`. Skills are operator-authored canon.

### 6. Validate — observe

```bash
uv run gz cli audit
uv run gz validate --documents --surfaces
uv run gz test
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan skill-command-doc-parity`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz cli audit > .gzkit/chores/skill-command-doc-parity/proofs/cli-audit.txt
uv run gz skill audit > .gzkit/chores/skill-command-doc-parity/proofs/skill-audit.txt
uv run gz validate --documents --surfaces > .gzkit/chores/skill-command-doc-parity/proofs/validate.txt
```

## Known Gaps (Baseline 2026-03-21)

Commands missing `docs/user/manpages/` pages:
- `gz lint`, `gz format`, `gz test`, `gz typecheck`, `gz check`
<!-- gz-validate-skip: command-shape -->
- `gz validate`, `gz tidy`, `gz superbook`, `gz interview`
- `gz chores show`, `gz chores advise`
- `gz skill new`, `gz skill list`

Structural gaps:
- `docs/user/manpages/` directory not populated
- No operator-facing skill reference alongside command reference

---

**End of CHORE: Skill & Command Documentation Parity**
