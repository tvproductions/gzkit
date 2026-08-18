Feature: Committed-rendition store, deterministic playback, and freshness gate

  The committed-rendition store holds a durable `.gzkit/renditions/<surface>/<consumer>.md`
  artifact. `sync_agents_md` plays it back deterministically (no LLM, no network).
  The freshness gate (`gz validate --rendition-freshness`) fails closed when the
  corpus has mutated after the committed rendition. `gz validate --invariant-coherence`
  diffs rendition playback against the committed rendered surface.

  Background:
    Given I have initialized a gzkit project

  @REQ-0.0.37-22-01
  Scenario: Rendition store loads byte-identically
    Given a committed rendition for "AGENTS.md" consumer "root" with content "# Test rendition\n"
    When I load the rendition for "AGENTS.md" consumer "root"
    Then the loaded bytes equal "# Test rendition\n"
    And loading again returns the same bytes

  @REQ-0.0.37-22-01
  Scenario: Rendition store fails closed when artifact is absent
    Given no committed rendition exists for "AGENTS.md" consumer "root"
    When I attempt to load the rendition for "AGENTS.md" consumer "root"
    Then a FileNotFoundError is raised

  @REQ-0.0.37-22-02
  Scenario: sync_agents_md renders AGENTS.md from committed rendition byte-identically
    Given a committed rendition for "AGENTS.md" consumer "root" with content "# Deterministic\n"
    When I run sync_agents_md
    Then AGENTS.md contains exactly "# Deterministic\n"
    And running sync_agents_md again produces the same AGENTS.md bytes

  @REQ-0.0.37-22-02
  Scenario: sync_agents_md does not call the model pipeline when a rendition exists
    Given a committed rendition for "AGENTS.md" consumer "root" with content "# Rendition\n"
    When I run sync_agents_md
    Then the model render pipeline was not invoked

  @REQ-0.0.37-22-03
  Scenario: Freshness gate is clean when the committed fingerprint matches the corpus
    Given a corpus for "AGENTS.md" with one entry
    And a committed rendition with provenance for "AGENTS.md" consumer "root"
    When I run the gz command "validate --rendition-freshness"
    Then the command exits with code 0
    And the output does not contain "WARNING [rendition-freshness"

  @REQ-0.0.37-22-03
  Scenario: Freshness gate fails closed on corpus content drift outside the MX hangar
    Given a corpus for "AGENTS.md" with one entry
    And a committed rendition with provenance for "AGENTS.md" consumer "root"
    And the corpus for "AGENTS.md" gains a new entry
    When I run the gz command "validate --rendition-freshness"
    Then the command exits with code 3

  @REQ-0.0.37-22-04
  Scenario: --invariant-coherence exits 3 when rendition playback differs from committed AGENTS.md
    Given a committed rendition for "AGENTS.md" consumer "root" with content "# Rendition\n"
    And AGENTS.md contains "# Different content\n"
    When I run the gz command "validate --invariant-coherence"
    Then the command exits with code 3

  @REQ-0.0.37-22-04
  Scenario: --invariant-coherence exits 0 when rendition playback matches AGENTS.md
    Given a committed rendition for "AGENTS.md" consumer "root" with content "# Match\n"
    And AGENTS.md contains "# Match\n"
    When I run the gz command "validate --invariant-coherence"
    Then the command exits with code 0

  @REQ-0.0.37-22-07
  Scenario: gz content commit promotes a candidate and freezes the corpus fingerprint
    Given a corpus for "AGENTS.md" with one entry
    And a staged candidate for "AGENTS.md" consumer "root" with content "# Candidate\n"
    When I run the gz command "content commit AGENTS.md --consumer root --attestor Jeffry --attestation-text done"
    Then the command exits with code 0
    And a committed rendition exists for "AGENTS.md" consumer "root"
    And a provenance sidecar exists for "AGENTS.md" consumer "root"
    And the ledger contains a "rendition_committed" event
