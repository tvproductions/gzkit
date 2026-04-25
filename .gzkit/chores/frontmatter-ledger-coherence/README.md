# Frontmatter-Ledger Reconciliation (ADR-0.0.16 OBPI-03)

Detect drift between ADR/OBPI YAML frontmatter and ledger truth, then
**automatically rewrite** the drifted `id`/`parent`/`lane`/`status` fields
to match the ledger. Ungoverned keys (`tags:`, `related:`, etc.) are
preserved byte-identically.

Replaces the prior read-only audit chore (v1.0.0) which advised hand-editing —
antithetical to ADR-0.0.16's ledger-wins doctrine.

## Quick Start

```bash
uv run gz frontmatter reconcile --dry-run
uv run gz frontmatter reconcile
```

## Lane

**heavy** — mutating, schema-validated receipt emission.

## Receipts

`artifacts/receipts/frontmatter-coherence/<YYYYMMDDTHHMMSSZ>.json`
