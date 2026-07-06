Feature: gz ontology read-only sonar
  The gz ontology verb group images the corpus-domain projection (ADR-0.32.0,
  OBPI-03) read-only: sense (structural sweep + seams), trace (lineage +
  provenance), resense (diff vs last sweep), seams (fast contacts-only), and
  reach (blast-radius), each with --json / --dot. The interface never writes
  graph state (Boundary Invariant #2); it only exits 0 as a sonar, never gating.

  @REQ-0.32.0-03-01
  Scenario: sense images the structural shape and exits 0 on a healthy tree
    Given the workspace is initialized
    When I run the gz command "ontology sense"
    Then the command exits with code 0
    And the output contains "STRUCTURAL"

  @REQ-0.32.0-03-06
  Scenario: sense --json emits the shape plus the rebuild-fidelity self-report
    Given the workspace is initialized
    When I run the gz command "ontology sense --json"
    Then the command exits with code 0
    And the output contains "fidelity"

  @REQ-0.32.0-03-06
  Scenario: sense --dot emits a graphviz rendering
    Given the workspace is initialized
    When I run the gz command "ontology sense --dot"
    Then the command exits with code 0
    And the output contains "digraph"

  @REQ-0.32.0-03-04
  Scenario: seams runs the fast contacts-only check and exits 0
    Given the workspace is initialized
    When I run the gz command "ontology seams"
    Then the command exits with code 0

  @REQ-0.32.0-03-03
  Scenario: resense reports cleanly when no baseline has been sensed yet
    Given the workspace is initialized
    When I run the gz command "ontology resense"
    Then the command exits with code 0

  @REQ-0.32.0-03-02
  Scenario: trace on an unknown node id exits with a user error
    Given the workspace is initialized
    When I run the gz command "ontology trace NO-SUCH-NODE-999"
    Then the command exits with code 1

  @REQ-0.32.0-03-05
  Scenario: reach on an unknown node id exits with a user error
    Given the workspace is initialized
    When I run the gz command "ontology reach NO-SUCH-NODE-999"
    Then the command exits with code 1
