---
name: gz-obpi-reconcile
description: OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, sync ADR table, write ledger proof. Absorbs gz-obpi-audit and gz-obpi-sync.
category: obpi-pipeline
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "3.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  skill-type: "orchestrator"
  govzero_layer: "Layer 1 - Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-obpi-reconcile (v2.0.0)

## Purpose

**Single-command OBPI reconciliation** — audit briefs against actual evidence, fix stale metadata, sync the ADR table, and write ledger proof.

This skill is the unified OBPI verification surface. It absorbs the former
`gz-obpi-audit` (Layer 1 evidence gathering) and `gz-obpi-sync` (Layer 3 table sync).

This skill ensures:

1. Each brief is verified against actual evidence (tests, coverage, @covers tags)
2. Stale briefs are fixed when evidence shows completion
3. Ledger entries record proof of each audit decision
4. ADR OBPI table is synced from corrected brief statuses

**Use when:** Before closeout ceremony, after completing work, periodic housekeeping,
or any time brief status might have drifted from reality.

---

## Trust Model

**Layer 1+2+3 — Full Stack:** This tool verifies evidence (L1), consumes/writes ledger (L2), and syncs derived state (L3).

- **Reads:** Code, tests, coverage reports, brief files, ledger
- **Writes:** Ledger entries (`logs/obpi-audit.jsonl`), brief files (Status, checkboxes), ADR OBPI table
- **Verifies:** Tests pass, coverage meets threshold, @covers tags present

---

## Invocation

```text
/gz-obpi-reconcile ADR-0.0.19
/gz-obpi-reconcile 0.0.19
```

---

## Workflow Phases

```text
╔══════════════════════════════════════════════════════════════════════╗
║  PHASE 1: AUDIT (Layer 1 — Evidence Gathering)                       ║
║  ────────────                                                        ║
║  For each brief:                                                     ║
║    1. Parse acceptance criteria                                      ║
║    2. Search for evidence (tests, coverage, @covers tags)            ║
║    3. Run tests, measure coverage                                    ║
║    4. Evaluate criteria against evidence                             ║
║    5. Write ledger entry (proof)                                     ║
║  Purpose: Verify truth, record proof                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 2: FIX BRIEFS (Layer 2 — Ledger Consumption)                 ║
║  ───────────────────                                                 ║
║  For briefs where all criteria PASS but Status is "Accepted":        ║
║    - Check all criteria boxes                                        ║
║    - Add evidence section                                            ║
║    - Update Status to "Completed"                                    ║
║  Purpose: Correct stale brief metadata                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 3: SYNC ADR TABLE (Layer 3 — File Sync)                      ║
║  ──────────────────────                                              ║
║  Read Status: from each brief, update ADR OBPI table to match.      ║
║  Flag: drift (table ≠ brief), orphans (brief without row),          ║
║        missing (row without brief).                                  ║
║  Purpose: Derived state matches source of truth                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 4: REPORT                                                     ║
║  ──────────────                                                      ║
║  Summary: briefs audited, briefs fixed, table synced, ledger loc     ║
║  Purpose: Human-readable outcome                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Procedure

### Phase 1: Audit Each Brief

**Goal:** Verify brief status reflects actual work completion.

For each `OBPI-{id}-*.md` brief:

```text
Agent action:
1. READ brief file
   - Extract: Status, Lane, Acceptance Criteria, Parent ADR

2. SEARCH for evidence
   - grep tests/ for @covers tags matching ADR
   - grep tests/ for OBPI references
   - Identify test files by keyword heuristics

3. RUN tests (if found)
   - uv run -m unittest -v {test_file}
   - Record: pass/fail, test count

4. MEASURE coverage
   - uv run coverage run -m unittest {test_file}
   - uv run coverage report --include='{module}'
   - Record: percentage vs 40% threshold

5. EVALUATE criteria
   - Map each criterion to evidence
   - Determine PASS/FAIL for each

6. WRITE ledger entry
   - Append JSON line to logs/obpi-audit.jsonl
   - Include: timestamp, evidence, criteria results, action
```

**Output:** Each brief verified, ledger populated with proof.

### Phase 2: Fix Stale Briefs

**Goal:** Update brief metadata when evidence shows completion.

For briefs where all criteria PASS but Status is "Accepted":

```text
Agent action:
1. Check all acceptance criteria boxes
2. Add evidence section with test/coverage references
3. Update Status: Accepted → Completed
4. Add completion date
```

**Output:** Stale briefs corrected to reflect actual completion.

### Phase 3: Sync ADR Table

**Goal:** Propagate corrected brief statuses to the ADR's OBPI table.

For each brief:

1. Read the `Status:` field from the brief file
2. Compare with the ADR OBPI table row
3. If drift detected: update the ADR table to match the brief
4. Flag orphans (brief exists, no table row) and missing (row exists, no brief)

```text
Agent action:
1. READ ADR file, locate OBPI Decomposition table
2. For each brief file, extract Status:
3. COMPARE table row vs brief status
4. UPDATE table rows where drift detected
5. REPORT: drift fixed, orphans, missing
```

### Phase 4: Report

**Goal:** Provide human-readable summary.

```markdown
## ADR-0.0.19 Reconciliation Report

**Timestamp:** 2026-01-26T15:00:00Z

### Progress

| Status | Count | Briefs |
|--------|-------|--------|
| Completed | 5 | 01, 02, 03, 04, 05 |
| Accepted | 4 | 06, 07, 08, 09 |

**Completion:** 56% (5/9)

