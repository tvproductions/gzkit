Feature: Lock-exchange coupling validator (ADR-0.0.41 / OBPI-0.0.41-04)
  As a governance maintainer,
  I want the lock-exchange coupling validator wired into gz check,
  so that every obpi_lock_released event after the OBPI-02 cutover
  is mechanically verified to carry a valid handoff register entry.

  @REQ-0.0.41-04-01
  Scenario: Validator passes on a clean ledger with no post-cutover releases
    Given the workspace is initialized
    When I run the gz command "validate --lock-exchange-coupling"
    Then the command exits with code 0

  @REQ-0.0.41-04-02
  Scenario: Validator fails on a post-cutover release with missing handoff_path
    Given the workspace is initialized
    And a post-cutover obpi_lock_released event with no handoff_path for "OBPI-0.0.41-04-bdd-test"
    When I run the gz command "validate --lock-exchange-coupling"
    Then the command exits with code 3
    And the output contains "OBPI-0.0.41-04-bdd-test"
