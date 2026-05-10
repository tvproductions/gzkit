# Authoring Guide Protocol

This document is the protocol specification for integrating editor plugins with
the gzkit authoring guide service. It describes the message envelope format,
lifecycle, versioning rules, error codes, and worked examples needed to implement
a compliant client.

**Audience:** Editor plugin authors who want to display real-time complexity
guidance inside their editor as a developer writes code.

---

## Overview

The gzkit authoring guide service exposes complexity hints to editor plugins
through a lightweight JSON-over-stdio protocol. The service runs as a subprocess
spawned by the editor and communicates over standard input/output using
LSP-style Content-Length framing.

**This protocol is gzkit-specific.** It borrows the envelope framing convention
from the Language Server Protocol but is not LSP-compatible and does not implement
the LSP specification.

### Starting the server

```
gz complexity guide --server
```

The server reads request messages from stdin and writes response messages to
stdout. Stderr is reserved for internal diagnostic output and must not be
consumed by the client.

---

## Content-Length Framing

All messages use LSP-style envelope framing. Each message consists of a header
section and a body section separated by a blank line (two CRLF sequences).

**Format:**

```
Content-Length: N\r\n
\r\n
<BODY>
```

Where `N` is the exact byte length of the UTF-8-encoded JSON body. Byte count,
not character count: multi-byte Unicode characters in string values count by
their UTF-8 byte width, not their code-point count.

**Reading a message (algorithm):**

1. Read lines from the stream until encountering `\r\n\r\n` (a bare CRLF after
   the last header line). Parse the `Content-Length` header value as a decimal
   integer `N`.
2. Read exactly `N` bytes from the stream. Do not read more; the next message
   begins immediately after byte `N`.
3. Decode the `N` bytes as UTF-8. Parse the result as JSON.

**Writing a message (algorithm):**

1. Serialize the JSON object to a UTF-8 string with no trailing newline.
2. Compute `N` as `len(serialized.encode("utf-8"))`.
3. Write `Content-Length: N\r\n\r\n` followed immediately by the `N`-byte body.

No other headers are defined. Clients and servers must ignore unrecognized
headers to allow future extension.

---

## Protocol Lifecycle

The protocol follows a strict initialize-then-work-then-shutdown sequence.
The server must reject any `analyze` request received before a successful
`initialize` handshake.

```
Client                        Server
  |                              |
  |--- initialize request ------>|
  |<-- initialize response ------|
  |                              |
  |--- analyze request --------->|  (zero or more)
  |<-- analyze response ---------|
  |                              |
  |--- analyze request --------->|
  |<-- analyze response ---------|
  |         ...                  |
  |                              |
  |--- shutdown request -------->|
  |<-- shutdown response --------|
  |                              |
  [server exits cleanly]
```

The server processes one request at a time. Clients that require concurrent
analysis must spawn separate server processes.

---

## Protocol Versioning

The protocol uses `major.minor` versioning. The current version is `1.0`.

- **Minor increment** — additive change (new optional params, new capability
  string). Backward compatible. Existing clients continue to work.
- **Major increment** — breaking change (removed method, changed required
  params, incompatible result shape). Clients must be updated.

The client declares its version in the `initialize` request via
`params.clientVersion`. The version string must match the pattern `\d+\.\d+`
(e.g. `"1.0"`, `"1.3"`, `"2.0"`). Additional patch components are permitted by
the schema pattern but the compatibility check uses only `major.minor`.

**Compatibility rule:** The server accepts the request when the client's major
version matches the server's major version. If the major versions differ, the
server returns a `VERSION_MISMATCH` error (code `-32099`) and terminates.

---

## Message Envelopes

### `initialize`

Establishes the session and negotiates version compatibility. Must be the first
request sent. The server rejects subsequent `initialize` calls on the same
session.

#### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string \| integer` | Yes | Caller-assigned correlation ID |
| `method` | `string` | Yes | Must be `"initialize"` |
| `params.clientVersion` | `string` | Yes | Client version (pattern: `\d+\.\d+`) |

#### Response (success)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string \| integer` | Echoes the request `id` |
| `result.version` | `string` | Server version string (e.g. `"1.0"`) |
| `result.capabilities` | `string[]` | Supported capability names (e.g. `["analyze"]`) |

#### Error behavior

Returns `VERSION_MISMATCH` (`-32099`) when client major version differs from
server major version. Returns `INVALID_PARAMS` (`-32602`) when `clientVersion`
is absent or does not match the required pattern.

---

### `analyze`

Analyzes a source file and returns authoring hints. Requires a completed
`initialize` handshake.

#### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string \| integer` | Yes | Caller-assigned correlation ID |
| `method` | `string` | Yes | Must be `"analyze"` |
| `params.file_path` | `string` | Yes | Absolute or workspace-relative path to the file |
| `params.cursor_position` | `integer \| null` | No | Optional cursor position (0-indexed byte offset); `null` or omitted means analyze the whole file |

#### Response (success)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string \| integer` | Echoes the request `id` |
| `result.hints` | `AuthoringHint[]` | List of authoring hints (may be empty) |

