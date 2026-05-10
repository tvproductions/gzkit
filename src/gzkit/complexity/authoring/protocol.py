r"""JSON-over-stdio protocol server for editor/IDE integration (OBPI-0.0.30-04).

Implements a Content-Length-framed JSON-RPC-like protocol over binary stdio.
Invoked by ``gz complexity-guide --server``. Three message types:
``initialize``, ``analyze``, ``shutdown``.

Framing follows the Language Server Protocol envelope:
    Content-Length: <N>\r\n\r\n<N bytes of UTF-8 JSON>

No third-party JSON-RPC library is used (stdlib-first doctrine).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import BinaryIO

from gzkit.complexity.authoring import engine

__all__ = [
    "PARSE_ERROR",
    "METHOD_NOT_FOUND",
    "INVALID_PARAMS",
    "VERSION_MISMATCH",
    "PROTOCOL_VERSION",
    "SUPPORTED_METHODS",
    "read_message",
    "write_message",
    "make_response",
    "make_error",
    "run_server",
]

PROTOCOL_VERSION = "1.0"
SUPPORTED_METHODS = ["initialize", "analyze", "shutdown"]

# JSON-RPC error codes
PARSE_ERROR = -32700
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
VERSION_MISMATCH = -32099


class ProtocolError(Exception):
    """Raised by handlers to signal a specific JSON-RPC error code."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def read_message(stream: BinaryIO) -> dict:
    """Read one Content-Length-framed message from ``stream``.

    Scans lines looking for ``Content-Length: N``.  After finding it,
    skips the blank separator and reads exactly N bytes.  Raises
    ``EOFError`` when the stream is exhausted before a complete message
    is read.  Raises ``ValueError`` on any other framing or JSON error.
    """
    content_length: int | None = None
    while True:
        raw_line = stream.readline()
        if raw_line == b"":
            raise EOFError("stream exhausted")
        line = raw_line.strip()
        if line.lower().startswith(b"content-length:"):
            try:
                content_length = int(line.split(b":", 1)[1].strip())
            except ValueError as exc:
                raise ValueError(f"Bad Content-Length value: {line!r}") from exc
        elif line == b"" and content_length is not None:
            break
        elif line == b"":
            # blank line before Content-Length header — skip
            continue
        else:
            # Unrecognized non-header content: framing error
            raise ValueError(f"Unexpected framing content: {line!r}")

    body = stream.read(content_length)
    if len(body) < content_length:
        raise EOFError("stream ended mid-body")
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON decode error: {exc}") from exc


def write_message(stream: BinaryIO, payload: dict) -> None:
    """Write ``payload`` as a Content-Length-framed message to ``stream``."""
    body = json.dumps(payload).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    stream.write(header + body)


def make_response(request_id: object, result: dict) -> dict:
    """Build a success response envelope."""
    return {"id": request_id, "result": result}


def make_error(request_id: object, code: int, message: str) -> dict:
    """Build an error response envelope."""
    return {"id": request_id, "error": {"code": code, "message": message}}


def handle_initialize(params: dict) -> dict:
    """Handle the ``initialize`` handshake.

    Validates the client's major version against ``PROTOCOL_VERSION``.
    Raises ``ProtocolError`` with ``VERSION_MISMATCH`` on mismatch.
    """
    client_version = params.get("clientVersion", PROTOCOL_VERSION)
    client_major = client_version.split(".")[0]
    server_major = PROTOCOL_VERSION.split(".")[0]
    if client_major != server_major:
        raise ProtocolError(
            VERSION_MISMATCH,
            f"Client major version {client_major!r} != server {server_major!r}",
        )
    return {"version": PROTOCOL_VERSION, "capabilities": SUPPORTED_METHODS}


def handle_analyze(params: dict) -> dict:
    """Handle the ``analyze`` request.

    Calls the authoring engine and returns serialized hints.
    Raises ``ProtocolError`` with ``INVALID_PARAMS`` when ``file_path`` is absent.
    """
    file_path = params.get("file_path")
    if not file_path:
        raise ProtocolError(INVALID_PARAMS, "Missing required param: file_path")
    hints = engine.analyze(Path(file_path))
    return {"hints": [h.model_dump() for h in hints]}


def handle_shutdown(params: dict) -> dict:  # noqa: ARG001
    """Handle the ``shutdown`` request."""
    return {"status": "ok", "shutdown": True}


def _configure_binary_stdio() -> None:
    r"""Reconfigure sys.stdin/stdout to binary mode at server startup.

    On Windows the CRT opens stdin/stdout in O_TEXT mode at the fd level,
    which allows \\n→\\r\\n translation and corrupts Content-Length framing.
    Calling msvcrt.setmode forces O_BINARY on the underlying fd.
    On POSIX this is a no-op.
    """
    if sys.platform == "win32":
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


_HANDLERS = {
    "initialize": handle_initialize,
    "analyze": handle_analyze,
    "shutdown": handle_shutdown,
}


def dispatch(request: dict) -> tuple[dict, bool]:
    """Route ``request`` to the correct handler.

    Returns ``(response_payload, should_shutdown)``.  ``should_shutdown`` is
    ``True`` only when the method is ``"shutdown"``.
    """
    req_id = request.get("id")
    method = request.get("method")
    if method is None:
        return make_error(req_id, METHOD_NOT_FOUND, "Missing 'method' field"), False
    handler = _HANDLERS.get(method)
    if handler is None:
        return make_error(req_id, METHOD_NOT_FOUND, f"Unknown method: {method!r}"), False
    params = request.get("params", {})
    try:
        result = handler(params)
    except ProtocolError as exc:
        return make_error(req_id, exc.code, exc.message), False
    except (KeyError, FileNotFoundError, OSError, ValueError) as exc:
        return make_error(req_id, INVALID_PARAMS, str(exc)), False
    should_shutdown = method == "shutdown"
    return make_response(req_id, result), should_shutdown


def run_server(
    *,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
) -> int:
    """Run the JSON-over-stdio protocol server loop.

    Reads Content-Length-framed messages from ``stdin`` (defaults to
    ``sys.stdin.buffer``), dispatches each, writes responses to ``stdout``
    (defaults to ``sys.stdout.buffer``).  Returns 0 on clean shutdown.

    Malformed framing or JSON produces a ``-32700`` error response, then the
    loop exits.  EOF with no pending message exits silently.
    """
    if stdin is None and stdout is None:
        _configure_binary_stdio()
    in_stream: BinaryIO = stdin if stdin is not None else sys.stdin.buffer
    out_stream: BinaryIO = stdout if stdout is not None else sys.stdout.buffer

    while True:
        try:
            msg = read_message(in_stream)
        except EOFError:
            break
        except ValueError:
            error_resp = make_error(None, PARSE_ERROR, "Parse error")
            write_message(out_stream, error_resp)
            out_stream.flush()
            break
        response, should_shutdown = dispatch(msg)
        write_message(out_stream, response)
        out_stream.flush()
        if should_shutdown:
            break
    return 0
