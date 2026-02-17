---
name: gz-adr-recon
description: ADR OBPI table reconciliation — Read ledger entries and sync ADR OBPI table status.
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  skill-type: "reconciler"
  govzero_layer: "Layer 2 — Ledger Consumption"
  consumes: ["logs/obpi-audit.jsonl"]
---

# gz-adr-recon (v1.0.0)

## Purpose

**ADR OBPI table reconciliation** that reads ledger entries and syncs ADR OBPI table status.

This skill ensures:

1. ADR OBPI table Status column matches ledger proof
2. Drift between table metadata and ledger entries is detected
3. Missing ledger proof is reported (brief has no audit receipt)

**Layer 2 — Ledger Consumption:** This tool **trusts the ledger**. It does NOT re-verify evidence, run tests, or check code. It reads proof written by Layer 1 tools (`gz-obpi-audit`) and synchronizes ADR tables accordingly.

**Use when:** After running `gz-obpi-reconcile`, before closeout ceremony, or when ADR table is stale.

---

## Invocation

```text
/gz-adr-recon ADR-0.0.21
/gz-adr-recon 0.0.21
```

**CLI equivalent:**

```bash
uv run -m opsdev adr recon ADR-0.0.21
uv run -m opsdev adr recon ADR-0.0.21 --dry-run
uv run -m opsdev adr recon ADR-0.0.21 --verbose
```

---

## Workflow Phases

```text
╔══════════════════════════════════════════════════════════════════════╗
║  PHASE 1: READ LEDGER                                                ║
║  ────────────────────                                                ║
║  1. Locate ADR folder                                                ║
║  2. Find logs/obpi-audit.jsonl                                       ║
║  3. Parse entries for this ADR                                       ║
║  4. Build map: OBPI-ID → latest ledger status                        ║
║  Purpose: Collect proof from Layer 1 tools                           ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 2: PARSE ADR TABLE                                            ║
║  ───────────────────────                                             ║
║  1. Read ADR markdown file                                           ║
║  2. Find OBPI Decomposition table                                    ║
║  3. Extract: # | OBPI | ... | Status for each row                    ║
║  Purpose: Capture current table metadata                             ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 3: DETECT DRIFT                                               ║
║  ──────────────────────                                              ║
║  Compare ledger status vs table status:                              ║
║    - DRIFT: ledger says Completed, table says Accepted               ║
║    - MISSING: table row has no ledger entry (no proof)               ║
║    - MATCH: ledger and table agree                                   ║
║  Purpose: Identify reconciliation work                               ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 4: SYNC TABLE                                                 ║
║  ─────────────────────                                               ║
║  For drift items (unless --dry-run):                                 ║
║    - Update table Status column to match ledger                      ║
║  Purpose: Align table with proof                                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  PHASE 5: REPORT                                                     ║
║  ──────────────────                                                  ║
║  Summary: briefs checked, drift found, table updated                 ║
║  Purpose: Human-readable outcome                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Procedure

### Phase 1: Read Ledger

**Goal:** Collect proof from Layer 1 tools.

```text
Agent action:
1. LOCATE ADR folder
   - docs/design/adr/{series}/ADR-{id}-{slug}/

2. FIND ledger file
   - logs/obpi-audit.jsonl within ADR folder

3. PARSE entries
   - Filter for entries matching this ADR
   - For each OBPI, keep latest entry (by timestamp)

4. BUILD map
   - OBPI-0.0.21-01 → Completed
   - OBPI-0.0.21-02 → Completed
   - ...
```

**Output:** Map of OBPI IDs to their latest ledger status.

### Phase 2: Parse ADR Table

**Goal:** Capture current table metadata.

```text
Agent action:
1. READ ADR markdown
   - ADR-{id}-{slug}.md

2. FIND OBPI table
   - Look for "OBPI Decomposition" heading
   - Parse markdown table with columns: # | OBPI | ... | Status

3. EXTRACT rows
   - Row 1: OBPI-0.0.21-01, Status: Accepted
   - Row 2: OBPI-0.0.21-02, Status: Completed
   - ...
```

**Output:** List of table rows with OBPI ID and current status.

### Phase 3: Detect Drift

**Goal:** Identify reconciliation work.

```text
Agent action:
For each table row:
  1. Look up OBPI in ledger map
  2. Compare:
     - If ledger status != table status → DRIFT
     - If OBPI not in ledger → MISSING
     - If ledger status == table status → MATCH
```

**Output:** List of drift items with before/after status.

### Phase 4: Sync Table

**Goal:** Align table with proof (unless --dry-run).

```text
Agent action:
For each DRIFT item:
  1. Find row in ADR markdown
  2. Update Status column to match ledger
  3. Write updated file
```

**Output:** ADR markdown updated with correct statuses.

### Phase 5: Report

**Goal:** Provide human-readable summary.

```markdown
## ADR-0.0.21 Table Reconciliation Report

