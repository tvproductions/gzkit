Feature: foundation kind closed to new authoring (ADR-0.34.0 / OBPI-0.34.0-02)
  As the operator,
  I want every foundation-authoring door to refuse new foundation ADRs,
  So that "no more foundation ADRs" is mechanically enforced, not remembered.

  Supersedes features/plan_create_nominal.feature, whose scenarios asserted the
  nominal-allocator gap hint. ADR-0.34.0 deleted that allocator along with the
  authoring path it served.

  @REQ-0.34.0-02-01
  Scenario: gz plan create --kind foundation is refused with recovery prose
    Given the workspace is initialized in heavy mode
    And the project has closed the foundation kind
    When I run the gz command "plan create sunset-demo --kind foundation --semver 0.0.99 --lane lite"
    Then the command exits with code 1
    And the output contains "closed to new"
    And the output contains "ADR-0.34.0"
    And the output contains "--kind feature"
    And the output contains "--kind pool"

  @REQ-0.34.0-02-01
  Scenario: closed-kind refusal fires before the semver-binding check
    Given the workspace is initialized in heavy mode
    And the project has closed the foundation kind
    When I run the gz command "plan create sunset-demo --kind foundation --semver 0.5.0 --lane lite"
    Then the command exits with code 1
    And the output contains "ADR-0.34.0"

  @REQ-0.34.0-02-01
  Scenario: feature authoring is unaffected by the closure
    Given the workspace is initialized in heavy mode
    When I run the gz command "plan create sunset-demo --kind feature --semver 0.35.0 --lane lite --dry-run"
    Then the command exits with code 0
