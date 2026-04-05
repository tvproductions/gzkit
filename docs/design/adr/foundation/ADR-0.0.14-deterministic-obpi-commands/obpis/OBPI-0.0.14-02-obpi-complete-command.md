---
id: OBPI-0.0.14-02-obpi-complete-command
parent: ADR-0.0.14-deterministic-obpi-commands
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.14-02: gz obpi complete command

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/ADR-0.0.14-deterministic-obpi-commands.md`
- **Checklist Items:** #5-6 - "gz obpi complete atomic transaction and rollback"

**Status:** Draft

## Objective

`gz obpi complete` atomically validates, writes evidence, flips status, records
attestation, and emits completion receipt in a single all-or-nothing transaction.
If any step fails, no files or ledger entries are modified.

## Lane

**Heavy** - New CLI subcommand with external contract (exit codes, flags, JSON output,
attestation semantics).

## Allowed Paths

- `src/gzkit/commands/obpi_cmd.py` (register subcommand)
- `src/gzkit/commands/obpi_complete.py` (new: complete command implementation)
- `src/gzkit/brief_writer.py` (new or existing: brief file manipulation)
- `src/gzkit/cli/parser_artifacts.py` (parser registration)
- `src/gzkit/ledger_events.py` (event types)
- `tests/test_obpi_complete_cmd.py` (new: unit tests)
- `features/obpi_complete.feature` (new: BDD scenarios)
- `features/steps/obpi_complete_steps.py` (new: step definitions)
- `docs/user/commands/obpi.md` (update with complete subcommand)

## Denied Paths

- `.claude/skills/` (skill migration is OBPI-03)
- `.gzkit/ledger.jsonl` (never edited manually)
- Lock management code (OBPI-01 scope)

## Requirements (FAIL-CLOSED)

1. `gz obpi complete` MUST validate the brief exists and is not already Completed
2. `gz obpi complete` MUST run `obpi validate` logic internally to check evidence sufficiency
3. `gz obpi complete` MUST write Implementation Summary and Key Proof evidence
   sections to the brief file using `###` (H3) headings
4. `gz obpi complete` MUST flip brief status to `Completed` in both frontmatter
   and body status markers
5. `gz obpi complete` MUST write an `obpi-audit` attestation ledger entry with
   attestor name, attestation text, and timestamp
6. `gz obpi complete` MUST emit an `obpi_receipt_emitted` event with completion evidence
7. If ANY step fails, ALL changes MUST be rolled back (no partial writes)
8. `--attestor` and `--attestation-text` are REQUIRED flags (not optional)
9. `--implementation-summary` and `--key-proof` are optional; if omitted, the
   command reads existing values from the brief
10. `--json` MUST produce machine-readable output to stdout
11. Exit codes: 0 = completed, 1 = validation failure, 2 = I/O error

> STOP-on-BLOCKERS: if the brief file does not exist, exit 1 with clear error message.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - full context

**Context:**

- [ ] `.claude/skills/gz-obpi-pipeline/SKILL.md` Stage 5 - current completion flow
- [ ] `src/gzkit/commands/obpi_cmd.py` - existing validate/emit-receipt logic

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/obpi_cmd.py` - `obpi_validate_cmd` and `obpi_emit_receipt_cmd`
- [ ] `src/gzkit/ledger.py` - ledger append pattern
- [ ] `src/gzkit/ledger_events.py` - event factory pattern
- [ ] Brief file format - YAML frontmatter + markdown body with evidence sections

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist items #5-6 quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/commands/obpi.md` updated with complete subcommand

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_complete.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification — happy path
gz obpi complete OBPI-0.0.14-01 \
  --attestor jeff \
  --attestation-text "Lock commands verified" \
  --implementation-summary "Implemented claim/release/check/list" \
  --key-proof "gz obpi lock claim OBPI-0.0.14-01 exits 0; gz obpi lock check exits 0"

# Specific verification — rollback on failure
gz obpi complete NONEXISTENT-OBPI --attestor jeff --attestation-text "test"
# Expected: exit 1, no files modified
```

## Acceptance Criteria

- [ ] REQ-0.0.14-02-01: Brief must exist and not be Completed (exit 1 otherwise)
- [ ] REQ-0.0.14-02-02: Internal validation checks evidence sufficiency before proceeding
- [ ] REQ-0.0.14-02-03: Evidence sections use `###` (H3) headings per hook requirement
- [ ] REQ-0.0.14-02-04: Brief status flipped in frontmatter and body markers atomically
- [ ] REQ-0.0.14-02-05: `obpi-audit` attestation entry written to ledger
- [ ] REQ-0.0.14-02-06: `obpi_receipt_emitted` event emitted with completion evidence
- [ ] REQ-0.0.14-02-07: Full rollback on any step failure (no partial writes)
- [ ] REQ-0.0.14-02-08: `--attestor` and `--attestation-text` are required
- [ ] REQ-0.0.14-02-09: `--json` produces valid machine-readable output

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
