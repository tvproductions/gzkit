Feature: gz validate --agents-md-map-conformance external CLI surface (OBPI-0.0.54-03)
  As a governance maintainer
  I want gz validate --agents-md-map-conformance and gz check to expose the
  map-not-encyclopedia validator as a registered, invokable CLI surface
  So that operator-facing enforcement of ADR-0.0.54 doctrine is a real verb,
  not just an internal audit function.

  Background:
    Given the workspace is initialized

  @REQ-0.0.54-03-02
  Scenario: gz validate --agents-md-map-conformance is a registered CLI scope and runs cleanly on an initialized workspace
    When I run the gz command "validate --agents-md-map-conformance"
    Then the command exits with code 0
    And the output contains "agents_md_map_conformance"

  @REQ-0.0.54-03-04
  Scenario: gz check help surfaces the validator step name to operators
    When I run the gz command "check --help"
    Then the command exits with code 0
    And the output contains "lint, format, typecheck, test"
