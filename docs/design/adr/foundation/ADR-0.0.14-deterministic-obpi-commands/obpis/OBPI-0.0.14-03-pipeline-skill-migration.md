---
id: OBPI-0.0.14-03-pipeline-skill-migration
parent: ADR-0.0.14-deterministic-obpi-commands
item: 3
lane: Heavy
status: attested_completed
---

# OBPI-0.0.14-03: Pipeline and lock skill migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/ADR-0.0.14-deterministic-obpi-commands.md`
- **Checklist Items:** #7-8 - "Pipeline and lock skill migration to CLI-only writes"

**Status:** Draft

## Objective

Rewrite the `gz-obpi-pipeline` and `gz-obpi-lock` skill prose so that every
lock, attestation, and completion instruction delegates to `gz obpi lock` and
`gz obpi complete` CLI commands. After migration, no skill text instructs an
agent to use the `Write` tool, `Edit` tool, or raw JSONL append for governance
artifacts (lock files, attestation ledgers, brief status changes).

### Prose-vs-Code Boundary

Skills are **markdown documents that instruct agents**, not executable code.
"Zero direct writes" means the skill prose contains no instructions that tell
an agent to write governance artifacts directly. Verification operates at two
levels:

1. **Static (grep):** The skill text contains no `Write` tool references
   targeting `.gzkit/locks/`, `obpi-audit.jsonl`, or brief status fields.
2. **Integration (end-to-end):** A pipeline dry-run using the migrated skill
   text produces CLI command invocations (visible in tool-use output), not
   direct Write/Edit tool calls to governance paths.

Level 1 is necessary but not sufficient. Level 2 confirms that the prose
actually achieves the intended delegation in practice.

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

### Prose Rewrite Requirements

1. REQUIREMENT: Pipeline Stage 1 lock acquisition — `gz-obpi-pipeline` SKILL.md
   Stage 1 MUST instruct agents to run `uv run gz obpi lock claim` instead of
   using the `Write` tool to create lock files
2. REQUIREMENT: Pipeline Stage 5 completion — `gz-obpi-pipeline` SKILL.md
   Stage 5 MUST instruct agents to run `uv run gz obpi complete` instead of
   direct brief writes, attestation JSONL appends, and separate emit-receipt calls
3. REQUIREMENT: Pipeline Stage 5 lock release — `gz-obpi-pipeline` SKILL.md
   Stage 5 MUST instruct agents to run `uv run gz obpi lock release` instead of
   directly deleting lock files
4. REQUIREMENT: Lock skill delegation — `gz-obpi-lock` SKILL.md MUST instruct
   agents to delegate all operations to `gz obpi lock` subcommands (claim,
   release, check, list)
5. REQUIREMENT: No fallback paths — NEVER leave "fallback" direct-write
   instructions in skill definitions; no "if the command fails, use Write as a
   fallback" language
6. REQUIREMENT: Stage structure preservation — the pipeline skill MUST NOT
   change its stage structure (5 stages remain)
7. REQUIREMENT: Abort/handoff lock release — lock release on abort/handoff MUST
   still work (instruct agents to use `gz obpi lock release --force`)

### Static Verification Requirements

8. REQUIREMENT: Zero Write tool references — after migration, grep for `Write`
   tool calls targeting `.gzkit/locks/` or attestation JSONL in both skills;
   count MUST be zero
9. REQUIREMENT: Zero Edit tool references — after migration, grep for `Edit`
   tool calls targeting brief status fields in pipeline Stage 5; count MUST be
   zero
10. REQUIREMENT: CLI command coverage — each skill MUST reference the
    corresponding `gz obpi` subcommand at least once per operation it delegates
    (claim, release, check, list, complete)

### Integration Verification Requirements

11. REQUIREMENT: Tool-use log verification — run the pipeline skill on a test
    OBPI and verify the tool-use log shows `Bash` calls to `gz obpi lock` and
    `gz obpi complete`, not `Write`/`Edit` calls to governance paths
12. REQUIREMENT: Ledger event parity — verify that a pipeline run with the
    migrated skill produces the same ledger events as the pre-migration flow
    (lock claimed, lock released, obpi-audit, receipt emitted)

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

### Level 1: Static (grep-based prose check)

