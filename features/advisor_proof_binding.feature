Feature: Advisor verdict <-> proof binding validator (ADR-0.0.29 / OBPI-0.0.29-08)
  As a governance maintainer,
  I want gate-time enforcement of the verdict <-> proof binding,
  so that no advisor diagnosis lands in fixtures or ledger events without
  the grounded proof its archetype + doctrinal-frame claims.

  Defense-in-depth backstop. Model-layer enforcement (OBPI-01) and
  engine-layer enforcement (OBPI-02) prevent empty-proof diagnoses at runtime;
  this validator catches any that nonetheless reach gate-time.

  @REQ-0.0.29-08-02
  Scenario: empty-proof fixture fails the validator with named file
    Given an advisor diagnosis fixture "empty.json" with empty proof
    And a conforming advisor diagnosis schema
    When I run the gz command "validate --advisor-proof-binding"
    Then the command exits with code 1
    And the output contains "tests/fixtures/advisor/empty.json"

  @REQ-0.0.29-08-03
  Scenario: ledger event citing empty-proof diagnosis fails with named event id
    Given an advisor diagnosis fixture "diag.json" with id "diag-bad" and empty proof
    And an intrinsic-complexity-attestation event "ica-evt-42" cites "diag-bad"
    And a conforming advisor diagnosis schema
    When I run the gz command "validate --advisor-proof-binding"
    Then the command exits with code 1
    And the output contains "ica-evt-42"
