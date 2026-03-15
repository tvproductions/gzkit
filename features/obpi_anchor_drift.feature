Feature: OBPI anchor drift reconciliation
  Completed OBPIs should fail closed on stale tracked scope without rewriting lifecycle state.

  Scenario: Reconcile preserves completion state while reporting stale anchor drift
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And a completed OBPI with anchor-tracked receipt exists for OBPI-0.1.0-01-demo
    And the tracked module changes after the completion anchor
    When I run the gz command "obpi reconcile OBPI-0.1.0-01-demo --json"
    Then the command exits non-zero
    And JSON path "runtime_state" equals "completed"
    And JSON path "anchor_state" equals "stale"
