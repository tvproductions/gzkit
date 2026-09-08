Feature: gz content compose — authoring-time compression candidate validation

  The compose subcommand accepts a candidate rendition text, validates
  invariant-tier verbatim preservation (0-Kelvin floor), computes per-tier
  byte evidence, writes the candidate artifact, and emits a ledger event.
  The tool is deterministic and NEVER writes a rendered surface.

  Background:
    Given I have initialized a gzkit project
    And the vendor manifest declares setpoint "lite" for (AgentContract, root)
    And the corpus for "AGENTS.md" contains an invariant entry "YOU OWN THE WORK COMPLETELY."
    And the corpus for "AGENTS.md" contains a compressible entry "Prefer stdlib JSONL."

  @REQ-0.0.37-21-01
  Scenario: Compose produces candidate rendition with byte evidence
    Given a candidate file containing the invariant entry and compressed compressible content
    When I run "gz content compose AGENTS.md --consumer root --candidate <file>"
    Then the command exits 0
    And the candidate file exists at ".gzkit/renditions/AGENTS.md/root.candidate.md"
    And the output includes "Byte evidence"
    And the output includes "setpoint=lite"
    And the ledger contains a "composition_candidate_emitted" event for surface "AGENTS.md"

  @REQ-0.0.37-21-02
  Scenario: Compose is deterministic
    Given a candidate file containing the invariant entry and some content
    When I run "gz content compose AGENTS.md --consumer root --candidate <file>" twice
    Then both runs exit 0
    And the byte evidence output is identical between runs

  @REQ-0.0.37-21-03
  Scenario: Invariant-tier entries appear verbatim in candidate
    Given a candidate file containing the invariant entry text verbatim
    When I run "gz content compose AGENTS.md --consumer root --candidate <file>"
    Then the command exits 0
    And the candidate at ".gzkit/renditions/AGENTS.md/root.candidate.md" contains the invariant text verbatim

  @REQ-0.0.37-21-04
  Scenario: Compose fails closed on absent corpus
    Given no corpus store exists for "MISSING.md"
    And a candidate file with some text
    When I run "gz content compose MISSING.md --consumer root --candidate <file>"
    Then the command exits non-zero
    And no candidate file is written at ".gzkit/renditions/MISSING.md/codex.candidate.md"

  @REQ-0.0.37-21-04
  Scenario: Compose fails closed on undeclared setpoint
    Given a candidate file containing the invariant entry text
    When I run "gz content compose AGENTS.md --consumer unknown-vendor --candidate <file>"
    Then the command exits non-zero
    And no candidate file is written for "unknown-vendor"

  @REQ-0.0.37-21-05
  Scenario: Compose does not modify rendered surfaces
    Given "AGENTS.md" exists with some content
    And "CLAUDE.md" exists with some content
    And a valid candidate file containing the invariant entry
    When I run "gz content compose AGENTS.md --consumer root --candidate <file>"
    Then the command exits 0
    And "AGENTS.md" is byte-unchanged
    And "CLAUDE.md" is byte-unchanged

  @REQ-0.35.0-05-01
  Scenario: Generated path derives an owned section's body from the corpus
    Given the prior committed rendition for "AGENTS.md" toward "root" contains a corpus-owned section and an unowned section
    And a valid section-ownership declaration exists for "AGENTS.md"
    When I run "gz content compose AGENTS.md --consumer root" with no candidate and empty stdin
    Then the command exits 0
    And the candidate at ".gzkit/renditions/AGENTS.md/root.candidate.md" contains the invariant text verbatim
    And the candidate at ".gzkit/renditions/AGENTS.md/root.candidate.md" does not contain "stale prior wording that must never survive generation"

  @REQ-0.35.0-05-02
  Scenario: Generated path carries an unowned section forward byte-verbatim
    Given the prior committed rendition for "AGENTS.md" toward "root" contains a corpus-owned section and an unowned section
    And a valid section-ownership declaration exists for "AGENTS.md"
    When I run "gz content compose AGENTS.md --consumer root" with no candidate and empty stdin
    Then the command exits 0
    And the candidate at ".gzkit/renditions/AGENTS.md/root.candidate.md" contains "carried forward text verbatim" verbatim

  @REQ-0.35.0-05-04
  Scenario: A generator run writes a lineage artifact covering every section
    Given the prior committed rendition for "AGENTS.md" toward "root" contains a corpus-owned section and an unowned section
    And a valid section-ownership declaration exists for "AGENTS.md"
    When I run "gz content compose AGENTS.md --consumer root" with no candidate and empty stdin
    Then the command exits 0
    And the lineage file exists at ".gzkit/renditions/AGENTS.md/root.candidate.lineage.json"
    And the lineage file declares owned, entry_ids, and byte_span for every section

  @REQ-0.35.0-05-05
  Scenario: Generated path refuses an off-route consumer
    When I run "gz content compose AGENTS.md --consumer codex" with no candidate and empty stdin
    Then the command exits non-zero
    And no candidate file is written for "codex"
    And no lineage file is written for "codex"

  @REQ-0.35.0-05-08
  Scenario: Two generator runs produce byte-identical candidate and lineage
    Given the prior committed rendition for "AGENTS.md" toward "root" contains a corpus-owned section and an unowned section
    And a valid section-ownership declaration exists for "AGENTS.md"
    When I run "gz content compose AGENTS.md --consumer root" with no candidate and empty stdin twice
    Then both runs exit 0
    And the candidate file is byte-identical between runs
    And the lineage file is byte-identical between runs
