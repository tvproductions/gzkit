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
