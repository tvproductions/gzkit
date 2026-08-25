Feature: Corpus retirement attestation (gz content retire)
  As a gzkit operator
  I want retiring floor-tier canon to require a named attestor
  So that no invariant-tier entry is un-bound without a human name on the decision

  # REQ-0.35.0-02-01: invariant tier + empty attestor -> refuse, write nothing
  @REQ-0.35.0-02-01
  Scenario: retiring an invariant-tier entry without an attestor fails closed
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "floor doctrine" at tier "invariant"
    When I retire the seeded entry with args "--reason superseded"
    Then the command exits with code 1
    And the corpus for "AGENTS.md" is byte-unchanged
    And no ledger event "corpus_entry_retired" was emitted

  # REQ-0.35.0-02-02: whitespace is not attestation
  @REQ-0.35.0-02-02
  Scenario: a whitespace-only attestor is refused
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "floor doctrine" at tier "invariant"
    When I retire the seeded entry with a whitespace-only attestor
    Then the command exits with code 1
    And the corpus for "AGENTS.md" is byte-unchanged

  # REQ-0.35.0-02-03: routine compressible retirement needs no attestor
  @REQ-0.35.0-02-03
  Scenario: retiring a compressible-tier entry without an attestor succeeds
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "routine note" at tier "compressible"
    When I retire the seeded entry with args "--reason superseded"
    Then the command exits with code 0

  # REQ-0.35.0-02-04: append-only — the raw log grows, the target survives verbatim
  @REQ-0.35.0-02-04
  Scenario: retirement appends a tombstone and never removes the retired row
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "floor doctrine" at tier "invariant"
    When I retire the seeded entry with args "--reason superseded --attestor g0"
    Then the command exits with code 0
    And the corpus for "AGENTS.md" grew by exactly 1 row
    And the retired entry is still present verbatim in the raw corpus log
    And the retired entry is absent from the effective corpus

  # REQ-0.35.0-02-05: fail closed on an unknown id, with three-part recovery prose
  @REQ-0.35.0-02-05
  Scenario: an unknown entry id fails closed and names a runnable next step
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "routine note" at tier "compressible"
    When I run the gz command "content retire AGENTS.md --entry no-such-id --reason probe"
    Then the command exits with code 1
    And the corpus for "AGENTS.md" is byte-unchanged
    And every gz command named in the recovery prose actually runs

  # REQ-0.35.0-02-06: text-keyed retirement is unreachable from the CLI
  @REQ-0.35.0-02-06
  Scenario: the retire parser exposes no text-valued selector
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    When I run the gz command "content retire --help"
    Then the command exits with code 0
    And the output contains "--entry"
    And the output contains "--attestor"
    And the output does not contain "--text"

  # REQ-0.35.0-02-07: both witnesses, carrying the RETIRED entry's tier
  @REQ-0.35.0-02-07
  Scenario: a successful retirement emits both ledger witnesses
    Given a control surface "AGENTS.md" with a "Behavior Rules" section
    And a corpus entry "floor doctrine" at tier "invariant"
    When I retire the seeded entry with args "--reason superseded --attestor g0"
    Then the command exits with code 0
    And ledger event "corpus_entry_appended" has field "surface" equal to "AGENTS.md"
    And ledger event "corpus_entry_retired" has field "surface" equal to "AGENTS.md"
    And ledger event "corpus_entry_retired" has field "attestor" equal to "g0"
    And ledger event "corpus_entry_retired" has field "tier" equal to "invariant"
