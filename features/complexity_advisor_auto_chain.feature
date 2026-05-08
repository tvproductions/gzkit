Feature: Complexity advisor auto-chain from xenon-as-gate failure (ADR-0.0.29 / OBPI-0.0.29-05)
  As a developer committing complexity-sensitive code,
  I want the pre-commit hook to run the advisor when xenon fails,
  so that warn-band crossings surface a diagnosis and block-band
  crossings prevent the commit.

  @REQ-0.0.29-05-01
  Scenario: clean commit — xenon passes, advisor not invoked
    Given a git repo with the auto-chain hook installed
    And a staged Python file with no complexity crossings
    When the pre-commit hook runs
    Then the hook exits with code 0
    And the advisor is not invoked

  @REQ-0.0.29-05-02
  @REQ-0.0.29-05-05
  @REQ-0.0.29-05-06
  @wip
  # @wip pending GHI #423: distilled-characteristics-2026-05-04 practitioner-eye
  # sections empty for all 12 metrics; advisor engine fail-closes at runtime.
  # Scenario step definitions are landed (GHI #417); this scenario is unblocked
  # once the operator authors the radon_cc practitioner-eye prose.
  Scenario: warn-band commit — xenon fails, advisor diagnoses warn crossing
    Given a git repo with the auto-chain hook installed
    And a staged Python file with a warn-band complexity crossing
    When the pre-commit hook runs
    Then the hook exits with code 0
    And stderr contains a diagnosis with "Archetype"

  @REQ-0.0.29-05-04
  @REQ-0.0.29-05-05
  @REQ-0.0.29-05-06
  @wip
  # @wip pending GHI #423: distilled-characteristics-2026-05-04 practitioner-eye
  # sections empty for all 12 metrics; advisor engine fail-closes at runtime.
  # Scenario step definitions are landed (GHI #417); this scenario is unblocked
  # once the operator authors the radon_cc practitioner-eye prose.
  Scenario: block-band commit — xenon fails, advisor diagnoses block crossing
    Given a git repo with the auto-chain hook installed
    And a staged Python file with a block-band complexity crossing
    When the pre-commit hook runs
    Then the hook exits with code 1
    And stderr contains a diagnosis with "Archetype"

  @REQ-0.0.29-05-03
  Scenario: SKIP-bypassed commit — neither xenon nor advisor runs
    Given a git repo with the auto-chain hook installed
    And a staged Python file with a block-band complexity crossing
    And the SKIP environment variable includes the hook id
    When the pre-commit hook runs with SKIP active
    Then the hook exits with code 0
    And the advisor is not invoked
