Feature: gz validate --complexity-thresholds rule body shape (OBPI-0.0.28-03)
  As a governance maintainer
  I want gz validate --complexity-thresholds to fail-close on malformed threshold tables
  So that downstream consumers (advisor, authoring-guidance, xenon-as-gate) never
  bind against a rule body the loader cannot parse, and the bootstrap-mode
  carve-out surfaces visibly to the operator without silently passing the gate.

  Background:
    Given the workspace is initialized

  @REQ-0.0.28-03-01
  Scenario: Well-formed rule body validates clean
    Given a well-formed complexity-thresholds fixture
    When I run the gz command "validate --complexity-thresholds"
    Then the command exits with code 0

  @REQ-0.0.28-03-06
  Scenario: gz validate help surfaces the new flag
    Given the workspace is initialized
    When I run the gz command "validate --help"
    Then the output contains "--complexity-thresholds"

  @REQ-0.0.28-03-07
  Scenario: Command doc references the new flag
    Given the workspace is initialized
    Then the repo file "docs/user/commands/validate.md" contains "--complexity-thresholds"

  @REQ-0.0.28-03-02
  Scenario: Rule body where any metric lacks a block band fails closed
    Given a complexity-thresholds fixture with radon_cc missing its block band
    When I run the gz command "validate --complexity-thresholds"
    Then the command exits with code 3
    And the output contains "radon_cc"

  @REQ-0.0.28-03-03
  Scenario: Off-enum corpus percentile fails closed
    Given a complexity-thresholds fixture with radon_cc carrying an off-enum percentile
    When I run the gz command "validate --complexity-thresholds"
    Then the command exits with code 3

  @REQ-0.0.28-03-04
  Scenario: Unparseable citation fails closed
    Given a complexity-thresholds fixture with a malformed citation block
    When I run the gz command "validate --complexity-thresholds"
    Then the command exits with code 3

  @REQ-0.0.28-03-05
  Scenario: Bootstrap-absolutes section emits a warning without failing
    Given a well-formed complexity-thresholds fixture with the bootstrap section
    When I run the gz command "validate --complexity-thresholds"
    Then the command exits with code 0
    And the output contains "Bootstrap"
