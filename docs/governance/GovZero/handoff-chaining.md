<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Handoff Document Chaining Protocol

**Status:** Active
**Last reviewed:** 2026-02-12
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)
**OBPI:** OBPI-0.0.25-07

---

## Overview

Session handoff documents can form **chains** that preserve context lineage across multiple engineering sessions.
Each document may declare a `continues_from` field in its YAML frontmatter pointing to its predecessor.
By following these links, an agent can reconstruct the full history of decisions and context for long-running work.

The chaining protocol defines the link format, traversal rules, and integrity checks that ensure chains remain reliable and navigable.

---

## Link Format

The `continues_from` field uses a canonical relative path from the repository root:

```yaml
continues_from: "{ADR-package}/handoffs/{previous-handoff}.md"
```

### Valid Examples

| Value | Description |
|-------|-------------|
| `ADR-0.0.25-session-handoff/handoffs/20260210T120000Z-session.md` | Full canonical path |
| `ADR-1.2.3-my-feature/handoffs/initial-handoff.md` | Different ADR package |

### Invalid Examples

| Value | Reason |
|-------|--------|
| `previous-session.md` | Bare filename, no path structure |
| `ADR-0.0.25-slug/previous.md` | Missing `/handoffs/` directory |
| `ADR-0.0.25-slug/handoffs/session.txt` | Non-`.md` extension |
| `some-dir/handoffs/session.md` | Missing `ADR-X.Y.Z-` prefix |
| _(empty)_ | Leave empty for chain root (first handoff) |

The format is validated by the regex pattern:

```text
^ADR-\d+\.\d+\.\d+-[\w-]+/handoffs/[\w.-]+\.md$
```

---

## Chain Traversal Rules

1. **Start from the newest** handoff document
2. **Read its `continues_from`** field from YAML frontmatter
3. **Resolve the path** relative to the repository root
4. **Follow the predecessor** — read its frontmatter, repeat
5. **Stop** when a document has no `continues_from` (chain root)
6. **Return oldest-first** — reverse the collected chain for chronological order

### Termination Conditions

| Condition | Behavior |
|-----------|----------|
| No `continues_from` field | Stop — chain root reached |
| `continues_from` is empty | Stop — chain root reached |
| Predecessor file not found | Stop — record error |
| Circular reference detected | Stop — record error |
| Depth limit reached (20) | Stop — record error |

---

## Chain Integrity Checks

The `check_chain_integrity()` function validates a chain and returns a `ChainIntegrityResult` with categorized findings.

### Errors (Hard Failures)

Errors make the chain invalid (`is_valid = False`):

| Check | Condition | Error Message |
|-------|-----------|---------------|
| Format | `continues_from` doesn't match canonical pattern | `Invalid continues_from format: ...` |
| Existence | Predecessor file does not exist on disk | `Predecessor file not found: ...` |
| Circular reference | A document appears twice in traversal | `Circular reference detected at ...` |
| Depth limit | Chain reaches 20 documents | `Chain depth 20 reaches limit of 20` |

### Warnings (Soft Advisories)

Warnings do not invalidate the chain (`is_valid = True`):

| Check | Condition | Warning Message |
|-------|-----------|-----------------|
| Depth advisory | Chain exceeds 5 documents | `Chain depth N exceeds advisory threshold of 5` |

---

## Data Types

### ChainIntegrityResult

Frozen dataclass returned by `check_chain_integrity()`:

| Field | Type | Description |
|-------|------|-------------|
| `chain` | `list[Path]` | Handoff paths, oldest to newest |
| `errors` | `list[str]` | Hard failures |
| `warnings` | `list[str]` | Soft advisories |
| `is_valid` | `bool` (property) | `True` when `len(errors) == 0` |

---

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `_CHAIN_DEPTH_LIMIT` | `20` | Maximum chain length before hard error |
| `_CHAIN_DEPTH_WARNING` | `5` | Advisory threshold for chain depth |
| `_CONTINUES_FROM_RE` | regex | Canonical format validation pattern |

---

## See Also

- [Handoff Document Validation](handoff-validation.md) — Document-level validation checks
- [Staleness Classification](staleness-classification.md) — Multi-factor staleness system
- [Session Handoff Schema](session-handoff-schema.md) — Schema specification
- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) — Architecture decision record
- Tests: `tests/governance/test_handoff_chaining.py`
