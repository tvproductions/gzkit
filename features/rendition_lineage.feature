Feature: gz validate --rendition-lineage — owned-section derivation from the corpus

  The rendition-lineage gate re-derives every section a surface's ownership
  declaration marks "corpus-owned" from the effective corpus and compares it
  against the committed rendition. Owned-section drift is fail-closed and
  names the offending section; unowned bytes are measured debt and never
  change the exit code (ADR-0.35.0 § Decision item 4).

  Background:
    Given I have initialized a gzkit project with a rendition surface
    And the corpus for the surface contains a canon entry for the owned section

  @REQ-0.35.0-06-01
  Scenario: Owned section matching the corpus exits 0
    Given a committed rendition whose owned section matches the corpus
    And a valid ownership declaration and committed lineage exist for it
    When I run "gz validate --rendition-lineage"
    Then the command exits 0

  @REQ-0.35.0-06-02
  Scenario: Owned section carrying non-derivable prose exits 3 naming the section
    Given a committed rendition whose owned section carries hand-authored prose the corpus never said
    And a valid ownership declaration and committed lineage exist for it
    When I run "gz validate --rendition-lineage"
    Then the command exits non-zero
    And the output names the section "owned-section"

  @REQ-0.35.0-06-03
  Scenario: Unowned section with arbitrary prose exits 0 and is reported as measured debt
    Given a committed rendition whose owned section matches the corpus
    And a valid ownership declaration and committed lineage exist for it
    When I run "gz validate --rendition-lineage"
    Then the command exits 0
    And the output includes "measured debt"
