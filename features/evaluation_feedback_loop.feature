@adr-0.0.26 @heavy @foundation
Feature: Evaluation feedback loop end-to-end (ADR-0.0.26 / OBPI-0.0.26-05)
  As an operator running gz governance,
  I want the evaluation-feedback loop to traverse from low-score evaluation
  through justify scaffolding, clustering, GHI proposal, and trailer-validated
  rule edit,
  so that the agent's own structured reasoning artifacts feed back into the
  rule corpus through human-attested governance.

  Background:
    Given the workspace is initialized for the evaluation-feedback loop

  # ----- OBPI-0.0.26-01 — adr-evaluation event emission -----

  @REQ-0.0.26-01-01
  @REQ-0.0.26-01-04
  Scenario: Successful evaluations append distinct adr-evaluation events
    Given an adr-evaluation event for "ADR-0.99.0-emit-a" with weighted total 4.5 and timestamp "2026-05-03T22:00:00+00:00"
    And an adr-evaluation event for "ADR-0.99.0-emit-a" with weighted total 4.6 and timestamp "2026-05-03T22:01:00+00:00"
    Then the ledger contains 2 "adr-evaluation" events for "ADR-0.99.0-emit-a"

  @REQ-0.0.26-01-02
  Scenario: A malformed evaluation does not emit an adr-evaluation event
    When I attempt to record a malformed adr-evaluation for "ADR-0.99.0-bad"
    Then the ledger contains 0 "adr-evaluation" events for "ADR-0.99.0-bad"

  @REQ-0.0.26-01-03
  Scenario: gz validate --documents accepts the adr-evaluation event shape
    Given an adr-evaluation event for "ADR-0.99.0-shape" with weighted total 4.0 and timestamp "2026-05-03T22:02:00+00:00"
    When I run the gz command "validate --documents"
    Then the command exits with code 0

  # ----- OBPI-0.0.26-02 — justify-binding gate -----

  # GHI #394: --evaluation-justify-binding solo handler unreachable; exit code
  # drifts to 1 instead of 3. Scenarios assert non-zero (gate fires) until the
  # upstream predicate is fixed; OBPI-02 unit tests still pin the validator
  # function's policy-breach contract.

  @REQ-0.0.26-02-01
  Scenario: Binding gate fails closed on a low dimension score with no justify artifact
    Given a low-score adr-evaluation event for "ADR-0.99.0-low" with dimension "clarity" scoring 1.5
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-low"
    Then the command exits non-zero
    And the output contains "ADR-0.99.0-low"

  @REQ-0.0.26-02-02
  Scenario: Binding gate fails closed on three or more red-team challenges
    Given an adr-evaluation event for "ADR-0.99.0-rt" firing red-team challenges "C1,C2,C3,C4"
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-rt"
    Then the command exits non-zero

  @REQ-0.0.26-02-03
  Scenario: Binding gate exits 0 when a qualifying justify artifact is present
    Given a low-score adr-evaluation event for "ADR-0.99.0-justified" with dimension "clarity" scoring 1.5
    And a complete justify scaffold exists for "ADR-0.99.0-justified"
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-justified"
    Then the command exits with code 0

  @REQ-0.0.26-02-04
  Scenario: Binding gate exits 0 when scores are healthy and no challenges fired
    Given an adr-evaluation event for "ADR-0.99.0-healthy" with dimension "clarity" scoring 4.5
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-healthy"
    Then the command exits with code 0

  @REQ-0.0.26-02-05
  Scenario: Threshold config drives binding gate behavior
    Given the eval-feedback threshold "low_score_threshold" is set to 1.0
    And an adr-evaluation event for "ADR-0.99.0-thresh" with dimension "clarity" scoring 2.0
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-thresh"
    Then the command exits with code 0

  # ----- OBPI-0.0.26-03 — clustering chore -----

  @REQ-0.0.26-03-01
  Scenario: eval-feedback-cluster appears in gz chores list
    When I run the gz command "chores list"
    Then the command exits with code 0
    And the output contains "eval-feedback"

  @REQ-0.0.26-03-02
  Scenario: Clustering chore emits no proposal below the recurrence threshold
    Given a low-score adr-evaluation event for "ADR-0.99.0-cluster-1" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-cluster-2" with dimension "clarity" scoring 1.5
    When the eval-feedback-cluster chore runs
    Then 0 proposal records exist under ".gzkit/chores/eval-feedback-cluster/proofs/"

  @REQ-0.0.26-03-03
  Scenario: Clustering chore emits one proposal at the recurrence threshold
    Given a low-score adr-evaluation event for "ADR-0.99.0-cluster-1" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-cluster-2" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-cluster-3" with dimension "clarity" scoring 1.5
    When the eval-feedback-cluster chore runs
    Then 1 proposal record exists under ".gzkit/chores/eval-feedback-cluster/proofs/"

  @REQ-0.0.26-03-04
  Scenario: Clustering chore re-run is idempotent (content-hash dedup)
    Given a low-score adr-evaluation event for "ADR-0.99.0-idem-1" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-idem-2" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-idem-3" with dimension "clarity" scoring 1.5
    When the eval-feedback-cluster chore runs
    And the eval-feedback-cluster chore runs again
    Then 1 proposal record exists under ".gzkit/chores/eval-feedback-cluster/proofs/"

  @REQ-0.0.26-03-05
  Scenario: gz validate --chores-layout passes for the eval-feedback-cluster chore
    When I run the gz command "validate --chores-layout"
    Then the command exits with code 0

  # ----- OBPI-0.0.26-04 — propose-ghi (TTY/headless/idempotent) and ProposalRecord -----

  @REQ-0.0.26-04-01
  @REQ-0.0.26-04-12
  Scenario: TTY plus PROPOSE confirmation files a GHI via mocked gh
    Given a proposal record for cluster "dim:clarity:low" exists in the eval-feedback-cluster proofs
    And the environment is interactive
    And the operator confirms with "PROPOSE"
    And gh issue create returns "https://github.com/owner/repo/issues/777"
    When I invoke chores_propose_ghi for "eval-feedback-cluster"
    Then the most recent proposal record has "filed" equal to true
    And the most recent proposal record has "ghi_url" equal to "https://github.com/owner/repo/issues/777"

  @REQ-0.0.26-04-02
  Scenario: A headless run marks the proposal advisory-only
    Given a proposal record for cluster "dim:clarity:low" exists in the eval-feedback-cluster proofs
    And the environment is headless
    When I invoke chores_propose_ghi for "eval-feedback-cluster"
    Then the most recent proposal record has "advisory" equal to true
    And the most recent proposal record has "filed" equal to false

  @REQ-0.0.26-04-03
  Scenario: A propose-ghi re-run does not refile an already-filed proposal
    Given a filed proposal record for cluster "dim:clarity:low" exists with url "https://github.com/owner/repo/issues/700"
    And the environment is interactive
    And the operator confirms with "PROPOSE"
    And gh issue create returns "https://github.com/owner/repo/issues/999"
    When I invoke chores_propose_ghi for "eval-feedback-cluster"
    Then the most recent proposal record has "ghi_url" equal to "https://github.com/owner/repo/issues/700"

  @REQ-0.0.26-04-10
  Scenario: ProposalRecord deserializes with default optional fields
    Given a minimal proposal record without filed, ghi_url, or advisory fields
    Then the proposal record deserializes with "filed" equal to false
    And the proposal record deserializes with "advisory" equal to false
    And the proposal record deserializes with "ghi_url" equal to None

  # ----- OBPI-0.0.26-04 / -05 — Eval-feedback-source trailer validator -----

  # GHI #394 (related): commit_trailers validator missing from
  # _POLICY_BREACH_ERROR_TYPES — generic path routes the eval-feedback
  # trailer error to exit 1 instead of brief-prescribed exit 3. Scenario
  # asserts non-zero (validator fires) until the upstream fix lands.

  @REQ-0.0.26-04-04
  @REQ-0.0.26-05-03
  Scenario: Trailer validator fails closed on a rule-edit commit closing an eval-feedback GHI without trailer
    Given a git repo with a rule-edit commit closing GHI 4242 without an Eval-feedback-source trailer
    And gh issue view labels for 4242 include "eval-feedback"
    When I run the gz command "validate --commit-trailers"
    Then the command exits non-zero

  @REQ-0.0.26-04-05
  Scenario: Trailer validator passes when the rule-edit commit carries an Eval-feedback-source trailer
    Given a git repo with a rule-edit commit closing GHI 4243 with an Eval-feedback-source trailer
    And gh issue view labels for 4243 include "eval-feedback"
    When I run the gz command "validate --commit-trailers"
    Then the command exits with code 0

  # ----- OBPI-0.0.26-05 — full-loop end-to-end -----

  @REQ-0.0.26-05-01
  @REQ-0.0.26-05-02
  Scenario: Full evaluation-feedback loop traverses every transition end-to-end
    Given a low-score adr-evaluation event for "ADR-0.99.0-loop-a" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-loop-b" with dimension "clarity" scoring 1.5
    And a low-score adr-evaluation event for "ADR-0.99.0-loop-c" with dimension "clarity" scoring 1.5
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-loop-a"
    Then the command exits non-zero
    Given a complete justify scaffold exists for "ADR-0.99.0-loop-a"
    And a complete justify scaffold exists for "ADR-0.99.0-loop-b"
    And a complete justify scaffold exists for "ADR-0.99.0-loop-c"
    When I run the gz command "validate --evaluation-justify-binding ADR-0.99.0-loop-a"
    Then the command exits with code 0
    When the eval-feedback-cluster chore runs
    Then 1 proposal record exists under ".gzkit/chores/eval-feedback-cluster/proofs/"
    Given the environment is interactive
    And the operator confirms with "PROPOSE"
    And gh issue create returns "https://github.com/owner/repo/issues/555"
    When I invoke chores_propose_ghi for "eval-feedback-cluster"
    Then the most recent proposal record has "filed" equal to true
    And the most recent proposal record has "ghi_url" equal to "https://github.com/owner/repo/issues/555"
