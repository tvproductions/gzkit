---
id: OBPI-0.99.0-01-fixture
parent: ADR-0.99.0-fixture-same-commit-backfill
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.99.0-01-fixture: Same-commit-backfill fixture (do not promote)

Synthetic OBPI for the same-commit-backfill fixture pair. Not a real OBPI.

## Acceptance Criteria

- [x] REQ-0.99.0-01-01: synthetic REQ — `@covers("REQ-0.99.0-01-01")`
  decorator and the OBPI's closing-receipt event share the same commit SHA.
  Heuristic flags this case as blocking (REQ-0.0.23-05-05).
