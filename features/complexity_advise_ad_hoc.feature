Feature: gz complexity advise — ad-hoc vs auto-chain presenter dispatch (ADR-0.0.29 / OBPI-0.0.29-06)
  As an operator using the complexity advisor ad-hoc or via auto-chain hook,
  I want the advisor to present output appropriate to the pathway:
  ad-hoc preview shows verbose diagnosis with full doctrinal frame,
  while auto-chain trigger-time shows a concise one-liner hint,
  so that operators get fast preview-before-fail guidance and hooks get compact, parseable output.

  @REQ-0.0.29-06-01
  Scenario: ad-hoc preview against clean file shows "no crossings"
    Given a synthetic complexity-advise environment with a clean Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity-thresholds.json"
    Then the command exits with code 0
    And the output contains "No crossings"

  @REQ-0.0.29-06-02
  Scenario: ad-hoc preview against warn-band file shows archetype and authority
    Given a synthetic complexity-advise environment with a warn-band Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity-thresholds.json"
    Then the command exits with code 0
    And the output contains "Archetype"
    And the output contains "Authority"

  @REQ-0.0.29-06-03
  Scenario: auto-chain against warn-band file produces concise one-liner
    Given a synthetic complexity-advise environment with a warn-band Python source
    When I run the gz command "complexity advise subject.py --rule-path complexity-thresholds.json --auto-chain"
    Then the command exits with code 0
    And the output contains "radon_cc"
    And the output does not contain "Doctrinal frame"
