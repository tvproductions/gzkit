---
id: ADR-pool.documented-decorator-contract
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.0.5
---

# ADR-pool.documented-decorator-contract

`@documented` decorator for CLI command handlers that co-locates documentation obligations with code. Declares required manpage, runbook steps, and governance relevance at the point of authorship so adding a command without documenting it is a visible omission.

Depends on ADR-0.0.5 (foundation scanner + manifest) being complete first — the decorator is the developer-facing contract, the scanner is the enforcement engine.
