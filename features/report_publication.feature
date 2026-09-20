Feature: Retained big-picture publication
  An operator-requested assessment is preserved and witnessed without replacing history.

  Scenario: Publish and retry a retained assessment
    Given a fresh empty project directory
    And a draft big-picture assessment with configured publication paths
    When I run "gz report publish --source draft.md --id 2026-09-19-assessment --json" as a subprocess
    Then the subprocess exits with code 0
    When I run "gz report publish --source draft.md --id 2026-09-19-assessment --json" as a subprocess
    Then the subprocess exits with code 0
    And the assessment is retained exactly with one publication witness
