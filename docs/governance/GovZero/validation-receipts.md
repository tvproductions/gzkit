# Validation Receipt Schema

**Status:** Active
**Last reviewed:** 2026-02-11
**Schema version:** `govzero.ledger.v1`
**Parent ADR:** ADR-0.0.24 (Validation Receipt Temporal Anchoring)

---

## Overview

Validation receipts anchor ADR/OBPI validation events to specific git commits, enabling
"valid as of" semantics. When an ADR is validated, a receipt records the exact commit SHA,
so later drift detection can determine whether code has changed since the last audit.

### Purpose

- **Temporal anchoring**: Every validation event is tied to a git commit
- **Drift detection**: Compare current HEAD against the last validation anchor to detect changes
- **Audit trail**: Machine-readable evidence of when and by whom validation occurred
- **Separation of concerns**: Validation receipts live in their own ledger, complementing the OBPI audit ledger

### Relationship to OBPI Audit Ledger

| Aspect | OBPI Audit Ledger | Validation Receipt Ledger |
|--------|-------------------|---------------------------|
| **File** | `obpi-audit.jsonl` | `adr-validation.jsonl` |
| **Scope** | Per-brief status audits | Per-ADR validation events |
| **Purpose** | Track OBPI status transitions | Anchor validation to git state |
| **Schema** | `obpi-audit`, `covers-map`, etc. | `validation` |

Both ledgers share the `govzero.ledger.v1` base schema (`LedgerEntryBase`) for consistency.

---

## Entry Schema

### validation

Records a validation event tied to a specific git commit.

```json
{
  "type": "validation",
  "timestamp": "2026-02-10T14:30:00Z",
  "schema_version": "govzero.ledger.v1",
  "agent": "claude-code",
  "session_id": "2026-02-10-adr-024-validation",
  "adr_id": "ADR-0.0.24",
  "event": "validated",
  "anchor": {
    "commit": "de80292",
    "tag": "v0.0.24",
    "semver": "0.0.24"
  },
  "evidence": {
    "tests_passed": true,
    "test_count": 15,
    "coverage_percent": 48.5,
    "gate2_pass": true
  },
  "attestor": "human:jeff"
}
```

### Common Fields (inherited from LedgerEntryBase)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"validation"` | Yes | Entry type discriminator |
| `timestamp` | string | Yes | ISO 8601 UTC timestamp (Z-suffixed) |
| `schema_version` | string | No | Schema version (default: `govzero.ledger.v1`) |
| `agent` | string | No | Agent that created the entry |
| `session_id` | string | No | Session identifier for grouping |

### Validation-Specific Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adr_id` | string | Yes | ADR identifier (format: `ADR-X.Y.Z`) |
| `event` | string | Yes | One of: `validated`, `completed`, `compliance_check` |
| `anchor` | object | Yes | Temporal anchor (see below) |
| `evidence` | object | No | Evidence payload (test results, coverage, etc.) |
| `attestor` | string | Yes | Human attestor (must be `human:<name>`, e.g., `human:jeff`). Only humans can attest — agents record evidence via the `agent` field. |

### ValidationAnchor Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `commit` | string | Yes | Git SHA, 7-40 lowercase hex characters |
| `tag` | string | No | Git tag if HEAD is tagged at validation time |
| `semver` | string | Yes | ADR semver version (e.g., `0.0.24`) |

---

## Event Types

| Event | When Used |
|-------|-----------|
| `validated` | ADR passes Gate 5 audit and is marked Validated |
| `completed` | ADR passes Gates 1-4 and is marked Completed |
| `compliance_check` | Periodic or on-demand compliance verification |

---

## Ledger File Location

Validation receipts are stored per-ADR alongside the existing OBPI audit ledger:

```text
docs/design/adr/{series}/ADR-{id}-{slug}/logs/adr-validation.jsonl
```

Example:

```text
docs/design/adr/adr-0.0.x/ADR-0.0.24-validation-receipt-temporal-anchoring/logs/adr-validation.jsonl
```

---

## Edge Case Behavior

| Scenario | Behavior |
|----------|----------|
| Ledger file does not exist | `read_receipts()` returns empty list |
| Ledger file is empty | `read_receipts()` returns empty list |
| Malformed JSONL line | Skipped with `warnings.warn()`; valid entries still returned |
| Duplicate receipts for same commit | All are preserved (idempotency is caller's responsibility) |

---

## Python API

### Creating and Writing Receipts

```python
from opsdev.lib.validation_receipt import (
    ValidationAnchor,
    ValidationReceipt,
    create_timestamp,
    write_receipt,
)
from pathlib import Path

receipt = ValidationReceipt(
    timestamp=create_timestamp(),
    adr_id="ADR-0.0.24",
    event="validated",
    anchor=ValidationAnchor(
        commit="de80292",
        tag="v0.0.24",
        semver="0.0.24",
    ),
    evidence={"tests_passed": True, "coverage_percent": 48.5},
    attestor="human:jeff",
    agent="claude-code",
    session_id="2026-02-10-session",
)

ledger_path = Path("docs/design/adr/adr-0.0.x/ADR-0.0.24-.../logs/adr-validation.jsonl")
write_receipt(receipt, ledger_path)
```

### Reading Receipts

```python
from opsdev.lib.validation_receipt import read_receipts
from pathlib import Path

ledger_path = Path("docs/design/adr/adr-0.0.x/ADR-0.0.24-.../logs/adr-validation.jsonl")

# Read all receipts
all_receipts = read_receipts(ledger_path)

# Filter by ADR
adr_receipts = read_receipts(ledger_path, adr_id="ADR-0.0.24")
```

---

## See Also

- [Ledger Schema](ledger-schema.md) — Base schema and OBPI audit entry types
- [Layered Trust Architecture](layered-trust.md) — Tool layer model
- [ADR Lifecycle](adr-lifecycle.md) — Status transitions
- Python module: `src/opsdev/lib/validation_receipt.py`
