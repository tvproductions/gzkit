Feature: Heavy lane Gate 4 governance
  Heavy-lane ADR workflows must enforce Gate 4 BDD checks.

  Scenario: Attestation is blocked until Gate 4 passes
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists
    And gate 2 and gate 3 are marked pass for ADR-0.1.0
    When I run the gz command "attest ADR-0.1.0 --status completed"
    Then the command exits non-zero
    And the output contains "Gate 4 must pass"

  Scenario: Closeout guidance includes Gate 4 BDD command
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits with code 0
    And the output contains "Gate 4 (BDD): uv run -m behave features/"

  Scenario: Heavy ADR status reports Gate 4 as pending when not checked
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists
    When I run the gz command "adr status ADR-0.1.0 --json"
    Then the command exits with code 0
    And JSON path "gates.4" equals "pending"

  Scenario: Pipeline guidance requires guarded git sync before completion accounting
    Given the workspace is initialized in heavy mode
    Then the file "AGENTS.md" contains "guarded git sync -> completion"
    And the file "AGENTS.md" contains "uv run gz git-sync --apply --lint --test"
