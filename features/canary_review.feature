Feature: Operator review of guard canaries is booked through a governed verb
  A guard canary's review was a hand-edited reviewed_by field, which could not tell an
  operator's review from an agent's (GHI #1161). gz canary review books the operator's
  verbatim words as a guard_canary_reviewed ledger event, the review's only witness.

  Scenario: canary review help names the witness flags
    When I run the gz command "canary review --help"
    Then the command exits with code 0
    And the output contains "--operator-text"
    And the output contains "--ruling-source"
    And the output contains "guard_canary_reviewed"

  Scenario: a review without the operator's words is a usage error
    When I run the gz command "canary review --claim gate-enrollment --attestor g0"
    Then the command exits with code 2
