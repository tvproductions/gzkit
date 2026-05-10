# Plan: OBPI-0.0.30-04 — Editor/IDE Integration Contract

**OBPI:** `OBPI-0.0.30-04-editor-protocol-contract`
**Parent ADR:** `ADR-0.0.30` (Complexity Authoring Guidance)
**Lane:** Heavy — Foundation kind
**Date:** 2026-05-10

---

## Context

OBPI-03 landed the `AuthoringHint` model (`hint.py`) and the authoring-time hint engine (`engine.py`). This OBPI extends that surface to a JSON-over-stdio LSP-style protocol, giving editor authors a stable machine-readable contract. The protocol server is invoked via `gz complexity-guide --server`; the client sends `initialize`, `analyze`, and `shutdown` messages over stdio; the server responds with JSON envelopes framed with Content-Length headers (LSP style). No editor implementations land here — only the server side and its specification document.

Sequencing: OBPI-03 ✅ → OBPI-01 ✅ → OBPI-02 ✅ → **OBPI-04 (this)** → OBPI-05

---

## Files

### New files
- `src/gzkit/complexity/authoring/protocol.py`
- `src/gzkit/schemas/authoring_guide_protocol.json`
- `tests/complexity/authoring/test_protocol.py`
- `features/authoring_guide_protocol.feature`
- `docs/governance/complexity/authoring-guide-protocol.md`

