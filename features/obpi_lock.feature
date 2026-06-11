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

  Scenario: Release removes lock (register entry via --abandon)
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.1.0-01"
    And I run "gz obpi lock release OBPI-0.1.0-01 --abandon tool_failure:demo --json"
    Then it exits with code 0
    And the JSON output field "status" is "released"

  Scenario: Release validates ownership
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.1.0-01" held by agent "codex"
    When I run "gz obpi lock release OBPI-0.1.0-01 --json"
    Then it exits with code 1
    And the JSON output field "status" is "ownership_error"

  Scenario: Release with force overrides ownership (register entry via --abandon)
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.1.0-01" held by agent "codex"
    When I run "gz obpi lock release OBPI-0.1.0-01 --force --abandon wrong_obpi_claimed:demo --json"
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

  # OBPI-0.0.41-02 — Claim/Release Safety Primitives (token-block discipline)
  # Scenarios are tagged with @REQ-X.Y.Z-NN-MM for behave coverage gate.

  @REQ-0.0.41-02-01 @REQ-0.0.41-02-02 @REQ-0.0.41-02-03
  Scenario: Race-condition interlock — concurrent claim conflicts
    Given the workspace is initialized
    And an OBPI lock exists for "OBPI-0.0.41-02" held by agent "agent-a"
    When I run "gz obpi lock claim OBPI-0.0.41-02 --json --agent agent-b"
    Then it exits with code 1
    And the JSON output field "status" is "conflict"

  @REQ-0.0.41-02-04 @REQ-0.0.41-02-05 @REQ-0.0.41-02-08
  Scenario: Release --abandon happy path writes degenerate handoff
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.0.41-02"
    And I run "gz obpi lock release OBPI-0.0.41-02 --abandon network_loss:demo --json"
    Then it exits with code 0
    And the JSON output field "status" is "released"
    And the JSON output field "category" is "network_loss"

  @REQ-0.0.41-02-06
  Scenario: Release --abandon rejects unregistered category
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.0.41-02"
    And I run "gz obpi lock release OBPI-0.0.41-02 --abandon fabricated:reason --json"
    Then it exits with code 1
    And the JSON output field "status" is "invalid_abandon"

  # OBPI-0.0.41-03 flipped the OBPI-02 staging warning (was @REQ-0.0.41-02-07,
  # "warns but succeeds") to fail-closed; this scenario is retagged to the
  # OBPI-03 fail-closed REQ. The OBPI-02 staging REQ is superseded (waiver:
  # obpi-0.0.41-02-req07-superseded-by-obpi-03-fail-closed).
  @REQ-0.0.41-03-01
  Scenario: Release without --abandon and no register entry fails closed (OBPI-03)
    Given the workspace is initialized
    When I run "gz obpi lock claim OBPI-0.0.41-02"
    And I run "gz obpi lock release OBPI-0.0.41-02"
    Then it exits with code 3
    And the output contains "FAIL-CLOSED"
    And the output contains "gz-session-handoff"
    And the output contains "--abandon"
