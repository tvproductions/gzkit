Feature: gz justify pre-execution reasoning walkthrough (ADR-0.0.19 / OBPI-0.0.19-05)
  As an operator authoring or attesting governance work,
  I want a deterministic 8-section reasoning scaffold for GHIs, OBPIs, or
  drafts and a validate subverb that gates completion on every section
  being filled,
  so that pre-execution reasoning is preserved as evidence rather than
  reconstructed post-hoc.

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Render scaffold for a GHI anchor with mocked gh
    Given gh issue view returns fixture body for "GHI-232"
    When I run the gz command "justify GHI-232"
    Then the command exits with code 0
    And the output contains "# Walkthrough: GHI-232"
    And the output contains "_[To be filled]_"

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Render scaffold for an OBPI anchor against a fixture brief
    Given a fixture OBPI brief for "OBPI-0.99.0-01"
    When I run the gz command "justify OBPI-0.99.0-01"
    Then the command exits with code 0
    And the output contains "# Walkthrough: OBPI-0.99.0-01"

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Render scaffold from --draft with --save and --draft-slug
    When I run the gz command "justify --draft 'pre-decision text' --save --draft-slug my-idea"
    Then the command exits with code 0
    And a scaffold artifact is written under "artifacts/justify"

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Reject ADR anchor with exit 1
    When I run the gz command "justify ADR-0.0.19"
    Then the command exits with code 1
    And the output contains "justify reasons about change instances"

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Reject --draft + --save without --draft-slug
    When I run the gz command "justify --draft 'orphan draft' --save"
    Then the command exits with code 1
    And the output contains "--draft-slug is required"

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Validate exits 0 on a complete walkthrough
    Given a complete justify walkthrough fixture at "filled.md"
    When I run the gz command "justify validate filled.md"
    Then the command exits with code 0

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Validate exits 1 on an incomplete walkthrough
    Given an incomplete justify walkthrough fixture at "incomplete.md"
    When I run the gz command "justify validate incomplete.md"
    Then the command exits with code 1
    And the output names an unfilled section ordinal

  @REQ-0.0.19-05-05
  @REQ-0.0.19-05-06
  Scenario: Validate exits 2 on a malformed walkthrough
    Given a malformed justify walkthrough fixture at "malformed.md"
    When I run the gz command "justify validate malformed.md"
    Then the command exits with code 2
