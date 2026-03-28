Feature: Closeout product proof gate
  The closeout command validates that each OBPI has operator-facing
  documentation proof before allowing ADR closeout to proceed.

  Scenario: Closeout blocked when OBPI has no product proof
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits non-zero
    And the output contains "MISSING"
    And the output contains "missing product proof"

  Scenario: Closeout allowed when OBPI has docstring proof
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    And the OBPI source file has public docstrings
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits with code 0
    And the output contains "docstring"

  Scenario: Closeout product proof shown in JSON mode
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    And the OBPI source file has public docstrings
    When I run the gz command "closeout ADR-0.1.0 --dry-run --json"
    Then the command exits with code 0
    And the output contains "product_proof"
