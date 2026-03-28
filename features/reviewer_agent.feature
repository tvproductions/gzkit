Feature: OBPI reviewer agent dispatch  # OBPI-0.23.0-03
  An independent reviewer agent verifies delivered work against OBPI
  promises with fresh-eyes assessment of promises-met, docs-quality,
  and closing-argument-quality.

  @review @dispatch
  Scenario: Reviewer prompt contains brief and closing argument
    Given an OBPI brief with 2 requirements
    And a closing argument "This work earned its closure by delivering X"
    And 2 changed files and 1 doc file
    When I compose the reviewer prompt
    Then the prompt contains the OBPI identifier
    And the prompt contains the brief content
    And the prompt contains the closing argument
    And the prompt contains all changed files
    And the prompt contains the doc file
    And the prompt contains the assessment JSON schema

  @review @dispatch
  Scenario: Reviewer prompt handles missing closing argument
    Given an OBPI brief with 1 requirements
    And no closing argument
    And 1 changed files and 0 doc file
    When I compose the reviewer prompt
    Then the reviewer prompt contains "No closing argument provided"

  @review @parse
  Scenario: Valid PASS assessment is parsed from agent output
    Given agent output with a valid PASS assessment for 2 requirements
    When I parse the reviewer assessment
    Then the assessment verdict is "PASS"
    And 2 promise assessments are returned
    And docs quality is "substantive"
    And closing argument quality is "earned"

  @review @parse
  Scenario: Valid FAIL assessment is parsed from agent output
    Given agent output with a valid FAIL assessment
    When I parse the reviewer assessment
    Then the assessment verdict is "FAIL"
    And docs quality is "missing"
    And closing argument quality is "missing"

  @review @parse
  Scenario: CONCERNS assessment with mixed promises
    Given agent output with a CONCERNS assessment and mixed promises
    When I parse the reviewer assessment
    Then the assessment verdict is "CONCERNS"
    And promise 1 is met
    And promise 2 is not met

  @review @parse
  Scenario: Invalid agent output returns no assessment
    Given agent output with no JSON block
    When I parse the reviewer assessment
    Then no assessment is returned

  @review @artifact
  Scenario: Assessment artifact is stored alongside the brief
    Given a parsed PASS reviewer assessment
    And a temporary ADR package directory
    When I store the reviewer assessment
    Then a REVIEW artifact file exists in the briefs directory
    And the artifact contains the verdict
    And the artifact contains promise assessments

  @review @ceremony
  Scenario: Assessment is formatted for ceremony display
    Given a parsed CONCERNS reviewer assessment with 3 promises
    When I format the assessment for ceremony
    Then the output contains a promise table with 3 rows
    And the output contains the docs quality
    And the output contains the closing argument quality
    And the output contains the verdict
