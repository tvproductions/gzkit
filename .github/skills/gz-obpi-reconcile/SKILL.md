---
name: gz-obpi-reconcile
description: OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, write ledger proof.
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "2.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  skill-type: "orchestrator"
  govzero_layer: "Layer 2 — Ledger Consumption"
  orchestrates: ["gz-obpi-audit"]
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-obpi-reconcile (v2.0.0)

## Purpose

**Single-command OBPI brief reconciliation** that audits briefs against evidence and fixes stale metadata.

This skill ensures:

1. Each brief is verified against actual evidence (tests, coverage, @covers tags)
2. Stale briefs are fixed when evidence shows completion
3. Ledger entries record proof of each audit decision

**Does NOT modify ADR OBPI table** — that is `gz-adr-recon`'s responsibility (Layer 3).

**Use when:** Before closeout ceremony, after completing work, or periodic housekeeping.

---

## Trust Model

**Layer 2 — Ledger Consumption:** This tool trusts ledger entries written by Layer 1.

- **Reads:** Ledger (`logs/obpi-audit.jsonl`), brief files
- **Writes:** Brief files (Status, checkboxes), ledger summary entries
- **Does NOT modify:** ADR OBPI tables (that's `gz-adr-recon`'s job)
- **Does NOT re-verify:** If the ledger says criteria passed, it passed

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
║  PHASE 1: AUDIT                                                      ║
║  ────────────                                                        ║
║  For each brief:                                                     ║
║    1. Parse acceptance criteria                                      ║
║    2. Search for evidence (tests, coverage, @covers tags)            ║
║    3. Evaluate criteria against evidence                             ║
║    4. Write ledger entry (proof)                                     ║
║  Purpose: Verify truth, record proof                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 2: FIX BRIEFS                                                 ║
║  ───────────────────                                                 ║
║  For briefs where all criteria PASS but Status is "Accepted":        ║
║    - Check all criteria boxes                                        ║
║    - Add evidence section                                            ║
║    - Update Status to "Completed"                                    ║
║  Purpose: Correct stale brief metadata                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 3: REPORT                                                     ║
║  ──────────────                                                      ║
║  Summary: briefs audited, briefs fixed, ledger location              ║
║  Note: ADR table NOT updated (use /gz-adr-recon for that)            ║
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

### Phase 3: Report

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
4. **Report all findings** — even if no changes made
5. **Stop on blocking errors** — don't proceed if tests fail
6. **Do NOT modify ADR OBPI table** — delegate to `/gz-adr-recon`

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

## Phase 3: Report

### ADR-0.0.19 Reconciliation Complete

| Status | Count |
|--------|-------|
| Completed | 5 |
| Accepted | 4 |

**Progress:** 56% (5/9)
**Briefs fixed:** 1 (OBPI-03)
**Ledger entries:** 9
**Location:** docs/design/adr/adr-0.0.x/ADR-0.0.19-.../logs/obpi-audit.jsonl

**Note:** ADR OBPI table NOT updated. Run `/gz-adr-recon ADR-0.0.19` to sync table from briefs.
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
| `gz-obpi-audit` | Phase 1 — individual brief audit |
| `gz-adr-verification` | Evidence source — @covers mapping |
| `gz-adr-recon` | ADR table sync (separate tool, Layer 3) |
| `gz-adr-audit` | Gate 5 closeout (orchestrates reconcile) |

---

## When to Run

| Trigger | Reason |
|---------|--------|
| Starting work on ADR | Baseline current state |
| Before closeout ceremony | Ensure all briefs accurate |
| After multi-agent session | Catch paperwork drift |
| Weekly housekeeping | Periodic hygiene |
| CI pre-merge | Governance gate (optional) |
