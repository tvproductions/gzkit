# ADR-0.1.0: enforced-governance-foundation

**Status:** Draft
**SemVer:** 0.1.0
**Parent PRD:** [PRD-GZKIT-1.0.0](../../../prd/PRD-GZKIT-1.0.0.md)
**Date Added:** 2026-01-13
**Lane:** Heavy (external CLI contract)

---

## Intent

Establish gzkit as a functional CLI for enforced governance. This ADR delivers the core covenant workflow (PRD → Constitution → Brief → ADR → Attestation) with persistent state tracking via JSONL ledger and Claude hooks for enforcement.

The differentiator from template scaffolders: state is tracked implicitly, and the agent cannot route around governance because hooks enforce ledger writes on artifact edits.

---

## Decision

### Core Commands

Implement 8 commands that form the complete governance workflow:

| Command | Purpose | Ledger Event |
|---------|---------|--------------|
| `gz init` | Scaffold project structure, ledger, hooks | `project_init` |
| `gz prd` | Create/validate PRD from template | `prd_created` |
| `gz constitute` | Create/validate constitution | `constitution_created` |
| `gz specify` | Create brief linked to PRD/constitution | `brief_created` |
| `gz plan` | Create ADR linked to brief | `adr_created` |
| `gz state` | Query ledger, display current state | (read-only) |
| `gz status` | Display gate status for active work | (read-only) |
| `gz attest` | Record human attestation | `attested` |

### Ledger System

Implement append-only JSONL ledger at `.gzkit/ledger.jsonl`:

```jsonl
{"schema":"gzkit.ledger.v1","event":"project_init","id":"gzkit","ts":"2026-01-13T..."}
{"schema":"gzkit.ledger.v1","event":"prd_created","id":"PRD-GZKIT-1.0.0","ts":"..."}
{"schema":"gzkit.ledger.v1","event":"constitution_created","id":"charter","ts":"..."}
{"schema":"gzkit.ledger.v1","event":"brief_created","id":"BRIEF-core","parent":"PRD-GZKIT-1.0.0","ts":"..."}
{"schema":"gzkit.ledger.v1","event":"adr_created","id":"ADR-0.1.0","parent":"BRIEF-core","ts":"..."}
{"schema":"gzkit.ledger.v1","event":"attested","adr":"ADR-0.1.0","term":"Completed","by":"jb","ts":"..."}
```

Every `gz` command (except `gz state` and `gz status`) appends to the ledger implicitly.

### Claude Hooks

Scaffold hooks on `gz init`:

