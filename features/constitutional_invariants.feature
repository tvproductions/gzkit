Feature: Constitutional invariant composition renderer (ADR-0.0.37, OBPI-0.0.37-02)
  As an operator maintaining gzkit governance
  I want the composition renderer to produce byte-deterministic output
  And I want --check mode to detect drift between the registry and AGENTS.md

  Background:
    Given the workspace is initialized
    And the constitutional invariant registry has at least one entry

  @REQ-0.0.37-02-01
  Scenario: Renderer produces identical bytes across consecutive invocations
    When I run "gz governance render --target agents-md --stdout" twice
    Then the two outputs are byte-identical

  @REQ-0.0.37-02-02
  Scenario: --check exits 0 when AGENTS.md matches rendered output
    Given AGENTS.md contains the current rendered output
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 0

  @REQ-0.0.37-02-02
  Scenario: --check exits 3 when AGENTS.md differs from rendered output
    Given AGENTS.md contains stale content
    When I run "gz governance render --target agents-md --check"
    Then the command exits with code 3
    And the output contains "@@"

  @REQ-0.0.37-02-04
  Scenario: Unsupported target exits nonzero with error message
    When I run "gz governance render --target skill-readme"
    Then the command exits non-zero
    And the output contains "unsupported target"

  @REQ-0.0.37-02-03
  Scenario: Write mode writes rendered bytes to AGENTS.md and reports byte count
    When I run "gz governance render --target agents-md"
    Then the command exits with code 0
    And the output contains "bytes"
    And AGENTS.md exists in the workspace

  @REQ-0.0.37-02-05
  Scenario: governance render verb resolves via gz governance render --help
    When I run "gz governance render --help"
    Then the command exits with code 0
    And the output contains "render"

  # OBPI-0.0.37-03 — Composition drift validator (gz validate --invariant-coherence)

  @REQ-0.0.37-03-01
  Scenario: gz validate --invariant-coherence exits 0 on matching AGENTS.md
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md matches the rendered registry output
    When I run "gz validate --invariant-coherence"
    Then the command exits with code 0

  @REQ-0.0.37-03-02
  Scenario: gz validate --invariant-coherence exits 3 on drift
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md differs from the rendered registry output
    When I run "gz validate --invariant-coherence"
    Then the command exits with code 3
    And the output contains "Diff (first 50 lines)"
    And the output contains "@@"

  @REQ-0.0.37-03-03
  Scenario: gz validate --invariant-coherence is read-only (no composition_rendered)
    Given the constitutional invariant registry has at least one entry
    And a committed AGENTS.md rendition exists
    When I run "gz validate --invariant-coherence"
    Then no "composition_rendered" event is appended to the ledger

  # OBPI-0.0.37-04 — Brief structural schema

  @REQ-0.0.37-04-01
  Scenario: BriefStructure model is frozen and rejects empty field lists
    Given a valid BriefStructure field set
    When I construct a BriefStructure instance
    Then the model is frozen and mutation raises an error
    And constructing with an empty allowlist raises ValidationError
    And constructing with an empty reqs list raises ValidationError

  @REQ-0.0.37-04-02
  Scenario: JSON Schema mirror has additionalProperties false and validates compliant instances
    Given the obpi_brief_structure.json schema file
    When I validate a compliant brief instance against it
    Then validation succeeds
    And an instance missing the reqs field fails validation

  @REQ-0.0.37-04-03
  Scenario: parse_brief returns LegacyBriefShape with warning for a legacy brief
    Given a legacy OBPI brief file without structured frontmatter fields
    When I call parse_brief on it in permissive mode
    Then the result is a LegacyBriefShape instance
    And a DeprecationWarning is emitted

  @REQ-0.0.37-04-04
  Scenario: parse_brief strict mode raises ValueError for a brief missing structured fields
    Given a legacy OBPI brief file without structured frontmatter fields
    When I call parse_brief on it with strict=True
    Then a ValueError is raised

  @REQ-0.0.37-04-05
  Scenario: The OBPI-0.0.37-04 brief round-trips through parse_brief as BriefStructure
    Given the OBPI-0.0.37-04 brief file with structured frontmatter
    When I call parse_brief on it
    Then the result is a BriefStructure instance
    And no DeprecationWarning is emitted

  # OBPI-0.0.37-13 — Reverse-parse migration to the master model

  @REQ-0.0.37-13-01
  Scenario: Import AGENTS.md populates pillars for every ## section
    Given the AGENTS.md file in the project root
    When I parse the file as AgentContract
    Then the model has more than 5 pillars
    And a pillar with title "Behavior Rules" exists with non-empty bullets

  @REQ-0.0.37-13-02
  Scenario: Bullet classification is joined from the advisory scorecard
    Given the AGENTS.md file in the project root
    When I parse the file as AgentContract
    Then a bullet containing "Never prefix" and "uv run gz" has classification "Mechanical"

  @REQ-0.0.37-13-03
  Scenario: agents.local.md content is captured as model rows via the AGENTS.md splice
    Given the AGENTS.md file in the project root
    When I parse the file as AgentContract
    Then a pillar line containing "Operator PII" is present in the model

  @REQ-0.0.37-13-04
  Scenario: Model to JSON and back is lossless
    Given the AGENTS.md file in the project root
    When I parse the file as AgentContract
    Then the model round-trips losslessly through JSON serialization

  @REQ-0.0.37-13-05
  Scenario: Unmatched bullets default to Ambiguous classification
    Given a minimal markdown document with an unmatchable rule
    When I parse it as AgentContract via the content API
    Then the custom-section bullet classification is "Ambiguous"

  # OBPI-0.0.37-14 — Wire sync through the renderer; retire the monolith

  @REQ-0.0.37-14-01
  Scenario: sync_agents_md renders AGENTS.md via the content model, not the monolith
    Given the constitutional invariant registry has at least one entry
    When I sync AGENTS.md via the model pipeline
    Then the committed AGENTS.md matches the model render

  @REQ-0.0.37-14-02
  Scenario: The project purpose is sourced through the model pipeline
    Given the constitutional invariant registry has at least one entry
    When I sync AGENTS.md via the model pipeline
    Then the rendered AGENTS.md contains the project purpose value

  @REQ-0.0.37-14-03
  Scenario: A hand-edit to AGENTS.md fails the invariant-coherence gate
    Given the constitutional invariant registry has at least one entry
    And AGENTS.md has been synced via the model pipeline
    When I hand-edit AGENTS.md outside the render path
    Then "gz validate --invariant-coherence" reports a coherence error

  @REQ-0.0.37-14-04
  Scenario: The model render is semantically equivalent to the pre-migration contract
    Given the constitutional invariant registry has at least one entry
    When I sync AGENTS.md via the model pipeline
    Then the rendered AGENTS.md contains the section "Behavior Rules"
    And the rendered AGENTS.md contains the section "Gate Covenant"

  # OBPI-0.0.37-15 — Per-vendor template selection

  @REQ-0.0.37-15-01
  Scenario: temperature_for resolves per-vendor temperature from manifest
    Given a vendor manifest declaring AgentContract temperatures codex=lite, claude=heavy
    When I call temperature_for for AgentContract and claude
    Then the resolved temperature is "heavy"

  @REQ-0.0.37-15-02
  Scenario: temperature_for fails closed for an undeclared vendor
    Given a vendor manifest declaring AgentContract temperatures codex=lite, claude=heavy
    When I call temperature_for for AgentContract and an unknown vendor
    Then a temperature ValueError is raised

  @REQ-0.0.37-15-03
  Scenario: Codex lite render includes all bullets (density projection retired)
    Given an AgentContract with a Judgment bullet and a plain bullet
    When I render the contract for codex at lite temperature
    Then the Judgment bullet is present in the rendered output
    And the plain bullet is also present in the rendered output

  @REQ-0.0.37-15-04
  Scenario: Temperature no longer differentiates a vendor render (selection retired)
    Given an AgentContract with a Judgment bullet and a plain bullet
    When I render the contract for codex at lite and codex at heavy
    Then the two rendered outputs are identical

  # OBPI-0.0.37-18 — Append-only corpus model

  @REQ-0.0.37-18-01
  Scenario: A corpus entry carries exactly its declared fields
    Given a corpus entry with all ten addressed fields populated
    Then the corpus entry model carries exactly its declared fields
    And constructing a corpus entry with an unknown field fails closed

  @REQ-0.0.37-18-02
  Scenario: The corpus is append-only and round-trips through JSONL
    Given an empty corpus
    When two corpus entries are appended
    Then the corpus holds two entries and the original empty corpus is unchanged
    And the corpus round-trips losslessly through JSONL

  @REQ-0.0.37-18-03
  Scenario: A corpus entry section must resolve to a contract Pillar
    Given an agent contract whose only section is "prime-directive"
    Then a corpus entry in section "prime-directive" validates against the contract
    And a corpus entry in section "no-such-section" fails validation

  @REQ-0.0.37-18-04
  Scenario: The corpus_entry JSON Schema mirrors the model
    Given the corpus_entry JSON Schema
    Then the schema accepts a conformant corpus entry
    And the schema rejects a corpus entry with an out-of-enum tier
