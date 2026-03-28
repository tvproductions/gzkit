Feature: Closeout ceremony enforcement
  The closeout ceremony presents a Defense Brief with closing arguments,
  product proof, and reviewer assessment. It blocks when evidence is missing.

  Scenario: Closeout dry-run shows Defense Brief section
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    And the OBPI source file has public docstrings
    And the OBPI brief has a closing argument
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits with code 0
    And the output contains "Defense Brief"
    And the output contains "Closing Arguments"

  Scenario: Closeout form includes Defense Brief when rendered
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    And the OBPI source file has public docstrings
    And the OBPI brief has a closing argument
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits with code 0
    And the output contains "Product Proof"

  Scenario: Defense Brief shows reviewer assessment when present
    Given the workspace is initialized in heavy mode
    And a heavy ADR exists with an OBPI brief
    And the OBPI source file has public docstrings
    And the OBPI brief has a closing argument
    And a reviewer assessment exists for the OBPI
    When I run the gz command "closeout ADR-0.1.0 --dry-run"
    Then the command exits with code 0
    And the output contains "Reviewer Assessment"
    And the output contains "PASS"
