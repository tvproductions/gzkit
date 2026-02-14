# GovZero Unified Ledger Schema

**Status:** Active
**Last reviewed:** 2026-01-29
**Schema version:** `govzero.ledger.v1`
**Parent ADR:** ADR-0.0.21 (GovZero Tooling Layered Trust Architecture)

---

## Overview

The GovZero unified ledger schema defines a standardized JSONL format for all Layer 1 governance tool
outputs. This enables Layer 2 tools to reliably consume structured evidence from multiple sources.

### Purpose

- **Machine-readable evidence**: All governance operations produce structured, parseable records
- **Discriminated union**: Type-safe parsing using the `type` field as discriminator
- **Backward compatibility**: Legacy entries without `type` field are auto-detected
- **Extensibility**: Evidence payloads allow custom fields for domain-specific data

### Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                     Layer 2 Tools                       │
│  (gz-adr-audit, dashboards, compliance reports)         │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ consumes
                          │
┌─────────────────────────────────────────────────────────┐
│                   JSONL Ledger Files                    │
│     obpi-audit.jsonl, covers-map.jsonl, etc.            │
│                (unified schema)                         │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ produces
                          │
┌─────────────────────────────────────────────────────────┐
│                     Layer 1 Tools                       │
│  gz-obpi-audit, gz-obpi-sync, gz-adr-verification       │
└─────────────────────────────────────────────────────────┘
```

---

## Entry Types

| Type | Description | Source Tool |
|------|-------------|-------------|
| `obpi-audit` | OBPI brief status audit results | gz-obpi-audit |
| `covers-map` | ADR → test mapping from @covers | gz-adr-verification |
| `coverage-run` | Module coverage measurement | coverage reporter |
| `reconciliation` | Reconciliation session summary | gz-obpi-reconcile |

---

## Common Fields

All entry types share these base fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes* | Entry type discriminator |
| `timestamp` | string | Yes | ISO 8601 UTC timestamp (Z-suffixed) |
| `schema_version` | string | No | Schema version (default: `govzero.ledger.v1`) |
| `agent` | string | No | Agent that created the entry |
| `session_id` | string | No | Session identifier for grouping |

*Legacy entries may omit `type`; it is inferred from content.

---

## Entry Schemas

### obpi-audit

Records the evaluation of an OBPI brief's acceptance criteria.

```json
{
  "type": "obpi-audit",
  "timestamp": "2026-01-26T14:45:00Z",
  "obpi_id": "OBPI-0.0.19-03",
  "adr_id": "ADR-0.0.19",
  "brief_status_before": "Accepted",
  "brief_status_after": "Completed",
  "lane": "Lite",
  "evidence": {
    "tests_found": ["tests/warehouse/test_manifest_purity.py"],
    "tests_passed": true,
    "test_count": 10,
    "coverage_module": "src/airlineops/warehouse/manifest.py",
    "coverage_percent": 46.05,
    "coverage_threshold": 40
  },
  "criteria_evaluated": [
    {
      "criterion": "Coverage ≥40%",
      "result": "PASS",
      "evidence": "46.05% achieved"
    }
  ],
  "action_taken": "brief_updated",
  "agent": "claude-code",
  "session_id": "2026-01-26-obpi-status-session"
}
```

#### obpi-audit Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `obpi_id` | string | Yes | OBPI identifier (format: `OBPI-X.Y.Z-NN`) |
| `adr_id` | string | Yes | Parent ADR identifier (format: `ADR-X.Y.Z`) |
| `brief_status_before` | BriefStatus | No* | Status before audit (verbose format) |
| `brief_status_after` | BriefStatus | No* | Status after audit (verbose format) |
| `brief_status` | BriefStatus | No* | Current status (compact format) |
| `lane` | Lane | No | Lane type (Lite or Heavy) |
| `evidence` | object | No | Evidence payload (structured or raw dict) |
| `evidence_verified` | boolean | No | Whether evidence was verified |
| `criteria_evaluated` | array | No | Per-criterion evaluation results |
| `action_taken` | AuditAction | No | Action taken during audit |
| `description` | string | No | Description for created briefs |
| `gap` | string | No | Gap description if incomplete |
| `test_evidence` | string | No | Compact test evidence string |

*At least one status field is required (verbose or compact).

#### Status Formats

**Verbose format** (status transition):

```json
{
  "brief_status_before": "Accepted",
  "brief_status_after": "Completed"
}
```

**Compact format** (current state):

```json
{
  "brief_status": "Completed"
}
```

### covers-map

Records the mapping between an ADR and its covering tests.

```json
{
  "type": "covers-map",
  "timestamp": "2026-01-26T14:45:00Z",
  "adr_id": "ADR-0.0.19",
  "tests": [
    "tests/warehouse/test_manifest_purity.py::TestManifestPurity",
    "tests/core/test_registrar_invariants.py::TestRegistrarInvariants"
  ],
  "coverage_pct": 46.5
}
```

#### covers-map Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adr_id` | string | Yes | ADR identifier (format: `ADR-X.Y.Z`) |
| `tests` | array | No | Test file/class paths covering this ADR |
| `coverage_pct` | number | No | Coverage percentage (0-100) |

### coverage-run

