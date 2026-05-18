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

  @REQ-0.0.36-02-01
  @REQ-0.0.36-02-02
  @REQ-0.0.36-02-04
  Scenario: Feature-lite OBPI emit-receipt fails without human attestation fields
    # ADR-0.0.36 collapse: feature-lite was previously self-closeable; the runtime
    # gate now requires human_attestation + attestation_text + attestation_date
    # for every OBPI completion, regardless of parent kind or lane.
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And I run the gz command "specify demo --parent ADR-0.1.0-f"
    When I emit-receipt for OBPI "OBPI-0.1.0-01-demo" with attestor "human:jeff" and evidence
      """
      {"value_narrative":"v","key_proof":"k"}
      """
    Then it exits with code 1
    And the output contains "human_attestation"

  @REQ-0.0.36-02-03
  @REQ-0.0.36-02-05
  Scenario: Feature-lite OBPI emit-receipt succeeds with full attestation evidence
    # Confirms the universal gate accepts a complete attestation payload for the
    # feature-lite cell that previously self-closed; also confirms _is_foundation_adr
    # taxonomy classification and _enforce_human_attestation_authenticity routing
    # remain intact (foundation/feature distinction still flows through evidence shape).
    Given the workspace is initialized
    And ADR-0.1.0 exists
    And I run the gz command "specify demo --parent ADR-0.1.0-f"
    When I emit-receipt for OBPI "OBPI-0.1.0-01-demo" with attestor "human:jeff" and evidence
      """
      {"value_narrative":"v","key_proof":"k","human_attestation":true,"attestation_text":"bdd test attestation","attestation_date":"2026-01-01"}
      """
    Then it exits with code 0
