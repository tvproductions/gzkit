Feature: gz validate --receipt-shape enforcement
  ADR-0.0.36 deprecates three legacy receipt shapes for obpi_receipt_emitted
  events dated on or after the cutoff date (2026-04-26). The --receipt-shape
  validator enforces these rules fail-closed on post-cutoff receipts and
  provides a waiver path for pre-cutoff legacy receipts.

  @REQ-0.0.36-03-01
  Scenario: --receipt-shape flag appears in gz validate --help
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--receipt-shape"

  @REQ-0.0.36-03-02
  Scenario: Post-cutoff receipt with attestation_requirement optional fails
    Given a minimal project with a post-cutoff receipt having attestation_requirement optional
    When I run "gz validate --receipt-shape"
    Then it exits with code 3

  @REQ-0.0.36-03-03
  Scenario: Post-cutoff receipt with unprefixed obpi_completion fails
    Given a minimal project with a post-cutoff receipt having obpi_completion completed
    When I run "gz validate --receipt-shape"
    Then it exits with code 3

  @REQ-0.0.36-03-04
  Scenario: Post-cutoff receipt with agent attestor fails
    Given a minimal project with a post-cutoff receipt having attestor agent:claude-code
    When I run "gz validate --receipt-shape"
    Then it exits with code 3

  @REQ-0.0.36-03-05
  Scenario: Pre-cutoff receipt with waiver present passes
    Given a minimal project with a pre-cutoff receipt and a matching waiver entry
    When I run "gz validate --receipt-shape"
    Then it exits with code 0

  @REQ-0.0.36-03-06
  Scenario: receipt-shape scope runs cleanly on a clean repository
    When I run "gz validate --receipt-shape"
    Then it exits with code 0

  @REQ-0.0.36-03-07
  Scenario: gz validate manpage documents --receipt-shape scope
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--receipt-shape"
