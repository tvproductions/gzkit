"""Tests for the JSON-over-stdio protocol server (OBPI-0.0.30-04)."""

from __future__ import annotations

import io
import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.complexity.authoring.protocol import (
    read_message,
    run_server,
    write_message,
)
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ADVISE_BAND_SOURCE = textwrap.dedent(
    """\
    def medium_complexity(x, y, z, w):
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
)


def _make_framed(method: str, params: dict | None = None, req_id: int = 1) -> bytes:
    """Return a Content-Length-framed JSON-RPC request message."""
    body = json.dumps({"id": req_id, "method": method, "params": params or {}}).encode()
    header = f"Content-Length: {len(body)}\r\n\r\n".encode()
    return header + body


def _run_with_messages(messages: list[bytes]) -> list[dict]:
    """Run protocol server against a sequence of messages; return parsed responses."""
    combined = b"".join(messages)
    stdin = io.BytesIO(combined)
    stdout = io.BytesIO()
    run_server(stdin=stdin, stdout=stdout)
    stdout.seek(0)
    responses = []
    try:
        while True:
            msg = read_message(stdout)
            responses.append(msg)
    except (EOFError, ValueError):
        pass
    return responses


# ---------------------------------------------------------------------------
# TestContentLengthFraming
# ---------------------------------------------------------------------------


class TestContentLengthFraming(unittest.TestCase):
    """REQ-0.0.30-04-01: Content-Length framing helpers."""

    @covers("REQ-0.0.30-04-01")
    def test_write_message_includes_content_length_header(self) -> None:
        buf = io.BytesIO()
        write_message(buf, {"id": 1, "result": "ok"})
        buf.seek(0)
        written = buf.read()
        self.assertTrue(written.startswith(b"Content-Length:"))

    @covers("REQ-0.0.30-04-01")
    def test_read_message_reads_correct_bytes(self) -> None:
        payload = {"id": 42, "method": "test", "params": {}}
        buf = io.BytesIO()
        write_message(buf, payload)
        buf.seek(0)
        result = read_message(buf)
        self.assertEqual(result, payload)


# ---------------------------------------------------------------------------
# TestHandshakeExchange
# ---------------------------------------------------------------------------


class TestHandshakeExchange(unittest.TestCase):
    """REQ-0.0.30-04-07: initialize handshake."""

    @covers("REQ-0.0.30-04-07")
    def test_initialize_returns_version_and_capabilities(self) -> None:
        responses = _run_with_messages(
            [
                _make_framed("initialize", {"clientVersion": "1.0"}),
                _make_framed("shutdown", req_id=2),
            ]
        )
        self.assertGreaterEqual(len(responses), 1)
        init_resp = responses[0]
        self.assertIn("result", init_resp)
        self.assertEqual(init_resp["result"]["version"], "1.0")
        self.assertIn("analyze", init_resp["result"]["capabilities"])


# ---------------------------------------------------------------------------
# TestAnalyzeWithCrossings
# ---------------------------------------------------------------------------


class TestAnalyzeWithCrossings(unittest.TestCase):
    """REQ-0.0.30-04-02: analyze with potentially high-complexity code."""

    @covers("REQ-0.0.30-04-02")
    def test_analyze_advise_band_file_returns_hints(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(_ADVISE_BAND_SOURCE)
            fixture_path = Path(f.name)
        try:
            responses = _run_with_messages(
                [
                    _make_framed(
                        "analyze",
                        {"file_path": str(fixture_path), "cursor_position": None},
                    ),
                    _make_framed("shutdown", req_id=2),
                ]
            )
            self.assertGreaterEqual(len(responses), 1)
            analyze_resp = responses[0]
            self.assertIn("result", analyze_resp)
            hints = analyze_resp["result"]["hints"]
            self.assertIsInstance(hints, list)
            self.assertGreater(len(hints), 0, "expected non-empty hints for advise-band fixture")
        finally:
            fixture_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# TestAnalyzeCleanFile
# ---------------------------------------------------------------------------


class TestAnalyzeCleanFile(unittest.TestCase):
    """REQ-0.0.30-04-03: analyze a clean/simple file returns empty hints list."""

    @covers("REQ-0.0.30-04-03")
    def test_analyze_clean_file_returns_hints_list(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("def simple(): pass\n")
            fixture_path = Path(f.name)
        try:
            responses = _run_with_messages(
                [
                    _make_framed(
                        "analyze",
                        {"file_path": str(fixture_path), "cursor_position": None},
                    ),
                    _make_framed("shutdown", req_id=2),
                ]
            )
            self.assertGreaterEqual(len(responses), 1)
            analyze_resp = responses[0]
            self.assertIn("result", analyze_resp)
            hints = analyze_resp["result"]["hints"]
            self.assertIsInstance(hints, list)
            self.assertEqual(hints, [], "expected empty hints for simple one-liner")
        finally:
            fixture_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# TestMalformedRequest
# ---------------------------------------------------------------------------


class TestMalformedRequest(unittest.TestCase):
    """REQ-0.0.30-04-04: malformed and missing-method requests."""

    @covers("REQ-0.0.30-04-04")
    def test_malformed_json_returns_parse_error(self) -> None:
        # Raw bytes, no Content-Length header — server should respond with -32700
        raw = b"not json\r\n"
        stdin = io.BytesIO(raw)
        stdout = io.BytesIO()
        run_server(stdin=stdin, stdout=stdout)
        stdout.seek(0)
        responses = []
        try:
            while True:
                msg = read_message(stdout)
                responses.append(msg)
        except (EOFError, ValueError):
            pass
        self.assertGreaterEqual(len(responses), 1)
        resp = responses[0]
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32700)

    @covers("REQ-0.0.30-04-04")
    def test_missing_method_returns_method_not_found(self) -> None:
        # Valid JSON, no "method" field
        body = json.dumps({"id": 1, "params": {}}).encode()
        header = f"Content-Length: {len(body)}\r\n\r\n".encode()
        framed = header + body

        responses = _run_with_messages([framed, _make_framed("shutdown", req_id=2)])
        self.assertGreaterEqual(len(responses), 1)
        resp = responses[0]
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)


# ---------------------------------------------------------------------------
# TestShutdownCleanExit
# ---------------------------------------------------------------------------


class TestShutdownCleanExit(unittest.TestCase):
    """REQ-0.0.30-04-05: shutdown terminates the server loop."""

    @covers("REQ-0.0.30-04-05")
    def test_shutdown_terminates_loop(self) -> None:
        stdin = io.BytesIO(_make_framed("shutdown"))
        stdout = io.BytesIO()
        result = run_server(stdin=stdin, stdout=stdout)
        self.assertEqual(result, 0)


# ---------------------------------------------------------------------------
# TestVersionMismatch
# ---------------------------------------------------------------------------


class TestVersionMismatch(unittest.TestCase):
    """REQ-0.0.30-04-06: incompatible major version returns VERSION_MISMATCH."""

    @covers("REQ-0.0.30-04-06")
    def test_major_version_mismatch_returns_error(self) -> None:
        responses = _run_with_messages([_make_framed("initialize", {"clientVersion": "99.0"})])
        self.assertGreaterEqual(len(responses), 1)
        resp = responses[0]
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32099)


if __name__ == "__main__":
    unittest.main()
