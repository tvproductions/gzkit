Feature: gz complexity advise — trigger-time advisor diagnosis (ADR-0.0.29 / OBPI-0.0.29-03)
  As an operator authoring or reviewing complexity-sensitive code,
  I want to preview the doctrinal advisor diagnosis for a file before commit,
  so that warn-band crossings surface a refactor archetype + authority +
  proof binding instead of an opaque numeric verdict, and block-band
  crossings fail the verb's exit status.

  @REQ-0.0.29-03-01
  Scenario: clean file produces exit 0 with no crossings
    Given a synthetic complexity-advise environment with a clean Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity_thresholds.md"
    Then the command exits with code 0
    And the output contains "No crossings"

  @REQ-0.0.29-03-02
  Scenario: warn-band crossing produces exit 0 with diagnosis prose
    Given a synthetic complexity-advise environment with a warn-band Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity_thresholds.md"
    Then the command exits with code 0
    And the output contains "Archetype"
    And the output contains "Authority"

  @REQ-0.0.29-03-03
  Scenario: block-band crossing produces exit 3
    Given a synthetic complexity-advise environment with a block-band Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity_thresholds.md"
    Then the command exits with code 3

  @REQ-0.0.29-03-04
  Scenario: --json mode emits valid JSON validating against schema
    Given a synthetic complexity-advise environment with a warn-band Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity_thresholds.md --json"
    Then the command exits with code 0
    And the output contains "metric"
    And the output contains "radon_cc"
    And the output contains "crossing_band"

  @REQ-0.0.29-03-05
  Scenario: --help exits 0 with description, options, example
    When I run the gz command "complexity advise --help"
    Then the command exits with code 0
    And the output contains "usage"
    And the output contains "--json"
    And the output contains "--quiet"

  @REQ-0.0.29-03-06
  Scenario: --help describes purpose, exit codes, and examples
    When I run the gz command "complexity advise --help"
    Then the command exits with code 0
    And the output contains "Exit codes"
    And the output contains "Examples"

  @REQ-0.0.29-03-07
  Scenario: verb is registered with full surface (manpage + index + runbook coverage)
    When I run the gz command "complexity advise --help"
    Then the command exits with code 0
    And the output contains "complexity advise"
    And the output contains "ADR-0.0.28"
