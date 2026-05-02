Feature: gz adr audit-check same-commit-window @covers backfill heuristic (ADR-0.0.23 / OBPI-0.0.23-05)
  As an auditor of a gzkit-governed project,
  I want gz adr audit-check to flag @covers(REQ-...) decorators introduced
  in the same commit as the REQ's closing receipt,
  so that the cosmetic-backfill anti-pattern from GHI #309 cannot silence
  the audit even when an agent drives the entire codebase end-to-end.

  Background:
    Given the workspace is initialized in heavy mode
    And the audit-thresholds file is present at "data/audit_thresholds.json"

  @REQ-0.0.23-05-09
  Scenario: Heavy-lane same-commit backfill exits 3 with the remediation hint
    Given a heavy ADR with a same-commit @covers backfill exists for OBPI-0.1.0-01-demo
    When I run the gz command "adr audit-check ADR-0.1.0-f"
    Then the command exits with code 3
    And the output contains "covers-backfill finding"
    And the output contains "Invariant 6f"
