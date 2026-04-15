Feature: ARB self-reporting middleware
  As an agent producing verification evidence for Heavy-lane attestations
  I want a CLI surface that wraps QA commands and emits validated receipts
  So that attestation-enrichment claims can cite deterministic artifacts.

  Scenario: arb surface exposes every rule-declared verb
    When I run the gz command "arb --help"
    Then the command exits with code 0
    And the output contains "ruff"
    And the output contains "step"
    And the output contains "ty"
    And the output contains "coverage"
    And the output contains "validate"
    And the output contains "advise"
    And the output contains "patterns"

  Scenario: arb validate returns zero-state cleanly on empty receipts dir
    When I run the gz command "arb validate --limit 5"
    Then the command exits with code 0
    And the output contains "ARB Receipt Validation"
    And the output contains "Receipts scanned"

  Scenario: arb advise returns zero-state cleanly on empty receipts dir
    When I run the gz command "arb advise --limit 5"
    Then the command exits with code 0
    And the output contains "ARB Advice"
    And the output contains "Recommendations"
    And the output contains "No findings in recent receipts"

  Scenario: arb patterns returns zero-state cleanly on empty receipts dir
    When I run the gz command "arb patterns --limit 5"
    Then the command exits with code 0
    And the output contains "ARB Pattern Extraction Report"

  Scenario: arb patterns compact mode emits single-line summary
    When I run the gz command "arb patterns --compact --limit 5"
    Then the command exits with code 0
    And the output contains "arb patterns:"

  Scenario: arb validate JSON output is machine-readable
    When I run the gz command "arb validate --json --limit 5"
    Then the command exits with code 0
    And the output contains "scanned"
    And the output contains "valid"
    And the output contains "unknown_schema"
