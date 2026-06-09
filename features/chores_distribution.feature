Feature: Chores distribution end-to-end
  Heavy-lane Gate 4 proof for ADR-0.0.21 (chores as gzkit surface).
  Exercises the install -> scaffold -> list -> repair lifecycle against the
  real installed gzkit package (editable install in .venv resolves
  importlib.resources('gzkit.chores') to the canonical source tree).

  @REQ-0.0.21-07-01
  @REQ-0.0.21-07-02
  @REQ-0.0.21-07-06
  @REQ-0.0.21-07-07
  Scenario: Package fallback works without gz init
    Given a fresh empty project directory
    When I run "gz chores list" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "quality-check"
    And the subprocess output contains "pool-triage"

  @REQ-0.0.21-07-03
  Scenario: gz init populates project chores and --explain reports project source
    Given a fresh empty project directory
    When I run "gz init --no-skeleton" as a subprocess
    And I run "gz chores list --explain" as a subprocess
    Then the subprocess exits with code 0
    And the file ".gzkit/chores/quality-check/CHORE.md" exists
    And every chore row in the subprocess output reports "project" source

  @REQ-0.0.21-07-04
  Scenario: Re-running gz init preserves operator edits to a chore
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "OPERATOR-EDIT-MARKER-XYZ"
    When I run "gz init --no-skeleton" as a subprocess
    Then the subprocess exits with code 0
    And the file ".gzkit/chores/quality-check/CHORE.md" contains "OPERATOR-EDIT-MARKER-XYZ"

  @REQ-0.0.21-07-05
  Scenario: Merge diff fires for canonical-only slug and --yes writes the merge
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the slug "quality-check" has been removed from ".gzkit/chores/registry.json"
    When I run "gz init --no-skeleton --yes" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "+ quality-check"
    And the registry ".gzkit/chores/registry.json" contains slug "quality-check"
