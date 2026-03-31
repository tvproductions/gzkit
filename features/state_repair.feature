Feature: State repair force-reconciliation
  The gz state --repair command force-reconciles all OBPI frontmatter
  status from ledger-derived state (ADR-0.0.9, OBPI-03).

  Scenario: Repair updates drifted frontmatter to match ledger
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief exists with frontmatter status "Draft"
    And the ledger marks OBPI-0.1.0-01 as completed
    When I run the gz command "state --repair"
    Then the command exits with code 0
    And the OBPI brief frontmatter status is "Completed"

  Scenario: Repair is idempotent
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief exists with frontmatter status "Completed"
    And the ledger marks OBPI-0.1.0-01 as completed
    When I run the gz command "state --repair"
    And I run the gz command "state --repair --json"
    Then the command exits with code 0
    And the JSON output field "total" equals 0

  Scenario: Repair reports changes in JSON mode
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief exists with frontmatter status "Draft"
    And the ledger marks OBPI-0.1.0-01 as completed
    When I run the gz command "state --repair --json"
    Then the command exits with code 0
    And the JSON output field "total" equals 1
