"""Step implementations for the advisor timeout BDD scenarios."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from behave import given, then, when


@given("a synthetic timeout environment with a slow callable exceeding {timeout}s timeout")
def step_impl_given_slow_callable(context, timeout):
    context.timeout_s = float(timeout)
    context.tmp_dir = tempfile.mkdtemp()
    context.log_path = Path(context.tmp_dir) / "advisor-failures.jsonl"

    def slow_callable() -> str:
        time.sleep(10)
        return "never"

    context.callable_ = slow_callable


@when("I invoke run_with_timeout using default context")
def step_impl_when_invoke(context):
    from gzkit.complexity.advisor.timeout import run_with_timeout

    context.result = run_with_timeout(
        context.callable_,
        timeout_s=context.timeout_s,
        log_path=context.log_path,
    )


@when("I invoke run_with_timeout using auto-chain context")
def step_impl_when_invoke_with_context(context):
    from gzkit.complexity.advisor.timeout import run_with_timeout

    context.result = run_with_timeout(
        context.callable_,
        timeout_s=context.timeout_s,
        log_path=context.log_path,
        context_file_paths=["src/example.py"],
        context_invocation="auto-chain",
    )


@then("the result is a TimeoutTimedOut with elapsed_s > 0")
def step_impl_then_timed_out(context):
    from gzkit.complexity.advisor.timeout import TimeoutTimedOut

    assert isinstance(context.result, TimeoutTimedOut), (
        f"Expected TimeoutTimedOut, got {type(context.result)}"
    )
    assert context.result.elapsed_s > 0


@then('the result callable_name is "{name}"')
def step_impl_then_callable_name(context, name):
    assert context.result.callable_name == name


@then("the log file contains a valid JSONL entry")
def step_impl_then_log_exists(context):
    assert context.log_path.exists(), f"Log file not found at {context.log_path}"
    content = context.log_path.read_text(encoding="utf-8").strip()
    context.log_entry = json.loads(content)
    assert "timestamp" in context.log_entry
    assert "callable_name" in context.log_entry
    assert "timeout_s" in context.log_entry
    assert "elapsed_s" in context.log_entry
    assert "context" in context.log_entry


@then('the log entry has callable_name "{name}"')
def step_impl_then_log_callable_name(context, name):
    assert context.log_entry["callable_name"] == name


@then('the log entry context invocation is "{invocation}"')
def step_impl_then_log_invocation(context, invocation):
    assert context.log_entry["context"]["invocation"] == invocation


@then("the log entry context file_paths is a list")
def step_impl_then_log_file_paths(context):
    assert isinstance(context.log_entry["context"]["file_paths"], list)
