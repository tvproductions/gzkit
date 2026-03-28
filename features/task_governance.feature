Feature: Task lifecycle governance
  TASK entities have lifecycle commands via gz task CLI.

  Scenario: gz task --help shows subcommands
    Given the workspace is initialized
    When I run the gz command "task --help"
    Then the command exits with code 0
    And the output contains "list"
    And the output contains "start"
    And the output contains "complete"
    And the output contains "block"
    And the output contains "escalate"

  Scenario: gz task list shows no tasks when none exist
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    When I run the gz command "task list OBPI-0.1.0-01"
    Then the command exits with code 0
    And the output contains "No tasks found"

  Scenario: gz task start transitions pending to in_progress
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    And a pending task TASK-0.1.0-01-01-01 exists
    When I run the gz command "task start TASK-0.1.0-01-01-01"
    Then the command exits with code 0
    And the output contains "Started"

  Scenario: gz task complete on pending task fails
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    When I run the gz command "task complete TASK-0.1.0-01-01-01"
    Then the command exits non-zero
    And the output contains "Invalid TASK transition"

  Scenario: gz task block records reason
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    And a pending task TASK-0.1.0-01-01-01 exists
    And I run the gz command "task start TASK-0.1.0-01-01-01"
    When I run the gz command "task block TASK-0.1.0-01-01-01 --reason Missing_API"
    Then the command exits with code 0
    And the output contains "Blocked"

  Scenario: gz task start resumes a blocked task
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    And a pending task TASK-0.1.0-01-01-01 exists
    And I run the gz command "task start TASK-0.1.0-01-01-01"
    And I run the gz command "task block TASK-0.1.0-01-01-01 --reason blocked"
    When I run the gz command "task start TASK-0.1.0-01-01-01"
    Then the command exits with code 0
    And the output contains "Resumed"

  Scenario: gz task list --json returns valid JSON
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    And a pending task TASK-0.1.0-01-01-01 exists
    And I run the gz command "task start TASK-0.1.0-01-01-01"
    When I run the gz command "task list OBPI-0.1.0-01 --json"
    Then the command exits with code 0
    And the output is valid JSON

  Scenario: gz task escalate records reason
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And an OBPI exists for ADR-0.1.0
    And a pending task TASK-0.1.0-01-01-01 exists
    And I run the gz command "task start TASK-0.1.0-01-01-01"
    When I run the gz command "task escalate TASK-0.1.0-01-01-01 --reason Needs_human_decision"
    Then the command exits with code 0
    And the output contains "Escalated"
