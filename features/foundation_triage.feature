Feature: Foundation Triage and Nominal Allocator (ADR-0.0.57 / OBPI-0.0.57-05)
  As an operator,
  I want foundation triage and nominal ID gap-allocation to work correctly,
  So that I can prioritize foundations by impact and allocate IDs without gaps.

  # The nominal-allocator gap-allocation scenario is superseded by ADR-0.34.0
  # (Foundation Sunset): --kind foundation is refused before any ID is
  # allocated, and the allocator itself was deleted. REQ-0.0.57-05-03 keeps
  # its coverage from the foundation-triage scenario below; the refusal is
  # covered by features/foundation_kind_closed.feature.

  @REQ-0.0.57-05-03
  Scenario: foundation-triage script produces structured JSON from in-flight foundations
    Given a foundation-triage fixture with ADRs "ADR-0.0.1,ADR-0.0.2" and insights mentioning "ADR-0.0.1"
    When I run the foundation-triage script with format "json"
    Then the output is valid JSON
    And the JSON contains an entry with id containing "ADR-0.0.1"
