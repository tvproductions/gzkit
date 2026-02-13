---
name: gz-obpi-sync
description: Sync OBPI status in ADR table from brief source files. Detects drift and reconciles. (Layer 3)
compatibility: Requires GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 — File Sync"
---

# gz-obpi-sync (v1.0.0)

## Purpose

Sync the ADR's OBPI table with the actual status in brief files. Briefs are source of truth; ADR table is derived.

> **⚠️ Warning:** This tool does NOT verify evidence. It reads `Status:` fields from brief files and
> syncs them to the ADR table without checking if code, tests, or documentation actually exist.
> For proof-based sync, use `gz-adr-recon` which consumes ledger entries written by `gz-obpi-audit`.

---

## Trust Model

**Layer 3 — File Sync:** This tool operates at the lowest trust level. It trusts that brief file
metadata is accurate without verification.

```text
Layer 1 (Evidence Gathering):
  gz-obpi-audit → verifies evidence, writes to ledger
           │
           ▼
Layer 2 (Ledger Consumption):
  gz-adr-recon → reads ledger, syncs ADR table (proof-based)
           │
           ▼
Layer 3 (File Sync):    ◄── THIS TOOL
  gz-obpi-sync → reads brief Status: field, syncs ADR table (no proof)
```

**Use cases for Layer 3:**

| Scenario | Why Layer 3 |
|----------|-------------|
| Bootstrapping new ADR | No ledger exists yet |
| Quick status check | Don't need full audit overhead |
| Legacy ADR cleanup | Briefs already marked, no ledger migration |

**When to prefer Layer 2 (`gz-adr-recon`):**

| Scenario | Why Layer 2 |
|----------|-------------|
| Pre-closeout verification | Need audit trail |
| Multi-agent sessions | Ledger provides single source of truth |
| Compliance workflows | Proof required for attestation |

---

## Invocation

```text
/gz-obpi-sync ADR-0.0.17
/gz-obpi-sync 0.0.17
```

---

## Semantics

Like `uv sync` — make derived state match source of truth.

| Source of Truth | Derived |
|-----------------|---------|
| `briefs/OBPI-*.md` (Status field) | ADR OBPI table (Status column) |

---

## Procedure

### Step 1: Locate ADR and Briefs

```bash
# Find ADR file
docs/design/adr/adr-{series}/ADR-{id}-*/ADR-{id}-*.md

# Find associated briefs
docs/design/adr/adr-{series}/ADR-{id}-*/briefs/OBPI-{id}-*.md
```

### Step 2: Extract Status from Each Brief

Parse the `Status:` field from each OBPI brief header. Canonical values:

| Status | Meaning |
|--------|---------|
| Accepted | Brief approved, work may begin |
| Completed | All gates pass, work done |

### Step 3: Compare with ADR Table

Read the OBPI Decomposition table in the ADR. Flag any rows where:

- ADR table status ≠ brief status (drift)
- Brief exists but not in ADR table (orphan)
- ADR table row has no corresponding brief (missing)

### Step 4: Report Status

```markdown
## ADR-{id}: {title} — OBPI Sync

**Completed:** {n}/{total} ({percent}%)

| # | Brief | ADR Table | Brief File | Action |
|---|-------|-----------|------------|--------|
| 12 | OBPI-0.0.17-12 | Pending | Completed | UPDATE |
| 15 | OBPI-0.0.17-15 | Pending | Completed | UPDATE |
...
```

### Step 5: Reconcile (Fix Drift)

Update ADR table rows to match brief source status.

---

## Example

```text
$ /gz-obpi-sync ADR-0.0.17

## ADR-0.0.17: Dataset Package Lifecycle — OBPI Sync

**Completed:** 16/21 (76%)

Drift detected:
| # | Brief | ADR Table | Brief File | Action |
|---|-------|-----------|------------|--------|
| 12 | OBPI-0.0.17-12 | Pending | Completed | FIXED |
| 15 | OBPI-0.0.17-15 | Pending | Completed | FIXED |

ADR table synced with brief source files.
```

---

## Related Skills

| Skill | Layer | Purpose |
|-------|-------|---------|
| gz-obpi-audit | Layer 1 | Verify evidence, write ledger entries |
| gz-adr-recon | Layer 2 | Proof-based ADR table sync from ledger |
| gz-obpi-reconcile | Layer 2 | Orchestrate audit + sync workflow |
| gz-adr-manager | — | Create/book ADRs |
| gz-adr-sync | Layer 3 | Sync ADR index/status from ADR files |
| gz-obpi-brief | — | Create OBPI briefs |
| gz-adr-audit | Layer 2 | Gate 5 verification |
