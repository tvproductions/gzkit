Feature: Constitutional invariant composition renderer (ADR-0.0.37, OBPI-0.0.37-02)
  As an operator maintaining gzkit governance
  I want the composition renderer to produce byte-deterministic output
  And I want --check mode to detect drift between the registry and AGENTS.md

  Background:
    Given the workspace is initialized
    And the constitutional invariant registry has at least one entry

  @REQ-0.0.37-02-01
  Scenario: Renderer produces identical bytes across consecutive invocations
    When I run "gz governance render --target agents-md --stdout" twice
    Then the two outputs are byte-identical

  @REQ-0.0.37-02-02
  Scenario: --check exits 0 when AGENTS.md matches rendered output
    Given AGENTS.md contains the current rendered output
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 0

  @REQ-0.0.37-02-02
  Scenario: --check exits 3 when AGENTS.md differs from rendered output
    Given AGENTS.md contains stale content
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 3
    And the output contains "@@"

  @REQ-0.0.37-02-04
  Scenario: Unsupported target exits nonzero with error message
    When I run "gz governance render --target skill-readme"
    Then the command exits non-zero
    And the output contains "unsupported target"

  @REQ-0.0.37-02-03
  Scenario: Write mode writes rendered bytes to AGENTS.md and reports byte count
    When I run "gz governance render --target agents-md"
    Then the command exits with code 0
    And the output contains "bytes"
    And AGENTS.md exists in the workspace

  @REQ-0.0.37-02-05
  Scenario: governance render verb resolves via gz governance render --help
    When I run "gz governance render --help"
    Then the command exits with code 0
    And the output contains "render"

  # OBPI-0.0.37-03 — Composition drift validator (gz validate --invariant-coherence)

  @REQ-0.0.37-03-01
  Scenario: gz validate --invariant-coherence exits 0 on matching AGENTS.md
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md matches the rendered registry output
    When I run "gz validate --invariant-coherence"
    Then the command exits with code 0

  @REQ-0.0.37-03-02
  Scenario: gz validate --invariant-coherence exits 3 on drift
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md differs from the rendered registry output
    When I run "gz validate --invariant-coherence"
    Then the command exits with code 3
    And the output contains "Diff (first 50 lines)"
    And the output contains "@@"

  @REQ-0.0.37-03-03
  Scenario: gz validate --invariant-coherence emits composition_rendered event
    Given the constitutional invariant registry has at least one entry
    When I run "gz validate --invariant-coherence"
    Then a "composition_rendered" event is appended to the ledger
