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

  Scenario: a legacy withdrawal without its human witness is a usage error
    When I run the gz command "wp withdraw-legacy OBPI-0.1.0-01 --reason r"
    Then the command exits with code 2

  Scenario: the runs report names what it reads
    When I run the gz command "wp runs --help"
    Then the command exits with code 0
    And the output contains "no marker is read"

  Scenario: an order the store does not hold is a user error
    Given the workspace is initialized
    And the requirements catalog is seeded
    When I run the gz command "wp order show ORD-99-nothing"
    Then the command exits with code 1
    And the output contains "is not in data/catalog/orders.json"

  Scenario: a package the store does not hold is a user error
    Given the workspace is initialized
    And the requirements catalog is seeded
    When I run the gz command "wp show WP-99-nothing"
    Then the command exits with code 1
    And the output contains "is not in data/catalog/work_packages.json"

  Scenario: recording an issue close without its reviewer is a usage error
    When I run the gz command "wp resolve WP-01-x 1183 --commit abc1234"
    Then the command exits with code 2

  Scenario: an issue close on a package the store does not hold is a user error
    When I run the gz command "wp resolve WP-99-nothing 1183 --commit abc1234 --reviewer r"
    Then the command exits with code 1

  Scenario: recording evidence without an entry is a usage error
    When I run the gz command "wp evidence WP-01-x"
    Then the command exits with code 2

  Scenario: acceptance on a package the store does not hold is blocked
    When I run the gz command "wp acceptance WP-99-nothing status"
    Then the command exits with code 3
