Feature: Intrinsic complexity attestation — two-path escape from refactor pressure (ADR-0.0.29 / OBPI-0.0.29-07)
  As an operator diagnosing a function with genuinely irreducible cyclomatic complexity,
  I want to formally attest that the complexity is intrinsic and cannot be safely decomposed,
  so that the advisor honors the attestation instead of surfacing repeated refactor recommendations.

  Two paths are provided:
  - Decorator path: @intrinsic_complexity(reason=..., attestor=...) annotated in code
  - Commit-time path: gz complexity advise <file>:<qualname> --attest-intrinsic

  @REQ-0.0.29-07-01
  Scenario: decorator-path attested function renders "intrinsic complexity attested" and exits 0
    Given a synthetic complexity-advise environment with a block-band Python source
    And the function "block_band" in "subject.py" is registered as intrinsically attested
    When I run the gz command "complexity advise subject.py --rule-path complexity_thresholds.md"
    Then the command exits with code 0
    And the output contains "intrinsic complexity attested"

  @REQ-0.0.29-07-03
  Scenario: --attest-intrinsic refused when function does not cross any band
    Given a synthetic complexity-advise environment with a clean Python source
    And the ledger directory exists at ".gzkit"
    When I run the gz command "complexity advise subject.py:add --attest-intrinsic --reason=irreducible --attestor=Jeffry --rule-path complexity_thresholds.md"
    Then the command exits with code 1
    And the output contains "does not cross any threshold band"

  @REQ-0.0.29-07-04
  Scenario: --attest-intrinsic with TTY confirmation writes one ledger event and exits 0
    Given a synthetic complexity-advise environment with a block-band Python source
    And the ledger directory exists at ".gzkit"
    When I run the gz command "complexity advise subject.py:block_band --attest-intrinsic --reason=irreducible-state-machine --attestor=Jeffry --rule-path complexity_thresholds.md" with simulated TTY attestation
    Then the command exits with code 0
    And the output contains "Intrinsic complexity attested"
    And the ledger contains an "intrinsic-complexity-attestation" event for "block_band"

  @REQ-0.0.29-07-05
  Scenario: --attest-intrinsic refused in headless environment
    Given a synthetic complexity-advise environment with a block-band Python source
    And the ledger directory exists at ".gzkit"
    When I run the gz command "complexity advise subject.py:block_band --attest-intrinsic --reason=irreducible-state-machine --attestor=Jeffry --rule-path complexity_thresholds.md"
    Then the command exits with code 1
    And the output contains "headless invocation refused"