Each `AuthoringHint` object carries:

| Field | Type | Description |
|-------|------|-------------|
| `metric` | `string` | Complexity metric key (e.g. `"radon_cc"`) |
| `precedence_band` | `"approaching" \| "approaching_warn"` | Position within the advise band |
| `crossing_value` | `number` | Observed metric value that triggered the hint |
| `archetype` | `string` | Canonical refactor archetype (see schema enum) |
| `doctrinal_frame_headline` | `string` | One-line excerpt from the cited doctrinal frame |
| `recommended_move` | `string` | Human-readable refactor recommendation |
| `file_path` | `string` | Source file path for editor navigation |
| `start_line` | `integer` | First line of the flagged region (1-indexed, inclusive) |
| `end_line` | `integer` | Last line of the flagged region (1-indexed, inclusive; `>= start_line`) |

#### Error behavior

Returns `INVALID_PARAMS` (`-32602`) when `file_path` is absent. Returns a
`METHOD_NOT_FOUND` (`-32601`) error when called before `initialize` completes.
If the file cannot be read, the server returns an empty `hints` list rather
than an error; the client should not treat an empty list as a failure.

---

### `shutdown`

Signals the server to flush any pending state and exit cleanly. The server
sends a response before exiting.

#### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string \| integer` | Yes | Caller-assigned correlation ID |
| `method` | `string` | Yes | Must be `"shutdown"` |
| `params` | `object` | Yes | Empty object `{}` |

#### Response (success)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string \| integer` | Echoes the request `id` |
| `result` | `object` | Empty object `{}` |

#### Error behavior

The server does not return errors for `shutdown`. If the server receives a
`shutdown` before `initialize`, it exits cleanly with an empty result.

---

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| `-32700` | `PARSE_ERROR` | The framing or JSON body is malformed and cannot be parsed |
| `-32601` | `METHOD_NOT_FOUND` | The `method` field is missing, empty, or names an unrecognized method |
| `-32602` | `INVALID_PARAMS` | A required parameter is absent or fails validation (e.g. missing `file_path`) |
| `-32099` | `VERSION_MISMATCH` | The client's major version is incompatible with the server's major version |

All error responses carry an `error` object with `code` (integer) and `message`
(human-readable string). The `result` field is absent when `error` is present,
and vice versa.

---

## Worked Examples

All byte counts below are the exact UTF-8 byte length of the JSON body. The
separator between the header and the body is `\r\n\r\n` (carriage return +
line feed twice).

---

### Example 1 — Initialize handshake

**Client sends:**

```
Content-Length: 63\r\n
\r\n
{"id":1,"method":"initialize","params":{"clientVersion":"1.0"}}
```

**Server responds:**

```
Content-Length: 62\r\n
\r\n
{"id":1,"result":{"version":"1.0","capabilities":["analyze"]}}
```

The client should inspect `result.capabilities` to determine which methods
the server supports before issuing further requests.

---

### Example 2 — Analyze request and response

After a successful initialize, the client sends an analyze request for a
source file. `cursor_position` is optional and may be omitted.

**Client sends:**

```
Content-Length: 76\r\n
\r\n
{"id":2,"method":"analyze","params":{"file_path":"/src/mymodule/parser.py"}}
```

**Server responds** (one hint returned):

```
Content-Length: 333\r\n
\r\n
{"id":2,"result":{"hints":[{"metric":"radon_cc","precedence_band":"approaching","crossing_value":9.0,"archetype":"arrowhead","doctrinal_frame_headline":"Nesting depth approaching warn threshold","recommended_move":"Flatten nested conditions using early returns","file_path":"/src/mymodule/parser.py","start_line":42,"end_line":78}]}}
```

The editor plugin should render each hint at the corresponding `start_line`
through `end_line` range. `recommended_move` is suitable for inline display;
`doctrinal_frame_headline` provides the doctrinal context.

---

### Example 3 — Error response (version mismatch)

A client running protocol version `2.0` attempts to initialize against a
server that implements `1.0`.

**Client sends:**

```
Content-Length: 63\r\n
\r\n
{"id":3,"method":"initialize","params":{"clientVersion":"2.0"}}
```

**Server responds:**

```
Content-Length: 129\r\n
\r\n
{"id":3,"error":{"code":-32099,"message":"VERSION_MISMATCH: client major version 2 is incompatible with server major version 1"}}
```

After returning the error, the server exits. The client must not send further
requests on this session.

---

## Schema References

The canonical JSON Schemas for protocol messages are located at:

- `src/gzkit/schemas/authoring_guide_protocol.json` — request/response envelope
  definitions (`RequestEnvelope`, `ResponseEnvelope`, `InitializeParams`,
  `InitializeResult`, `AnalyzeParams`, `AnalyzeResult`)
- `src/gzkit/schemas/authoring_hint.json` — `AuthoringHint` object shape

These schemas are the normative source of truth for field names, types, and
constraints. This document describes intent and behavior; the schemas describe
the machine-verifiable contract.
