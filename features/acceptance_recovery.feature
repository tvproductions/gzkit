Feature: Acceptance proof survives legitimate repair without hiding defects
  Real disposable projects exercise proof execution, persistence, and consumers.
  Reviewer transport fixtures are synthetic; their judgments are test inputs.

  Scenario: Equivalent execution and independent repair closure reach attestation request
    Given a disposable acceptance project
    When a required finding is repaired and independently closed
    Then equivalent proof reexecution preserves readiness through reload
    And the real ceremony requests human attestation
    And both CLI entrypoints report ready with successful process exits

  Scenario: A coherent shared oracle does not demonstrate sensitivity
    Given a disposable acceptance project
    When a shared oracle and an independent oracle face the same production defect
    Then only the independently derived expectation supplies proof

  Scenario Outline: An interrupted active mutation restores exact bytes and permits recovery
    Given a disposable acceptance project
    When proof execution times out after activation with <newline> source bytes
    Then no proof is recorded and the original source is restored exactly
    And a subsequent clean execution records valid proof

    Examples:
      | newline |
      | LF      |
      | CRLF    |

  Scenario: Module import failure earns no behavioral kill
    Given a disposable acceptance project
    When the production control breaks module import
    Then that execution supplies no valid behavioral proof

  Scenario: Same-test diagnostic failure cannot justify the required behavioral claim
    Given a disposable acceptance project
    When an earlier diagnostic assertion masks the contract assertion
    Then the failure trace distinguishes diagnostic masking from required sensitivity
