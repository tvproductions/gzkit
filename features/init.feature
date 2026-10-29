Feature: gz init — the uv-built project and the version-aware canonical refresh
  Heavy-lane Gate 4 proof for OBPI-0.0.32-05 under ADR-0.0.32 (canonical
  surface packaging). Exercises the three-state IDENTICAL/STALE/EDITED
  detection in :func:`gzkit.commands.init_cmd._refresh_canonical_surfaces`
  via the operator-facing ``gz init --update`` flag. The first scenario is
  RO-9 tranche 7's operator flow: ``gz init --project-type`` builds the
  project through uv and leaves it inside the Astral discipline.

  Scenario: gz init builds a package project through uv
    Given a fresh empty project directory
    When I run "gz init --project-type package --attestor-handle g0" as a subprocess
    Then the subprocess exits with code 0
    And the file "pyproject.toml" contains "uv_build"
    And the file "pyproject.toml" contains "[project.scripts]"
    And the file "pyproject.toml" does not contain "authors"
    And the file "uv.lock" exists
    And the file ".github/workflows/ci.yml" contains "uv sync --locked"
    And the file "data/astral_discipline_baseline.json" exists
    When I run "gz validate --astral-discipline" as a subprocess
    Then the subprocess exits with code 0

  @REQ-0.0.32-05-01
  @REQ-0.0.32-05-07
  Scenario: stale canonical refreshes cleanly
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator deletes ".gzkit/chores/quality-check/CHORE.md"
    When I run "gz init --update" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "STALE"
    And the subprocess output contains ".gzkit/chores/quality-check/CHORE.md"
    And the file ".gzkit/chores/quality-check/CHORE.md" exists

  @REQ-0.0.32-05-02
  @REQ-0.0.32-05-05
  @REQ-0.0.32-05-06
  @REQ-0.0.32-05-07
  Scenario: project-edit preservation (EDITED state is not overwritten)
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "OPERATOR-OWN-CLAUSE"
    When I run "gz init --update" as a subprocess
    Then the subprocess exits with code 3
    And the subprocess output contains "EDITED"
    And the file ".gzkit/chores/quality-check/CHORE.md" contains "OPERATOR-OWN-CLAUSE"

  @REQ-0.0.32-05-03
  @REQ-0.0.32-05-05
  @REQ-0.0.32-05-07
  Scenario: conflict reporting — unresolved EDITED entries surface in summary
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "OPERATOR-OWN-CLAUSE"
    And the operator edits ".gzkit/chores/pool-triage/CHORE.md" with marker "OPERATOR-OWN-CLAUSE"
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
    And the operator deletes ".gzkit/chores/quality-check/CHORE.md"
    When I run "gz init --update --dry-run" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "Dry run"
    And the subprocess output contains "STALE"
    And the file ".gzkit/chores/quality-check/CHORE.md" does not exist
