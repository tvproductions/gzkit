Feature: Reporter rendering presets
  The reporter module provides consistent Rich rendering for CLI tables and panels.

  Scenario: status_table renders governance table
    Given a status_table with title "ADR Status" and columns "ADR,Lane,Status" and 2 rows
    When the table is rendered to text
    Then the rendered output contains "ADR Status"
    And the rendered output contains "ADR-0.1.0"

  Scenario: status_table renders empty state
    Given a status_table with title "ADR Status" and columns "ADR" and 0 rows
    When the table is rendered to text
    Then the rendered output contains "No data."

  Scenario: kv_table renders key-value pairs
    Given a kv_table with title "Overview" and 3 pairs
    When the table is rendered to text
    Then the rendered output contains "Overview"
    And the rendered output contains "Lane"
    And the rendered output contains "heavy"

  Scenario: ceremony_panel renders with double border
    Given a ceremony_panel with title "Closeout" and 2 items
    When the panel is rendered to text
    Then the rendered output contains "Closeout"
    And the rendered output contains "Step 1"

  Scenario: list_table renders simple catalog
    Given a list_table with title "Chores" and columns "Slug,Title" and 2 rows
    When the table is rendered to text
    Then the rendered output contains "Chores"
    And the rendered output contains "chore-a"

  Scenario: list_table renders empty state
    Given a list_table with title "Skills" and columns "Name" and 0 rows
    When the table is rendered to text
    Then the rendered output contains "No items found."
