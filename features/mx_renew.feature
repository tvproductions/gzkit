Feature: MX lease renewal
  As the operator resuming a drydock session whose lease ran out
  I want one command that renews the lease without leaving the hangar
  So that a resume does not cost the full-strength exit gate (GHI #1261).

  Scenario: the mx group offers renew beside enter and exit
    When I run the gz command "mx --help"
    Then the command exits with code 0
    And the output contains "renew"

  Scenario: renew refuses when no session is open
    When I run the gz command "mx renew --attestor g0"
    Then the command exits with code 1
    And the output contains "no open MX session to renew"
