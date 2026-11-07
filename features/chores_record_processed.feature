Feature: A processed tautological-test op is booked through a gz verb
  GHI #1305: the decommission-tautological-tests chore promised a
  chore_decommission_processed ledger event per processed item and no verb
  wrote one. `gz chores record-processed` books it, refusing before any write
  when the slug, the work order or the file is wrong.

  Scenario: Another chore's slug is refused
    Given a fresh empty project directory
    When I run "gz chores record-processed some-other-chore --file tests/test_x.py --disposition convert --task TASK-x" as a subprocess
    Then the subprocess exits with code 1
    And the subprocess output contains "books no processed items"

  Scenario: A file the baseline never flagged is refused
    Given a fresh empty project directory
    When I run "gz init --no-skeleton" as a subprocess
    And I run "gz chores record-processed decommission-tautological-tests --file tests/test_x.py --disposition convert --task TASK-x" as a subprocess
    Then the subprocess exits with code 1
    And the subprocess output contains "holds no op"
