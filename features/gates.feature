Feature: gz gates frontmatter integration (ADR-0.0.16 / OBPI-0.0.16-02)
  As an operator running governance gates,
  I want Gate 1 to mechanically block on frontmatter-ledger drift,
  so that stale frontmatter never masquerades as truth during attestation.

  Background:
    Given the workspace is initialized
    And ADR-0.1.0 exists

  @REQ-0.0.16-02-02
  @REQ-0.0.16-02-03
  Scenario: Gate 1 blocks on status frontmatter drift with exit 3
    Given ADR-0.1.0 has drifted status frontmatter "Completed"
    When I run the gz command "gates --gate 1 --adr ADR-0.1.0"
    Then the command exits with code 3
    And the output contains "status"
    And the output contains "gz chores run frontmatter-ledger-coherence"

  @REQ-0.0.16-02-04
  Scenario: gz gates rejects the --skip-frontmatter bypass flag
    When I run the gz command "gates --skip-frontmatter --adr ADR-0.1.0"
    Then the command exits non-zero
    And the output contains "unrecognized arguments"
