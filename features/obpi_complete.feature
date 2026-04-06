Feature: OBPI atomic completion
  gz obpi complete atomically validates, writes evidence, flips status,
  records attestation, and emits a completion receipt in a single
  all-or-nothing transaction.

  Scenario: Missing OBPI exits 1
    Given the workspace is initialized
    When I run "gz obpi complete NONEXISTENT-99 --attestor jeff --attestation-text Verified"
    Then it exits with code 1

  Scenario: Help text shows required flags
    Given the workspace is initialized
    When I run "gz obpi complete -h"
    Then it exits with code 0
    And the output contains "--attestor"
    And the output contains "--attestation-text"
