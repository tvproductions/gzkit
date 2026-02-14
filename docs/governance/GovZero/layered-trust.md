# GovZero Layered Trust Architecture

**Status:** Active
**Last reviewed:** 2026-01-29
**Parent ADR:** ADR-0.0.21 (GovZero Tooling Layered Trust Architecture)

---

## Overview

GovZero tooling follows a **layered trust architecture** where tools are organized by their
relationship to evidence:

- **Layer 1** tools gather evidence and write proof to the ledger
- **Layer 2** tools consume ledger entries and trust them as proof
- **Layer 3** tools synchronize files without verification

This separation enables cross-verification (tools check each other's work) and creates an
audit trail (ledger entries are receipts).

---

## The Three Layers

```text
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: Evidence Gathering                                        │
│  ───────────────────────────                                        │
│  Tools: gz-obpi-audit, gz-adr-verification, coverage reporters      │
│  Action: Run tests, measure coverage, verify criteria               │
│  Output: Ledger entries (proof)                                     │
│  Trust: Trusts nothing — verifies everything                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ writes
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        JSONL LEDGER FILES                           │
│              logs/obpi-audit.jsonl, covers-map.jsonl                │
│                    (structured proof records)                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ reads
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: Ledger Consumption                                        │
│  ───────────────────────────                                        │
│  Tools: gz-obpi-reconcile, gz-adr-recon, gz-adr-audit               │
│  Action: Read ledger, update metadata, generate reports             │
│  Output: Updated briefs, ADR tables, audit reports                  │
│  Trust: Trusts ledger entries — does NOT re-verify                  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ updates
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: File Synchronization                                      │
│  ────────────────────────────                                       │
│  Tools: gz-adr-sync, gz-obpi-sync                                   │
│  Action: Sync index files from source files                         │
│  Output: adr_index.md, adr_status.md                                │
│  Trust: Trusts file content — no verification                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Evidence Gathering

**Purpose:** Verify actual work and record proof.

**Principle:** Trust nothing. Run the tests. Measure the coverage. Check the code.

| Tool | What It Verifies | Ledger Entry Type |
|------|------------------|-------------------|
| `gz-obpi-audit` | Brief acceptance criteria vs evidence | `obpi-audit` |
| `gz-adr-verification` | @covers tags → test mapping | `covers-map` |
| Coverage reporters | Module coverage vs threshold | `coverage-run` |

**Workflow:** Read source artifacts → Execute verification → Write ledger entry → Do NOT update metadata files

```bash
# Example: gz-obpi-audit verifies a brief and writes ledger entry
/gz-obpi-audit OBPI-0.0.19-03

# Output: ledger entry in logs/obpi-audit.jsonl
{"type": "obpi-audit", "obpi_id": "OBPI-0.0.19-03", "criteria_evaluated": [...], ...}
```

---

## Layer 2: Ledger Consumption

**Purpose:** Update metadata based on verified proof.

**Principle:** Trust the ledger. If Layer 1 said it passed, it passed.

| Tool | What It Updates | Ledger Entry Consumed |
|------|-----------------|----------------------|
| `gz-obpi-reconcile` | Brief files (Status, checkboxes) | `obpi-audit` |
| `gz-adr-recon` | ADR OBPI tables | `obpi-audit`, `reconciliation` |
| `gz-adr-audit` | Audit reports, attestation | All entry types |

**Workflow:** Read ledger → Trust results (no re-verification) → Update metadata → Write summary entry

```bash
# Example: gz-obpi-reconcile reads ledger, fixes stale briefs
/gz-obpi-reconcile ADR-0.0.19

# Reads: logs/obpi-audit.jsonl
# Updates: briefs/OBPI-0.0.19-*.md (Status, checkboxes)
# Does NOT update: ADR OBPI table (that's gz-adr-recon's job)
```

---

## Layer 3: File Synchronization

**Purpose:** Keep index files in sync with source files.

**Principle:** Read file metadata, update indexes. No verification.

| Tool | Source | Target |
|------|--------|--------|
| `gz-adr-sync` | ADR files | adr_index.md, adr_status.md |
| `gz-obpi-sync` | Brief files | ADR OBPI table |
| `gz-adr-manager` | User input | New ADR + briefs |
| `gz-obpi-brief` | User input | New OBPI brief |

**Workflow:** Read source file metadata → Update target index → No verification (trusts content as-is)

**Layer 3 vs Layer 2 for OBPI Table Sync:**

Two tools can update the ADR OBPI table:

| Tool | Layer | Source | Use Case |
|------|-------|--------|----------|
| `gz-adr-recon` | 2 | Ledger entries | Proof-based sync (preferred) |
| `gz-obpi-sync` | 3 | Brief file `Status:` field | Bootstrapping, quick sync (no proof) |

**When to use Layer 3 (`gz-obpi-sync`):**

- Bootstrapping a new ADR before any ledger exists
- Quick status check without full audit overhead
- Legacy ADR cleanup where briefs are already marked

**When to use Layer 2 (`gz-adr-recon`):**

- Pre-closeout verification (audit trail required)
- Multi-agent sessions (ledger is single source of truth)
- Compliance workflows (proof required for attestation)

---

## Tool Boundaries

| Tool | Layer | Reads | Writes | Does NOT Touch |
|------|-------|-------|--------|----------------|
| gz-obpi-audit | 1 | Code, tests, briefs | Ledger | Brief files, ADR table |
| gz-adr-verification | 1 | Tests (@covers) | Ledger | ADR files |
| gz-obpi-reconcile | 2 | Ledger, briefs | Brief files, ledger | ADR OBPI table |
| gz-adr-recon | 2 | Ledger | ADR OBPI table | Brief files |
| gz-adr-audit | 2 | Ledger | Audit report | Source files |
| gz-adr-sync | 3 | ADR files | Index files | Ledger |
| gz-obpi-sync | 3 | Brief files | ADR OBPI table | Ledger |

---

## When to Use Each Tool

| Scenario | Tool | Layer |
|----------|------|-------|
| "Did this brief's work get done?" | gz-obpi-audit | 1 |
| "Which tests cover this ADR?" | gz-adr-verification | 1 |
| "Update stale brief metadata" | gz-obpi-reconcile | 2 |
| "Sync ADR table from ledger (proof-based)" | gz-adr-recon | 2 |
| "Prepare for closeout ceremony" | gz-adr-audit | 2 |
| "Update ADR index after status change" | gz-adr-sync | 3 |
| "Quick ADR table sync (no proof)" | gz-obpi-sync | 3 |

### Common Workflows

**Before closeout ceremony:**

```text
1. gz-obpi-audit (Layer 1) — verify each brief, write ledger
2. gz-obpi-reconcile (Layer 2) — fix stale briefs from ledger
3. gz-adr-recon (Layer 2) — sync ADR table from ledger
4. gz-adr-audit (Layer 2) — generate audit report for attestation
```

**After completing work on a brief:**

```text
1. gz-obpi-audit (Layer 1) — verify the brief, write ledger
2. gz-obpi-reconcile (Layer 2) — update brief Status if criteria pass
```

---

## Design Principles

### 1. Ledger Is the API

Tools communicate via ledger entries, not direct calls. Layer 1 writes; Layer 2 reads.

### 2. Verification Happens Once

Layer 1 verifies. Layer 2 trusts the verification. No re-running tests in Layer 2.

### 3. Clear Ownership

- OBPI tools own brief-level concerns
- ADR tools own ADR-level concerns
- No tool reaches across boundaries

### 4. Audit Trail

Every verification produces a ledger entry. The trail is the proof.

---

## Skill File Annotations

Each skill's SKILL.md includes a `govzero_layer` metadata field:

```yaml
metadata:
  govzero_layer: "Layer 1 — Evidence Gathering"
  # or
  govzero_layer: "Layer 2 — Ledger Consumption"
  # or
  govzero_layer: "Layer 3 — File Sync"
```

**Canonical values:**

| Value | Meaning |
|-------|---------|
| `"Layer 1 — Evidence Gathering"` | Verifies work, writes proof to ledger |
| `"Layer 2 — Ledger Consumption"` | Reads ledger, trusts proof, updates metadata |
| `"Layer 3 — File Sync"` | Syncs files without verification |

**Prose requirement:** Each skill should also include a description section (e.g., `## Trust Model`
or `**Layer:**` callout) explaining the layer behavior in human terms.

This makes the architecture explicit and machine-readable.

---

## See Also

- [Ledger Schema](ledger-schema.md) — JSONL entry format specifications
- [GovZero Charter](charter.md) — Gate definitions and authority
- [ADR-0.0.21](../../design/adr/adr-0.0.x/ADR-0.0.21-govzero-tooling-layered-trust/ADR-0.0.21-govzero-tooling-layered-trust.md) — Architecture decision record
- [Audit Protocol](audit-protocol.md) — Closeout ceremony procedure
