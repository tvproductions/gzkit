Feature: Work packages run through the gz wp verbs
  A work package's record is edited only through gz verbs, and its lifecycle and
  change ladder live in the ledger (drydock RO-5 tranche 2,
  docs/governance/harbor-ro5-work-packages.md).

  Scenario: the wp group lists every verb the operator named
    When I run the gz command "wp --help"
    Then the command exits with code 0
    And the output contains "initiate"
    And the output contains "freeze"
    And the output contains "close"
    And the output contains "change"

  Scenario: closing without the Gate 5 attestor is a usage error
    When I run the gz command "wp close WP-01-x --decision proceed --residual-risk none --evidence E"
    Then the command exits with code 2

  Scenario: a package the store does not hold is a user error
    When I run the gz command "wp show WP-99-nothing"
    Then the command exits with code 1