### Modified files
- `src/gzkit/commands/complexity_guide.py` — add `server: bool = False` param; dispatch to `protocol.run_server()`
- `src/gzkit/cli/parser_artifacts.py` — register `--server` flag on `complexity-guide` subparser
- `docs/user/runbook.md` — add protocol server entry under "Complexity doctrine surfaces"
- `docs/governance/advisory-rules-audit.md` — scorecard entry for protocol surface
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-04-editor-protocol-contract.md` — evidence section only

**NOTE — Allowed Paths gap (flagged in plan-audit):** `complexity_guide.py` and `parser_artifacts.py` are absent from the brief's Allowed Paths list. REQ-6 explicitly requires touching both ("handled by adding the flag in this OBPI's CLI patch"). The brief must be updated before the pipeline hook validates paths. Recommendation: add both paths to the brief's Allowed Paths before implementation proceeds.

---

## Steps

### Step 1: TDD RED — Write failing tests

Create `tests/complexity/authoring/test_protocol.py` with failing tests for all REQs. Use `io.BytesIO` to mock stdio; use `tempfile.NamedTemporaryFile` for fixture files. All test methods decorated with `@covers("REQ-0.0.30-04-NN")`.

Required test cases:
- `TestHandshakeExchange.test_initialize_returns_version_and_capabilities` — sends `initialize` with version `1.0`; asserts response carries `version="1.0"` and `capabilities=["initialize","analyze","shutdown"]` (@covers REQ-0.0.30-04-07)
- `TestAnalyzeRequest.test_analyze_advise_band_file_returns_hints` — sends `analyze` with a fixture file containing a high-CC function; asserts `result["hints"]` is non-empty, each hint validates against `authoring_guide_protocol.json` schema (@covers REQ-0.0.30-04-01, REQ-0.0.30-04-02)
- `TestAnalyzeCleanFile.test_analyze_clean_file_returns_empty_hints` — sends `analyze` with a single-line fixture; asserts `result["hints"] == []` (@covers REQ-0.0.30-04-03)
- `TestMalformedRequest.test_malformed_envelope_returns_named_error` — sends garbage JSON; asserts response has `error.code == PARSE_ERROR` and no crash (@covers REQ-0.0.30-04-04)
- `TestShutdownCleanExit.test_shutdown_exits_zero` — sends `shutdown`; asserts `run_server` returns 0 or the loop terminates cleanly (@covers REQ-0.0.30-04-05)
- `TestVersionMismatch.test_major_version_mismatch_returns_named_error` — sends `initialize` with `clientVersion="99.0"`; asserts `error.code == VERSION_MISMATCH` (@covers REQ-0.0.30-04-06)
- `TestJSONSchema.test_schema_validates_well_formed_envelope` — validates a well-formed request envelope passes jsonschema (@covers REQ-0.0.30-04-03)
- `TestJSONSchema.test_schema_rejects_malformed_envelope` — validates envelope missing required `method` fails jsonschema (@covers REQ-0.0.30-04-04)

Run `uv run -m unittest tests/complexity/authoring/test_protocol.py -v` — all tests must fail (RED).

### Step 2: Implement `src/gzkit/complexity/authoring/protocol.py` (GREEN)

Module-level constants:
```python
PROTOCOL_VERSION = "1.0"
SUPPORTED_METHODS = ["initialize", "analyze", "shutdown"]
PARSE_ERROR = -32700
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
VERSION_MISMATCH = -32099
```

Named helpers (function-size discipline, REQ-10):
- `read_message(stream: BinaryIO) -> dict` — reads `Content-Length: N\r\n\r\n` header, reads N bytes, JSON-decodes; raises `ParseError` on malformed input
- `write_message(stream: BinaryIO, payload: dict) -> None` — JSON-encodes, writes `Content-Length: N\r\n\r\n` + bytes
- `make_response(request_id, result: dict) -> dict` — builds `{"id": id, "result": result}`
- `make_error(request_id, code: int, message: str) -> dict` — builds `{"id": id, "error": {"code": code, "message": message}}`
- `handle_initialize(params: dict) -> dict` — validates `clientVersion` major matches `1`; raises `VersionMismatchError` on mismatch; returns `{"version": PROTOCOL_VERSION, "capabilities": SUPPORTED_METHODS}`
- `handle_analyze(params: dict) -> dict` — validates `file_path` present; calls `engine.analyze(Path(params["file_path"]))`; serializes each `AuthoringHint` via `.model_dump()`; returns `{"hints": [...]}`
- `handle_shutdown(params: dict) -> dict` — returns `{"status": "ok"}`
- `dispatch(request: dict) -> dict` — routes `request["method"]` to handler; catches `KeyError`/`TypeError` → `INVALID_PARAMS` error; catches unknown method → `METHOD_NOT_FOUND` error
- `run_server(*, stdin: BinaryIO | None = None, stdout: BinaryIO | None = None) -> int` — cross-platform UTF-8 reconfiguration per REQ-11; main `while True` loop: `read_message` → `dispatch` → `write_message`; break on shutdown; return 0

Cross-platform: at server startup, reconfigure stdin/stdout to binary mode (Windows `msvcrt.setmode` where available, passthrough on POSIX).

Run `uv run -m unittest tests/complexity/authoring/test_protocol.py -v` — all tests must pass (GREEN).

### Step 3: Create `src/gzkit/schemas/authoring_guide_protocol.json`

JSON Schema (Draft 2020-12) defining:
- `RequestEnvelope`: required `id` (str|int), `method` (str), `params` (object)
- `ResponseEnvelope`: required `id`; oneOf `result` (object) or `error` (object with `code`, `message`)
- `AnalyzeParams`: `file_path` (str, required), `cursor_position` (int, nullable)
- `AnalyzeResult`: `hints` (array, items `$ref authoring_hint.json`)
- `InitializeParams`: `clientVersion` (str, required)
- `InitializeResult`: `version` (str), `capabilities` (array of str)

Cross-reference `authoring_hint.json` via `$ref` for the hint shape.

Run `uv run gz arb typecheck` to verify no schema import errors.

### Step 4: Register `--server` flag in CLI (additive to OBPI-01)

In `src/gzkit/cli/parser_artifacts.py`:
- Find the `complexity-guide` subparser registration
- Add: `complexity_guide_parser.add_argument("--server", action="store_true", default=False, help="Start JSON-over-stdio LSP-style protocol server for editor/IDE integration.")`

In `src/gzkit/commands/complexity_guide.py`:
- Add `server: bool = False` keyword param to `complexity_guide_cmd`
- At the top of the function body, before path-checking logic: `if server: from gzkit.complexity.authoring import protocol; raise SystemExit(protocol.run_server())`
- Wire `args.server` through from the CLI dispatcher

Run `uv run -m unittest tests/complexity/authoring/test_protocol.py -v` after this step — tests must still pass.

### Step 5: Author `docs/governance/complexity/authoring-guide-protocol.md`

Create directory `docs/governance/complexity/` if it does not exist.

Sections (editor-author-facing prose):
1. **Overview** — what the protocol is, who it's for (editor plugin authors), how to invoke (`gz complexity-guide --server`)
2. **Protocol Lifecycle** — initialize → analyze* → shutdown sequence diagram (ASCII)
3. **Message Envelopes** — each of `initialize`, `analyze`, `shutdown` documented with params schema, result schema, and error behavior
4. **Protocol Versioning** — semver-style `major.minor`; minor = additive; major = breaking; client declares version in initialize; mismatch behavior
5. **Error Codes** — table of named codes (PARSE_ERROR, METHOD_NOT_FOUND, INVALID_PARAMS, VERSION_MISMATCH) with descriptions
6. **Worked Examples** — exactly three, in fenced code blocks:
   - Example 1: initialize handshake (client request + server response)
   - Example 2: analyze request + response (with hints)
   - Example 3: error response (malformed request)
7. **Content-Length Framing** — how to read/write LSP-style envelopes

Run `uv run mkdocs build --strict` — must pass.

### Step 6: Write BDD scenario `features/authoring_guide_protocol.feature`

Feature: `Complexity Guide Protocol`

One scenario tagged `@REQ-0.0.30-04-01 @REQ-0.0.30-04-02 @REQ-0.0.30-04-03`:

```gherkin
@REQ-0.0.30-04-01 @REQ-0.0.30-04-02 @REQ-0.0.30-04-03
Scenario: Editor client completes handshake, analyze, and shutdown
  Given a complexity guide protocol server is started with a fixture file containing advise-band crossings
  When a client sends an initialize request with version "1.0"
  Then the server responds with version "1.0" and supported capabilities
  When a client sends an analyze request for the fixture file
  Then the server responds with a non-empty hints list
  When a client sends a shutdown request
  Then the server exits cleanly
