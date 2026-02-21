---
name: gz-obpi-audit
description: Audit OBPI brief status against actual code/test evidence. Records proof in JSONL ledger.
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md"
  govzero-gates-covered: "Gate 2 (TDD), brief status integrity"
  govzero_layer: "Layer 1 — Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-obpi-audit (v1.1.0)

## Purpose

Audit an OBPI brief to verify its status matches actual evidence (tests, coverage, code).
**Records all findings in a JSONL ledger** for proof and traceability.

**Problem solved:** Agent completes work but forgets to update brief metadata. Brief stays
"Accepted" when it should be "Completed". Audit detects this and provides evidence trail.

---

## Trust Model

**Layer 1 — Evidence Gathering:** This tool trusts nothing. It verifies actual evidence.

- **Reads:** Code, tests, coverage reports, brief files
- **Writes:** Ledger entries (`logs/obpi-audit.jsonl`)
- **Does NOT modify:** Brief files, ADR tables (those are Layer 2's job)

---

## Invocation

```text
/gz-obpi-audit OBPI-0.0.19-03
/gz-obpi-audit 0.0.19-03
/gz-obpi-audit ADR-0.0.19          # Audit all briefs for an ADR
```

---

## Workflow: Sync → Audit → Sync

The correct workflow is **three-step**:

```text
┌─────────────────────────────────────────────────────────────────┐
│  1. gz-obpi-sync ADR-X.Y.Z                                      │
│     └── Sync ADR table from brief statuses (trust briefs)       │
│                                                                 │
│  2. gz-obpi-audit ADR-X.Y.Z                                     │
│     └── Verify each brief against evidence                      │
│     └── Fix briefs where work done but status stale             │
│     └── Write audit receipt to ledger                           │
│                                                                 │
│  3. gz-obpi-sync ADR-X.Y.Z                                      │
│     └── Re-sync ADR table with corrected brief statuses         │
└─────────────────────────────────────────────────────────────────┘
```

**Why sync twice?** First sync catches manual updates. Audit verifies and fixes. Second sync
propagates fixes to ADR table.

---

## Ledger Output

**Location:** `docs/design/adr/adr-{series}/ADR-{id}-{slug}/logs/obpi-audit.jsonl`

Each audit appends a JSON line:

```json
{
  "type": "obpi-audit",
  "timestamp": "2026-01-26T14:30:00Z",
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
    "coverage_threshold": 40,
    "covers_tags": ["@covers ADR-0.0.19"],
    "docstring_markers": ["PURE FUNCTION", "deterministic"]
  },
  "criteria_evaluated": [
    {"criterion": "Warehouse docstrings document contract → manifest flow", "result": "PASS", "evidence": "manifest.py:266"},
    {"criterion": "Manifest generation is pure", "result": "PASS", "evidence": "test_determinism_same_contract_same_hash"},
    {"criterion": "No policy-specific period calculations", "result": "PASS", "evidence": "grep returned empty"},
    {"criterion": "Tests use generic contract schemas", "result": "PASS", "evidence": "TestGenericContractSchemas class"},
    {"criterion": "Coverage ≥40%", "result": "PASS", "evidence": "46.05%"}
  ],
  "action_taken": "brief_updated",
  "agent": "claude-code",
  "session_id": "optional-session-reference"
}
```

**Ledger guarantees:**
- Append-only (never modify existing lines)
- One line per audit (even if no changes made)
- Machine-readable for downstream tooling

---

## Procedure

### Step 1: Pre-Sync (Optional but Recommended)

```bash
/gz-obpi-sync ADR-0.0.19
```

Ensures ADR table is current before audit begins.

### Step 2: Locate and Parse Brief

```bash
# Find brief file
docs/design/adr/adr-{series}/ADR-{adr-id}-*/briefs/OBPI-{id}-*.md
```

Extract:
- **Status:** (Accepted | Completed)
- **Lane:** (Lite | Heavy)
- **Acceptance Criteria:** (checked `[x]` vs unchecked `[ ]`)
- **Parent ADR:** for `@covers` tag matching

### Step 3: Gather Evidence

#### 3a. Find Tests

```bash
# By @covers tag (preferred)
grep -rn "@covers.*ADR-{adr-id}" tests/

# By OBPI reference
grep -rn "OBPI-{id}" tests/

# By keyword heuristic from brief objective
grep -rn "{keyword}" tests/
```

#### 3b. Run Tests

```bash
uv run -m unittest -v {test_file}
```

Record: test count, pass/fail, runtime

#### 3c. Measure Coverage

```bash
uv run coverage run -m unittest {test_file}
uv run coverage report --include='{module_path}'
```

Record: percentage, threshold comparison

#### 3d. Check Docstrings/Markers

```bash
grep -n "PURE FUNCTION\|deterministic\|purity" {module_path}
```

Record: line numbers, markers found

### Step 4: Evaluate Criteria

For each acceptance criterion:

| Criterion Pattern | Evidence Check |
|-------------------|----------------|
| "Tests exist/pass" | Test file found + exit 0 |
| "Coverage ≥X%" | coverage report ≥ X |
| "Docstrings document X" | grep finds markers |
| "No X in code" | grep returns empty |
| "Y pattern used" | grep finds Y |

### Step 5: Write Ledger Entry

**CRITICAL:** Before making any changes, append a JSONL entry to the ledger.

```bash
# Ensure logs directory exists
mkdir -p docs/design/adr/adr-{series}/ADR-{id}-{slug}/logs/

# Append audit record
echo '{...json...}' >> docs/design/adr/adr-{series}/ADR-{id}-{slug}/logs/obpi-audit.jsonl
```

### Step 6: Update Brief (if warranted)

If all criteria pass but brief status is "Accepted":

1. Check all criteria boxes (`[ ]` → `[x]`)
2. Add evidence section with commands
3. Update status to `Completed`
4. Add completion date

### Step 7: Post-Sync

```bash
/gz-obpi-sync ADR-0.0.19
```

Propagates brief status changes to ADR table.

---

## Lane-Specific Checks

| Lane | Required Evidence |
|------|-------------------|
| **Lite** | Tests pass + coverage ≥40% |
| **Heavy** | Lite + BDD pass + docs/manpage updated |

---

## Audit Modes

### Single Brief Audit

```text
/gz-obpi-audit OBPI-0.0.19-03
```

Audits one brief, writes one ledger entry.

### Full ADR Audit

```text
/gz-obpi-audit ADR-0.0.19
```

Audits all briefs for the ADR:
- Iterates through `briefs/OBPI-{id}-*.md`
- Writes one ledger entry per brief
- Produces summary report

---

## Example Ledger Query

To find all audits for an ADR:

```bash
cat docs/design/adr/adr-0.0.x/ADR-0.0.19-*/logs/obpi-audit.jsonl | jq -s '.'
```

To find briefs that were auto-completed:

```bash
cat logs/obpi-audit.jsonl | jq 'select(.action_taken == "brief_updated")'
```

---

## Failure Modes

| Symptom | Cause | Recovery |
|---------|-------|----------|
| No tests found | Work not done | Write tests with @covers |
| Tests fail | Broken code | Fix before audit |
| Coverage < 40% | Incomplete tests | Add tests |
| Brief says Completed, no evidence | Premature status | Revert to Accepted |

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-obpi-sync` | Syncs ADR table ← brief status (pre/post audit) |
| `gz-adr-verification` | Maps @covers → ADR (evidence source) |
| `gz-obpi-brief` | Creates briefs (audit target) |
| `gz-adr-audit` | Full Gate 5 closeout (uses obpi-audit) |

---

## Ledger Schema (v1)

```json
{
  "type": "obpi-audit",
  "$schema": "OBPI-AUDIT-LEDGER-v1",
  "timestamp": "ISO-8601",
  "obpi_id": "OBPI-X.Y.Z-NN",
  "adr_id": "ADR-X.Y.Z",
  "brief_status_before": "Accepted|Completed",
  "brief_status_after": "Accepted|Completed",
  "lane": "Lite|Heavy",
  "evidence": {
    "tests_found": ["path/to/test.py"],
    "tests_passed": true,
    "test_count": 10,
    "coverage_module": "path/to/module.py",
    "coverage_percent": 46.05,
    "coverage_threshold": 40,
    "covers_tags": ["@covers ADR-X.Y.Z"],
    "docstring_markers": ["marker1", "marker2"],
    "bdd_scenarios": ["optional for Heavy"]
  },
  "criteria_evaluated": [
    {"criterion": "text", "result": "PASS|FAIL", "evidence": "location"}
  ],
  "action_taken": "none|brief_updated|flagged_for_review",
  "agent": "agent-name",
  "session_id": "optional"
}
```
