---
id: ADR-0.99.0-fixture-legit-evolution
status: Completed
kind: feature
semver: 0.99.0
lane: lite
parent: PRD-FIXTURE-1.0.0
date: 2026-04-02
---

# ADR-0.99.0-fixture-legit-evolution: Legitimate-evolution fixture (do not promote)

Synthetic ADR used by `tests/fixtures/adr_audit_covers_backfill/`. Not a real
ADR; does not enter the artifact graph. Mirrors the shape `gz adr audit-check`
walks so the heuristic can observe a decorator that pre-dates its closing
receipt by more than both thresholds.

## Decision

The decorator at `tests/test_decorator.py:7` landed in commit `aaaaaaa`
(2026-02-01), 30 commits / 60 days before the closing receipt commit
`bbbbbbb` (2026-04-02). Either gap exceeds defaults — heuristic does not flag.

## Checklist

- [x] OBPI-0.99.0-01-fixture