**`.claude/settings.json`:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/ledger-writer.py"
          }
        ]
      }
    ]
  }
}
```

**`.claude/hooks/ledger-writer.py`:**
- Fires on PostToolUse for Edit/Write tools
- Matches governance artifact patterns (`docs/adr/**`, `docs/briefs/**`, etc.)
- Appends `artifact_edited` event to ledger
- Exits 0 (non-blocking on failure)

### Templates

Provide minimal templates for:

| Template | Location |
|----------|----------|
| PRD (hardened) | `src/gzkit/templates/prd.md` |
| Constitution | `src/gzkit/templates/constitution.md` |
| Brief | `src/gzkit/templates/brief.md` |
| ADR | `src/gzkit/templates/adr.md` |

Templates include required sections per GovZero doctrine.

### Directory Structure

`gz init` creates:

```
.gzkit/
├── ledger.jsonl
└── config.json
.claude/
├── settings.json
└── hooks/
    └── ledger-writer.py
docs/
├── prd/
├── constitutions/
├── briefs/
└── adr/
```

---

## Interfaces

### CLI (External)

```bash
gz init [project-name]              # Scaffold project
gz prd <name>                       # Create PRD
gz constitute [name]                # Create constitution
gz specify <brief-name>             # Create brief
gz plan <adr-name> --brief <brief>  # Create ADR
gz state [--json|--blocked|--ready] # Query state
gz status [--json]                  # Gate status
gz attest [--force] [--reason]      # Record attestation
```

### Config (`.gzkit/config.json`)

```json
{
  "mode": "lite",
  "paths": {
    "prd": "docs/prd",
    "constitutions": "docs/constitutions",
    "briefs": "docs/briefs",
    "adr": "docs/adr",
    "audit": "docs/audit"
  }
}
```

### Ledger Schema (`gzkit.ledger.v1`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema` | string | yes | Schema identifier |
| `event` | string | yes | Event type |
| `id` | string | yes | Artifact identifier |
| `parent` | string | no | Parent artifact ID |
| `ts` | string | yes | ISO 8601 UTC timestamp |
| `by` | string | no | Human identity (attestation) |
| `term` | string | no | Attestation term |
| `session` | string | no | Claude session ID (hooks) |
| `path` | string | no | File path (hooks) |

---

## Rationale

### Why ledger from day one?

Without state tracking, gzkit is a template scaffolder. The ledger is what makes governance *enforceable*—it creates an audit trail that persists across sessions and cannot be silently bypassed.

### Why hooks from day one?

The agent forgetting problem: if ledger writes require explicit calls, the agent will forget. Hooks make enforcement implicit—any edit to a governance artifact triggers a ledger append automatically.

### Why not SQLite?

JSONL is sufficient for MVP:
- Human-readable (can `cat` the file)
- Git-friendly (append-only, line-based diffs)
- Queryable via `jq` or Python
- No additional dependency

SQLite cache can be added in future if query performance becomes an issue.

---

## Consequences

### Positive

- Complete governance workflow from PRD to attestation
- State persists across sessions via ledger
- Agent cannot route around governance (hooks enforce)
- Human-readable artifacts (Markdown + JSONL)
- Git-native (all artifacts are text files)

### Negative

- Hooks require Claude Code (not portable to other AI tools)
- Ledger grows unbounded (rotation not implemented in 0.1.0)
- No gate verification yet (`gz implement`, `gz gates` deferred)

### Neutral

- Templates are minimal; will harden based on usage
- Config schema is simple; will extend as needed

---

## Acceptance Criteria

### AC-001: Project Initialization

- [ ] `gz init test-project` creates all directories
- [ ] `.gzkit/ledger.jsonl` created and empty
- [ ] `.gzkit/config.json` created with defaults
- [ ] `.claude/settings.json` created with hook config
- [ ] `.claude/hooks/ledger-writer.py` created and executable
- [ ] `project_init` event appended to ledger

### AC-002: PRD Command

- [ ] `gz prd PRD-FOO-1.0.0` creates PRD from template
- [ ] PRD contains hardened sections (invariants, gate mapping, Q&A, attestation)
- [ ] `prd_created` event appended to ledger

### AC-003: Constitution Command

- [ ] `gz constitute` creates constitution from template
- [ ] `constitution_created` event appended to ledger

### AC-004: Brief Command

- [ ] `gz specify my-feature` creates brief
- [ ] Brief links to constitution
- [ ] `brief_created` event appended to ledger with `parent`

### AC-005: ADR Command

- [ ] `gz plan ADR-0.1.0 --brief my-feature` creates ADR
- [ ] ADR links to brief
- [ ] `adr_created` event appended to ledger with `parent`

### AC-006: State Command

- [ ] `gz state` parses ledger and displays state
- [ ] `gz state --json` outputs valid JSON
- [ ] `gz state --blocked` shows blocked items
- [ ] `gz state --ready` shows ready items

### AC-007: Status Command

- [ ] `gz status` displays lane and gate status
- [ ] `gz status --json` outputs valid JSON

### AC-008: Attestation Command

- [ ] `gz attest` prompts for term
- [ ] `attested` event appended to ledger
- [ ] Attestation recorded in ADR

### AC-009: Hooks

- [ ] Hook fires on Edit/Write to `docs/adr/**`
- [ ] Hook fires on Edit/Write to `docs/briefs/**`
- [ ] `artifact_edited` event appended to ledger
- [ ] Hook includes session ID

---

## OBPIs

Work items derived from this ADR (One Brief Per Item):

| ID | Description | Status |
|----|-------------|--------|
| [OBPI-0.1.0-01](briefs/OBPI-0.1.0-01-gz-init.md) | Implement `gz init` with ledger and hooks scaffolding | Pending |
| [OBPI-0.1.0-02](briefs/OBPI-0.1.0-02-gz-prd.md) | Implement `gz prd` with hardened template | Pending |
| [OBPI-0.1.0-03](briefs/OBPI-0.1.0-03-gz-constitute.md) | Implement `gz constitute` with template | Pending |
| [OBPI-0.1.0-04](briefs/OBPI-0.1.0-04-gz-specify.md) | Implement `gz specify` with parent linking | Pending |
| [OBPI-0.1.0-05](briefs/OBPI-0.1.0-05-gz-plan.md) | Implement `gz plan` with brief linking | Pending |
| [OBPI-0.1.0-06](briefs/OBPI-0.1.0-06-gz-state.md) | Implement `gz state` with ledger parsing | Pending |
| [OBPI-0.1.0-07](briefs/OBPI-0.1.0-07-gz-status.md) | Implement `gz status` for gate display | Pending |
| [OBPI-0.1.0-08](briefs/OBPI-0.1.0-08-gz-attest.md) | Implement `gz attest` with ledger write | Pending |
| [OBPI-0.1.0-09](briefs/OBPI-0.1.0-09-ledger-writer-hook.md) | Implement ledger-writer hook script | Pending |
| [OBPI-0.1.0-10](briefs/OBPI-0.1.0-10-templates.md) | Create minimal templates (PRD, constitution, brief, ADR) | Pending |

---

## Evidence

### Gate 1 (ADR)

- This document
- Parent: [PRD-GZKIT-1.0.0](../../../prd/PRD-GZKIT-1.0.0.md)
- Closeout Form: [ADR-CLOSEOUT-FORM.md](ADR-CLOSEOUT-FORM.md)

### Gate 2 (TDD)

- Tests: `tests/` (pending)
- Coverage: ≥40% target

### Gate 3 (Docs)

- Command docs: `docs/commands/` (pending)
- `uv run mkdocs build` passes

### Gate 4 (BDD)

- CLI scenarios: (deferred to 0.2.0)

### Gate 5 (Human)

- Attestation: (pending)

---

## Attestation Block

| Field | Value |
|-------|-------|
| Attestation Term | — |
| Attested By | — |
| Attested At | — |
| Evidence | — |

Human attestation required before status changes to Completed.
