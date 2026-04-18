Feature: gz frontmatter reconcile ledger-wins reconciliation (ADR-0.0.16 / OBPI-0.0.16-03)
  As an operator remediating frontmatter drift,
  I want gz frontmatter reconcile to rewrite drifted fields to match the ledger
  so that frontmatter stays consistent with its source of truth without hand-editing.

  Background:
    Given the workspace is initialized
    And ADR-0.1.0 exists

  @REQ-0.0.16-03-02
  Scenario: Reconcile rewrites drifted lane and emits a receipt
    Given ADR-0.1.0 has drifted lane frontmatter "heavy"
    When I run the gz command "frontmatter reconcile"
    Then the command exits with code 0
    And ADR-0.1.0 frontmatter "lane" equals "lite"
    And a frontmatter-coherence receipt exists

  @REQ-0.0.16-03-03
  Scenario: Dry-run leaves ADR files untouched but emits the receipt
    Given ADR-0.1.0 has drifted lane frontmatter "heavy"
    When I run the gz command "frontmatter reconcile --dry-run"
    Then the command exits with code 0
    And ADR-0.1.0 frontmatter "lane" equals "heavy"
    And a frontmatter-coherence receipt exists

  @REQ-0.0.16-03-07
  Scenario: Unmapped status term exits with policy-breach code
    Given ADR-0.1.0 has drifted status frontmatter "Nonsense"
    When I run the gz command "frontmatter reconcile"
    Then the command exits with code 3
    And the output contains "Nonsense"
