Feature: OBPI completion REQ-coverage gate
  gz obpi complete refuses completion when any REQ in the closing brief's
  ## Acceptance Criteria section lacks a passing @covers-decorated test.
  Heavy and foundation-kind briefs are fail-closed; lite-non-foundation briefs
  emit a warning and proceed. The override path (--accept-uncovered) records a
  ledger event and requires --attestor-present for agent-relayed acceptance.

  # GHI #412: agent-relayed --attestor-present is refused for foundation-kind
  # and sensitivity:security scopes. Scenarios that exercise the happy-path
  # coverage gate via attestor-present use heavy-feature (still triggers the
  # heavy-lane fail-closed rule) rather than heavy-foundation.
  @REQ-0.0.25-01-01
  Scenario: Gate passes when all REQs have passing covering tests
    Given the workspace is initialized in heavy mode
    And a heavy-feature OBPI "OBPI-FIXTURE-01-01" with REQ "REQ-0.0.98-01-01" exists
    And a covering test for "REQ-0.0.98-01-01" that passes exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000001" exists
    And a pipeline marker for "OBPI-FIXTURE-01-01" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-01" citing receipt "arb-step-unittest-00000000000000000000000000000001" using attestor-present
    Then the exit code is 0

  @REQ-0.0.25-01-02
  Scenario: Gate exits 3 when heavy-lane REQ has no covering test
    Given the workspace is initialized in heavy mode
    And a heavy-foundation OBPI "OBPI-FIXTURE-01-02" with REQ "REQ-0.0.98-01-02" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000002" exists
    And a pipeline marker for "OBPI-FIXTURE-01-02" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-02" citing receipt "arb-step-unittest-00000000000000000000000000000002" using attestor-present
    Then the exit code is 3
    And the output mentions "REQ-0.0.98-01-02"

  @REQ-0.0.25-01-03
  Scenario: Foundation-kind lite-lane brief exits 3 for uncovered REQ
    Given the workspace is initialized in heavy mode
    And a foundation-lite OBPI "OBPI-FIXTURE-01-03" with REQ "REQ-0.0.98-01-03" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000003" exists
    And a pipeline marker for "OBPI-FIXTURE-01-03" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-03" citing receipt "arb-step-unittest-00000000000000000000000000000003" using attestor-present
    Then the exit code is 3

  @REQ-0.0.25-01-04
  Scenario: Lite-non-foundation brief warns and proceeds for uncovered REQ
    Given the workspace is initialized in heavy mode
    And a lite-feature OBPI "OBPI-FIXTURE-01-04" with REQ "REQ-0.0.98-01-04" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000004" exists
    And a pipeline marker for "OBPI-FIXTURE-01-04" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-04" citing receipt "arb-step-unittest-00000000000000000000000000000004" using attestor-present
    Then the exit code is 0
    And the output mentions "Warning"

  @REQ-0.0.25-01-05
  Scenario: Gate exits 3 when covering test fails
    Given the workspace is initialized in heavy mode
    And a heavy-foundation OBPI "OBPI-FIXTURE-01-05" with REQ "REQ-0.0.98-01-05" exists
    And a covering test for "REQ-0.0.98-01-05" that fails exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000005" exists
    And a pipeline marker for "OBPI-FIXTURE-01-05" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-05" citing receipt "arb-step-unittest-00000000000000000000000000000005" using attestor-present
    Then the exit code is 3

  @REQ-0.0.25-01-06
  Scenario: Any one passing covering test satisfies the REQ
    Given the workspace is initialized in heavy mode
    And a heavy-feature OBPI "OBPI-FIXTURE-01-06" with REQ "REQ-0.0.98-01-06" exists
    And a covering test for "REQ-0.0.98-01-06" that passes exists
    And a second covering test for "REQ-0.0.98-01-06" that fails exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000006" exists
    And a pipeline marker for "OBPI-FIXTURE-01-06" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-01-06" citing receipt "arb-step-unittest-00000000000000000000000000000006" using attestor-present
    Then the exit code is 0

  @REQ-0.0.25-02-01
  Scenario: Override path proceeds and records ledger event via attestor-present
    Given the workspace is initialized in heavy mode
    And a heavy-feature OBPI "OBPI-FIXTURE-02-01" with REQ "REQ-0.0.98-02-01" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000007" exists
    And a pipeline marker for "OBPI-FIXTURE-02-01" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-02-01" accepting "REQ-0.0.98-02-01" reason "agent-relayed TTY-path proxy" citing "arb-step-unittest-00000000000000000000000000000007" using attestor-present
    Then the exit code is 0
    And the ledger contains an "obpi_completion_uncovered_accept" event

  @REQ-0.0.25-02-02
  Scenario: Headless override without pipeline marker is refused
    Given the workspace is initialized in heavy mode
    And a heavy-foundation OBPI "OBPI-FIXTURE-02-02" with REQ "REQ-0.0.98-02-02" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000008" exists
    When I complete coverage-gate OBPI "OBPI-FIXTURE-02-02" accepting "REQ-0.0.98-02-02" reason "no-marker" citing "arb-step-unittest-00000000000000000000000000000008" without attestor-present
    Then the exit code is 3

  @REQ-0.0.25-02-03
  Scenario: Partial accept-uncovered still fails for unwaived REQ
    Given the workspace is initialized in heavy mode
    And a heavy-foundation OBPI "OBPI-FIXTURE-02-03" with REQs "REQ-0.0.98-03-01" and "REQ-0.0.98-03-02" exists
    And a valid arb step receipt "arb-step-unittest-00000000000000000000000000000009" exists
    And a pipeline marker for "OBPI-FIXTURE-02-03" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-02-03" accepting only "REQ-0.0.98-03-01" reason "partial" citing "arb-step-unittest-00000000000000000000000000000009" using attestor-present
    Then the exit code is 3

  @REQ-0.0.25-02-04
  Scenario: gz adr emit-receipt --event closed blocked when OBPI has unwaived REQ gap
    Given the workspace is initialized in heavy mode
    And a heavy ADR "ADR-FIXTURE-02-04" with a completed OBPI "OBPI-FIXTURE-02-04" carrying unwaived REQ "REQ-0.0.98-02-04" exists
    When I emit ADR receipt for "ADR-FIXTURE-02-04" event "closed" attestor "BDD User" text "closing"
    Then the exit code is 3

  @REQ-0.0.25-02-05
  Scenario: accept-uncovered without accept-uncovered-reason exits 1
    Given the workspace is initialized in heavy mode
    And a heavy-foundation OBPI "OBPI-FIXTURE-02-05" with REQ "REQ-0.0.98-02-05" exists
    And a valid arb step receipt "arb-step-unittest-0000000000000000000000000000000a" exists
    And a pipeline marker for "OBPI-FIXTURE-02-05" is active
    When I complete coverage-gate OBPI "OBPI-FIXTURE-02-05" accepting "REQ-0.0.98-02-05" without reason citing "arb-step-unittest-0000000000000000000000000000000a" using attestor-present
    Then the exit code is 1

  @REQ-0.0.25-03-01
  Scenario: This feature file exists with scenario tags for all covered REQs
    Given the workspace is the live repository
    Then the file "features/obpi_completion_coverage_gate.feature" exists

  @REQ-0.0.25-03-02
  Scenario: AGENTS.md OBPI Acceptance Protocol names the REQ-coverage gate
    Given the workspace is the live repository
    Then AGENTS.md "OBPI Acceptance Protocol" section mentions "REQ-coverage gate"

  @REQ-0.0.25-03-03
  Scenario: obpi-complete manpage documents the accept-uncovered flag
    Given the workspace is the live repository
    Then the file "docs/user/commands/obpi-complete.md" contains "--accept-uncovered"

  @REQ-0.0.25-03-04
  Scenario: CLI audit passes in the live repository post-edit
    Given the workspace is the live repository
    When I run the gz command "cli audit"
    Then the exit code is 0
