Feature: Persona control surface
  Agent personas define behavioral identity frames stored in
  .gzkit/personas/ and loaded at dispatch boundaries (ADR-0.0.11).

  Scenario: List personas in initialized workspace with no files
    Given the workspace is initialized
    When I run the gz command "personas list"
    Then the command exits with code 0

  Scenario: List personas shows implementer when file exists
    Given the workspace is initialized
    And a persona file "implementer" exists
    When I run the gz command "personas list --json"
    Then the command exits with code 0
    And the output contains "implementer"
    And the output contains "methodical"

  Scenario: List personas shows main-session when file exists
    Given the workspace is initialized
    And a persona file "main-session" exists
    When I run the gz command "personas list --json"
    Then the command exits with code 0
    And the output contains "main-session"
    And the output contains "methodical"

  Scenario: AGENTS.md persona section references main-session grounding
    Given the workspace is initialized
    Then the file "AGENTS.md" contains "main-session"
    And the file "AGENTS.md" contains "craftsperson"
    And the file "AGENTS.md" contains "governance not as overhead"

  Scenario: AGENTS.md persona section lists available personas with roles
    Given the workspace is initialized
    Then the file "AGENTS.md" contains "implementer"
    And the file "AGENTS.md" contains "narrator"
    And the file "AGENTS.md" contains "pipeline-orchestrator"
    And the file "AGENTS.md" contains "quality-reviewer"
    And the file "AGENTS.md" contains "spec-reviewer"

  Scenario: Personas list is read-only
    Given the workspace is initialized
    And a persona file "implementer" exists
    When I run the gz command "personas list"
    Then the command exits with code 0
    And the output contains "implementer"

  Scenario: Persona drift reports with governance evidence
    Given the workspace is initialized
    And the ledger contains governance events
    When I run the gz command "personas drift --persona default-agent --json"
    Then the command exits with code 0
    And the output is valid JSON

  Scenario: Persona drift filters to single persona
    Given the workspace is initialized
    And the ledger contains governance events
    When I run the gz command "personas drift --persona default-agent --json"
    Then the command exits with code 0
    And the output contains "default-agent"

  Scenario: Persona drift help includes description
    Given the workspace is initialized
    When I run the gz command "personas drift --help"
    Then the command exits with code 0
    And the output contains "behavioral proxies"
