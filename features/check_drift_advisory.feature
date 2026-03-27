Feature: Advisory drift detection in gz check
  The gz check command includes drift detection as an advisory (non-blocking)
  check that runs after all blocking quality checks complete.

  Scenario: Check help shows json flag
    When I run the gz command "check --help"
    Then the command exits with code 0
    And the output contains "--json"
    And the output contains "advisory drift"
