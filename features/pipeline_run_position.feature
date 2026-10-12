Feature: Pipeline run position
  The pipeline marker reports the stage a run has reached and the position
  inside it, never the stage the launch named (OBPI-0.35.0-15, GHI #1172).

  @REQ-0.35.0-15-04
  Scenario Outline: A launch with nothing after it reports its launch values and no position
    Given a pipeline run launched with entry "<entry>"
    When the launch markers and the ledger replay are read
    Then the marker entry is "<entry>" and its stage is "<stage>"
    And the marker resume point is "<resume_point>"
    And the marker carries no blockers and its required human action is "<human_action>"
    And neither the marker nor the ledger replay reports a position

    Examples: the full launch and each --from entry
      | entry    | stage     | resume_point | human_action |
      | full     | implement | verify       | none         |
      | verify   | verify    | ceremony     | none         |
      | ceremony | ceremony  | sync         | attestation  |
      | sync     | sync      | none         | none         |

  @REQ-0.35.0-15-07
  Scenario: An advanced marker keeps its readers working and both files identical
    Given a pipeline run launched with entry "full"
    And the run has recorded a Stage 2 dispatch
    When the run records a crossing into "verify" at phase "verification"
    Then the fence reads stage "verify" from both marker files
    And the fence refuses a production write at the stage reached
    And the resume command is the one the stage reached prescribes
    And the recorded dispatch is still read from the marker
    And the launch nonce, start time, entry and receipt state are unchanged
    And both marker files hold the same bytes

  @REQ-0.35.0-15-01
  Scenario: A run launched in full reads each stage its commands take it to
    Given a project whose run was launched in full through gz obpi pipeline
    When the run crosses the boundary "gz obpi pipeline --from=verify with a failing command"
    Then both marker files read stage "verify" and not the launch stage
    When the run crosses the boundary "gz obpi pipeline --from=verify with every command passing"
    Then both marker files read stage "ceremony" and not the launch stage
    When the run crosses the boundary "gz obpi complete"
    Then both marker files read stage "sync" and not the launch stage
    And the marker was updated later than the run started
    And both marker files hold the same bytes

  @REQ-0.35.0-15-01
  Scenario: An unbroken run reaches ceremony and sync with no relaunch
    Given a project whose run was launched in full through gz obpi pipeline
    When the run crosses the boundary "gz obpi present-evidence"
    Then both marker files read stage "ceremony" and not the launch stage
    And the marker entry is still "full" and its nonce is the launch's
    When the run crosses the boundary "gz obpi complete"
    Then both marker files read stage "sync" and not the launch stage
    And the marker was updated later than the run started
    And the marker entry is still "full" and its nonce is the launch's
    And the ledger holds 1 launch for the run

  @REQ-0.35.0-15-02
  Scenario Outline: A command that begins a stage's work moves the run and names its position
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "<from>"
    When the run crosses the boundary "<boundary>"
    Then the command appended <events> stage transitions
    And the command recorded the "<kind>" "<label>" inside stage "<stage>"
    And both marker files name what the ledger last recorded

    Examples: the work-starting boundaries of Requirement 2 (a)
      | from      | boundary                                                  | events | stage     | kind  | label            |
      | implement | gz obpi pipeline --from=verify with a failing command     | 2      | verify    | phase | verification     |
      | implement | gz obpi pipeline --from=verify with every command passing | 3      | ceremony  | round | ceremony         |
      | implement | gz obpi pipeline --from=ceremony                          | 1      | ceremony  | round | ceremony         |
      | implement | gz obpi present-evidence                                  | 1      | ceremony  | round | present-evidence |
      | implement | gz obpi complete                                          | 1      | sync      | step  | complete         |
      | ceremony  | gz task start                                             | 1      | implement | task  | TASK             |
      | ceremony  | gz obpi dispatch --task 2                                 | 1      | implement | task  | task 2           |

  @REQ-0.35.0-15-02
  Scenario Outline: A check or a bookkeeping command records inside the stage the run has reached
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "<stage>"
    When the run crosses the boundary "<boundary>"
    Then the command appended <events> stage transitions
    And the command recorded the "<kind>" "<label>" inside stage "<stage>"
    And both marker files name what the ledger last recorded
    And the fence reads stage "<stage>" from both marker files

    Examples: the in-place boundaries of Requirement 2 (b)
      | stage     | boundary                                              | events | kind  | label               |
      | implement | gz obpi precomplete                                   | 1      | task  | precomplete         |
      | verify    | gz obpi precomplete                                   | 1      | phase | precomplete         |
      | ceremony  | gz obpi precomplete                                   | 1      | round | precomplete         |
      | sync      | gz obpi precomplete                                   | 1      | step  | precomplete         |
      | ceremony  | gz obpi precomplete with the short id                 | 1      | round | precomplete         |
      | implement | gz obpi verify-packet                                 | 1      | task  | verify-packet       |
      | ceremony  | gz obpi verify-packet                                 | 1      | round | verify-packet       |
      | ceremony  | gz obpi acceptance review                             | 1      | round | acceptance-review   |
      | implement | gz obpi acceptance human-review                       | 1      | task  | acceptance-review   |
      | ceremony  | gz task complete                                      | 1      | round | TASK                |
      | verify    | gz task block                                         | 1      | phase | TASK                |
      | sync      | gz task escalate                                      | 1      | step  | TASK                |
      | verify    | gz obpi pipeline --from=verify with a failing command | 2      | phase | verification-failed |

  @REQ-0.35.0-15-02
  Scenario: A command run after the receipt has ended the run records nothing
    Given a project whose run was launched in full through gz obpi pipeline
    When the run crosses the boundary "gz obpi complete"
    And the run crosses the boundary "gz obpi precomplete"
    And the run crosses the boundary "gz task start"
    Then the ledger holds 1 stage transition for the run

  @REQ-0.35.0-15-02
  Scenario: A check finds the stage reached on the ledger when the marker is gone
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "verify"
    When both marker files are deleted
    And the run crosses the boundary "gz obpi precomplete"
    Then the command recorded the "phase" "precomplete" inside stage "verify"
    And the ledger says the run has reached stage "verify"

  @REQ-0.35.0-15-06
  Scenario Outline: The session orientation shows the stage a run has reached and its position
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "<stage>"
    When the session orientation is collected
    Then the orientation reports the run at stage "<stage>" with a "<kind>" position
    And the orientation position is the last boundary the ledger recorded
    And the orientation section names stage "<stage>" and that position, not the launch stage

    Examples: a run that has left the stage its launch named
      | stage    | kind  |
      | verify   | phase |
      | ceremony | round |
      | sync     | step  |

  @REQ-0.35.0-15-03
  Scenario Outline: gz state --repair rebuilds a deleted marker to the stage and position it held
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "<stage>"
    When both marker files are deleted
    And gz state --repair is run
    Then the repair reports the run rebuilt at stage "<stage>"
    And both marker files name what the ledger last recorded
    And the rebuilt marker carries the time of the last recorded crossing
    And the rebuilt marker carries the nonce and the entry the launch event recorded

    Examples: a run that has crossed a recorded boundary
      | stage    |
      | verify   |
      | ceremony |
      | sync     |

  @REQ-0.35.0-15-03
  Scenario: gz state --repair rebuilds a launch with nothing after it to its launch values
    Given a project whose run was launched in full through gz obpi pipeline
    When both marker files are deleted
    And gz state --repair is run
    Then the repair reports the run rebuilt at stage "implement"
    And both rebuilt marker files read stage "implement" and no position
    And the rebuilt marker carries the time of the launch event
    And the rebuilt marker carries the nonce and the entry the launch event recorded

  @REQ-0.35.0-15-03
  Scenario: gz state --repair restores a deleted legacy marker as a copy of the per-OBPI marker
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "verify"
    When the legacy marker file is deleted
    And gz state --repair is run
    Then both marker files hold the same bytes
    And the per-OBPI marker file is byte for byte what it was before the repair
    And the repair reports the legacy marker file restored and nothing rebuilt or declined

  @REQ-0.35.0-15-05
  Scenario: gz state --repair leaves a marker on disk exactly as it is
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "verify"
    When gz state --repair is run
    Then both marker files are byte for byte what they were before the repair
    And the repair reports nothing rebuilt and nothing declined

  @REQ-0.35.0-15-05
  Scenario: A rebuilt marker keeps the time of its last crossing and is not cleared as stale
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "verify"
    When both marker files are deleted
    And gz state --repair is run
    And gz obpi pipeline --clear-stale is run
    Then both marker files name what the ledger last recorded
    And the rebuilt marker carries the time of the last recorded crossing

  @REQ-0.35.0-15-05
  Scenario: gz state --repair declines a run whose last crossing is past the stale bound
    Given a project whose run was launched in full through gz obpi pipeline
    And the run has reached stage "verify"
    And every ledger event of the run is older than the stale bound
    When both marker files are deleted
    And gz state --repair is run
    Then no marker file is on disk
    And the repair declines the run and says why
