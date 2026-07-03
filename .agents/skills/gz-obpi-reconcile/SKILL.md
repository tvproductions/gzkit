---
name: gz-obpi-reconcile
persona: main-session
description: OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, sync ADR table, write ledger proof. Absorbs gz-obpi-audit and gz-obpi-sync.
category: obpi-pipeline
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "3.2.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  skill-type: "orchestrator"
  govzero_layer: "Layer 1 - Evidence Gathering"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-03
model: sonnet
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

### Common Rationalizations

These thoughts mean STOP — you are about to skip evidence-backed verification:

| Thought | Reality |
|---------|---------|
| "The briefs look correct, reconciliation is unnecessary" | Brief status drifts silently. Only evidence-backed auditing reveals the actual state. |
| "Tests pass so the OBPIs must be complete" | Tests verify code behavior, not brief metadata. A passing test suite with stale brief statuses is common. |
| "I'll update the ADR table manually instead" | Manual table updates bypass the ledger. Phase 2-to-3 flow ensures proof precedes derived state. |
| "One brief is still in progress, I'll reconcile the rest later" | Partial reconciliation creates inconsistent snapshots. Run for the full ADR. |
| "The ledger already has entries from a previous audit" | Stale ledger entries do not reflect current evidence. Each reconciliation writes fresh proof. |
| "Coverage is close to 40%, I'll round up" | The threshold is fail-closed. 39.9% is FAIL, not "close enough." |

### Red Flags

- ADR OBPI table shows "Completed" but brief file still says "Accepted"
- Ledger entries are older than the most recent code changes to OBPI-scoped files
- Agent updates ADR table directly without running Phase 1 audit first
- Brief marked Completed without evidence section citing test files and coverage
- Phase 3 (table sync) runs before Phase 1 (audit) — derived state updated before source verified

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

Use `gz obpi audit` as the deterministic evidence step — it locates tests,
runs them, measures coverage, evaluates criteria, and appends the
`obpi-audit` ledger entry in one call. The ledger schema it emits matches
the Ledger Schema v1 documented below (`obpi_audit_cmd._build_entry`).

```bash
# Audit a single OBPI
uv run gz obpi audit OBPI-X.Y.Z-NN

# Audit all OBPIs for an ADR in one pass
uv run gz obpi audit --adr ADR-X.Y.Z

# JSON output for programmatic consumption
uv run gz obpi audit OBPI-X.Y.Z-NN --json
```

After the audit, emit the reconcile receipt using:

```bash
uv run gz obpi emit-receipt OBPI-X.Y.Z-NN --event validated
```

**Phantom OBPI remediation:** If Phase 1 surfaces an OBPI that exists in
the ledger graph (via `obpi_created` event) but has no on-disk brief file,
use `gz obpi withdraw` to clean it from the graph before Phase 2. Both
withdraw and supersede are witnessed transitions (a `human_attested` witness
per the OBPI-01 state machine), so each requires `--attestor`:

```bash
uv run gz obpi withdraw OBPI-X.Y.Z-NN --reason "phantom entry from promotion" --attestor "<human>"
```

**Superseded-OBPI remediation:** When a reconciled OBPI has been replaced by
another that carries its intent forward (not merely retired), record the
replacement lineage with `gz obpi supersede` rather than a bare withdraw —
the superseding OBPI id is preserved on the graph node:

```bash
uv run gz obpi supersede OBPI-X.Y.Z-NN --by OBPI-X.Y.Z-MM --rationale "replaced by redesigned brief" --attestor "<human>"
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
| `gz-adr-sync` | ADR-level reconciliation and full governance sync (Layers 1-3) |

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
