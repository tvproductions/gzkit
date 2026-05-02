# @covers REQ-0.0.24-01-01
# @covers REQ-0.0.24-01-02
# @covers REQ-0.0.24-01-03
# @covers REQ-0.0.24-01-04
# @covers REQ-0.0.24-01-05
# @covers REQ-0.0.24-01-06
# @covers REQ-0.0.24-02-01
# @covers REQ-0.0.24-02-02
# @covers REQ-0.0.24-02-03
# @covers REQ-0.0.24-02-04
# @covers REQ-0.0.24-02-05
# @covers REQ-0.0.24-04-01
# @covers REQ-0.0.24-04-02
# @covers REQ-0.0.24-04-03
Feature: Attestation receipt-binding gate (ADR-0.0.24)
  As a governance maintainer relying on ARB receipts as proof of attestation
  I want gz validate --attestation-receipts and the gz obpi complete /
  gz adr emit-receipt gates to mechanically verify cited ARB receipts
  So that fabricated receipt IDs cannot pass for real evidence on heavy or
  foundation work, and lite-non-foundation work warns transparently.

  # ----------------------------------------------------------------------
  # OBPI-0.0.24-01 validator scope (gz validate --attestation-receipts)
  # ----------------------------------------------------------------------

  @REQ-0.0.24-01-01
  Scenario: Valid receipt resolves on heavy lane
    Given the workspace is initialized in heavy mode
    And an arb step receipt "arb-step-typecheck-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" with exit_status 0 exists
    When I run "gz validate --attestation-receipts 'typecheck clean (typecheck: receipt arb-step-typecheck-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa)' --lane heavy --kind feature"
    Then it exits with code 0
    And the output contains "resolved"

  @REQ-0.0.24-01-02
  Scenario: Missing receipt fails closed on heavy lane
    Given the workspace is initialized in heavy mode
    And no arb receipts exist in the receipts root
    When I run "gz validate --attestation-receipts 'lint clean (lint: receipt arb-ruff-deadbeef00000000000000000000beef)' --lane heavy --kind feature"
    Then it exits with code 3
    And the output contains "no receipt file at"

  @REQ-0.0.24-01-03
  Scenario: Status mismatch fails closed
    Given the workspace is initialized in heavy mode
    And an arb step receipt "arb-step-unittest-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" with exit_status 1 exists
    When I run "gz validate --attestation-receipts 'unittest fixtures (unittest: receipt arb-step-unittest-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb)' --lane heavy --kind feature"
    Then it exits with code 3
    And the output contains "exit_status=1"

  @REQ-0.0.24-01-04
  Scenario: Claim category mismatch fails closed
    Given the workspace is initialized in heavy mode
    And an arb step receipt "arb-step-typecheck-cccccccccccccccccccccccccccccccc" with exit_status 0 exists
    When I run "gz validate --attestation-receipts 'lint clean (lint: receipt arb-step-typecheck-cccccccccccccccccccccccccccccccc)' --lane heavy --kind feature"
    Then it exits with code 3
    And the output contains "cited 'lint' but receipt is 'typecheck'"

  @REQ-0.0.24-01-05
  Scenario: Malformed receipt id is reported
    Given the workspace is initialized in heavy mode
    And no arb receipts exist in the receipts root
    When I run "gz validate --attestation-receipts 'lint clean (lint: receipt arb-ruff-ZZZZ-not-canonical)' --lane heavy --kind feature"
    Then the command exits non-zero
    And the output contains "malformed"

  @REQ-0.0.24-01-06
  Scenario: Zero receipts on heavy lane fails closed
    Given the workspace is initialized in heavy mode
    And no arb receipts exist in the receipts root
    When I run "gz validate --attestation-receipts 'narrative-only attestation' --lane heavy --kind feature"
    Then it exits with code 3

  @REQ-0.0.24-01-06
  Scenario: Zero receipts on lite-non-foundation passes warn-only
    Given the workspace is initialized
    And no arb receipts exist in the receipts root
    When I run "gz validate --attestation-receipts 'narrative-only attestation' --lane lite --kind feature"
    Then it exits with code 0

  # ----------------------------------------------------------------------
  # OBPI-0.0.24-02 gate wiring (gz obpi complete + gz adr emit-receipt)
  # ----------------------------------------------------------------------

  @REQ-0.0.24-02-01
  Scenario: Heavy lane completion with valid receipt records meta-receipt-bind
    Given the workspace is initialized in heavy mode
    And a heavy-lane brief "OBPI-0.99.0-01-fixture" under feature ADR "ADR-0.99.0-fixture" exists on disk
    And an arb step receipt "arb-step-unittest-dddddddddddddddddddddddddddddddd" with exit_status 0 exists
    And a pipeline marker for "OBPI-0.99.0-01-fixture" is active
    When I complete OBPI "OBPI-0.99.0-01-fixture" with attestation citing "arb-step-unittest-dddddddddddddddddddddddddddddddd" using attestor-present
    Then it exits with code 0
    And the ledger contains an event with field "event" equal to "audit_receipt_emitted" whose extra.receipt_event is "meta-receipt-bind"
    And the ledger contains an event with field "event" equal to "obpi_receipt_emitted"

  @REQ-0.0.24-02-02
  @REQ-0.0.24-04-03
  Scenario: Heavy lane completion with missing receipt fails closed and writes no completion event
    Given the workspace is initialized in heavy mode
    And a heavy-lane brief "OBPI-0.99.0-02-fixture" under feature ADR "ADR-0.99.0-fixture-b" exists on disk
    And no arb receipts exist in the receipts root
    When I complete OBPI "OBPI-0.99.0-02-fixture" with attestation citing "arb-ruff-deadbeef00000000000000000000beef" using attestor-present
    Then it exits with code 3
    And the ledger does not contain an event for "OBPI-0.99.0-02-fixture" with receipt_event "completed"

  @REQ-0.0.24-02-03
  Scenario: Lite non-foundation completion with missing receipt warns and proceeds
    Given the workspace is initialized
    And a lite-feature brief "OBPI-0.99.0-03-fixture" under feature ADR "ADR-0.99.0-fixture-c" exists on disk
    And no arb receipts exist in the receipts root
    When I complete OBPI "OBPI-0.99.0-03-fixture" with attestation citing "arb-ruff-deadbeef11111111111111111111beef" without attestor-present
    Then it exits with code 0
    And the ledger contains an event for "OBPI-0.99.0-03-fixture" with receipt_event "completed"

  @REQ-0.0.24-02-04
  Scenario: Foundation kind lite lane completion with missing receipt fails closed
    Given the workspace is initialized
    And a lite-foundation brief "OBPI-0.0.99-04-fixture" under foundation ADR "ADR-0.0.99-fixture-d" exists on disk
    And no arb receipts exist in the receipts root
    When I complete OBPI "OBPI-0.0.99-04-fixture" with attestation citing "arb-ruff-deadbeef22222222222222222222beef" using attestor-present
    Then it exits with code 3
    And the ledger does not contain an event for "OBPI-0.0.99-04-fixture" with receipt_event "completed"

  @REQ-0.0.24-02-05
  Scenario: Heavy ADR emit-receipt validated with missing receipt fails closed
    Given the workspace is initialized in heavy mode
    And a heavy feature ADR "ADR-0.99.0-fixture-e" exists on disk
    And no arb receipts exist in the receipts root
    When I emit ADR receipt for "ADR-0.99.0-fixture-e" event "validated" attestor "BDD User" attestation citing "arb-ruff-deadbeef33333333333333333333beef"
    Then the command exits non-zero

  # ----------------------------------------------------------------------
  # OBPI-0.0.24-04 self-coverage (the BDD tier itself)
  # ----------------------------------------------------------------------

  @REQ-0.0.24-04-01
  @REQ-0.0.24-04-02
  Scenario: behave-req-tags validator passes when scenarios cover all REQs
    Given the workspace is the live repository
    When I run the gz command "validate --behave-req-tags"
    Then the command exits with code 0