```

Implement step definitions using subprocess to launch `gz complexity-guide --server` with piped stdio (or use `protocol.run_server` directly via `io.BytesIO`).

Run `uv run -m behave features/authoring_guide_protocol.feature` — must pass.

### Step 7: Advisory scorecard entry

In `docs/governance/advisory-rules-audit.md`, add entry for the protocol surface:
- Surface: `src/gzkit/schemas/authoring_guide_protocol.json`
- Classification: **Mechanical** (JSON Schema is the enforcement artifact; drift in protocol envelopes is caught by schema validation, not human review)
- Rule scope: OBPI-0.0.30-04 editor/IDE integration contract

### Step 8: Update `docs/user/runbook.md`

Under "Complexity doctrine surfaces" section (around line 820), add:

```
`gz complexity-guide --server` (OBPI-0.0.30-04) starts the JSON-over-stdio protocol server for editor/IDE integration. Editors communicate via LSP-style Content-Length–framed JSON envelopes (initialize → analyze* → shutdown). Protocol specification: [`docs/governance/complexity/authoring-guide-protocol.md`](governance/complexity/authoring-guide-protocol.md).
```

### Step 9: Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name unittest-scoped -- uv run -m unittest tests/complexity/authoring/test_protocol.py -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/authoring_guide_protocol.feature
uv run gz validate --documents
```

All must exit 0.

---

## Verification (from brief)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/authoring/test_protocol.py -v
uv run -m behave features/authoring_guide_protocol.feature
```

---

## Notes

- Function-size discipline: `protocol.py` decomposes into named helpers (`read_message`, `write_message`, `handle_*`, `dispatch`, `run_server`); no single function should exceed ~25 lines.
- Cross-platform: `run_server` reconfigures stdio to UTF-8 binary at startup; no Windows-vs-POSIX divergence in protocol semantics.
- `tempfile`-backed fixtures used throughout tests; `io.BytesIO` mocks stdio without spawning a subprocess in unit tests.
- NEVER include operator personal email in code, spec, fixtures, or commit messages.
- Denied paths: `hint.py`, `engine.py`, `complexity_guide.py` (OBPI-01 scope), skills (`**`). Only `--server` flag wiring touches `complexity_guide.py` and `parser_artifacts.py` per REQ-6; brief Allowed Paths must be updated to include them.
