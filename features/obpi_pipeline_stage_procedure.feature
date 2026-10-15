Feature: Pipeline stage procedures are served at stage entry
  The runtime delivers each stage's procedure when the stage is entered, as a
  pointer to a pinned file beside the skill, and refuses a stage whose file is
  not the bytes it expects (OBPI-0.35.0-17; the skill body cut over to the
  invocation text in OBPI-0.35.0-20).

  @REQ-0.35.0-17-04
  Scenario: A full launch serves Stage 1 and Stage 2 and no other stage
    Given a project seeded so its OBPI can be launched
    When the pipeline is launched in full
    Then the launch output serves the procedures for stages "1,2"
    And the launch output serves no procedure for stages "3,4,5"
    And every served procedure's digest is the digest of its file

  @REQ-0.35.0-17-04
  Scenario Outline: An entry through --from serves each stage it visits, byte for byte
    Given a project seeded so its OBPI can be launched
    When the pipeline is launched with "<flag>" and its stage work stood in for
    Then the launch output serves the procedures for stages "<served>"
    And the launch output serves no procedure for stages "<not served>"
    And every served procedure's digest is the digest of its file

    Examples: each --from value the parser registers
      | flag            | served | not served |
      | --from=verify   | 1,3,4  | 2,5        |
      | --from=ceremony | 1,4    | 2,3,5      |

  @REQ-0.35.0-17-05
  Scenario: A missing stage file refuses the launch before any marker is written
    Given a project seeded so its OBPI can be launched
    And the served procedure for stage 2 is missing
    When the pipeline is launched in full and exits 1
    Then the output names the missing file, the rule it breaks and the recovery command
    And no pipeline marker was written

  @REQ-0.35.0-17-05
  Scenario: An altered stage file refuses the launch and names both digests
    Given a project seeded so its OBPI can be launched
    And the served procedure for stage 4 has been altered
    When the pipeline is launched in full and exits 1
    Then the output names the altered file with the digest found and the digest expected
    And no pipeline marker was written
