Feature: Patch release discovery CLI
  The gz patch release command discovers qualifying GHIs since the last tag,
  computes the next patch version, and (unless --dry-run) writes a manifest
  and ledger event.

  Scenario: Help text exits zero and lists flags
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --help"
    Then the command exits with code 0
    And the output contains "--dry-run"
    And the output contains "--json"

  Scenario: Dry run reports discovery without executing
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --dry-run"
    Then the command exits with code 0
    And the output contains "Patch Release Discovery"
    And the output contains "GHIs discovered"

  Scenario: Dry run JSON output is well-formed
    Given the workspace is initialized in heavy mode
    When I run the gz command "patch release --dry-run --json"
    Then the command exits with code 0
    And JSON path "ghi_count" equals "0"
    And JSON path "tag" equals "None"
