Feature: Corpus capture (gz content remember)
  As a gzkit operator
  I want to capture an addressed entry into a surface's append-only corpus
  So that the source of truth grows without ever hand-editing a rendered surface

  # REQ-0.0.37-19-01: append one addressed entry + exit 0
  @REQ-0.0.37-19-01
  Scenario: remember appends an addressed entry to the per-surface corpus store
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    When I run the gz command "content remember AGENTS.md --section behavior-rules --text capture-note"
    Then the command exits with code 0
    And the file ".gzkit/corpus/AGENTS.md.jsonl" exists

  # REQ-0.0.37-19-02: the rendered surface is never modified
  @REQ-0.0.37-19-02
  Scenario: remember does not modify the rendered surface
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    When I run the gz command "content remember AGENTS.md --section behavior-rules --text capture-note"
    Then the command exits with code 0
    And the file "AGENTS.md" contains "## Behavior Rules"
    And the file ".gzkit/corpus/AGENTS.md.jsonl" exists

  # REQ-0.0.37-19-03: a corpus_entry_appended ledger event is emitted
  @REQ-0.0.37-19-03
  Scenario: remember emits a corpus_entry_appended ledger event
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    When I run the gz command "content remember AGENTS.md --section behavior-rules --text x --tier invariant"
    Then the command exits with code 0
    And ledger event "corpus_entry_appended" has field "surface" equal to "AGENTS.md"
    And ledger event "corpus_entry_appended" has field "tier" equal to "invariant"

  # REQ-0.0.37-19-04: fail closed on an unknown surface, no entry written
  @REQ-0.0.37-19-04
  Scenario: remember fails closed on an unknown surface
    When I run the gz command "content remember NOPE.md --section behavior-rules --text x"
    Then the command exits non-zero
    And the file ".gzkit/corpus/NOPE.md.jsonl" does not exist

  # REQ-0.35.0-08-04: a stale committed rendition yields the post-append advisory, exit 0
  @REQ-0.35.0-08-04
  Scenario: remember advises landing when the append leaves a committed rendition stale
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a committed "root" rendition of "AGENTS.md" on a stale corpus fingerprint
    When I run the gz command "content remember AGENTS.md --section behavior-rules --text capture-note"
    Then the command exits with code 0
    And the file ".gzkit/corpus/AGENTS.md.jsonl" exists
    And the output contains "ADR-0.0.37 § Decision Re-Alignment"
    And the output contains "uv run gz content land AGENTS.md"
    And the output contains "--attestation-text"

  # REQ-0.35.0-08-05: with no committed rendition nothing drifted, so no advisory
  @REQ-0.35.0-08-05
  Scenario: remember stays silent when there is no committed rendition to drift
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    When I run the gz command "content remember AGENTS.md --section behavior-rules --text capture-note"
    Then the command exits with code 0
    And the file ".gzkit/corpus/AGENTS.md.jsonl" exists
    And the output does not contain "committed rendition(s)"

  # REQ-0.35.0-08-04: the command the advisory prints is the one that recovers
  @REQ-0.35.0-08-04
  Scenario: the attested landing command the advisory prints recovers the drift it announced
    Given a three-consumer landing project with an unchanged corpus
    And the landing project's surface "LandSurface.md" is a parseable contract
    When I run the gz command "content remember LandSurface.md --section owned-section --text operator-rule-text"
    Then the command exits with code 0
    And the output contains "(alpha, beta, gamma)"
    And the output contains "ADR-0.0.37 § Decision Re-Alignment"
    And the output contains "uv run gz content land LandSurface.md"
    And I keep the advisory the command printed
    When I run the gz command "content land LandSurface.md"
    Then the command exits with code 1
    And the output contains "attestor"
    When I run the land command the advisory printed with attestor "g0" and attestation text "operator rule attested"
    Then the command exits with code 0
    And every consumer sidecar carries attestation text "operator rule attested" and one shared landing id
