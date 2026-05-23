Feature: gz plan create nominal foundation ID allocator (ADR-0.0.57 / OBPI-0.0.57-02)
  As an operator,
  I want gz plan create --kind foundation to suggest the next free nominal ID,
  So that I can create foundation ADRs in impact order, not strict ID order.

  @REQ-0.0.57-02-01
  Scenario: Error hint shows lowest gap when foundation tree is sparse
    Given the workspace is initialized in heavy mode
    And foundation ADRs exist for IDs "1,2,5,7"
    When I run the gz command "plan create my-adr --kind foundation --semver 99.0.0 --dry-run"
    Then the command exits with code 1
    And the output contains "0.0.3"

  @REQ-0.0.57-02-03
  Scenario: Error hint shows next integer when foundation tree is contiguous
    Given the workspace is initialized in heavy mode
    And foundation ADRs exist for IDs "1,2,3"
    When I run the gz command "plan create my-adr --kind foundation --semver 99.0.0 --dry-run"
    Then the command exits with code 1
    And the output contains "0.0.4"
