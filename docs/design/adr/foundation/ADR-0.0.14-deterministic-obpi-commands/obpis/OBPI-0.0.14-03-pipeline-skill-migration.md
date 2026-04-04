---
id: OBPI-0.0.14-03
parent: ADR-0.0.14-deterministic-obpi-commands
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.14-03: Pipeline and lock skill migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/ADR-0.0.14-deterministic-obpi-commands.md`
- **Checklist Items:** #7-8 - "Pipeline and lock skill migration to CLI-only writes"

**Status:** Draft

## Objective

The `gz-obpi-pipeline` and `gz-obpi-lock` skills contain zero direct file writes
to governance artifacts. Every lock, attestation, and completion operation
delegates to `gz obpi lock` and `gz obpi complete` CLI commands.

## Lane

**Heavy** - Modifies external skill contracts (pipeline behavior changes observable
to operators).

## Allowed Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` (rewrite Stage 1 lock + Stage 5 completion)
- `.claude/skills/gz-obpi-pipeline/DISPATCH.md` (update if subagent instructions reference direct writes)
- `.claude/skills/gz-obpi-lock/SKILL.md` (rewrite to delegate to CLI)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (canon mirror)
- `.gzkit/skills/gz-obpi-lock/SKILL.md` (canon mirror)
- `docs/user/runbook.md` (update OBPI lifecycle references)

## Denied Paths

- `src/gzkit/commands/` (command code is OBPI-01 and OBPI-02 scope)
- `src/gzkit/ledger.py` (no direct ledger modifications)
- `.gzkit/ledger.jsonl` (never edited manually)

## Requirements (FAIL-CLOSED)

1. `gz-obpi-pipeline` SKILL.md Stage 1 MUST use `uv run gz obpi lock claim` instead
   of direct `Write` to lock files
2. `gz-obpi-pipeline` SKILL.md Stage 5 MUST use `uv run gz obpi complete` instead of
   direct brief writes, attestation JSONL appends, and separate emit-receipt calls
3. `gz-obpi-pipeline` SKILL.md Stage 5 MUST use `uv run gz obpi lock release` instead
   of direct lock file deletion
4. `gz-obpi-lock` SKILL.md MUST delegate all operations to `gz obpi lock` subcommands
5. NEVER leave "fallback" direct-write paths in skill definitions
6. The pipeline skill MUST NOT change its stage structure (5 stages remain)
7. Lock release on abort/handoff MUST still work (via `gz obpi lock release --force`)
8. After migration, grep for `Write` tool calls touching `.gzkit/locks/` or
   attestation JSONL in both skills — count MUST be zero

> STOP-on-BLOCKERS: OBPI-01 and OBPI-02 must be completed before this OBPI begins.
> The CLI commands must exist before skills can delegate to them.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - full context

**Context:**

- [ ] `.claude/skills/gz-obpi-pipeline/SKILL.md` - full pipeline protocol (all 5 stages)
- [ ] `.claude/skills/gz-obpi-lock/SKILL.md` - current lock protocol
- [ ] `.claude/skills/gz-obpi-pipeline/DISPATCH.md` - subagent dispatch instructions

**Prerequisites (check existence, STOP if missing):**

- [ ] `gz obpi lock claim` works: `uv run gz obpi lock claim TEST-ID --agent test --ttl 5`
- [ ] `gz obpi complete` works: verified via OBPI-02 evidence

**Existing Code (understand current state):**

- [ ] Inventory all `Write` tool references in `gz-obpi-pipeline/SKILL.md`
- [ ] Inventory all `Write` tool references in `gz-obpi-lock/SKILL.md`
- [ ] Inventory all direct JSONL appends in both skills

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist items #7-8 quoted

### Gate 2: TDD

- [ ] Skill migration verified by running a pipeline dry-run
- [ ] No direct-write patterns remain (grep verification)

### Code Quality

- [ ] Skills are well-structured and follow existing patterns

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Runbook updated with new command references

### Gate 4: BDD (Heavy only)

- [ ] Pipeline end-to-end scenario passes with new commands

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
# Verify no direct writes remain in pipeline skill
grep -c "Write.*locks" .claude/skills/gz-obpi-pipeline/SKILL.md
# Expected: 0

grep -c "ledger.*append\|jsonl.*write\|Write.*audit" .claude/skills/gz-obpi-pipeline/SKILL.md
# Expected: 0

# Verify lock skill delegates to CLI
grep -c "gz obpi lock" .claude/skills/gz-obpi-lock/SKILL.md
# Expected: >= 4 (claim, release, check, list)

# Verify docs build
uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] REQ-0.0.14-03-01: Pipeline Stage 1 uses `gz obpi lock claim` (no direct Write)
- [ ] REQ-0.0.14-03-02: Pipeline Stage 5 uses `gz obpi complete` (no direct brief/ledger writes)
- [ ] REQ-0.0.14-03-03: Pipeline Stage 5 uses `gz obpi lock release` (no direct file delete)
- [ ] REQ-0.0.14-03-04: Lock skill delegates entirely to `gz obpi lock` subcommands
- [ ] REQ-0.0.14-03-05: Zero `Write` tool calls to `.gzkit/locks/` in either skill
- [ ] REQ-0.0.14-03-06: Zero direct JSONL appends to attestation ledgers in either skill
- [ ] REQ-0.0.14-03-07: Pipeline stage structure unchanged (5 stages)
- [ ] REQ-0.0.14-03-08: Abort/handoff lock release works via `--force`

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
