Feature: gz validate --waiver-ratchet honesty contract
  ADR-0.0.73 Boundary Invariant #8 requires every registered waiver/grandfather/
  baseline surface that gates a gz check step to declare exactly one honesty
  mechanism (closed-set lock, dated cutover, or monotonic shrink-ratchet), so a
  waiver list cannot silently launder "not built" into "attested green". The
  --waiver-ratchet scope fails closed (exit 3) on any unratcheted or unregistered
  surface (OBPI-0.0.73-09).

  @REQ-0.0.73-09-04
  @REQ-0.0.73-09-05
  Scenario: --waiver-ratchet flag is wired into gz validate and documented
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--waiver-ratchet"

  @REQ-0.0.73-09-02
  Scenario: A registry whose every surface is ratcheted passes
    Given a project where every registered waiver surface is ratcheted
    When I run "gz validate --waiver-ratchet"
    Then it exits with code 0

  @REQ-0.0.73-09-01
  @REQ-0.0.73-09-03
  Scenario: A shrink-ratchet waiver list grown past its baseline fails closed
    Given a project with a waiver surface grown past its committed baseline
    When I run "gz validate --waiver-ratchet"
    Then it exits with code 3

  @REQ-0.0.73-09-06
  Scenario: An unregistered waiver data file fails closed as a silent bypass
    Given a project with an unregistered waiver data file
    When I run "gz validate --waiver-ratchet"
    Then it exits with code 3
