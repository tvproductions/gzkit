Feature: Patch release CLI scaffold
  The gz patch release command is a scaffold that accepts --dry-run and
  --json flags and exits cleanly with placeholder output.

  Scenario: Help text exits zero and lists flags
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --help"
    Then the command exits with code 0
    And the output contains "--dry-run"
    And the output contains "--json"

  Scenario: Dry run exits zero with placeholder
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --dry-run"
    Then the command exits with code 0
    And the output contains "patch release"

  Scenario: JSON output is valid
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --json"
    Then the command exits with code 0
    And JSON path "status" equals "not_implemented"
