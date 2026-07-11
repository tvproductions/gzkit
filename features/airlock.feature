Feature: gz airlock entry/exit membrane
  The gz airlock in verb surfaces the airlock-IN three-beat gate (ADR-0.33.0,
  OBPI-0.33.0-02): DECLARE -> PING -> RECONCILE -> decide; the co-equal gz
  airlock out verb surfaces the airlock-OUT exit drift-diff (OBPI-0.33.0-03):
  drift-diff -> findings -> closed decision menu -> fresh-transit routing -> L2.
  Both are diagnostic-only tracers — surfaced drift/NO-GO reports but still
  exits 0; only an unresolvable target brief exits 1. For a real leaf OBPI the
  ontology sonar returns no dependents and no parent invariants are supplied, so
  the seam-map/drift-diff layers are empty and the verdict is proceed/clean (the
  documented calibration frontier).

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

  @REQ-0.33.0-03-02
  Scenario: airlock out runs the exit drift-diff for a real target and exits 0
    Given the gzkit repository working tree
    When I run "gz airlock out --target OBPI-0.33.0-01 --dry-run" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "decision menu: leave_it_be, modify, repair, adjust_maps"

  @REQ-0.33.0-03-02
  Scenario: airlock out --json emits a machine-readable exit-report payload
    Given the gzkit repository working tree
    When I run "gz airlock out --target OBPI-0.33.0-01 --dry-run --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "adjust_maps"