Records module-level coverage measurement results.

```json
{
  "type": "coverage-run",
  "timestamp": "2026-01-26T14:45:00Z",
  "module": "src/airlineops/warehouse/manifest.py",
  "percent": 46.05,
  "threshold": 40,
  "result": "PASS"
}
```

#### coverage-run Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `module` | string | Yes | Module path |
| `percent` | number | Yes | Coverage percentage achieved (0-100) |
| `threshold` | number | Yes | Coverage threshold required (0-100) |
| `result` | CoverageResult | Yes | Pass/fail result |

### reconciliation

Records summary of a reconciliation session.

```json
{
  "type": "reconciliation",
  "timestamp": "2026-01-26T23:15:00Z",
  "reconciliation_session": "gz-obpi-reconcile",
  "adr_id": "ADR-0.0.19",
  "phase": "full_reconciliation",
  "briefs_audited": 12,
  "pre_sync_drift": 0,
  "completed_count": 10,
  "accepted_count": 2,
  "agent": "claude-code"
}
```

#### reconciliation Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reconciliation_session` | string | Yes | Session identifier |
| `adr_id` | string | Yes | ADR identifier being reconciled |
| `phase` | string | Yes | Reconciliation phase |
| `briefs_audited` | integer | No | Number of briefs audited |
| `pre_sync_drift` | integer | No | Drift count before sync |
| `completed_count` | integer | No | Number of completed briefs |
| `accepted_count` | integer | No | Number of accepted briefs |

---

## Type Definitions

### BriefStatus

Valid ADR/OBPI status values (canonical per GovZero lifecycle):

```text
Pool | Draft | Proposed | Accepted | Completed | Validated | Superseded | Abandoned
```

### AuditResult

Criterion evaluation results:

```text
PASS | FAIL | PARTIAL | DEFERRED | UNKNOWN
```

### Lane

Validation lane types:

```text
Lite | Heavy
```

### AuditAction

Actions taken during audit:

```text
none | brief_updated | created | status_corrected
```

### CoverageResult

Coverage threshold comparison:

```text
PASS | FAIL
```

---

## Legacy Compatibility

Entries created before schema unification may lack the `type` field. The schema auto-detects
entry type from content:

| Content Pattern | Inferred Type |
|-----------------|---------------|
| `obpi_id` + `adr_id` present | `obpi-audit` |
| `reconciliation_session` present | `reconciliation` |

**New entries MUST include the `type` field.**

---

## Validation API

### Python

```python
from opsdev.lib.ledger_schema import (
    validate_ledger_entry,
    is_valid_ledger_entry,
    parse_ledger_entry,
    LedgerValidationError,
)

# Validate and raise on error
entry = {"type": "obpi-audit", ...}
try:
    validate_ledger_entry(entry)  # Returns True or raises
except LedgerValidationError as e:
    print(f"Validation failed: {e}")

# Check validity without exception
if is_valid_ledger_entry(entry):
    print("Valid")

# Parse into typed model
parsed = parse_ledger_entry(entry)
print(f"Type: {parsed.type}, OBPI: {parsed.obpi_id}")
```

### Creating Entries

```python
from opsdev.lib.ledger_schema import (
    ObpiAuditEntry,
    create_timestamp,
)

entry = ObpiAuditEntry(
    timestamp=create_timestamp(),
    obpi_id="OBPI-0.0.21-01",
    adr_id="ADR-0.0.21",
    brief_status="Completed",
    lane="Lite",
    action_taken="brief_updated",
)

# Serialize to JSON for JSONL
import json
line = json.dumps(entry.model_dump(mode="json"))
```

---

## Ledger File Locations

Ledgers are stored per-ADR in the ADR-contained folder structure:

```text
docs/design/adr/{series}/ADR-{id}-{slug}/logs/obpi-audit.jsonl
```

Example:

```text
docs/design/adr/adr-0.0.x/ADR-0.0.19-AIRAC-orchestrated-warehouse-pipeline/logs/obpi-audit.jsonl
```

---

## Extensibility

### Custom Evidence Fields

The `evidence` field in `obpi-audit` entries accepts arbitrary additional fields:

```json
{
  "evidence": {
    "tests_found": ["tests/foo.py"],
    "tests_passed": true,
    "custom_metric": 42,
    "domain_specific_data": {"key": "value"}
  }
}
```

### New Entry Types

To add a new entry type:

1. Create a new model class inheriting from `LedgerEntryBase`
2. Add `type: Literal["new-type"]` as discriminator
3. Add to `LedgerEntry` union type
4. Update `model_map` in validation functions
5. Add tests in `tests/governance/test_ledger_schema.py`
6. Document in this file

---

## See Also

- [Layered Trust Architecture](layered-trust.md) — Tool layer model and boundaries
- [ADR-0.0.21](../../design/adr/adr-0.0.x/ADR-0.0.21-govzero-tooling-layered-trust/ADR-0.0.21-govzero-tooling-layered-trust.md) — Architecture decision record
- [GovZero Charter](charter.md) — Gate definitions and authority
- [ADR Lifecycle](adr-lifecycle.md) — Status transitions
- Python module: `src/opsdev/lib/ledger_schema.py`
