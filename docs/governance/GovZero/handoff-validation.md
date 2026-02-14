<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Handoff Document Validation

**Status:** Active
**Last reviewed:** 2026-02-12
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)
**OBPI:** OBPI-0.0.25-06

---

## Overview

Session handoff documents must be validated before they can serve as reliable context for agent resume workflows. The validation module implements a **fail-closed** philosophy: every check returns a list of violations, and only an empty list means the document is clean.

Six validation checks run in sequence, with errors accumulated (not short-circuited) so that a single pass reveals all issues.

---

## Validation Checks

### 1. Frontmatter Parsing

Extracts YAML frontmatter delimited by `---` markers. Validates:

- Opening and closing `---` delimiters are present
- YAML is syntactically valid
- Content is a YAML mapping (not a list or scalar)

### 2. Frontmatter Schema

Validates the parsed frontmatter against `HandoffFrontmatter` (Pydantic model):

| Field | Type | Validation |
|-------|------|------------|
| `mode` | `"CREATE"` or `"RESUME"` | Literal enum |
| `adr_id` | string | Matches `ADR-X.Y.Z` |
| `branch` | string | Required, non-empty |
| `timestamp` | string | ISO 8601 parseable |
| `agent` | string | Required, non-empty |
| `obpi_id` | string or null | Matches `OBPI-X.Y.Z-NN` |
| `session_id` | string or null | Optional |
| `continues_from` | string or null | Optional |

Extra fields are forbidden (`extra="forbid"`). Model is frozen (immutable after creation).

### 3. Placeholder Detection

Scans the document body (frontmatter stripped, HTML comments removed) for placeholder markers:

| Pattern | Examples |
|---------|----------|
| `TBD` | "TBD", "tbd" |
| `TODO` | "TODO: finish this" |
| `FIXME` | "FIXME later" |
| `PLACEHOLDER` | "PLACEHOLDER value" |
| `XXX` | "XXX needs work" |
| `CHANGEME` | "CHANGEME" |
| `...` (standalone) | Ellipsis on its own line |

Detection is case-insensitive and uses word boundaries to avoid false positives within longer words.

### 4. Secret Detection

Scans full content for potential leaked credentials:

| Pattern | Matches |
|---------|---------|
| `password=` | Password assignments |
| `secret=` | Secret assignments |
| `token=` | Token assignments |
| `api_key=` | API key assignments |
| `Bearer <token>` | Authorization headers |
| `PRIVATE KEY` | PEM key blocks |
| `sk-<20+ chars>` | OpenAI API keys |
| `ghp_<20+ chars>` | GitHub personal access tokens |

The `sk-` and `ghp_` patterns use negative lookbehind `(?<![a-zA-Z])` to avoid false positives (e.g., `task-management` does not match `sk-`).

### 5. Required Sections

Verifies all seven required `##` section headings are present:

1. Current State Summary
2. Important Context
3. Decisions Made
4. Immediate Next Steps
5. Pending Work / Open Loops
6. Verification Checklist
7. Evidence / Artifacts

Optional sections (e.g., "Environment State") are not checked.

### 6. Referenced File Existence

In the "Evidence / Artifacts" section, backtick-quoted strings that look like file paths (contain `/` or `.`) are resolved against the repository root. Missing files are reported.

Heuristics skip non-path content:

- Strings starting with `-`, `$`, `uv`, `git` (commands)
- Strings without `/` or `.` (variable names, not paths)

---

## Python API

```python
from opsdev.governance.handoff_validation import (
    validate_handoff_document,
    parse_frontmatter,
    HandoffFrontmatter,
    HandoffValidationError,
)
from pathlib import Path

# Full validation (returns list of error strings)
content = Path("handoffs/session.md").read_text()
errors = validate_handoff_document(content, base_path=Path("."))
if errors:
    for e in errors:
        print(f"  - {e}")
else:
    print("Document is valid.")

# Parse frontmatter only
data = parse_frontmatter(content)
fm = HandoffFrontmatter(**data)
print(fm.mode, fm.adr_id)
```

### Individual Validators

```python
from opsdev.governance.handoff_validation import (
    validate_no_placeholders,
    validate_no_secrets,
    validate_sections_present,
    validate_referenced_files,
)

violations = validate_no_placeholders(content)
violations = validate_no_secrets(content)
missing = validate_sections_present(content)
missing_files = validate_referenced_files(content, Path("."))
```

---

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `HANDOFF_SCHEMA_VERSION` | `"govzero.handoff.v1"` | Schema version identifier |
| `REQUIRED_SECTIONS` | 7-element tuple | Required `##` section headings |

---

## Error Handling

- `HandoffValidationError` is raised by `parse_frontmatter()` for structural issues (missing delimiters, invalid YAML)
- `pydantic.ValidationError` is raised by `HandoffFrontmatter` for schema violations
- `validate_handoff_document()` catches both and returns them as strings in the error list
- All other validators return `list[str]` — empty means clean, non-empty lists the violations

---

## See Also

- [Session Handoff Schema](session-handoff-schema.md) -- Schema specification
- [Staleness Classification](staleness-classification.md) -- Multi-factor staleness system
- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) -- Architecture decision record
- Source: `src/opsdev/governance/handoff_validation.py`
- Tests: `tests/governance/test_handoff_validation.py`
