Feature: gz handoff verb (list, resume, create)
  The gz handoff verb surfaces session handoff documents under
  .gzkit/handoffs/ (ADR-0.0.65, OBPI-0.0.65-03): `list` and `resume` are
  read-only projections over the real handoff corpus; `create` authors a new
  handoff document but routes through the fail-closed validate_handoff_document
  gate — on any violation nothing is written and the verb exits 1.

  @REQ-0.0.65-03-01
  Scenario: handoff list surfaces the handoff corpus as JSON
    Given the gzkit repository working tree
    When I run "gz handoff list --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "path"

  @REQ-0.0.65-03-01
  Scenario: handoff list scopes to a single ADR
    Given the gzkit repository working tree
    When I run "gz handoff list --adr ADR-0.0.65 --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "ADR-0.0.65"

  @REQ-0.0.65-03-02
  Scenario: handoff resume reports staleness for the newest handoff
    Given the gzkit repository working tree
    When I run "gz handoff resume --adr ADR-0.0.65 --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "staleness"

  @REQ-0.0.65-03-03
  Scenario: handoff create is fail-closed on an invalid ADR id
    Given the gzkit repository working tree
    When I run "gz handoff create --adr ADR-BOGUS --slug x --agent g0 --decisions no-op" as a subprocess
    Then the subprocess exits with code 1
    And the subprocess output contains "Refusing to write handoff"

  @REQ-0.0.65-03-03
  Scenario: handoff create authors a valid handoff document
    Given a fresh empty project directory
    And the workspace has been initialized via gz init
    When I run "gz handoff create --adr ADR-0.0.65 --slug bdd-test --agent g0 --decisions test-decision --json" as a subprocess
    Then the subprocess exits with code 0
    And the subprocess output contains "path"
