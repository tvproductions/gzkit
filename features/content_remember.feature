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
