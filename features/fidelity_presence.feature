Feature: gz validate --fidelity-presence enforcement
  ADR-0.0.73 Boundary Invariant #4 requires every non-pool ADR Decision to ship
  a parseable ## Fidelity Assertions block — runnable commands that exercise the
  ADR's thesis against the real system. The --fidelity-presence scope mechanizes
  that invariant: it fails closed (exit 3) on any non-pool ADR Decision lacking a
  block, minus the pre-existing block-less ADRs grandfathered in
  data/fidelity_presence_grandfather.json (OBPI-0.0.73-08).

  @REQ-0.0.73-08-01
  Scenario: --fidelity-presence flag appears in gz validate --help
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--fidelity-presence"

  @REQ-0.0.73-08-01
  Scenario: A block-less non-pool ADR Decision fails closed
    Given a project with a block-less non-pool ADR Decision
    When I run "gz validate --fidelity-presence"
    Then it exits with code 3

  @REQ-0.0.73-08-01
  Scenario: A corpus where every non-pool ADR Decision carries a block passes
    Given a project where every non-pool ADR Decision carries a Fidelity Assertions block
    When I run "gz validate --fidelity-presence"
    Then it exits with code 0
