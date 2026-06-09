Feature: gz init --update — version-aware canonical refresh
  Heavy-lane Gate 4 proof for OBPI-0.0.32-05 under ADR-0.0.32 (canonical
  surface packaging). Exercises the three-state IDENTICAL/STALE/EDITED
  detection in :func:`gzkit.commands.init_cmd._refresh_canonical_surfaces`
  via the operator-facing ``gz init --update`` flag.

  @REQ-0.0.32-05-01
  @REQ-0.0.32-05-07
  Scenario: stale canonical refreshes cleanly
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "DRIFTED-WITHOUT-MARKER-XYZ"
    When I run "gz init --update" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "STALE"
    And the subprocess output contains ".gzkit/chores/quality-check/CHORE.md"

  @REQ-0.0.32-05-02
  @REQ-0.0.32-05-05
  @REQ-0.0.32-05-06
  @REQ-0.0.32-05-07
  Scenario: project-edit preservation (EDITED state is not overwritten)
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "<!-- gzkit-canonical-version: 0.1.0 -->"
    When I run "gz init --update" as a subprocess
    Then the subprocess exits with code 3
    And the subprocess output contains "EDITED"
    And the file ".gzkit/chores/quality-check/CHORE.md" contains "<!-- gzkit-canonical-version: 0.1.0 -->"

  @REQ-0.0.32-05-03
  @REQ-0.0.32-05-05
  @REQ-0.0.32-05-07
  Scenario: conflict reporting — unresolved EDITED entries surface in summary
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "<!-- gzkit-canonical-version: 0.1.0 -->"
    And the operator edits ".gzkit/chores/pool-triage/CHORE.md" with marker "<!-- gzkit-canonical-version: 0.1.0 -->"
    When I run "gz init --update" as a subprocess
    Then the subprocess exits with code 3
    And the subprocess output contains "Conflicts (EDITED"
    And the subprocess output contains ".gzkit/chores/quality-check/CHORE.md"
    And the subprocess output contains ".gzkit/chores/pool-triage/CHORE.md"

  @REQ-0.0.32-05-04
  @REQ-0.0.32-05-08
  Scenario: dry-run prints per-artifact action without writing
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "DRIFTED-WITHOUT-MARKER-XYZ"
    When I run "gz init --update --dry-run" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "Dry run"
    And the subprocess output contains "STALE"
    And the file ".gzkit/chores/quality-check/CHORE.md" contains "DRIFTED-WITHOUT-MARKER-XYZ"
