<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# GovZero Session Handoff Schema

**Status:** Active
**Last reviewed:** 2026-02-11
**Schema version:** `govzero.handoff.v1`
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)

---

## Overview

The session handoff schema defines the structure for agent context preservation documents. Handoff documents enable reliable session transfer — an agent captures its working state, decisions, and next steps so a subsequent session can resume without information loss.

### Purpose

- **Zero-ambiguity context transfer**: Structured format ensures nothing is lost between sessions
- **Validated resumption**: Fail-closed validation prevents agents from proceeding on stale or incomplete context
- **Chained lineage**: `continues_from` links create an audit trail across sessions
- **Compound learning**: Each session's insights feed into future sessions via structured Evidence sections

### Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                   Resuming Agent                         │
│         (validates, loads, verifies, executes)           │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ reads + validates
                          │
┌─────────────────────────────────────────────────────────┐
│               Handoff Document (.md)                     │
│     YAML frontmatter + 7 required Markdown sections      │
│           (stored in {ADR-package}/handoffs/)             │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ creates + validates
                          │
┌─────────────────────────────────────────────────────────┐
│                   Creating Agent                         │
│      (scaffolds, populates, validates, stores)           │
└─────────────────────────────────────────────────────────┘
```

---

## YAML Frontmatter

Every handoff document begins with YAML frontmatter between `---` delimiters.

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | `CREATE` \| `RESUME` | Yes | Handoff mode — CREATE for new documents, RESUME for continuation |
| `adr_id` | string | Yes | Parent ADR identifier (format: `ADR-X.Y.Z`) |
| `branch` | string | Yes | Git branch at time of handoff |
| `timestamp` | string | Yes | ISO 8601 UTC timestamp (Z-suffix or offset) |
| `agent` | string | Yes | Agent that created the document (e.g., `claude-code`) |
| `obpi_id` | string | No | Current OBPI being worked (format: `OBPI-X.Y.Z-NN`) |
| `session_id` | string | No | Session grouping identifier |
| `continues_from` | string | No | Relative path to predecessor handoff (chaining) |

### Example

```yaml
---
mode: CREATE
adr_id: ADR-0.0.25
branch: feature/session-handoff
timestamp: "2026-02-11T14:30:00Z"
agent: claude-code
obpi_id: OBPI-0.0.25-03
session_id: handoff-session-001
continues_from: handoffs/2026-02-10T09-00-00Z-schema-draft.md
---
```

### Field Validation Rules

- **`adr_id`**: Must match pattern `ADR-\d+\.\d+\.\d+` (three-part SemVer)
- **`timestamp`**: Must parse as valid ISO 8601 via `datetime.fromisoformat()`
- **`obpi_id`**: If present, must match pattern `OBPI-\d+\.\d+\.\d+-\d{2}` (SemVer + 2-digit sequence)
- **`mode`**: Exactly `CREATE` or `RESUME` (case-sensitive)
- **Extra fields**: Forbidden — unknown keys cause validation failure

---

## Required Sections

Every handoff document body must contain these 7 section headings as level-2 Markdown headers (`## Heading`):

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Current State Summary** | What has been done, current phase, success/failure of last action |
| 2 | **Important Context** | Non-obvious knowledge the resuming agent needs (constraints, gotchas, config locations) |
| 3 | **Decisions Made** | Decisions with rationale and rejected alternatives |
| 4 | **Immediate Next Steps** | Ordered list of 3-5 concrete next actions |
| 5 | **Pending Work / Open Loops** | Deferred or blocked items that must be completed |
| 6 | **Verification Checklist** | Commands and checks to verify handoff accuracy |
| 7 | **Evidence / Artifacts** | File paths and descriptions of session outputs |

### Optional Section

| Section | Purpose |
|---------|---------|
| **Environment State** | Python version, package versions, OS-specific notes, database state |

---

## Validation Rules

All validation is **fail-closed** — any violation prevents the document from being accepted.

