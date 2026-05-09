Feature: gz complexity guide — authoring-time hint surface (ADR-0.0.30 / OBPI-0.0.30-01)
  As an operator editing complexity-sensitive code,
  I want to preview authoring-time complexity hints on a file before committing,
  so that advise-band crossings surface a refactor archetype + guidance headline
  + recommended move before reaching gate time, without blocking the build.

  @REQ-0.0.30-01-01
  Scenario: Clean file produces exit 0 with no-hints message
    Given a synthetic complexity-guide environment with a clean Python source
    When I run the gz command "complexity guide subject.py"
    Then the command exits with code 0
    And the output contains "No advise-band hints found"

  @REQ-0.0.30-01-02
  Scenario: File with advise-band crossings produces prose hint blocks
    Given a synthetic complexity-guide environment with an advise-band Python source
    When I run the gz command "complexity guide subject.py"
    Then the command exits with code 0
    And the output contains "Archetype"
    And the output contains "Move"

  @REQ-0.0.30-01-03
  Scenario: --json mode produces valid JSON with AuthoringHint fields
    Given a synthetic complexity-guide environment with an advise-band Python source
    When I run the gz command "complexity guide subject.py --json"
    Then the command exits with code 0
    And the output contains "precedence_band"
    And the output contains "recommended_move"
    And the output contains "archetype"

  @REQ-0.0.30-01-04
  @REQ-0.0.30-01-05
  Scenario: --help exits 0 with standard sections (and exit 3 is never produced)
    When I run the gz command "complexity guide --help"
    Then the command exits with code 0
    And the output contains "usage"
    And the output contains "options"
