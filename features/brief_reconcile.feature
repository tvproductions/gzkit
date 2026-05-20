# Step definitions are authored when the operator-facing surfaces land
# (OBPI-0.0.37-06 adds the gz-brief-reconcile CLI verb plus features/steps/);
# OBPI-0.0.37-05's allowlist scopes this file to the .feature contract only.
# Scenarios are @wip so the pre-merge behave gate skips them until steps exist.
Feature: OBPI Brief Reconciliation Engine (CIC-2)
  As a gzkit operator
  I want the reconciliation engine to detect drift between OBPI briefs and project reality
  So that implementation begins and completes only when the brief matches current project shape

  # REQ-0.0.37-05-01: Engine entry point and ReconcileResult structure

  @wip
  @REQ-0.0.37-05-01
  Scenario: reconcile_brief returns a ReconcileResult with all five delta fields
    Given an OBPI brief file at "tests/fixtures/brief_reconcile/passing.md"
    When I run reconcile_brief against the project root
    Then the result is a ReconcileResult with brief_id "OBPI-0.0.37-05-brief-reconcile-engine"
    And the result has an allowlist_delta field
    And the result has a discovery_delta field
    And the result has a verification_delta field
    And the result has a req_count_delta field
    And the result has a citation_delta field
    And has_drift is False

  # REQ-0.0.37-05-02: Allowlist dimension (missing_on_disk + missing_in_brief)

  @wip
  @REQ-0.0.37-05-02
  Scenario: allowlist dimension reports missing_on_disk for a non-existent allowlisted path
    Given an OBPI brief that allowlists "src/gzkit/governance/nonexistent_module.py"
    When I run reconcile_brief against the project root
    Then the allowlist_delta.missing_on_disk contains "src/gzkit/governance/nonexistent_module.py"
    And has_drift is True

  @wip
  @REQ-0.0.37-05-02
  Scenario: allowlist dimension reports missing_in_brief for a sibling module imported by REQ tests
    Given an OBPI brief whose allowlist contains "src/gzkit/foo/a.py"
    And a REQ test imports a sibling module "src/gzkit/foo/b.py" absent from the allowlist
    When I run reconcile_brief against the project root
    Then the allowlist_delta.missing_in_brief contains "src/gzkit/foo/b.py"
    And has_drift is True

  @wip
  @REQ-0.0.37-05-02
  Scenario: missing_in_brief neighborhood filter excludes cross-cutting utility imports
    Given an OBPI brief whose allowlist contains "src/gzkit/foo/a.py"
    And a REQ test imports the cross-cutting utility "src/gzkit/traceability.py"
    When I run reconcile_brief against the project root
    Then the allowlist_delta.missing_in_brief does not contain "src/gzkit/traceability.py"

  # REQ-0.0.37-05-03: Verification verb dimension

  @wip
  @REQ-0.0.37-05-03
  Scenario: verification-verb dimension reports an unregistered gz verb
    Given an OBPI brief whose Verification section references an unregistered gz verb
    When I run reconcile_brief against the project root
    Then the verification_delta.unresolved_verbs contains that verb
    And has_drift is True

  @wip
  @REQ-0.0.37-05-03
  Scenario: a registered gz verb is not reported as unresolved
    Given an OBPI brief whose Verification section references a registered gz verb
    When I run reconcile_brief against the project root
    Then the verification_delta.unresolved_verbs does not contain that verb

  # REQ-0.0.37-05-04: REQ count dimension

  @wip
  @REQ-0.0.37-05-04
  Scenario: req count dimension reports non-zero delta when REQ count does not match acceptance criteria
    Given an OBPI brief with 2 REQUIREMENT lines and 1 acceptance criteria checkbox
    When I run reconcile_brief against the project root
    Then the req_count_delta.delta is non-zero
    And has_drift is True

  @wip
  @REQ-0.0.37-05-04
  Scenario: req count dimension reports zero delta when counts match
    Given an OBPI brief with 1 REQUIREMENT line and 1 acceptance criteria checkbox
    When I run reconcile_brief against the project root
    Then the req_count_delta.delta is 0

  # REQ-0.0.37-05-05: Citation tuples dimension

  @wip
  @REQ-0.0.37-05-05
  Scenario: citation dimension reports stale citations for non-existent artifact files
    Given an OBPI brief with a citation to "docs/does-not-exist-anywhere.md"
    When I run reconcile_brief against the project root
    Then the citation_delta.stale_citations contains a tuple with "docs/does-not-exist-anywhere.md"
    And has_drift is True

  @wip
  @REQ-0.0.37-05-05
  Scenario: citation dimension does not report citations whose artifact file exists
    Given an OBPI brief with a citation to an artifact file that exists on disk
    When I run reconcile_brief against the project root
    Then the citation_delta.stale_citations is empty

  # REQ-0.0.37-05-06: gz validate --brief-reconcile (structured-brief escalation)

  @wip
  @REQ-0.0.37-05-06
  Scenario: gz validate --brief-reconcile exits 0 when no structured brief has drift
    Given no structured OBPI brief in the corpus has drift
    When I run the gz command "validate --brief-reconcile"
    Then the exit code is 0

  @wip
  @REQ-0.0.37-05-06
  Scenario: gz validate --brief-reconcile exits 3 when a structured brief has drift
    Given a structured OBPI brief in the corpus has drift in at least one dimension
    When I run the gz command "validate --brief-reconcile"
    Then the exit code is 3

  @wip
  @REQ-0.0.37-05-06
  Scenario: gz validate --brief-reconcile does not escalate drift on legacy briefs
    Given a legacy OBPI brief in the corpus has drift but no structured brief does
    When I run the gz command "validate --brief-reconcile"
    Then the exit code is 0

  @wip
  @REQ-0.0.37-05-06
  Scenario: gz validate --brief-reconcile reports which brief has drift
    Given a structured OBPI brief in the corpus has drift
    When I run the gz command "validate --brief-reconcile"
    Then the output contains the brief ID
    And the output contains which dimension has drift

  # REQ-0.0.37-05-07: Engine purity

  @wip
  @REQ-0.0.37-05-07
  Scenario: the reconciliation engine writes no files
    Given an OBPI brief file at "tests/fixtures/brief_reconcile/passing.md"
    When I run reconcile_brief against the project root
    Then no files in the project are written or modified

  @wip
  @REQ-0.0.37-05-07
  Scenario: the reconciliation engine emits no ledger events
    Given the current ledger event count
    And an OBPI brief file at "tests/fixtures/brief_reconcile/passing.md"
    When I run reconcile_brief against the project root
    Then the ledger event count is unchanged
