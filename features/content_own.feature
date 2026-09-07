Feature: Governed section-ownership lowering path (gz content own)
  As a gzkit operator
  I want an unowned section whose content the corpus carries to become corpus-owned
  So that the decrease-only unowned-byte ratchet falls to what the surface measures, under attestation

  # GHI #974: the same corpus-attestation shape as `gz content unown`
  Scenario: an empty attestor is refused and nothing is written
    Given a control surface "Doc.md" with an unowned section the corpus fully carries
    When I own section "alpha-section" with args "--reason a-real-reason"
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "unowned_ratchet_updated" was emitted

  Scenario: a section the corpus does not fully carry is refused
    Given a control surface "Doc.md" with an unowned section the corpus only partly carries
    When I own section "alpha-section" with args "--attestor g0 --reason corpus-carries-it"
    Then the command exits with code 1
    And the ownership declaration for "Doc.md" is byte-unchanged
    And no ledger event "unowned_ratchet_updated" was emitted

  Scenario: a fully carried section becomes corpus-owned and the floor falls to the measured remainder
    Given a control surface "Doc.md" with an unowned section the corpus fully carries
    When I own section "alpha-section" with args "--attestor g0 --reason corpus-carries-it"
    Then the command exits with code 0
    And section "alpha-section" of "Doc.md" is declared "corpus-owned"
    And the unowned-byte floor for "Doc.md" equals the measured remaining unowned span
    And ledger event "unowned_ratchet_updated" has field "section" equal to "alpha-section"
    And ledger event "unowned_ratchet_updated" has field "attestor" equal to "g0"
    And ledger event "unowned_ratchet_updated" has field "reason" equal to "corpus-carries-it"
    And the ownership declaration for "Doc.md" reloads through the real loader
