Feature: gz adr promote --kind taxonomy enforcement (ADR-0.0.17 / OBPI-0.0.17-03)
  As an operator promoting a pool ADR,
  I want --kind to declare and enforce taxonomic intent at promotion time,
  so that pool->canonical promotion is explicit, atomic, and audit-recorded.

  Background:
    Given the workspace is initialized
    And a pool ADR "ADR-pool.sample-work" with target scope exists

  @REQ-0.0.17-03-01
  Scenario: --kind appears in --help with three choices
    When I run the gz command "adr promote --help"
    Then the command exits with code 0
    And the output contains "--kind"
    And the output contains "foundation"
    And the output contains "feature"
    And the output contains "pool"

  @REQ-0.0.17-03-01
  Scenario: --kind pool is rejected with exit 1
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind pool"
    Then the command exits with code 1
    And the output contains "source"

  # In a project that HAS closed the kind, the closed-kind guard refuses outright
  # before the semver check runs. Closure is project-local, so the scenario states
  # that precondition rather than assuming it (GHI #740); REQ-0.0.17-03-02's
  # foundation semver-binding branch is proven for open projects at
  # tests/commands/test_adr_promote.py::test_foundation_rejects_non_zero_zero_semver.
  @REQ-0.34.0-02-02
  Scenario: --kind foundation is refused with recovery prose
    Given the project has closed the foundation kind
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind foundation"
    Then the command exits with code 1
    And the output contains "closed to new"
    And the output contains "ADR-0.34.0"
    And the output contains "--kind feature"
    And the output contains "--kind pool"
    And the file "design/adr/foundation/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" does not exist

  @REQ-0.0.17-03-03
  Scenario: --kind feature rejects 0.0.x semver
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.0.18 --kind feature"
    Then the command exits with code 1
    And the file "design/adr/pre-release/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md" does not exist

  @REQ-0.0.17-03-04
  Scenario: validation failure leaves no governance artifact behind
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind foundation"
    Then the command exits with code 1
    And the file "design/adr/foundation/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" does not exist
    And the file "design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" does not exist

  # Exercised on --kind feature: REQ-0.0.17-03-05's claim (a promoted ADR carries
  # kind: in its frontmatter) is kind-agnostic, and ADR-0.34.0 closed the
  # foundation route this scenario originally used.
  @REQ-0.0.17-03-05
  Scenario: promoted ADR carries kind: in frontmatter
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind feature --force"
    Then the command exits with code 0
    And the file "design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" contains "kind: feature"
    And the file "design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" contains "id: ADR-0.6.0-sample-work"

  @REQ-0.0.17-03-06
  Scenario: --kind feature lands the promoted ADR in pre-release/
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind feature --force"
    Then the command exits with code 0
    And the file "design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md" exists

  @REQ-0.0.17-03-07
  Scenario: ledger artifact_renamed event records kind and semver
    When I run the gz command "adr promote ADR-pool.sample-work --semver 0.6.0 --kind feature --force"
    Then the command exits with code 0
    And ledger event "artifact_renamed" has field "kind" equal to "feature"
    And ledger event "artifact_renamed" has field "semver" equal to "0.6.0"
    And ledger event "artifact_renamed" has field "reason" equal to "pool_promotion"
    And ledger event "artifact_renamed" has field "new_id" equal to "ADR-0.6.0-sample-work"
