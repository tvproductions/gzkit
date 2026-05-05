Feature: gz validate --complexity-doctrine-links link integrity (OBPI-0.0.27-07)
  As a governance maintainer
  I want gz validate --complexity-doctrine-links to fail-close on broken citations
  So that operators following an advisor diagnosis at 2am never land on a
  missing or stale distilled-characteristics document.

  Background:
    Given the workspace is initialized

  @REQ-0.0.27-07-01
  Scenario: Well-formed citation resolves clean
    Given a complexity-doctrine fixture with a well-formed citation
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 0

  @REQ-0.0.27-07-02
  Scenario: Missing distilled-characteristics file fails closed
    Given a complexity-doctrine fixture with a missing distilled file
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 3
    And the output contains "distilled-characteristics-1999-01-01.md"

  @REQ-0.0.27-07-03
  Scenario: Unresolved section anchor fails closed
    Given a complexity-doctrine fixture with an unresolved anchor
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 3
    And the output contains "nonexistent-metric"

  @REQ-0.0.27-07-04
  Scenario: Non-portable corpus revision fails closed
    Given a complexity-doctrine fixture with a non-portable corpus revision
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 3
    And the output contains "doctrine-amendment-protocol"

  @REQ-0.0.27-07-05
  Scenario: Speculative-skip marker bypasses a forward-reference citation
    Given a complexity-doctrine fixture with a speculative-skip marker
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 0

  @REQ-0.0.27-07-06
  Scenario: Validator integrates into gz validate --complexity-doctrine-links direct invocation
    When I run the gz command "validate --complexity-doctrine-links"
    Then the command exits with code 0
    And the output contains "complexity_doctrine_links"

  @REQ-0.0.27-07-07
  Scenario: Validate command doc documents the flag with example
    When I check that the file "docs/user/commands/validate.md" contains "--complexity-doctrine-links"
    Then the file is documented
