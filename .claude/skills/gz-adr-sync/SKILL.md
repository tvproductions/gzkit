---
name: gz-adr-sync
description: Sync ADR index and status tables from ADR source files. Detects drift and reconciles.
compatibility: GovZero v6 framework; maintains canonical ADR registry and lifecycle state tables
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/adr-lifecycle.md, docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md"
  govzero-gates-covered: "All (registry maintenance)"
  govzero_layer: "Layer 3 — File Sync"
opsdev_command: adr-docs
invocation: uv run -m opsdev adr-docs
---

# gz-adr-sync (v6.0.0)

Sync ADR index and status tables from ADR source files.

---

## Semantics

Like `uv sync` — make derived state match source of truth.

| Source of Truth | Derived |
|-----------------|---------|
| `ADR-*.md` files | `adr_index.md`, `adr_status.md` |

---

## Trust Model

**Layer 3 — File Sync:** This tool syncs files without verification.

- **Reads:** ADR markdown files (Status, Date fields)
- **Writes:** `adr_index.md`, `adr_status.md`
- **Does NOT verify:** ADR content correctness, OBPI completion
- **Does NOT touch:** Ledger files

---

## When to Use

- After adding or updating ADRs
- When ADR status changes
- As part of docs composite

---

## Invocation

```text
/gz-adr-sync
```

---

## Procedure

### Step 1: Sync ADR Index + Status Table

```bash
uv run -m opsdev adr-docs
```

This updates `docs/design/adr/adr_index.md` and `docs/design/adr/adr_status.md`.

---

## Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--quiet` | `false` | Suppress non-essential output |

---

## Sequence

```text
gz-adr-sync
├── generate_adr_index() → adr_index.md
└── generate_adr_status_table() → adr_status.md
```

---

## Policy

- Regenerates from source ADR files
- Updates are idempotent
- Part of docs composite with `--adr` flag

---

## Failure Modes

| Symptom | Cause | Recovery |
|---------|-------|----------|
| Parse error | Invalid ADR format | Fix ADR frontmatter |
| Missing file | ADR directory issue | Check ADR paths |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| gz-adr-manager | Create/book ADRs |
| gz-obpi-sync | Sync OBPI status in ADR table from briefs |
| gz-obpi-brief | Create OBPI briefs |
| gz-adr-audit | Gate 5 verification |

---

## References

- Command: `src/opsdev/commands/adr_tools.py`
- Library: `src/opsdev/lib/adr.py`
- Output: `docs/design/adr/adr_index.md`, `docs/design/adr/adr_status.md`
