Feature: Requirement coverage reporting CLI
  The gz covers command reports requirement coverage from @covers
  annotations at ADR, OBPI, and REQ granularity.

  Scenario: All-REQ coverage summary exits with code 0
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and a decorator-covered test exists
    When I run the gz command "covers --json --adr-dir design/adr --test-dir tests"
    Then the command exits with code 0
    And JSON path "summary.total_reqs" equals "1"
    And JSON path "summary.covered_reqs" equals "1"

  Scenario: Filter by ADR shows only matching REQs
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and a decorator-covered test exists
    When I run the gz command "covers ADR-0.1.0 --json --adr-dir design/adr --test-dir tests"
    Then the command exits with code 0
    And JSON path "summary.total_reqs" equals "1"

  Scenario: Plain output is one-per-line
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with one REQ and a decorator-covered test exists
    When I run the gz command "covers --plain --adr-dir design/adr --test-dir tests"
    Then the command exits with code 0
    And the output contains "covered"

  Scenario: Help text shows description and options
    When I run the gz command "covers --help"
    Then the command exits with code 0
    And the output contains "--json"
    And the output contains "--plain"

  Scenario: No REQs found returns empty summary
    Given the workspace is initialized
    And ADR-0.1.0 exists
    When I run the gz command "covers --json --adr-dir design/adr --test-dir tests"
    Then the command exits with code 0
    And JSON path "summary.total_reqs" equals "0"

  Scenario: Audit-check includes coverage section in JSON output
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with covered and uncovered REQs exists
    When I run the gz command "adr audit-check ADR-0.1.0 --json"
    Then JSON path "coverage.total_reqs" equals "2"
    And JSON path "coverage.covered_reqs" equals "1"
    And JSON path "coverage.uncovered_reqs" equals "1"

  Scenario: Audit-check flags uncovered REQs as blocking coverage findings
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI brief with covered and uncovered REQs exists
    When I run the gz command "adr audit-check ADR-0.1.0 --json"
    Then the command exits with code 1
    And JSON path "coverage_findings" is not empty
    And JSON path "passed" equals "False"
