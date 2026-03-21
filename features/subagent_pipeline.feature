Feature: Subagent pipeline dispatch lifecycle
  Stage 2 controller dispatches implementer subagents per plan task
  with model-aware routing and structured result handling.

  @dispatch
  Scenario: Tasks are extracted from a heading-format plan
    Given a plan with heading-format tasks
    When I extract plan tasks
    Then 3 tasks are found
    And task 1 description is "Add the model"

  @dispatch
  Scenario: Tasks are extracted from a numbered-list plan
    Given a plan with numbered-list tasks
    When I extract plan tasks
    Then 2 tasks are found

  @dispatch
  Scenario: Empty plan yields zero tasks
    Given an empty plan
    When I extract plan tasks
    Then 0 tasks are found

  @dispatch
  Scenario: Simple task routes to haiku model
    Given a dispatch state with 1 task and 2 allowed paths
    Then task 1 model is "haiku"
    And task 1 complexity is "simple"

  @dispatch
  Scenario: Standard task routes to sonnet model
    Given a dispatch state with 1 task and 4 allowed paths
    Then task 1 model is "sonnet"
    And task 1 complexity is "standard"

  @dispatch
  Scenario: Complex task routes to opus model
    Given a dispatch state with 1 task and 7 allowed paths
    Then task 1 model is "opus"
    And task 1 complexity is "complex"

  @dispatch
  Scenario: DONE result advances to next task
    Given a dispatch state with 2 tasks and 1 allowed paths
    And task 1 is dispatched
    When task 1 returns DONE
    Then the dispatch action is "advance"
    And task 1 status is "done"

  @dispatch
  Scenario: DONE on last task completes dispatch
    Given a dispatch state with 1 task and 1 allowed paths
    And task 1 is dispatched
    When task 1 returns DONE
    Then the dispatch action is "complete"

  @dispatch
  Scenario: DONE_WITH_CONCERNS logs concerns and advances
    Given a dispatch state with 2 tasks and 1 allowed paths
    And task 1 is dispatched
    When task 1 returns DONE_WITH_CONCERNS with concern "might break X"
    Then the dispatch action is "advance"
    And all concerns include "might break X"

  @dispatch
  Scenario: NEEDS_CONTEXT triggers redispatch
    Given a dispatch state with 1 task and 1 allowed paths
    And task 1 is dispatched
    When task 1 returns NEEDS_CONTEXT
    Then the dispatch action is "redispatch"

  @dispatch
  Scenario: NEEDS_CONTEXT circuit breaker after max retries
    Given a dispatch state with 1 task and 1 allowed paths
    And task 1 has been dispatched 2 times
    When task 1 returns NEEDS_CONTEXT
    Then the dispatch action is "handoff"
    And task 1 status is "blocked"

  @dispatch
  Scenario: BLOCKED triggers fix attempt
    Given a dispatch state with 1 task and 1 allowed paths
    And task 1 is dispatched
    When task 1 returns BLOCKED
    Then the dispatch action is "fix"

  @dispatch
  Scenario: BLOCKED after max fix attempts triggers handoff
    Given a dispatch state with 1 task and 1 allowed paths
    And task 1 has been dispatched 2 times
    When task 1 returns BLOCKED
    Then the dispatch action is "handoff"
    And task 1 status is "blocked"

  @dispatch
  Scenario: Prompt includes allowed files and rules
    Given a dispatch task for "Add validation" with paths "src/a.py,src/b.py"
    When I compose the implementer prompt
    Then the prompt contains "src/a.py"
    And the prompt contains "### Rules"

  @dispatch
  Scenario: Result JSON is parsed from agent output
    Given agent output with a DONE result JSON block
    When I parse the handoff result
    Then the parsed status is "DONE"
    And the parsed files changed include "src/x.py"

  @dispatch
  Scenario: Dispatch record tracks subagent lifecycle
    Given a subagent dispatch record for task 1 as "Implementer" with model "sonnet"
    When the dispatch record is completed with status "done"
    Then the completed record has a completion timestamp
    And the completed record status is "done"

  @dispatch
  Scenario: Dispatch aggregation computes correct totals
    Given 3 completed dispatch records with statuses "done,blocked,done_with_concerns"
    When I aggregate dispatch results
    Then aggregation shows 2 completed and 1 blocked

  @dispatch
  Scenario: Model routing loads defaults
    Given no pipeline config file
    When I load model routing config
    Then implementer simple model is "haiku"
    And reviewer complex model is "opus"

  @dispatch
  Scenario: Agent file validation detects missing files
    Given a project directory with no agent files
    When I validate agent files
    Then validation finds 4 errors