### Audit Actions

| Brief | Before | After | Action |
|-------|--------|-------|--------|
| OBPI-03 | Accepted | Completed | Fixed (evidence found) |

### Table Sync

| Brief | Table Status | Brief Status | Action |
|-------|-------------|-------------|--------|
| OBPI-03 | Accepted | Completed | FIXED |

### Ledger

Location: `docs/design/adr/adr-0.0.x/ADR-0.0.19-.../logs/obpi-audit.jsonl`
Entries written: 9
```

---

## Agent Execution Contract

When this skill is invoked, the agent MUST:

1. **Execute phases sequentially** — no skipping
2. **Write ledger before fixing briefs** — proof precedes action
3. **Run tests before claiming PASS** — no assumptions
4. **Sync ADR table after fixing briefs** — derived state must match source
5. **Report all findings** — even if no changes made
6. **Stop on blocking errors** — don't proceed if tests fail

### Error Handling

| Error | Action |
|-------|--------|
| Brief not found | Skip, report as missing |
| Tests fail | Log failure, do NOT mark Completed |
| Coverage < 40% | Log gap, do NOT mark Completed |
| ADR table parse error | Stop, report blocker |

---

## Lane-Aware Audit

| Lane | Criteria to Verify |
|------|-------------------|
| **Lite** | Tests pass, coverage ≥40% |
| **Heavy** | Lite + BDD scenarios + docs/manpage updated |

Agent should check brief's `Lane:` field and apply appropriate checks.

---

## Ledger Aggregation

After full reconciliation, ledger contains one entry per brief:

```bash
# Count audited briefs
wc -l logs/obpi-audit.jsonl

# Find fixed briefs
jq -r 'select(.action_taken == "brief_updated") | .obpi_id' logs/obpi-audit.jsonl

# Summary by result
jq -r '.criteria_evaluated[].result' logs/obpi-audit.jsonl | sort | uniq -c
```

---

## Example Session

```text
User: /gz-obpi-reconcile ADR-0.0.19

Agent: Starting OBPI reconciliation for ADR-0.0.19...

## Phase 1: Audit

### OBPI-0.0.19-01 (canonicalize-librarian)
Status: Completed
Lane: Lite
Evidence: tests/librarian/test_policy_contracts.py (15 tests, 52% coverage)
Criteria: 5/5 PASS
Action: None (already Completed)
Ledger: ✓ written

### OBPI-0.0.19-02 (registrar-source-of-truth)
Status: Completed
Lane: Lite
Evidence: tests/core/test_registrar_invariants.py (8 tests, 44% coverage)
Criteria: 5/5 PASS
Action: None (already Completed)
Ledger: ✓ written

### OBPI-0.0.19-03 (warehouse-data-plane)
Status: Accepted
Lane: Lite
Evidence: tests/warehouse/test_manifest_purity.py (10 tests, 46% coverage)
Criteria: 5/5 PASS
Ledger: ✓ written (status drift detected)

[...continues for all briefs...]

## Phase 2: Fix Briefs

### OBPI-0.0.19-03
- All criteria PASS but Status was "Accepted"
- ✓ Checked acceptance criteria boxes
- ✓ Added evidence section
- ✓ Updated Status: Accepted → Completed
- ✓ Added completion date

## Phase 3: Sync ADR Table

OBPI-03: Table status Accepted → Completed (synced from brief)
All other rows already match.

## Phase 4: Report

### ADR-0.0.19 Reconciliation Complete

| Status | Count |
|--------|-------|
| Completed | 5 |
| Accepted | 4 |

**Progress:** 56% (5/9)
**Briefs fixed:** 1 (OBPI-03)
**Table rows synced:** 1
**Ledger entries:** 9
**Location:** docs/design/adr/adr-0.0.x/ADR-0.0.19-.../logs/obpi-audit.jsonl
```

---

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Report what would change, don't modify files |
| `--brief OBPI-NN` | Audit single brief instead of all |
| `--verbose` | Show detailed evidence for each criterion |

---

## Related Skills

| Skill | Role in Workflow |
|-------|------------------|
| `gz-obpi-specify` | Creates the briefs this skill audits |
| `gz-obpi-pipeline` | Calls this skill at Stage 5 |
| `gz-obpi-lock` | Coordinates multi-agent access to briefs |
| `gz-adr-audit` | Gate 5 closeout (uses reconcile for evidence) |
| `gz-adr-recon` | ADR-level reconciliation (Layer 2, ledger-driven) |

---

## Ledger Schema (v1)

**Location:** `docs/design/adr/adr-{series}/ADR-{id}-{slug}/logs/obpi-audit.jsonl`

Each audit appends a JSON line per brief:

```json
{
  "type": "obpi-audit",
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
    "covers_tags": ["@covers ADR-X.Y.Z"]
  },
  "criteria_evaluated": [
    {"criterion": "text", "result": "PASS|FAIL", "evidence": "location"}
  ],
  "action_taken": "none|brief_updated|flagged_for_review",
  "agent": "agent-name"
}
```

**Ledger guarantees:** Append-only, one line per audit, machine-readable.

---

## When to Run

| Trigger | Reason |
|---------|--------|
| Starting work on ADR | Baseline current state |
| Before closeout ceremony | Ensure all briefs accurate |
| After multi-agent session | Catch paperwork drift |
| Weekly housekeeping | Periodic hygiene |
| CI pre-merge | Governance gate (optional) |
| Pipeline Stage 5 | Post-implementation verification |
