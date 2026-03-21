"""BDD steps for subagent pipeline dispatch lifecycle."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from behave import given, then, when

from gzkit.pipeline_runtime import (
    DispatchTask,
    TaskComplexity,
    advance_dispatch,
    aggregate_dispatch_results,
    complete_subagent_dispatch_record,
    compose_implementer_prompt,
    create_dispatch_state,
    create_subagent_dispatch_record,
    extract_plan_tasks,
    handle_task_result,
    load_model_routing_config,
    parse_handoff_result,
    validate_agent_files,
)
from gzkit.roles import (
    HandoffResult,
    HandoffStatus,
)

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
@when("task {idx:d} is dispatched")
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


# ---------------------------------------------------------------------------
# Dispatch tracking integration (OBPI-0.18.0-05)
# ---------------------------------------------------------------------------


@given('a subagent dispatch record for task {idx:d} as "{role}" with model "{model}"')
def step_create_dispatch_record(context, idx, role, model):
    context.dispatch_record = create_subagent_dispatch_record(idx, role, model)


@when('the dispatch record is completed with status "{status}"')
def step_complete_dispatch_record(context, status):
    context.completed_record = complete_subagent_dispatch_record(context.dispatch_record, status)


@then("the completed record has a completion timestamp")
def step_record_has_completed_at(context):
    assert context.completed_record.completed_at is not None


@then('the completed record status is "{status}"')
def step_record_status(context, status):
    assert context.completed_record.status == status


@given('{count:d} completed dispatch records with statuses "{statuses_csv}"')
def step_create_completed_records(context, count, statuses_csv):
    statuses = [s.strip() for s in statuses_csv.split(",")]
    context.completed_records = []
    for i, status in enumerate(statuses, 1):
        rec = create_subagent_dispatch_record(i, "Implementer", "sonnet")
        completed = complete_subagent_dispatch_record(rec, status)
        context.completed_records.append(completed)


@when("I aggregate dispatch results")
def step_aggregate(context):
    context.aggregation = aggregate_dispatch_results(context.completed_records)


@then("aggregation shows {completed:d} completed and {blocked:d} blocked")
def step_check_aggregation(context, completed, blocked):
    assert context.aggregation.completed == completed, (
        f"Expected {completed} completed, got {context.aggregation.completed}"
    )
    assert context.aggregation.blocked == blocked, (
        f"Expected {blocked} blocked, got {context.aggregation.blocked}"
    )


@given("no pipeline config file")
def step_no_config(context):
    context.temp_dir = tempfile.mkdtemp()
    context.project_root = Path(context.temp_dir)


@when("I load model routing config")
def step_load_routing(context):
    context.routing_config = load_model_routing_config(context.project_root)


@then('implementer simple model is "{model}"')
def step_implementer_simple(context, model):
    assert context.routing_config.implementer["simple"] == model


@then('reviewer complex model is "{model}"')
def step_reviewer_complex(context, model):
    assert context.routing_config.reviewer["complex"] == model


@given("a project directory with no agent files")
def step_no_agent_files(context):
    context.temp_dir = tempfile.mkdtemp()
    context.project_root = Path(context.temp_dir)


@when("I validate agent files")
def step_validate_agents(context):
    context.validation_errors = validate_agent_files(context.project_root)


@then("validation finds {count:d} errors")
def step_validation_error_count(context, count):
    assert len(context.validation_errors) == count, (
        f"Expected {count} errors, got {len(context.validation_errors)}"
    )


# ---------------------------------------------------------------------------
# Stage 2 dispatch loop
# ---------------------------------------------------------------------------


@given("a plan with {count:d} tasks")
def step_plan_with_n_tasks(context, count):
    context.plan_tasks = [{"id": str(i + 1), "description": f"Task {i + 1}"} for i in range(count)]


@given("allowed paths {paths}")
def step_allowed_paths(context, paths):
    context.allowed_paths = json.loads(paths)


@given("brief requirements {reqs}")
def step_brief_requirements(context, reqs):
    context.brief_requirements = json.loads(reqs)


@when('the controller creates dispatch state for "{obpi_id}" under "{adr_id}"')
def step_create_dispatch_state(context, obpi_id, adr_id):
    context.dispatch_state = create_dispatch_state(
        obpi_id, adr_id, context.plan_tasks, context.allowed_paths
    )


@when("dispatches each task sequentially with DONE results")
def step_dispatch_all_done(context):
    state = context.dispatch_state
    context.prompts = []
    reqs = getattr(context, "brief_requirements", [])
    for i, rec in enumerate(state.records):
        advance_dispatch(state, i)
        prompt = compose_implementer_prompt(rec.task, reqs)
        context.prompts.append(prompt)
        result = HandoffResult(
            status=HandoffStatus.DONE, files_changed=["a.py"], tests_added=[], concerns=[]
        )
        handle_task_result(state, i, result)


@then("all {count:d} tasks are completed")
def step_all_tasks_completed(context, count):
    assert context.dispatch_state.completed_count == count, (
        f"Expected {count} completed, got {context.dispatch_state.completed_count}"
    )


@then("dispatch state is finished")
def step_dispatch_finished(context):
    assert context.dispatch_state.is_finished, "Dispatch state is not finished"


@then("each task prompt includes brief requirements")
def step_prompts_include_reqs(context):
    reqs = getattr(context, "brief_requirements", [])
    for i, prompt in enumerate(context.prompts):
        for req in reqs:
            assert req in prompt, f"Task {i + 1} prompt missing requirement: {req}"


@then("task {idx:d} remains pending")
def step_task_pending(context, idx):
    from gzkit.pipeline_runtime import TaskStatus

    task_index = idx - 1
    assert context.dispatch_state.records[task_index].status == TaskStatus.PENDING, (
        f"Task {idx} is not PENDING"
    )


@then("dispatch state has {count:d} blocked task")
def step_blocked_count(context, count):
    assert context.dispatch_state.blocked_count == count, (
        f"Expected {count} blocked, got {context.dispatch_state.blocked_count}"
    )


# ---------------------------------------------------------------------------
# Two-stage review dispatch (OBPI-0.18.0-07)
# ---------------------------------------------------------------------------


@then("review should be dispatched for task {idx:d}")
def step_review_should_dispatch(context, idx):
    from gzkit.pipeline_runtime import should_dispatch_review

    record = context.dispatch_state.records[idx - 1]
    assert record.result is not None, f"Task {idx} has no result yet"
    assert should_dispatch_review(record.result.status), (
        f"Review should be dispatched for status {record.result.status}"
    )


@then("review should not be dispatched for task {idx:d}")
def step_review_should_not_dispatch(context, idx):
    from gzkit.pipeline_runtime import should_dispatch_review

    record = context.dispatch_state.records[idx - 1]
    assert record.result is not None, f"Task {idx} has no result yet"
    assert not should_dispatch_review(record.result.status), (
        f"Review should NOT be dispatched for status {record.result.status}"
    )


@when("both reviews pass for task {idx:d}")
def step_both_reviews_pass(context, idx):
    from gzkit.pipeline_runtime import handle_review_cycle
    from gzkit.roles import ReviewResult, ReviewVerdict

    spec_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
    quality_pass = ReviewResult(verdict=ReviewVerdict.PASS, findings=[], summary="OK")
    context.review_action = handle_review_cycle(
        context.dispatch_state, idx - 1, spec_pass, quality_pass
    )


@then('the review action is "{action}"')
def step_check_review_action(context, action):
    assert context.review_action == action, (
        f"Expected review action '{action}', got '{context.review_action}'"
    )


@when("spec review finds critical issue for task {idx:d}")
def step_spec_critical(context, idx):
    from gzkit.pipeline_runtime import handle_review_cycle
    from gzkit.roles import ReviewFinding, ReviewFindingSeverity, ReviewResult, ReviewVerdict

    spec_fail = ReviewResult(
        verdict=ReviewVerdict.FAIL,
        findings=[
            ReviewFinding(
                file="a.py",
                severity=ReviewFindingSeverity.CRITICAL,
                message="Requirement not met",
            )
        ],
        summary="Fails spec",
    )
    context.review_action = handle_review_cycle(context.dispatch_state, idx - 1, spec_fail, None)


@then("task {idx:d} review fix count is {count:d}")
def step_review_fix_count(context, idx, count):
    record = context.dispatch_state.records[idx - 1]
    assert record.review_fix_count == count, (
        f"Expected review_fix_count {count}, got {record.review_fix_count}"
    )
