Feature: Governed insight authoring (gz insights remember)
  As a gzkit operator or agent
  I want to append schema-valid records to the insights store via a governed verb
  So that hand-authored appends never drift from the InsightRecord schema

  # REQ-0.0.72-03-05: append one schema-valid record + exit 0
  @REQ-0.0.72-03-05
  Scenario: remember appends a schema-valid record to the insights store
    When I run the gz command "insights remember --type improvement --scope obpi-pipeline --summary capture-note"
    Then the command exits with code 0
    And the file ".gzkit/insights/agent-insights.jsonl" exists
    And the file ".gzkit/insights/agent-insights.jsonl" contains "capture-note"

  # REQ-0.0.72-03-05: empty required field fails closed, no line written
  @REQ-0.0.72-03-05
  Scenario: remember fails closed on an empty required summary
    When I run the gz command "insights remember --type improvement --scope obpi-pipeline --summary """
    Then the command exits non-zero
    And the file ".gzkit/insights/agent-insights.jsonl" does not exist
