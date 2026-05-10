Feature: gz justify complexity hints integration (ADR-0.0.30 / OBPI-0.0.30-05)
  As an operator running gz justify on an OBPI whose Allowed Paths include .py files,
  I want authoring-time complexity hints to surface automatically in the scaffold,
  so that advise-band crossings are visible during pre-execution reasoning without
  requiring a separate gz complexity-guide invocation.

  @REQ-0.0.30-05-01
  Scenario: justify with .py paths and advise-band crossings injects hints heading
    Given a justify fixture with .py allowed paths and an advise-band Python source
    When I run the gz command "justify OBPI-0.99.1-01"
    Then the command exits with code 0
    And the output contains "### Authoring-time complexity hints"

  @REQ-0.0.30-05-02
  Scenario: justify with no .py allowed paths skips the hints heading
    Given a justify fixture with no .py allowed paths
    When I run the gz command "justify OBPI-0.99.1-02"
    Then the command exits with code 0
    And the output does not contain "### Authoring-time complexity hints"

  @REQ-0.0.30-05-03
  @REQ-0.0.30-05-04
  Scenario: justify engine failure fails open — heading absent, command exits 0
    Given a justify fixture with .py allowed paths but engine unavailable
    When I run the gz command "justify OBPI-0.99.1-03"
    Then the command exits with code 0
    And the output does not contain "### Authoring-time complexity hints"

  @REQ-0.0.30-05-05
  @REQ-0.0.30-05-06
  Scenario: skill amendment artifact exists with bumped version and synced mirrors
    Given the canonical gz-justify skill amendment is in place
    Then the gz-justify skill version is "6.1.0"
    And the gz-justify skill body contains "Authoring-time complexity hints"
    And the gz-justify vendor mirrors are byte-identical to the canonical
