"""Behave step definitions for the complexity guide protocol server (OBPI-0.0.30-04).

Uses io.BytesIO to drive the protocol server in-process — no subprocess.
The server is stateless per-call so messages are replayed cumulatively:
each Then step runs the server with all queued messages so far plus a
synthetic shutdown to flush the server's response loop.

@covers REQ-0.0.30-04-01
@covers REQ-0.0.30-04-02
@covers REQ-0.0.30-04-03
"""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

from behave import given, then, when  # type: ignore[import-untyped]

from gzkit.complexity.authoring.protocol import read_message, run_server

# A medium-complexity function that crosses the advise band (CC = 5, threshold = 4)
_ADVISE_SOURCE = """\
def medium(x, y, z, w):
    if x > 0:
        return x + y
    elif x < 0:
        return -x
    elif y > 0:
        return y + z
    elif y < 0:
        return -y
    else:
        return w
"""

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."

_SYNTHETIC_SHUTDOWN_BODY = json.dumps({"id": 99, "method": "shutdown", "params": {}}).encode(
    "utf-8"
)
_SYNTHETIC_SHUTDOWN = (
    f"Content-Length: {len(_SYNTHETIC_SHUTDOWN_BODY)}\r\n\r\n".encode("ascii")
    + _SYNTHETIC_SHUTDOWN_BODY
)


def _distilled_characteristics(metric: str = "radon_cc") -> str:
    return "\n".join(
        [
            "---",
            "corpus_revision: 1",
            "---",
            "",
            "# Distilled complexity characteristics — synthetic fixture",
            "",
            f"## Metric: `{metric}`",
            "",
            "Across the corpus, synthetic distribution applies.",
            "",
            "**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.",
            "",
            "### Practitioner-eye observation",
            "",
            _PRACTITIONER_EYE_SENTINEL,
            "",
        ]
    )


def _rule_data(metric: str, distilled_path: Path, anchor: str) -> str:
    return json.dumps(
        {
            "corpus_revision": 1,
            "citation": {
                "distilled_characteristics_path": distilled_path.as_posix(),
                "section_anchor": anchor,
                "corpus_revision": 1,
            },
            "bands": [
                {
                    "metric": metric,
                    "corpus_percentile": 75,
                    "absolute_number": 4.0,
                    "trigger_semantic": "advise",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 90,
                    "absolute_number": 7.0,
                    "trigger_semantic": "warn",
                },
                {
                    "metric": metric,
                    "corpus_percentile": 95,
                    "absolute_number": 11.0,
                    "trigger_semantic": "block",
                },
            ],
        }
    )


def _build_synthetic_environment() -> None:
    """Materialize distilled doc + threshold data at canonical path in CWD.

    The protocol's handle_analyze calls engine.analyze which loads the
    threshold table from DEFAULT_RULE_PATH (.gzkit/rules/complexity-thresholds.json)
    relative to CWD. Without this scaffold the analyze dispatch returns an
    error envelope rather than a result envelope.
    """
    cwd = Path.cwd()
    complexity_dir = cwd / "docs" / "governance" / "complexity"
    complexity_dir.mkdir(parents=True, exist_ok=True)
    distilled_path = complexity_dir / "distilled-characteristics-synthetic.md"
    distilled_path.write_text(_distilled_characteristics(), encoding="utf-8")

    rule_dir = cwd / ".gzkit" / "rules"
    rule_dir.mkdir(parents=True, exist_ok=True)
    rule_path = rule_dir / "complexity-thresholds.json"
    anchor = "radon-cc"
    rule_path.write_text(
        _rule_data("radon_cc", distilled_path.relative_to(cwd), anchor),
        encoding="utf-8",
    )


def _collect_responses(messages: list[bytes]) -> list[dict]:
    """Run the server with the given messages and return all response dicts."""
    combined = b"".join(messages)
    stdin = io.BytesIO(combined)
    stdout = io.BytesIO()
    run_server(stdin=stdin, stdout=stdout)
    stdout.seek(0)
    responses: list[dict] = []
    try:
        while True:
            msg = read_message(stdout)
            responses.append(msg)
    except (EOFError, ValueError):
        pass
    return responses


@given("a complexity guide protocol server is started")
def step_server_started(context) -> None:  # type: ignore[no-untyped-def]
    _build_synthetic_environment()
    context.protocol_messages: list[bytes] = []
    context.protocol_fixture: Path | None = None
    context.protocol_exit_code: int | None = None


@when('a client sends an initialize request with version "{version}"')
def step_send_initialize(context, version: str) -> None:  # type: ignore[no-untyped-def]
    body = json.dumps(
        {"id": 1, "method": "initialize", "params": {"clientVersion": version}}
    ).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    context.protocol_messages.append(header + body)


@when("a client sends an analyze request for a Python fixture file")
def step_send_analyze(context) -> None:  # type: ignore[no-untyped-def]
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(_ADVISE_SOURCE)
        context.protocol_fixture = Path(f.name)
    body = json.dumps(
        {
            "id": 2,
            "method": "analyze",
            "params": {
                "file_path": str(context.protocol_fixture),
                "cursor_position": None,
            },
        }
    ).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    context.protocol_messages.append(header + body)