**Timestamp:** 2026-01-29T15:00:00Z

### Summary

| Metric | Count |
|--------|-------|
| Table rows | 9 |
| Ledger entries | 7 |
| Drift detected | 2 |
| Missing proof | 2 |

### Drift Items

| OBPI | Table Status | Ledger Status | Action |
|------|--------------|---------------|--------|
| OBPI-0.0.21-03 | Accepted | Completed | Updated |
| OBPI-0.0.21-04 | Accepted | Completed | Updated |

### Missing Proof

| OBPI | Table Status | Note |
|------|--------------|------|
| OBPI-0.0.21-08 | Accepted | No ledger entry — run /gz-obpi-audit |
| OBPI-0.0.21-09 | Accepted | No ledger entry — run /gz-obpi-audit |
```

---

## Agent Execution Contract

When this skill is invoked, the agent MUST:

1. **Trust the ledger** — Do NOT re-verify evidence
2. **Read ledger before modifying table** — Proof precedes action
3. **Report all findings** — Even if no changes made
4. **Respect --dry-run** — Report only, don't modify files
5. **Handle missing ledger gracefully** — Report as "no proof" not "failure"

### Error Handling

| Error | Action |
|-------|--------|
| ADR folder not found | Stop, report as blocker |
| Ledger file missing | Report as "no ledger — run gz-obpi-reconcile first" |
| Table parse error | Stop, report malformed table |
| Partial ledger | Report missing entries, sync what exists |

---

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Report what would change, don't modify files |
| `--verbose` | Show detailed output for each OBPI |

---

## Example Session

```text
User: /gz-adr-recon ADR-0.0.21

Agent: Starting ADR table reconciliation for ADR-0.0.21...

## Phase 1: Read Ledger

Location: docs/design/adr/adr-0.0.x/ADR-0.0.21-.../logs/obpi-audit.jsonl
Entries found: 7

Ledger status map:
- OBPI-0.0.21-01: Completed
- OBPI-0.0.21-02: Completed
- OBPI-0.0.21-03: Completed
- OBPI-0.0.21-04: Completed
- OBPI-0.0.21-05: (no entry)
- OBPI-0.0.21-06: (no entry)
- OBPI-0.0.21-07: Accepted

## Phase 2: Parse ADR Table

Table rows found: 9

## Phase 3: Detect Drift

| OBPI | Table | Ledger | Status |
|------|-------|--------|--------|
| OBPI-01 | Accepted | Completed | DRIFT |
| OBPI-02 | Completed | Completed | MATCH |
| OBPI-03 | Accepted | Completed | DRIFT |
| OBPI-04 | Accepted | Completed | DRIFT |
| OBPI-05 | Accepted | (none) | MISSING |
| OBPI-06 | Accepted | (none) | MISSING |
| OBPI-07 | Accepted | Accepted | MATCH |
| OBPI-08 | Accepted | (none) | MISSING |
| OBPI-09 | Accepted | (none) | MISSING |

## Phase 4: Sync Table

Updated 3 rows:
- OBPI-01: Accepted → Completed
- OBPI-03: Accepted → Completed
- OBPI-04: Accepted → Completed

## Phase 5: Report

**ADR-0.0.21 Table Reconciliation Complete**

| Metric | Count |
|--------|-------|
| Table rows | 9 |
| Rows synced | 3 |
| Missing proof | 4 |

**Note:** 4 briefs have no ledger entry. Run `/gz-obpi-audit` to generate proof.
```

---

## Related Skills

| Skill | Role in Workflow |
|-------|------------------|
| `gz-obpi-audit` | Layer 1 — writes ledger entries (run first) |
| `gz-obpi-reconcile` | Layer 2 — orchestrates audit + brief fix |
| `gz-adr-audit` | Layer 2 — Gate 5 closeout (consumes this tool's output) |
| `gz-adr-sync` | Layer 3 — index/status file sync |

---

## When to Run

| Trigger | Reason |
|---------|--------|
| After gz-obpi-reconcile | Sync table after briefs updated |
| Before closeout ceremony | Ensure table reflects proof |
| After multi-agent session | Catch ADR table drift |
| When table looks stale | Manual reconciliation |

---

## Trust Model

```text
Layer 1 (Evidence Gathering):
  gz-obpi-audit → writes proof to ledger
           │
           ▼
     logs/obpi-audit.jsonl
           │
           ▼
Layer 2 (Ledger Consumption):
  gz-adr-recon → reads ledger, syncs ADR table
           │
           ▼
     ADR OBPI table (updated)
```

**This tool trusts the ledger.** It does not:
- Run tests
- Check coverage
- Verify @covers tags
- Read brief files

It only reads ledger entries and updates the ADR table to match.
