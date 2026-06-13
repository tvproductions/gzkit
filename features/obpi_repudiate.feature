Feature: gz obpi repudiate — operator-gated completion repudiation
  gz obpi repudiate reverses a fraudulent or erroneous OBPI completion
  without permanent retirement, keeping the OBPI live for re-completion.

  @REQ-0.0.71-02-01
  Scenario: Repudiate verb is registered and dry-run reaches the lookup path
    Given the workspace is initialized
    When I run "gz obpi repudiate NONEXISTENT-99 --cause model-induced-fabrication --reason smoke --attestor Jeff --dry-run"
    Then it exits with code 1

  @REQ-0.0.71-02-02
  Scenario: Empty attestor fails closed (exit 1) before any ledger write
    Given the workspace is initialized
    When I run "gz obpi repudiate NONEXISTENT-99 --cause operator-error --reason smoke --attestor ''"
    Then it exits with code 1

  @REQ-0.0.71-02-03
  Scenario: Empty reason fails closed (exit 1) before any ledger write
    Given the workspace is initialized
    When I run "gz obpi repudiate NONEXISTENT-99 --cause operator-error --reason '' --attestor Jeff"
    Then it exits with code 1

  @REQ-0.0.71-02-05
  Scenario: Invalid cause value rejected by parser (exit 2)
    Given the workspace is initialized
    When I run "gz obpi repudiate OBPI-0.0.71-02 --cause bad-cause --reason smoke --attestor Jeff"
    Then it exits with code 2

  Scenario: Help text shows required flags
    Given the workspace is initialized
    When I run "gz obpi repudiate -h"
    Then it exits with code 0
    And the output contains "--cause"
    And the output contains "--reason"
    And the output contains "--attestor"
