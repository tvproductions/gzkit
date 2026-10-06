Feature: gz validate --bullet-retention — classification ownership and source-aware retention

  A scorecard row attributed to a corpus-owned section takes its classification
  from the corpus entry it cites, never from the scorecard cell. A disagreement
  is reported while the corpus value binds, an unreviewed capture default refuses
  to bind, a skill-sourced row is retained against its own source file, a
  pinned row the audit no longer reads is named, an absent scorecard is
  refused while its rows stay pinned, and a pinned row is held when nothing
  but the pinned file enrolls the project
  (ADR-0.35.0 § Decision item 9; GHI #737, GHI #939).

  Background:
    Given a project whose control surface has one corpus-owned section

  @REQ-0.35.0-10-01
  Scenario: The corpus class enforces an owned bullet the scorecard scores Judgment
    Given the owned corpus entry is classified "Mechanical"
    And the scorecard scores the owned bullet "Judgment"
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes "e-owned"

  @REQ-0.35.0-10-02
  Scenario: A pinned row the scorecard no longer carries fails closed
    Given the owned corpus entry is classified "Judgment"
    And the scorecard scores the owned bullet "Judgment"
    And the pinned identities list a row the scorecard no longer carries
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes "fixture-contract #2"

  @REQ-0.35.0-10-02
  Scenario: An absent scorecard fails closed while its rows stay pinned
    Given the owned corpus entry is classified "Judgment"
    And the scorecard scores the owned bullet "Judgment"
    And the scorecard file is removed
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes "is absent"

  @REQ-0.35.0-10-02
  Scenario: A pinned row is held when nothing but the pinned file enrolls the project
    Given the project carries no ownership declaration
    And the scorecard's only row is pinned and attributed to a skill file
    And the scorecard is emptied
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes "fixture-contract #1"

  @REQ-0.35.0-10-03
  Scenario: A disagreement is reported while the corpus value binds
    Given the owned corpus entry is classified "Judgment"
    And the scorecard scores the owned bullet "Mechanical"
    When I run "gz validate --bullet-retention"
    Then the command exits 0
    And the output includes "the corpus value binds"

  @REQ-0.35.0-10-04
  Scenario: An unreviewed capture default refuses to bind
    Given the owned corpus entry is classified "Ambiguous"
    And the scorecard scores the owned bullet "Judgment"
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes "e-owned"
    And the output includes "Ambiguous"

  @REQ-0.35.0-10-08
  Scenario: A skill-sourced row is retained by its skill file
    Given the owned corpus entry is classified "Judgment"
    And the scorecard scores the owned bullet "Judgment"
    And a Mechanical scorecard row attributed to a skill file that carries its text
    When I run "gz validate --bullet-retention"
    Then the command exits 0

  @REQ-0.35.0-10-09
  Scenario: A skill-sourced row absent from its skill file fails closed
    Given the owned corpus entry is classified "Judgment"
    And the scorecard scores the owned bullet "Judgment"
    And a Mechanical scorecard row attributed to a skill file that lacks its text
    When I run "gz validate --bullet-retention"
    Then the command exits non-zero
    And the output includes ".gzkit/skills/demo/SKILL.md"
