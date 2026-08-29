Feature: gz upgrade surface-only refresh

  gz upgrade refreshes .gzkit/<surface>/ from the installed wheel's package
  data. Narrower than gz init --update: no manifest mutation, no scaffolder
  hooks, no agent sync. Surface content only.

  @REQ-0.0.32-14-01
  Scenario: gz upgrade is a registered subcommand
    Given the workspace is initialized
    When I run the gz command "upgrade --help"
    Then the command exits with code 0
    And the output contains "upgrade"
    And the output contains "--surface"

  @REQ-0.0.32-14-01
  Scenario: upgrade subcommand flag --force is available
    Given the workspace is initialized
    When I run the gz command "upgrade --help"
    Then the command exits with code 0
    And the output contains "--force"
    And the output contains "--dry-run"

  @REQ-0.0.32-14-02
  Scenario: unknown surface name exits 1 with token named
    Given the workspace is initialized
    When I run the gz command "upgrade --surface badtoken"
    Then the command exits with code 1
    And the output contains "badtoken"

  @REQ-0.0.32-14-02
  Scenario: unknown token in comma list exits 1
    Given the workspace is initialized
    When I run the gz command "upgrade --surface skills,nosuchsurface"
    Then the command exits with code 1
    And the output contains "nosuchsurface"

  @REQ-0.0.32-14-03
  Scenario: EDITED conflict detection without --force exits 3
    Given the workspace is initialized
    And the project has an EDITED skill at ".gzkit/skills/gz-status/SKILL.md"
    When I run the gz command "upgrade --surface skills"
    Then the command exits with code 3

  @REQ-0.0.32-14-04
  Scenario: --force overwrites EDITED artifacts and exits 0
    Given the workspace is initialized
    And the project has an EDITED skill at ".gzkit/skills/gz-status/SKILL.md"
    When I run the gz command "upgrade --surface skills --force"
    Then the command exits with code 0

  @REQ-0.0.32-14-06
  Scenario: bootstrap retrofit when .gzkit/skills/ does not exist
    Given the workspace is initialized
    And the .gzkit/skills directory is removed
    When I run the gz command "upgrade --surface skills"
    Then ".gzkit/skills" exists after the command

  @REQ-0.0.32-14-05
  Scenario: --dry-run on a fresh workspace reports and exits 0
    Given the workspace is initialized
    When I run the gz command "upgrade --dry-run"
    Then the command exits with code 0

  @REQ-0.0.32-14-07
  Scenario: idempotent second run exits 0
    Given the workspace is initialized
    When I run the gz command "upgrade"
    Then the command exits with code 0
    When I run the gz command "upgrade"
    Then the command exits with code 0

  @REQ-0.0.32-14-08
  Scenario: manifest.json not mutated by gz upgrade
    Given the workspace is initialized
    And I record the manifest checksum
    When I run the gz command "upgrade"
    Then the manifest checksum is unchanged

  @REQ-0.0.32-14-09
  Scenario: manpage exists and docs build passes
    Given the workspace is initialized
    When I run the gz command "validate --documents"
    Then the command exits with code 0