@when("a client sends a shutdown request")
def step_send_shutdown(context) -> None:  # type: ignore[no-untyped-def]
    body = json.dumps({"id": 3, "method": "shutdown", "params": {}}).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    context.protocol_messages.append(header + body)

    combined = b"".join(context.protocol_messages)
    stdin = io.BytesIO(combined)
    stdout = io.BytesIO()
    exit_code = run_server(stdin=stdin, stdout=stdout)
    context.protocol_exit_code = exit_code
    stdout.seek(0)
    context.protocol_responses: list[dict] = []
    try:
        while True:
            msg = read_message(stdout)
            context.protocol_responses.append(msg)
    except (EOFError, ValueError):
        pass


@then('the server responds with protocol version "{version}" and supported capabilities')
def step_check_initialize_response(context, version: str) -> None:  # type: ignore[no-untyped-def]
    # Run server with queued messages so far (just initialize) + synthetic shutdown
    # to get the initialize response before the analyze and shutdown messages are queued.
    responses = _collect_responses(context.protocol_messages + [_SYNTHETIC_SHUTDOWN])
    assert len(responses) >= 1, f"Expected at least 1 response, got {len(responses)}"
    resp = responses[0]
    assert "result" in resp, f"Expected 'result' in initialize response, got: {resp}"
    assert resp["result"]["version"] == version, (
        f"Expected version {version!r}, got {resp['result'].get('version')!r}"
    )
    assert "analyze" in resp["result"]["capabilities"], (
        f"Expected 'analyze' in capabilities: {resp['result'].get('capabilities')}"
    )


@then("the server responds with a hints list")
def step_check_analyze_response(context) -> None:  # type: ignore[no-untyped-def]
    # Run server with queued messages so far (initialize + analyze) + synthetic shutdown.
    responses = _collect_responses(context.protocol_messages + [_SYNTHETIC_SHUTDOWN])
    assert len(responses) >= 2, (
        f"Expected at least 2 responses, got {len(responses)}; responses: {responses}"
    )
    resp = responses[1]
    assert "result" in resp, f"Expected 'result' in analyze response, got: {resp}"
    assert isinstance(resp["result"]["hints"], list), (
        f"Expected hints to be a list, got: {type(resp['result'].get('hints'))}"
    )


@then("the server exits cleanly")
def step_check_shutdown(context) -> None:  # type: ignore[no-untyped-def]
    assert context.protocol_exit_code == 0, (
        f"Expected exit code 0, got {context.protocol_exit_code}"
    )
    if context.protocol_fixture and context.protocol_fixture.exists():
        context.protocol_fixture.unlink()


@when("a client sends an analyze request for a clean Python fixture file")
def step_send_analyze_clean(context) -> None:  # type: ignore[no-untyped-def]
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write("def simple(): pass\n")
        context.protocol_fixture = Path(f.name)
    body = json.dumps(
        {
            "id": 2,
            "method": "analyze",
            "params": {
                "file_path": str(context.protocol_fixture),
                "cursor_position": None,
            },
        }
    ).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    context.protocol_messages.append(header + body)


@then("the server responds with an empty hints list")
def step_check_empty_hints_response(context) -> None:  # type: ignore[no-untyped-def]
    responses = _collect_responses(context.protocol_messages + [_SYNTHETIC_SHUTDOWN])
    assert len(responses) >= 1, f"Expected at least 1 response, got {len(responses)}"
    resp = responses[0]
    assert "result" in resp, f"Expected 'result' in analyze response, got: {resp}"
    hints = resp["result"]["hints"]
    assert hints == [], f"Expected empty hints for clean fixture, got: {hints}"


@when("a client sends a malformed envelope")
def step_send_malformed(context) -> None:  # type: ignore[no-untyped-def]
    context.protocol_messages.append(b"not json\r\n")
    stdin = io.BytesIO(b"".join(context.protocol_messages))
    stdout = io.BytesIO()
    context.protocol_exit_code = run_server(stdin=stdin, stdout=stdout)
    stdout.seek(0)
    context.protocol_responses = []
    try:
        while True:
            msg = read_message(stdout)
            context.protocol_responses.append(msg)
    except (EOFError, ValueError):
        pass


@then("the server responds with parse error code -32700")
def step_check_parse_error(context) -> None:  # type: ignore[no-untyped-def]
    assert len(context.protocol_responses) >= 1, "Expected an error response"
    resp = context.protocol_responses[0]
    assert "error" in resp, f"Expected 'error' in response, got: {resp}"
    assert resp["error"]["code"] == -32700, (
        f"Expected error code -32700, got {resp['error'].get('code')}"
    )


@then("the server responds with version mismatch error code -32099")
def step_check_version_mismatch_error(context) -> None:  # type: ignore[no-untyped-def]
    responses = _collect_responses(context.protocol_messages + [_SYNTHETIC_SHUTDOWN])
    assert len(responses) >= 1, f"Expected at least 1 response, got {len(responses)}"
    resp = responses[0]
    assert "error" in resp, f"Expected 'error' in response, got: {resp}"
    assert resp["error"]["code"] == -32099, (
        f"Expected error code -32099, got {resp['error'].get('code')}"
    )
