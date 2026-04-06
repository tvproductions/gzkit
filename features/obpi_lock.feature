Feature: OBPI lock management
  Multi-agent work locks for OBPI coordination via gz obpi lock commands.

  Scenario: Claim creates a lock file
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.1.0-01 --json"
    Then it exits with code 0
    And the JSON output field "status" is "claimed"

  Scenario: Claim fails when held by another agent
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.1.0-01" held by agent "codex"
    When I run "gz obpi lock claim OBPI-0.1.0-01 --json"
    Then it exits with code 1
    And the JSON output field "status" is "conflict"

  Scenario: Release removes lock
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.1.0-01"
    And I run "gz obpi lock release OBPI-0.1.0-01 --json"
    Then it exits with code 0
    And the JSON output field "status" is "released"

  Scenario: Release validates ownership
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.1.0-01" held by agent "codex"
    When I run "gz obpi lock release OBPI-0.1.0-01 --json"
    Then it exits with code 1
    And the JSON output field "status" is "ownership_error"

  Scenario: Release with force overrides ownership
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.1.0-01" held by agent "codex"
    When I run "gz obpi lock release OBPI-0.1.0-01 --force --json"
    Then it exits with code 0
    And the JSON output field "status" is "released"

  Scenario: Check exits 0 when held
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.1.0-01"
    And I run "gz obpi lock check OBPI-0.1.0-01 --json"
    Then it exits with code 0
    And the JSON output field "status" is "held"

  Scenario: Check exits 1 when free
    Given the workspace is initialized
    When I run "gz obpi lock check OBPI-0.1.0-01 --json"
    Then it exits with code 1
    And the JSON output field "status" is "free"

  Scenario: List shows active locks
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.1.0-01"
    And I run "gz obpi lock list --json"
    Then it exits with code 0
    And the JSON output field "count" is "1"

  Scenario: List auto-reaps expired locks
    Given the workspace is initialized
    And an expired OBPI lock exists for "OBPI-0.1.0-01"
    When I run "gz obpi lock list --json"
    Then it exits with code 0
    And the JSON output field "count" is "0"

  Scenario: Deprecated lock-claim alias works
    Given the workspace is initialized
    When I run "gz obpi lock-claim OBPI-0.1.0-01 --json"
    Then it exits with code 0
    And the JSON output field "status" is "claimed"
