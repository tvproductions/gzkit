"""BDD steps for OBPI lock management commands."""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

from behave import given, then, when

from gzkit.cli import main
from gzkit.lock_manager import LockData, write_lock


def _invoke(args: list[str]) -> tuple[int, str]:
    """Invoke the gz CLI and capture output."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


@given('an OBPI lock exists for "{obpi_id}" held by agent "{agent_name}"')
def step_create_lock_held(context, obpi_id: str, agent_name: str) -> None:
    """Create a lock file directly for testing conflict scenarios."""
    lock_data = LockData(
        obpi_id=obpi_id,
        agent=agent_name,
        pid=1234,
        session_id="test-session-1",
        claimed_at=datetime.now(UTC).isoformat(),
        branch="main",
        ttl_minutes=120,
    )
    write_lock(Path("."), lock_data)


@given('an expired OBPI lock exists for "{obpi_id}"')
def step_create_expired_lock(context, obpi_id: str) -> None:
    """Create an expired lock file (claimed 200 minutes ago)."""
    claimed_at = datetime.now(UTC).replace(year=datetime.now(UTC).year - 1).isoformat()
    lock_data = LockData(
        obpi_id=obpi_id,
        agent="test-agent",
        pid=5678,
        session_id="test-session-2",
        claimed_at=claimed_at,
        branch="main",
        ttl_minutes=120,
    )
    write_lock(Path("."), lock_data)


@when('I run "{command}"')
def step_run_command(context, command: str) -> None:
    """Parse and invoke a gz command."""
    args = shlex.split(command)
    # Remove "gz " prefix if present
    if args and args[0] == "gz":
        args = args[1:]
    context.exit_code, context.output = _invoke(args)


@then("it exits with code {expected:d}")
def step_exit_code(context, expected: int) -> None:
    """Assert the command exited with the expected code."""
    assert context.exit_code == expected, (
        f"Expected exit code {expected}, got {context.exit_code}. Output: {context.output}"
    )


@then('the JSON output field "{field}" is "{expected}"')
def step_json_field_equals(context, field: str, expected: str) -> None:
    """Parse JSON output and compare a field value."""
    try:
        payload = json.loads(context.output)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Failed to parse JSON output: {context.output}") from exc

    if field not in payload:
        raise AssertionError(
            f"Field '{field}' not found in JSON output. Keys: {list(payload.keys())}"
        )

    actual = payload[field]
    # Handle int vs string comparison
    actual_str = str(actual)
    assert actual_str == expected, (
        f"Field '{field}' mismatch: expected '{expected}', got '{actual_str}' (raw: {actual}). "
        f"Full output: {context.output}"
    )
