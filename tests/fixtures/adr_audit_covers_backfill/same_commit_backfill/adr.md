---
id: ADR-0.99.0-fixture-same-commit-backfill
status: Completed
kind: foundation
semver: 0.0.99
lane: heavy
parent: PRD-FIXTURE-1.0.0
date: 2026-04-02
---

# ADR-0.99.0-fixture-same-commit-backfill: Same-commit-backfill fixture (do not promote)

Synthetic ADR used by `tests/fixtures/adr_audit_covers_backfill/`. Not a real
ADR. Heavy-lane × foundation-kind on purpose so the heuristic exercises its
fail-close branch (REQ-0.0.23-05-05).

## Decision

The decorator at `tests/test_decorator.py:7` and the closing receipt for
`REQ-0.99.0-01-01` were authored in the same commit `ccccccc` (2026-04-02).
Both gaps == 0; heuristic flags as blocking and exits 3.

## Checklist

- [x] OBPI-0.99.0-01-fixture
