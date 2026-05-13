Feature: gz validate --distribution T0 static audit
  Validates that the distribution invariant validator correctly detects drift
  between pyproject.toml wheel includes, the baseline manifest, and on-disk
  canonical surface trees (ADR-0.0.32-07).

  @REQ-0.0.32-07-01
  @REQ-0.0.32-07-07
  Scenario: --distribution flag is registered and appears in gz validate --help
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--distribution"

  @REQ-0.0.32-07-01
  @REQ-0.0.32-07-02
  @REQ-0.0.32-07-03
  @REQ-0.0.32-07-05
  @REQ-0.0.32-07-11
  Scenario: ON_DISK_NOT_INCLUDED drift detected exits 3
    Given a minimal project with a skills surface file not covered by any include glob
    When I run "gz validate --distribution"
    Then it exits with code 3
    And the output contains "ON_DISK_NOT_INCLUDED"
    And the output contains "pyproject.toml"
