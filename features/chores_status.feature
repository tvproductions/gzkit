Feature: Chore staleness is readable without running a chore
  GHI #936: a chore's currency gate was readable only by running the chore it
  gates, so nothing outside a run reported an overdue chore. `gz chores status`
  reads every chore's band from its declaration and run record, and announces
  without gating: every band exits 0.

  Scenario: A project that has never run a chore reads its bands and exits 0
    Given a fresh empty project directory
    When I run "gz chores status" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "overdue"
    And the subprocess output contains "unmeasured"

  Scenario: The JSON board carries every band count
    Given a fresh empty project directory
    When I run "gz chores status --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "counts"
    And the subprocess output contains "due_since"
