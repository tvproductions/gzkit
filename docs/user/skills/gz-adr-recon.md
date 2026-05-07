# /gz-adr-recon (ARCHIVED)

> **Archived 2026-05-07.** This skill has been consolidated into [`/gz-adr-sync`](gz-adr-sync.md).

---

## Migration

| Old invocation | New invocation |
|---|---|
| `/gz-adr-recon ADR-<X.Y.Z>` | `/gz-adr-sync ADR-<X.Y.Z>` |
| `/gz-adr-recon` (global) | `/gz-adr-sync` |

`/gz-adr-sync` runs the same Layer 2 ledger reconciliation as this skill, plus Layer 1 evidence discovery and Layer 3 registration, in a single end-to-end workflow.
