Feature: Persona sync to vendor mirrors
  Persona files in .gzkit/personas/ are mirrored to vendor surfaces
  by gz agent sync control-surfaces (ADR-0.0.13 item 3).

  Scenario: Sync mirrors personas to Claude surface
    Given the workspace is initialized
    And a persona file "implementer" exists
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the file ".claude/personas/implementer.md" exists

  Scenario: Manifest includes personas control surface
    Given the workspace is initialized
    When I run the gz command "agent sync control-surfaces"
    Then the command exits with code 0
    And the file ".gzkit/manifest.json" contains "personas"

  # Cross-project portability scenarios (OBPI-0.0.13-06)

  Scenario: Init scaffolds default personas in clean workspace
    Given the workspace is initialized
    Then the file ".gzkit/personas/default-agent.md" exists
    And the file ".gzkit/personas/default-reviewer.md" exists

  Scenario: Scaffolded personas pass surface validation
    Given the workspace is initialized
    When I run the gz command "validate --surfaces"
    Then the command exits with code 0
