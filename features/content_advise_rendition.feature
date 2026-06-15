Feature: gz content advise-rendition — advisor-QC info-retention verdict

  The advise-rendition subcommand records an agent-supplied
  information-retained-per-byte verdict for a candidate rendition as an ARB
  receipt the operator cites at Gate 5. The tool is deterministic (no LLM /
  network call) and advisory, never gating: any score is recorded and the
  command exits 0. The only fail-closed path is a structurally malformed
  verdict — an empty explanation — which writes no receipt (ADR-0.0.39
  explanation-before-verdict doctrine).

  Background:
    Given I have initialized a gzkit project

  @REQ-0.0.37-24-01
  Scenario: A low retention score is advisory — recorded, exits 0
    When I run advise-rendition for "AGENTS.md" consumer "codex" score "0.12" explanation "Two Promotable bullets dropped — measurable info loss, surfaced for the operator."
    Then the command exits 0
    And an advisor-QC receipt is written
    And the ledger contains a "rendition_advisor_verdict" event for surface "AGENTS.md"

  @REQ-0.0.37-24-01
  Scenario: A high retention score is recorded the same way — exits 0
    When I run advise-rendition for "AGENTS.md" consumer "codex" score "0.94" explanation "All Mechanical bullets retained; two Promotable bullets combined cleanly."
    Then the command exits 0
    And an advisor-QC receipt is written

  @REQ-0.0.37-24-02
  Scenario: An empty explanation fails closed — no receipt written
    When I run advise-rendition for "AGENTS.md" consumer "codex" score "0.5" explanation " "
    Then the command exits non-zero
    And no advisor-QC receipt is written
    And the ledger has no "rendition_advisor_verdict" event

  @REQ-0.0.37-24-03
  Scenario: Identical input yields a byte-identical receipt (deterministic, no LLM)
    When I run advise-rendition twice for "AGENTS.md" consumer "codex" score "0.77" explanation "Deterministic body under identical inputs."
    Then both advise-rendition runs exit 0
    And the two advisor-QC receipts are byte-identical
