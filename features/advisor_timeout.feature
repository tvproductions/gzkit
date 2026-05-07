Feature: Advisor timeout primitive — fail-open on timeout (ADR-0.0.29 / OBPI-0.0.29-09)
  As an operator whose pre-commit hook invokes the complexity advisor,
  I want the advisor to time out gracefully and never block my commit,
  so that a hanging analysis produces a logged warning instead of a wedged terminal.

  @REQ-0.0.29-09-02
  Scenario: callable exceeds timeout and returns TimeoutTimedOut with elapsed_s
    Given a synthetic timeout environment with a slow callable exceeding 0.2s timeout
    When I invoke run_with_timeout using default context
    Then the result is a TimeoutTimedOut with elapsed_s > 0
    And the result callable_name is "slow_callable"

  @REQ-0.0.29-09-03
  Scenario: timeout logs failure entry to advisor-failures.jsonl
    Given a synthetic timeout environment with a slow callable exceeding 0.2s timeout
    When I invoke run_with_timeout using auto-chain context
    Then the log file contains a valid JSONL entry
    And the log entry has callable_name "slow_callable"
    And the log entry context invocation is "auto-chain"
    And the log entry context file_paths is a list
