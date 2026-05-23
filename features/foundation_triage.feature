Feature: Foundation Triage and Nominal Allocator (ADR-0.0.57 / OBPI-0.0.57-05)
  As an operator,
  I want foundation triage and nominal ID gap-allocation to work correctly,
  So that I can prioritize foundations by impact and allocate IDs without gaps.

  @REQ-0.0.57-05-03
  Scenario: nominal-allocator gap-allocation suggests lowest free integer
    Given the workspace is initialized in heavy mode
    And foundation ADRs exist for IDs "1,2,4"
    When I run the gz command "plan create gap-test --kind foundation --semver 99.0.0 --dry-run"
    Then the command exits with code 1
    And the output contains "0.0.3"

  @REQ-0.0.57-05-03
  Scenario: foundation-triage script produces structured JSON from in-flight foundations
    Given a foundation-triage fixture with ADRs "ADR-0.0.1,ADR-0.0.2" and insights mentioning "ADR-0.0.1"
    When I run the foundation-triage script with format "json"
    Then the output is valid JSON
    And the JSON contains an entry with id containing "ADR-0.0.1"
