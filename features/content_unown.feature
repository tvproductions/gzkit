Feature: Attested section-ownership raise-path (gz content unown)
  As a gzkit operator
  I want un-owning a corpus-owned section to require a named attestor and reason
  So that the decrease-only unowned-byte ratchet only ever rises under attestation

  # REQ-0.35.0-04-04: empty or whitespace attestor/reason -> refuse, write nothing
  @REQ-0.35.0-04-04
  Scenario: an empty attestor is refused
    Given a control surface "Doc.md" with an ownership declaration
    When I unown section "alpha-section" with args "--reason a-real-reason"
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "section_ownership_unowned" was emitted

  @REQ-0.35.0-04-04
  Scenario: a whitespace-only attestor is refused
    Given a control surface "Doc.md" with an ownership declaration
    When I unown section "alpha-section" with a whitespace-only attestor
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "section_ownership_unowned" was emitted

  @REQ-0.35.0-04-04
  Scenario: an empty reason is refused
    Given a control surface "Doc.md" with an ownership declaration
    When I unown section "alpha-section" with args "--attestor g0"
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "section_ownership_unowned" was emitted

  @REQ-0.35.0-04-04
  Scenario: a whitespace-only reason is refused
    Given a control surface "Doc.md" with an ownership declaration
    When I unown section "alpha-section" with a whitespace-only reason
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "section_ownership_unowned" was emitted

  # REQ-0.35.0-04-05: attested raise -> section flips, floor rises by its measured span
  @REQ-0.35.0-04-05
  Scenario: a valid attestor and reason un-owns a corpus-owned section
    Given a control surface "Doc.md" with an ownership declaration
    When I unown section "alpha-section" with args "--attestor g0 --reason moving-to-prose-doc"
    Then the command exits with code 0
    And section "alpha-section" of "Doc.md" is declared "unowned"
    And the unowned-byte floor for "Doc.md" rose by exactly that section's measured span
    And ledger event "section_ownership_unowned" has field "section" equal to "alpha-section"
    And ledger event "section_ownership_unowned" has field "attestor" equal to "g0"
    And ledger event "section_ownership_unowned" has field "reason" equal to "moving-to-prose-doc"
    And the ledger event's prior and new floor fields match the seed floor and its measured rise
