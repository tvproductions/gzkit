# @covers REQ-0.30.0-04-04
Feature: knowledge generate/refresh CLI smoke
  As an operator
  I want a CLI command to generate and refresh the OKF knowledge bundle
  So that the orientation bundle is available from a single idempotent command.

  @REQ-0.30.0-04-04
  Scenario: generate emits the OKF bundle and exits 0
    When I run the gz command "knowledge generate"
    Then the command exits with code 0

  @REQ-0.30.0-04-04
  Scenario: refresh is idempotent — re-running after generate exits 0
    When I run the gz command "knowledge generate"
    Then the command exits with code 0
    When I run the gz command "knowledge refresh"
    Then the command exits with code 0
