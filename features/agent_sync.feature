Feature: gz agent sync control-surfaces dual-direction propagation
  gz agent sync control-surfaces propagates .gzkit/<surface>/ to both
  src/gzkit/<surface>/ (wheel-shipping pkg copy) and .[vendor]/<surface>/
  (vendor mirrors) in a single invocation (OBPI-0.0.32-08).

  @REQ-0.0.32-08-01
  Scenario: Sync propagates canonical skills to vendor mirrors
    Given the workspace is initialized with agent surfaces
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the file ".claude/skills/gz-prd/SKILL.md" exists

  @REQ-0.0.32-08-08
  Scenario: Post-sync validate --surfaces reports clean
    Given the workspace is initialized with agent surfaces
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    When I run the gz command "validate --surfaces"
    Then the command exits with code 0

  @REQ-0.0.32-08-04
  Scenario: Re-running sync on freshly-synced state is a no-op
    Given the workspace is initialized with agent surfaces
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the output contains "Sync complete"

  @REQ-0.44.0-01-01
  Scenario: Initialization creates a usable managed Codex baseline
    Given the workspace is initialized with agent surfaces
    Then the file ".codex/config.toml" exists
    And the file ".codex/config.toml" contains "# gzkit-managed-codex-config: v1"
    And the managed Codex baseline is parseable and complete

  @REQ-0.44.0-01-02
  Scenario: Initialization preserves a pre-existing operator Codex config
    Given an unmarked operator Codex config exists
    When I run the gz command "init --no-skeleton"
    Then the command exits with code 0
    And the Codex config equals the original operator bytes

  @REQ-0.44.0-01-02
  Scenario: Repair preserves operator settings added to the generated baseline
    Given the workspace is initialized with agent surfaces
    And the managed Codex config has operator settings
    When I run the gz command "init --no-skeleton"
    Then the command exits with code 0
    And the Codex config equals the original operator bytes

  @REQ-0.44.0-01-03
  Scenario: Sync writes only the configured Codex config path
    Given the workspace is initialized with agent surfaces
    And the Codex config path is configured as "config/codex.toml"
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the file "config/codex.toml" exists
    And the file ".codex/config.toml" does not exist
    And the manifest Codex config path equals "config/codex.toml"

  @REQ-0.44.0-01-04
  Scenario: Surface validation rejects managed Codex config drift
    Given the workspace is initialized with agent surfaces
    And the managed Codex config has drifted
    When I run the gz command "validate --surfaces"
    Then the command exits non-zero
    And the output contains ".codex/config.toml"

  @REQ-0.44.0-01-04
  Scenario: Surface validation reports a missing managed Codex config
    Given the workspace is initialized with agent surfaces
    And the managed Codex config is missing
    When I run the gz command "validate --surfaces"
    Then the command exits non-zero
    And the output contains "Configured Codex config is missing"
    And the output contains "Generated surface missing"

  @REQ-0.44.0-01-04
  Scenario: Surface validation accepts an operator-owned Codex config
    Given an unmarked operator Codex config exists
    And the workspace is initialized with agent surfaces
    When I run the gz command "validate --surfaces"
    Then the command exits with code 0
    And the Codex config equals the original operator bytes

  @REQ-0.44.0-01-04
  Scenario: A customized default survives a custom-path move and fails validation
    Given the workspace is initialized with agent surfaces
    And the managed Codex config has operator settings
    And the Codex config path is configured as "config/codex.toml"
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the Codex config equals the original operator bytes
    When I run the gz command "validate --surfaces"
    Then the command exits non-zero
    And the output contains "Obsolete default Codex config"
