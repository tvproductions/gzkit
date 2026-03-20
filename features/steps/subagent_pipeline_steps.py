"""BDD steps for subagent pipeline dispatch lifecycle."""

from __future__ import annotations

import json

from behave import given, then, when

from gzkit.pipeline_runtime import (
    DispatchTask,
    TaskComplexity,
    advance_dispatch,
    compose_implementer_prompt,
    create_dispatch_state,
    extract_plan_tasks,
    handle_task_result,
    parse_handoff_result,
)
from gzkit.roles import HandoffResult, HandoffStatus

# ---------------------------------------------------------------------------
# Plan extraction
# ---------------------------------------------------------------------------


@given("a plan with heading-format tasks")
def step_heading_plan(context):
    context.plan_content = (
        "## Task 1: Add the model\n## Task 2: Write tests\n## Task 3: Update docs\n"
    )


@given("a plan with numbered-list tasks")
def step_numbered_plan(context):
    context.plan_content = "1. First thing\n2. Second thing\n"


@given("an empty plan")
def step_empty_plan(context):
    context.plan_content = ""


@when("I extract plan tasks")
def step_extract_tasks(context):
    context.extracted_tasks = extract_plan_tasks(context.plan_content)


@then("{count:d} tasks are found")
def step_task_count(context, count):
    assert len(context.extracted_tasks) == count, (
        f"Expected {count} tasks, got {len(context.extracted_tasks)}"
    )


@then('task {idx:d} description is "{desc}"')
def step_task_description(context, idx, desc):
    task = context.extracted_tasks[idx - 1]
    assert task["description"] == desc, f"Expected '{desc}', got '{task['description']}'"


# ---------------------------------------------------------------------------
# Dispatch state and model routing
# ---------------------------------------------------------------------------


@given("a dispatch state with {count:d} task and {paths:d} allowed paths")
@given("a dispatch state with {count:d} tasks and {paths:d} allowed paths")
def step_create_state(context, count, paths):
    tasks = [{"id": str(i), "description": f"Task {i}"} for i in range(1, count + 1)]
    allowed = [f"file{i}.py" for i in range(paths)]
    context.dispatch_state = create_dispatch_state("OBPI-X", "ADR-X", tasks, allowed)


@given("task {idx:d} is dispatched")
def step_dispatch_task(context, idx):
    advance_dispatch(context.dispatch_state, idx - 1)


@given("task {idx:d} has been dispatched {count:d} times")
def step_dispatched_n_times(context, idx, count):
    record = context.dispatch_state.records[idx - 1]
    record.dispatch_count = count
    from gzkit.pipeline_runtime import TaskStatus

    record.status = TaskStatus.IN_PROGRESS


@then('task {idx:d} model is "{model}"')
def step_task_model(context, idx, model):
    task = context.dispatch_state.records[idx - 1].task
    assert task.model == model, f"Expected model '{model}', got '{task.model}'"


@then('task {idx:d} complexity is "{complexity}"')
def step_task_complexity(context, idx, complexity):
    task = context.dispatch_state.records[idx - 1].task
    assert task.complexity == complexity, (
        f"Expected complexity '{complexity}', got '{task.complexity}'"
    )


# ---------------------------------------------------------------------------
# Result handling
# ---------------------------------------------------------------------------


@when("task {idx:d} returns DONE")
def step_result_done(context, idx):
    result = HandoffResult(status=HandoffStatus.DONE, files_changed=["a.py"])
    context.dispatch_action = handle_task_result(context.dispatch_state, idx - 1, result)


@when("task {idx:d} returns NEEDS_CONTEXT")
def step_result_needs_context(context, idx):
    result = HandoffResult(status=HandoffStatus.NEEDS_CONTEXT)
    context.dispatch_action = handle_task_result(context.dispatch_state, idx - 1, result)


@when("task {idx:d} returns BLOCKED")
def step_result_blocked(context, idx):
    result = HandoffResult(status=HandoffStatus.BLOCKED, concerns=["blocker"])
    context.dispatch_action = handle_task_result(context.dispatch_state, idx - 1, result)


@when('task {idx:d} returns DONE_WITH_CONCERNS with concern "{concern}"')
def step_result_done_with_concerns(context, idx, concern):
    result = HandoffResult(status=HandoffStatus.DONE_WITH_CONCERNS, concerns=[concern])
    context.dispatch_action = handle_task_result(context.dispatch_state, idx - 1, result)


@then('the dispatch action is "{action}"')
def step_check_action(context, action):
    assert context.dispatch_action == action, (
        f"Expected action '{action}', got '{context.dispatch_action}'"
    )


@then('task {idx:d} status is "{status}"')
def step_check_task_status(context, idx, status):
    record = context.dispatch_state.records[idx - 1]
    assert record.status == status, f"Expected status '{status}', got '{record.status}'"


@then('all concerns include "{concern}"')
def step_check_all_concerns(context, concern):
    assert concern in context.dispatch_state.all_concerns, (
        f"Expected '{concern}' in all_concerns: {context.dispatch_state.all_concerns}"
    )


# ---------------------------------------------------------------------------
# Prompt composition
# ---------------------------------------------------------------------------


@given('a dispatch task for "{desc}" with paths "{paths_csv}"')
def step_create_task(context, desc, paths_csv):
    paths = [p.strip() for p in paths_csv.split(",")]
    context.dispatch_task = DispatchTask(
        task_id=1,
        description=desc,
        allowed_paths=paths,
        complexity=TaskComplexity.SIMPLE,
        model="haiku",
    )


@when("I compose the implementer prompt")
def step_compose_prompt(context):
    context.prompt = compose_implementer_prompt(context.dispatch_task, [])


@then('the prompt contains "{text}"')
def step_prompt_contains(context, text):
    assert text in context.prompt, f"Expected '{text}' in prompt"


# ---------------------------------------------------------------------------
# Result parsing
# ---------------------------------------------------------------------------


@given("agent output with a DONE result JSON block")
def step_agent_output(context):
    data = {
        "status": "DONE",
        "files_changed": ["src/x.py"],
        "tests_added": [],
        "concerns": [],
    }
    context.agent_output = f"Some text\n```json\n{json.dumps(data)}\n```\nDone."


@when("I parse the handoff result")
def step_parse_result(context):
    context.parsed_result = parse_handoff_result(context.agent_output)


@then('the parsed status is "{status}"')
def step_parsed_status(context, status):
    assert context.parsed_result is not None, "Parsed result is None"
    assert context.parsed_result.status == status, (
        f"Expected '{status}', got '{context.parsed_result.status}'"
    )


@then('the parsed files changed include "{path}"')
def step_parsed_files(context, path):
    assert path in context.parsed_result.files_changed, (
        f"Expected '{path}' in {context.parsed_result.files_changed}"
    )
