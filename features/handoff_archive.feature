Feature: gz handoff archive verb (move-not-delete retention)
  gz handoff archive relocates handoffs older than a threshold from
  .gzkit/handoffs/ into .gzkit/handoffs/archive/ (ADR-0.0.65, OBPI-0.0.65-05),
  honoring the lock-coupling, chain-integrity, and migration-floor guards.
  --dry-run reports the plan and mutates nothing; every scenario here is
  --dry-run against the live tree (never a destructive move).

  @REQ-0.0.65-05-05
  Scenario: dry-run reports the would-move set as JSON and mutates nothing
    Given the gzkit repository working tree
    When I run "gz handoff archive --older-than 30d --dry-run --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "would_move"
    And the subprocess output contains "dry_run"

  @REQ-0.0.65-05-02
  Scenario: the dry-run plan surfaces the lock-coupling skip bucket
    Given the gzkit repository working tree
    When I run "gz handoff archive --older-than 30d --dry-run --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "skipped_locked"

  @REQ-0.0.65-05-03
  Scenario: the dry-run plan surfaces the chain-integrity skip bucket
    Given the gzkit repository working tree
    When I run "gz handoff archive --older-than 30d --dry-run --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "skipped_chained"

  @REQ-0.0.65-05-05
  Scenario: an invalid --older-than value is rejected fail-closed
    Given the gzkit repository working tree
    When I run "gz handoff archive --older-than bogus --dry-run" as a subprocess
    Then the subprocess exits with code 1
