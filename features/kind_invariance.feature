Feature: gz validate --kind-invariance enforcement
  Validates that the kind-invariance validator correctly enumerates
  foundation-kind ADRs and asserts each carries a substantive
  ## Why foundation tier? section (ADR-0.0.35, OBPI-04).

  @REQ-0.0.35-04-01
  Scenario: --kind-invariance flag is registered and appears in gz validate --help
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--kind-invariance"

  @REQ-0.0.35-04-02
  Scenario: foundation ADR with substantive Why-foundation-tier section passes
    Given a minimal project with a foundation ADR carrying a substantive Why-foundation-tier section
    When I run "gz validate --kind-invariance"
    Then it exits with code 0

  @REQ-0.0.35-04-03
  Scenario: foundation ADR missing the Why-foundation-tier section fails
    Given a minimal project with a foundation ADR missing the Why-foundation-tier section
    When I run "gz validate --kind-invariance"
    Then it exits with code 3
    And the output contains "kind_invariance"

  @REQ-0.0.35-04-04
  Scenario: foundation ADR with placeholder-only body fails
    Given a minimal project with a foundation ADR carrying a placeholder-only Why-foundation-tier section
    When I run "gz validate --kind-invariance"
    Then it exits with code 3
    And the output contains "kind_invariance"

  @REQ-0.0.35-04-05
  Scenario: feature ADR is not enumerated by the validator
    Given a minimal project with only a feature ADR
    When I run "gz validate --kind-invariance"
    Then it exits with code 0