| # | Rule | Function | Behavior |
|---|------|----------|----------|
| 1 | **Frontmatter present** | `parse_frontmatter()` | Opening/closing `---` delimiters, valid YAML mapping |
| 2 | **Frontmatter valid** | `HandoffFrontmatter` model | All required fields present and well-formed |
| 3 | **No placeholders** | `validate_no_placeholders()` | Body must not contain TBD, TODO, FIXME, PLACEHOLDER, XXX, CHANGEME, or standalone `...` |
| 4 | **No secrets** | `validate_no_secrets()` | Content must not contain `password=`, `secret=`, `token=`, `api_key=`, `Bearer`, or `PRIVATE KEY` |
| 5 | **Sections present** | `validate_sections_present()` | All 7 required section headings must appear |
| 6 | **References valid** | `validate_referenced_files()` | Backtick-quoted paths in Evidence section must exist on disk |

### Placeholder Detection

Placeholder scanning **strips HTML comments** before matching, so template guidance in `<!-- comments -->` does not trigger false positives. The scan applies only to the document body (frontmatter is excluded).

Detected patterns (case-insensitive):

```text
TBD | TODO | FIXME | PLACEHOLDER | XXX | CHANGEME | ... (standalone)
```

### Secret Detection

Secret scanning applies to the **entire document** (including frontmatter). Detected patterns:

```text
password= | secret= | token= | api_key= | Bearer <token> | PRIVATE KEY
```

---

## Staleness Classification

From ADR-0.0.25 Decision 4, handoff documents are classified by age:

| Classification | Age | Action |
|----------------|-----|--------|
| **Fresh** | < 24 hours | Resume directly |
| **Slightly Stale** | 24h - 72h | Resume with caution, verify key assumptions |
| **Stale** | 72h - 7 days | Human verification required before resume |
| **Very Stale** | > 7 days | Human verification required; consider re-creating |

Staleness is computed from the `timestamp` field in frontmatter relative to the current time.

---

## Chaining Protocol

From ADR-0.0.25 Decision 5, handoff documents form chains via the `continues_from` field.

### Rules

1. **New chains**: First handoff in a chain has `continues_from` empty/null
2. **Continuation**: Subsequent handoffs set `continues_from` to the relative path of the predecessor
3. **Lineage traversal**: Follow `continues_from` links to reconstruct full session history
4. **Validation**: `continues_from` path, if set, should resolve to an existing file on disk

### Example Chain

```text
handoffs/2026-02-01T10-00-00Z-schema-design.md
  └─ continues_from: (none — chain start)

handoffs/2026-02-02T14-00-00Z-schema-tests.md
  └─ continues_from: handoffs/2026-02-01T10-00-00Z-schema-design.md

handoffs/2026-02-03T09-00-00Z-schema-docs.md
  └─ continues_from: handoffs/2026-02-02T14-00-00Z-schema-tests.md
```

---

## Storage Conventions

Handoff documents are stored per-ADR in the ADR package directory:

```text
docs/design/adr/{series}/ADR-{id}-{slug}/handoffs/{timestamp}-{slug}.md
```

Example:

```text
docs/design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/
  handoffs/
    2026-02-01T10-00-00Z-schema-design.md
    2026-02-02T14-00-00Z-schema-tests.md
```

---

## Validation API

### Python

The schema model and validation functions are currently defined in `tests/governance/test_handoff_schema.py` (to be extracted to a source module by OBPI-0.0.25-06).

```python
from tests.governance.test_handoff_schema import (
    HandoffFrontmatter,
    HandoffValidationError,
    parse_frontmatter,
    validate_handoff_document,
    validate_no_placeholders,
    validate_no_secrets,
    validate_sections_present,
    validate_referenced_files,
    HANDOFF_SCHEMA_VERSION,
    REQUIRED_SECTIONS,
)

# Parse and validate frontmatter
content = Path("handoff.md").read_text()
data = parse_frontmatter(content)
fm = HandoffFrontmatter(**data)
print(f"Mode: {fm.mode}, ADR: {fm.adr_id}")

# Full document validation (fail-closed)
errors = validate_handoff_document(content, base_path=Path("."))
if errors:
    for e in errors:
        print(f"  FAIL: {e}")
else:
    print("  PASS: document is valid")
```

---

## See Also

- [Layered Trust Architecture](layered-trust.md) — Tool layer model and boundaries
- [Unified Ledger Schema](ledger-schema.md) — Companion schema for JSONL governance ledgers
- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) — Architecture decision record
- [GovZero Charter](charter.md) — Gate definitions and authority
- [ADR Lifecycle](adr-lifecycle.md) — Status transitions
- Template: `.github/skills/gz-session-handoff/assets/handoff-template.md`
- Tests: `tests/governance/test_handoff_schema.py`
