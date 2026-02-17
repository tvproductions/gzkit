---
name: gz-adr-verification
description: Generate ADR→tests verification report using @covers mappings. GovZero v6 skill.
compatibility: GovZero v6 framework; verifies ADR→tests traceability for Gate 2 compliance
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md"
  govzero-gates-covered: "Gate 2 (TDD), linkage verification"
  govzero_layer: "Layer 1 — Evidence Gathering"
opsdev_command: adr verify
invocation: uv run -m opsdev adr verify
---

# gz-adr-verification

Discover @covers decorator mappings and generate ADR→tests verification report.

**Command:** `uv run -m opsdev adr verify`

**Layer:** Layer 1 — Evidence Gathering

---

## When to Use

- After adding new tests with @covers decorators
- After creating or updating ADRs
- To verify ADR test coverage
- As part of governance audits

---

## Procedure

### 1. Run Verification

Execute the verification command:

```bash
uv run -m opsdev adr verify
```

This scans tests for @covers decorators and maps them to ADRs.

### 2. Review Report

The command generates:

- ADR→tests mapping (which tests cover each ADR)
- Uncovered ADRs (ADRs without test coverage)
- Coverage statistics

### 3. Address Gaps

For uncovered ADRs:

1. Identify the ADR requirements
2. Write tests covering the ADR behavior
3. Add `@covers("ADR-X.Y.Z")` decorator to tests
4. Re-run verification to confirm coverage

---

## Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--quiet` | `false` | Suppress non-essential output |
| `--verbose` | `false` | Enable verbose output |

---

## What It Checks

| Check | Description |
|-------|-------------|
| @covers mappings | Tests decorated with `@covers("ADR-...")` |
| ADR existence | Referenced ADRs exist in docs/design/adr/ |
| Coverage gaps | ADRs without corresponding tests |

---

## Policy

- **Dual output:** Writes ledger entries AND prints human-readable report to stdout
- **@covers pattern:** Tests use `@covers("ADR-X.Y.Z")` decorator
- **ADR naming:** ADRs follow `ADR-X.Y.Z` semver pattern

---

## Ledger Interaction

| Operation | Target | Description |
|-----------|--------|-------------|
| **Writes** | `logs/covers-map.jsonl` | One entry per ADR with @covers tests |
| **Reads** | None | |

Each run appends entries to the ledger:

```json
{
  "type": "covers-map",
  "adr_id": "ADR-0.0.19",
  "tests": ["tests/warehouse/test_manifest.py"],
  "coverage_pct": null,
  "timestamp": "2026-01-29T12:00:00Z",
  "schema_version": "govzero.ledger.v1"
}
```

---

## Failure Modes

| Symptom | Cause | Recovery |
|---------|-------|----------|
| Uncovered ADR | No tests reference the ADR | Write tests with @covers decorator |
| Invalid ADR reference | @covers points to non-existent ADR | Fix decorator to valid ADR ID |
| Parse error | Malformed @covers decorator | Fix decorator syntax |

---

## References

- Command: `src/opsdev/commands/governance/cli_setup.py`
- Library: `src/opsdev/lib/adr_governance.py`
- Related: `.github/skills/gz-adr-audit/SKILL.md`
