Feature: Spec-test-code drift detection CLI
  The gz drift command detects governance drift by scanning OBPI briefs,
  test @covers references, and the active code change set.

  Scenario: No drift detected exits with code 0
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and a matching test exists
    When I run the gz command "drift --json --adr-dir design/adr --test-dir tests"
    Then the command exits with code 0
    And JSON path "summary.total_drift_count" equals "0"

  Scenario: Unlinked spec exits with code 1
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and no matching test exists
    When I run the gz command "drift --json --adr-dir design/adr --test-dir tests"
    Then the command exits with code 1
    And JSON path "summary.unlinked_spec_count" equals "1"

  Scenario: Plain output is one-per-line
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and no matching test exists
    When I run the gz command "drift --plain --adr-dir design/adr --test-dir tests"
    Then the command exits with code 1
    And the output contains "unlinked"

  Scenario: Help text shows description and options
    When I run the gz command "drift --help"
    Then the command exits with code 0
    And the output contains "--json"
    And the output contains "--plain"
