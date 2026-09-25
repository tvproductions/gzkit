Feature: Retention gate for gz content commit (OBPI-0.35.0-14, ADR-0.35.0 Decision 10)

  When a candidate drops a block the prior committed rendition carried, `gz content
  commit` refuses to promote it unless a `--retention-map` accounts for every
  condition of every removed block. The 2026-09-17 compression of root AGENTS.md
  dropped 23 binding conditions and every check passed (GHI #1090, #1091); this
  gate is the mechanical floor: byte comparison proves what it can, an
  independent reviewer extracts conditions, and the operator rules every drop.

  @REQ-0.35.0-14-01
  Scenario: a lossy candidate committed without --retention-map exits 3 and writes nothing
    Given a prior committed rendition with provenance for "AGENTS.md" consumer "codex" with text "Block one stays.\n\nBlock two must not vanish silently."
    And a staged candidate rendition for "AGENTS.md" consumer "codex" with content "Block one stays."
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text done"
    Then the command exits with code 3
    And the output contains "Block two must not vanish silently."
    And the committed rendition for "AGENTS.md" consumer "codex" equals the prior text
    And the provenance sidecar for "AGENTS.md" consumer "codex" is unchanged since seeding
    And the file ".gzkit/renditions/AGENTS.md/codex.retention.json" does not exist
    And no "rendition_committed" ledger event was written

  @REQ-0.35.0-14-04
  Scenario: a DROPPED condition's id must appear in this invocation's attestation text
    Given a prior committed rendition with provenance for "AGENTS.md" consumer "codex" with text "Deprecated note: old policy text."
    And a staged candidate rendition for "AGENTS.md" consumer "codex" with content "replacement body."
    And a retention map "map.json" for "AGENTS.md" consumer "codex" dropping condition "C1" for removed block "Deprecated note: old policy text." with reason "superseded by replacement body"
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text 'attest without the drop id' --retention-map map.json"
    Then the command exits with code 3
    And the output contains "dropped-id-not-attested"
    And the file ".gzkit/renditions/AGENTS.md/codex.retention.json" does not exist
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text 'attest completed; C1 drop accepted' --retention-map map.json"
    Then the command exits with code 0
    And the retention sidecar for "AGENTS.md" consumer "codex" holds the map "map.json"

  @REQ-0.35.0-14-05
  Scenario: a byte-identical re-render commits without a map
    Given a prior committed rendition with provenance for "AGENTS.md" consumer "codex" with text "Block text stays exactly as it was."
    And a staged candidate rendition for "AGENTS.md" consumer "codex" with content "Block text stays exactly as it was."
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text done"
    Then the command exits with code 0

  @REQ-0.35.0-14-06
  Scenario: the GHI #1090 replay -- an all-KEPT map is refused, the complete DROPPED-and-attested map lands
    Given the GHI #1090 replay is staged for "AGENTS.md" consumer "codex"
    And a retention map "map.json" for the GHI #1090 replay marking the accept-uncovered condition KEPT
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text 'all kept' --retention-map map.json"
    Then the command exits with code 3
    And the output contains "kept-span-not-in-candidate"
    Given the same retention map "map.json" with the accept-uncovered condition DROPPED and its id attested
    When I run the gz command "content commit AGENTS.md --consumer codex --attestor g0 --attestation-text 'C1 drop accepted for the accept-uncovered clause' --retention-map map.json"
    Then the command exits with code 0
    And the retention sidecar for "AGENTS.md" consumer "codex" holds the map "map.json"
