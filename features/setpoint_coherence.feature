Feature: gz validate --setpoint-coherence enforcement
  Validates that every (content_type, vendor) pair declared in
  data/vendor-manifest.json content_type_routes carries a legal declared
  compression setpoint in content_type_temperatures (OBPI-0.0.37-20).

  @REQ-0.0.37-20-01
  Scenario: --setpoint-coherence flag is registered and appears in gz validate --help
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--setpoint-coherence"

  @REQ-0.0.37-20-03
  Scenario: a manifest with a legal setpoint for every routed pair passes
    Given a project whose vendor manifest declares a setpoint for every routed pair
    When I run "gz validate --setpoint-coherence"
    Then it exits with code 0

  @REQ-0.0.37-20-01
  Scenario: a routed pair with no declared setpoint fails closed
    Given a project whose vendor manifest routes a pair with no declared setpoint
    When I run "gz validate --setpoint-coherence"
    Then it exits with code 3
    And the output contains "content_type_temperatures"

  @REQ-0.0.37-20-02
  Scenario: an illegal setpoint token fails closed
    Given a project whose vendor manifest declares an illegal setpoint token
    When I run "gz validate --setpoint-coherence"
    Then it exits with code 3
    And the output contains "Illegal setpoint token"
