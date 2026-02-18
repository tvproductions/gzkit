# Architectural Enforcement Protocol

**Purpose:** Mechanisms to ensure agents follow architecture, not just read it.
**Status:** Proposed
**Last reviewed:** 2026-02-04

---

## Problem Statement

Documentation makes the right answer *findable*. It doesn't make it *unavoidable*.

Previous failures:

- OBPI briefs said "delegate to existing adapters"
- Agents created standalone implementations anyway
- Tests passed but architecture was violated

---

## Three Enforcement Layers

### Layer 1: Code-Level Validation (Automated)

**What:** Tests that validate architectural compliance via AST analysis.

**Location:** `tests/architecture/`

**Implementation:**

```python
# tests/architecture/test_adapter_compliance.py
"""Validate all adapters follow delegation pattern (ADR-0.1.16)."""

import ast
from pathlib import Path
import unittest

ADAPTER_DIR = Path("src/airlineops/warehouse/adapters")
REQUIRED_IMPORT = "airlineops.warehouse.ingest.adapters"


class TestAdapterArchitecturalCompliance(unittest.TestCase):
    """AST-based validation of adapter delegation rule."""

    def test_all_adapters_import_from_legacy(self):
        """Every adapter MUST import from warehouse/ingest/adapters/."""
        violations = []

        for adapter_file in ADAPTER_DIR.glob("*.py"):
            if adapter_file.name.startswith("_"):
                continue

            tree = ast.parse(adapter_file.read_text())
            has_required_import = False

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and REQUIRED_IMPORT in node.module:
                        has_required_import = True
                        break

            if not has_required_import:
                violations.append(adapter_file.name)

        self.assertEqual(
            violations, [],
            f"Adapters missing delegation imports: {violations}\n"
            f"Per ADR-0.1.16, adapters MUST import from {REQUIRED_IMPORT}"
        )

    def test_adapters_under_line_limit(self):
        """Adapters should be thin facades (<300 lines)."""
        violations = []

        for adapter_file in ADAPTER_DIR.glob("*.py"):
            if adapter_file.name.startswith("_"):
                continue

            line_count = len(adapter_file.read_text().splitlines())
            if line_count > 300:
                violations.append(f"{adapter_file.name}: {line_count} lines")

        self.assertEqual(
            violations, [],
            f"Adapters exceeding 300 lines (too much business logic): {violations}"
        )
```

**Run:** `uv run -m unittest tests.architecture.test_adapter_compliance -v`

---

### Layer 2: Agent Checkpoint Protocol (Process)

**What:** Required verification output BEFORE any implementation.

**Add to OBPI template:**

```markdown
### ARCHITECTURAL VERIFICATION (MANDATORY — BEFORE CODE)

**Complete this section BEFORE writing any code. Copy-paste and fill in:**

```text
## Architectural Checkpoint

**Bounded Context:** [Discovery | Planning | Acquisition | Ingestion | Validation | Reporting]

**I am working in the ______ context, which:**
- OWNS: [list what this context owns]
- DOES NOT OWN: [list what this context does NOT own]

**Invariants that apply to this work:**
- [ ] Single-active HOT contract (if applicable)
- [ ] Single-active COLD contract (if applicable)
- [ ] Adapter delegation rule (if adapter work)
- [ ] Manifest determinism (if manifest work)

**Canonical format for this dataset:** [YYYY-Qn | YYYY-MM | YYCC | YYYY | STATIC]

**I will DELEGATE to:** [list existing modules I will import from]
**I will IMPLEMENT:** [list only the thin facade/protocol compliance]

**STOP CONDITIONS:**
- [ ] I cannot identify my bounded context → STOP, ask human
- [ ] I cannot find the module to delegate to → STOP, ask human
- [ ] I'm writing >50 lines of business logic → STOP, wrong approach
```

**If you cannot complete this checkpoint, STOP and emit BLOCKERS.**

---

### Layer 3: Architectural Compliance Check (Skill)

**What:** A runnable chore that audits the codebase against `config/architecture.json`.

**Location:** `docs/governance/GovZero/` policy + `gz` quality/validation commands

**Chore definition:**

```json
{
  "architectural-compliance-audit": {
    "description": "Audit code against architecture.json invariants",
    "command": "uv run gz check",
    "checks": [
      "adapter_delegation_rule",
      "bounded_context_imports",
      "invariant_enforcement"
    ]
  }
}
```

**Output format:**

```text
## Architectural Compliance Audit

### Adapter Delegation Rule (ADR-0.1.16)
✓ bts_db1b_ticket.py — imports from adapters/bts/db1b_ticket
✓ bts_db1b_coupon.py — imports from adapters/bts/db1b_coupon
✗ bts_foo.py — MISSING delegation import

### Bounded Context Violations
✓ No cross-context imports detected

### Invariant Enforcement
✓ Single-active HOT — enforced in registrar.py:407
✓ Single-active COLD — enforced in registrar.py:184

**Result:** 1 violation detected. See above.
```

---

## Integration with OBPI Workflow

### Before Implementation

1. Agent reads `docs/design/architecture/system-manifest.md`
2. Agent completes **Architectural Checkpoint** in brief
3. Human reviews checkpoint before approving implementation

### During Implementation

1. Agent runs `uv run -m unittest tests.architecture -v` after each file
2. Violations fail immediately — no "fix later"

### After Implementation

1. Agent runs architectural compliance chore
2. Results included in OBPI completion evidence
3. Human attestation includes architectural compliance

---

## Enforcement Matrix

| Mechanism | When | What It Catches | Automated? |
|-----------|------|-----------------|------------|
| AST import tests | CI/pre-commit | Missing delegation imports | ✓ |
| Line count tests | CI/pre-commit | Too much business logic | ✓ |
| Checkpoint protocol | Before coding | Wrong bounded context | ✗ (human review) |
| Compliance chore | After coding | Cross-context violations | ✓ |
| Human attestation | Before completion | Architectural misalignment | ✗ (human gate) |

---

## Failure Modes This Prevents

| Previous Failure | Enforcement That Blocks It |
|------------------|---------------------------|
| Standalone adapter (no delegation) | AST import test fails |
| Adapter with 500 lines of logic | Line count test fails |
| Agent in wrong bounded context | Checkpoint requires explicit declaration |
| Agent bypasses registrar | Cross-context import check |
| Agent doesn't understand architecture | Checkpoint forces articulation |

---

## Implementation Checklist

- [ ] Create `tests/architecture/test_adapter_compliance.py`
- [ ] Add architectural checkpoint to OBPI template
- [ ] Create architectural compliance chore
- [ ] Add to pre-commit hooks (optional)
- [ ] Update AGENTS.md with enforcement requirements

---

## See Also

- [System Manifest](../architecture/system-manifest.md) — Bounded contexts and invariants
- [ADR-0.1.16](../../design/adr/adr-0.1.x/ADR-0.1.16-unified-adapter-architecture/) — Adapter delegation rule
- [OBPI Template](../../../.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md) — Brief format