```bash
# Verify no Write tool instructions targeting governance paths in pipeline skill
grep -ciE "Write.*(locks|obpi-audit|\.lock\.json)" .claude/skills/gz-obpi-pipeline/SKILL.md
# Expected: 0

# Verify no direct JSONL append instructions in pipeline skill
grep -ciE "(append|write).*(jsonl|ledger)" .claude/skills/gz-obpi-pipeline/SKILL.md
# Expected: 0

# Verify no Edit tool instructions for brief status in pipeline Stage 5
grep -ciE "Edit.*(status|frontmatter)" .claude/skills/gz-obpi-pipeline/SKILL.md
# Expected: 0

# Verify lock skill references CLI commands
grep -c "gz obpi lock" .claude/skills/gz-obpi-lock/SKILL.md
# Expected: >= 4 (claim, release, check, list)

# Verify no Write tool instructions in lock skill for governance paths
grep -ciE "Write.*(locks|\.lock\.json)" .claude/skills/gz-obpi-lock/SKILL.md
# Expected: 0
```

### Level 2: Integration (end-to-end behavior)

```bash
# Run pipeline on a test OBPI and inspect tool-use log for CLI delegation
# (manual verification — run pipeline skill, check that Stage 1 invokes
# gz obpi lock claim and Stage 5 invokes gz obpi complete + gz obpi lock release)

# Verify docs build
uv run mkdocs build --strict
```

### Level 2 acceptance criteria (what to look for in tool-use output)

1. Stage 1 tool-use log shows `Bash: uv run gz obpi lock claim ...` (not `Write: .gzkit/locks/...`)
2. Stage 5 tool-use log shows `Bash: uv run gz obpi complete ...` (not `Write: ...brief.md`)
3. Stage 5 tool-use log shows `Bash: uv run gz obpi lock release ...` (not file deletion)
4. Ledger contains `obpi_lock_claimed`, `obpi_lock_released`, `obpi-audit`, and
   `obpi_receipt_emitted` events matching the test OBPI

## Acceptance Criteria

### Prose Rewrite (REQs 1-7)

- [ ] REQ-0.0.14-03-01: Pipeline Stage 1 instructs `gz obpi lock claim` (no Write tool for locks)
- [ ] REQ-0.0.14-03-02: Pipeline Stage 5 instructs `gz obpi complete` (no direct brief/ledger writes)
- [ ] REQ-0.0.14-03-03: Pipeline Stage 5 instructs `gz obpi lock release` (no direct file delete)
- [ ] REQ-0.0.14-03-04: Lock skill delegates entirely to `gz obpi lock` subcommands
- [ ] REQ-0.0.14-03-05: No fallback direct-write language in either skill
- [ ] REQ-0.0.14-03-06: Pipeline stage structure unchanged (5 stages)
- [ ] REQ-0.0.14-03-07: Abort/handoff instructs `gz obpi lock release --force`

### Static Verification (REQs 8-10)

- [ ] REQ-0.0.14-03-08: Zero `Write` tool references to `.gzkit/locks/` or `.lock.json` in either skill
- [ ] REQ-0.0.14-03-09: Zero `Edit` tool references to brief status in pipeline Stage 5
- [ ] REQ-0.0.14-03-10: Each skill references `gz obpi` subcommands for every delegated operation

### Integration Verification (REQs 11-12)

- [ ] REQ-0.0.14-03-11: Pipeline dry-run tool-use log shows Bash calls to `gz obpi`, not Write/Edit to governance paths
- [ ] REQ-0.0.14-03-12: Pipeline run produces same ledger events as pre-migration flow

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


grep -c 'gz obpi lock' .claude/skills/gz-obpi-lock/SKILL.md returns 13; grep -ciE 'Write.*(locks|obpi-audit)' .claude/skills/gz-obpi-pipeline/SKILL.md returns 0

### Implementation Summary


- Files modified: .claude/skills/gz-obpi-lock/SKILL.md, .claude/skills/gz-obpi-pipeline/SKILL.md, .claude/skills/gz-obpi-pipeline/DISPATCH.md, .gzkit/skills/gz-obpi-lock/SKILL.md, .gzkit/skills/gz-obpi-pipeline/SKILL.md, docs/user/runbook.md
- Tests added: (none — prose-only migration)
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: (none)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed
- Date: 2026-04-06

---

**Brief Status:** Completed

**Date Completed:** 2026-04-06

**Evidence Hash:** -
