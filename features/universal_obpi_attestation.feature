Feature: Universal OBPI attestation doctrine surface
  ADR-0.0.36 collapses the Lane & Kind Attestation Matrix to a universal binding
  rule. AGENTS.md and all mirrors must reflect the new doctrine.

  @REQ-0.0.36-01-01
  Scenario: Deprecated self-close phrase is absent from workspace AGENTS.md
    Given the workspace is initialized with agent surfaces in heavy mode
    Then the file "AGENTS.md" does not contain "Self-closeable after evidence"

  @REQ-0.0.36-01-02
  Scenario: Universal attestation binding rule is present in workspace AGENTS.md
    Given the workspace is initialized with agent surfaces in heavy mode
    Then the file "AGENTS.md" contains "ALWAYS required for every OBPI completion"
    And the file "AGENTS.md" contains "regardless"

  @REQ-0.0.36-01-03
  Scenario: Lane and kind axes are retained for gate-firing scope in workspace AGENTS.md
    Given the workspace is initialized with agent surfaces in heavy mode
    Then the file "AGENTS.md" contains "Gate 3"
    And the file "AGENTS.md" contains "Gate 4"
    And the file "AGENTS.md" contains "which gates"

  @REQ-0.0.36-01-04
  Scenario: GHI #342 and ADR-0.0.36 cited inline in workspace AGENTS.md
    Given the workspace is initialized with agent surfaces in heavy mode
    Then the file "AGENTS.md" contains "GHI #342"
    And the file "AGENTS.md" contains "ADR-0.0.36"

  @REQ-0.0.36-01-05
  Scenario: Workspace AGENTS.md mirror reflects the universal attestation rule
    Given the workspace is initialized with agent surfaces in heavy mode
    Then the file "AGENTS.md" contains "Universal OBPI Attestation"
    And the file "AGENTS.md" does not contain "Lane & Kind & Sensitivity Attestation Matrix"
