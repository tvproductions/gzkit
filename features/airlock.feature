Feature: gz airlock-IN preflight membrane
  The gz airlock in verb surfaces the airlock-IN three-beat gate (ADR-0.33.0,
  OBPI-0.33.0-02): DECLARE -> PING -> RECONCILE -> decide. It is a
  diagnostic-only tracer — a NO-GO prints a refusal but still exits 0; only an
  unresolvable target brief exits 1. For a real leaf OBPI the ontology sonar
  returns no dependents and no parent invariants are supplied, so the seam-map
  push/pull layers are empty and the decision is proceed (the documented
  calibration frontier).

  @REQ-0.33.0-02-06
  Scenario: airlock in runs the preflight for a real target and exits 0
    Given the gzkit repository working tree
    When I run "gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "decision: proceed"

  @REQ-0.33.0-02-06
  Scenario: airlock in --json emits a machine-readable preflight payload
    Given the gzkit repository working tree
    When I run "gz airlock in --target OBPI-0.33.0-01 --dry-run --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "proceed"
