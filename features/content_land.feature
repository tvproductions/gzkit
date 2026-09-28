Feature: Multi-consumer landing under one corpus attestation (gz content land)
  As a gzkit operator
  I want one governed command that lands a corpus change on every routed consumer
  So that one attestation on the corpus delta covers the whole set, an interrupted
  landing is inspectable and resumable, and nothing is ever half-attested

  # OBPI-0.35.0-07, ADR-0.35.0 Decision 6. Every scenario runs in an isolated
  # synthetic project: surface "LandSurface.md" routed to consumers alpha, beta
  # and gamma, whose committed sidecars predate one appended corpus entry.

  @REQ-0.35.0-07-01
  Scenario: land without a surface is a usage error
    When I run the gz command "content land"
    Then the command exits with code 2
    And the output contains "the following arguments are required: surface"

  @REQ-0.35.0-07-02
  Scenario: a staging failure at the second consumer modifies no committed artifact
    Given a three-consumer landing project with a new corpus delta
    When I land the delta with staging failing at consumer "beta"
    Then the command exits with code 2
    And no committed landing artifact changed
    And no landing journal exists
    And no "rendition_landed" ledger event was written

  @REQ-0.35.0-07-02
  Scenario: a replace failure after the first published file stays incomplete and resumes from verified hashes
    Given a three-consumer landing project with a new corpus delta
    When I land the delta with replacement failing after the first published file
    Then the command exits with code 2
    And the output contains "is incomplete"
    And the landing journal is in phase "publishing"
    And no "rendition_landed" ledger event was written
    When I resume the landing while recording every replaced file
    Then the command exits with code 0
    And the resume replaced no file that was already at its new hash
    And every landing target is at its recorded new hash
    And exactly one "rendition_landed" ledger event carries the landing id

  @REQ-0.35.0-07-03
  Scenario: a new delta with an empty or whitespace attestation writes nothing
    Given a three-consumer landing project with a new corpus delta
    When I run the gz command "content land LandSurface.md --attestor '' --attestation-text 'corpus delta attested'"
    Then the command exits with code 1
    And the project tree is byte-unchanged
    When I run the gz command "content land LandSurface.md --attestor g0 --attestation-text '   '"
    Then the command exits with code 1
    And the project tree is byte-unchanged
    And the output contains "Next:"

  @REQ-0.35.0-07-03
  Scenario: a forged sidecar is not reusable evidence of an unchanged corpus
    Given a three-consumer landing project with an unchanged corpus
    And the provenance sidecar of consumer "beta" claims bytes that are not on disk
    When I run the gz command "content land LandSurface.md"
    Then the command exits with code 1
    And the project tree is byte-unchanged
    And the output contains "'beta': its rendition_fingerprint does not match"

  @REQ-0.35.0-07-03
  Scenario: an unchanged corpus re-renders on its verified evidence without a new attestation
    Given a three-consumer landing project with an unchanged corpus
    When I run the gz command "content land LandSurface.md"
    Then the command exits with code 0
    And every consumer sidecar carries attestation text "baseline attested" and one shared landing id

  @REQ-0.35.0-07-04
  Scenario: every sidecar shares one attestation and one landing id, with exactly one event
    Given a three-consumer landing project with a new corpus delta
    When I run the gz command "content land LandSurface.md --attestor g0 --attestation-text 'corpus delta attested'"
    Then the command exits with code 0
    And every consumer sidecar carries attestation text "corpus delta attested" and one shared landing id
    And exactly one "rendition_landed" ledger event carries the landing id

  @REQ-0.35.0-07-05
  Scenario: the journal exists mid-landing with the full consumer set and is absent once complete
    Given a three-consumer landing project with a new corpus delta
    When I land the delta and interrupt it after consumer "alpha"
    Then the command exits with code 2
    And the landing journal names consumers "alpha, beta, gamma" and the live corpus fingerprint
    When I run the gz command "content land LandSurface.md"
    Then the command exits with code 0
    And no landing journal exists

  @REQ-0.35.0-07-06
  Scenario: status classifies consumers by fingerprints and never by mtimes
    Given a three-consumer landing project with a new corpus delta
    When I land the delta and interrupt it after consumer "alpha"
    And I set different mtimes on the renditions of consumers "beta" and "gamma"
    And I query the status of the recorded landing
    Then the command exits with code 0
    And the status classifies "alpha" as "new"
    And the status classifies "beta" as "old"
    And the status classifies "gamma" as "old"
    When I overwrite the rendition of consumer "alpha" beside its good sidecar
    And I query the status of the recorded landing
    Then the status classifies "alpha" as "indeterminate"
    And the project tree is byte-unchanged since the last status query

  @REQ-0.35.0-07-07
  Scenario: resume leaves the already-landed consumer byte-unchanged
    Given a three-consumer landing project with a new corpus delta
    When I land the delta and interrupt it after consumer "alpha"
    And I record the bytes of consumer "alpha"
    And I run the gz command "content land LandSurface.md"
    Then the command exits with code 0
    And the bytes of consumer "alpha" are unchanged
    And every landing target is at its recorded new hash

  @REQ-0.35.0-07-08
  Scenario: a landing killed mid-staging resumes without any attestation prompt
    Given a three-consumer landing project with a new corpus delta
    When I land the delta and the process is killed after one staged file
    Then the landing journal is in phase "prepared"
    When I resume the landing with any prompt failing the scenario
    Then the command exits with code 0
    And every consumer sidecar carries attestation text "corpus delta attested" and one shared landing id
    And exactly one "rendition_landed" ledger event carries the landing id

  @REQ-0.35.0-07-08
  Scenario: an explicit attestation on resume is ignored and the recorded one is kept
    Given a three-consumer landing project with a new corpus delta
    When I land the delta and interrupt it after consumer "alpha"
    And I run the gz command "content land LandSurface.md --attestor someone --attestation-text 'a different text'"
    Then the command exits with code 0
    And the output contains "were ignored"
    And every consumer sidecar carries attestation text "corpus delta attested" and one shared landing id
    And exactly one "rendition_landed" ledger event carries the landing id

  @REQ-0.35.0-07-10
  Scenario: a removed block refuses the whole landing until a valid map per consumer lands with it
    Given a three-consumer landing project whose candidates remove a block
    And a retention map dropping condition "C1" for each consumer
    When I run the gz command "content land LandSurface.md --attestor g0 --attestation-text 'corpus delta attested'"
    Then the command exits with code 3
    And the output contains "missing-retention-map"
    And the project tree is byte-unchanged
    When I run the gz command "content land LandSurface.md --attestor g0 --attestation-text 'corpus delta attested' --retention-map alpha.map.json --retention-map beta.map.json --retention-map gamma.map.json"
    Then the command exits with code 3
    And the output contains "dropped-id-not-attested"
    And the project tree is byte-unchanged
    When I run the gz command "content land LandSurface.md --attestor g0 --attestation-text 'corpus delta attested; C1 drop accepted' --retention-map alpha.map.json --retention-map beta.map.json --retention-map gamma.map.json"
    Then the command exits with code 0
    And every consumer has a published retention sidecar
