---
id: OBPI-0.0.30-04-editor-protocol-contract
parent: ADR-0.0.30
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.30-04-editor-protocol-contract: Editor/IDE Integration Contract

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md`
- **Checklist Item:** #4 — "Editor/IDE integration contract specification (LSP-style JSON-over-stdio protocol at `src/gzkit/complexity/authoring/protocol.py` + spec document at `docs/governance/complexity/authoring-guide-protocol.md`; no editor implementations in this ADR)"

**Status:** Draft

## Objective

Implement the JSON-over-stdio LSP-style protocol server side at `src/gzkit/complexity/authoring/protocol.py`, author the protocol specification document at `docs/governance/complexity/authoring-guide-protocol.md` for editor authors, and provide the JSON Schema for message envelopes at `src/gzkit/schemas/authoring_guide_protocol.json`. NO editor implementations land in this ADR — the contract is what editor authors consume.

## Lane

**Heavy** — New protocol contract is a forward-facing specification consumed by external editor authors; specification stability is doctrinal. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/authoring/protocol.py` — JSON-over-stdio server implementation
- `src/gzkit/schemas/authoring_guide_protocol.json` — JSON Schema for message envelopes
- `tests/complexity/authoring/test_protocol.py`
- `features/authoring_guide_protocol.feature` — behave scenarios tagged with REQ IDs
- `docs/governance/complexity/authoring-guide-protocol.md` — specification document for editor authors
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces" pointing at the spec for editor authors
- `docs/governance/advisory-rules-audit.md` — scorecard entry for the new protocol surface
- `src/gzkit/commands/complexity_guide.py` — additive `--server` flag only per REQ-6; no other behavior changes
- `src/gzkit/cli/parser_artifacts.py` — register `--server` flag on complexity-guide subparser per REQ-6
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-04-editor-protocol-contract.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/authoring/hint.py`, `engine.py` — projection and engine are OBPI-03 (consumed, not edited)
- `.gzkit/skills/**` — skills are OBPI-02 + OBPI-05
- Any editor-specific plugin code — out of scope per parent ADR § Decision rationale #3
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The protocol implements three message envelopes per the parent ADR's Decision: `initialize` (handshake; client declares its supported version; server responds with its version + capabilities); `analyze` (input: file path + optional cursor position; output: list of `AuthoringHint` with line ranges); `shutdown` (graceful close).
2. REQUIREMENT: Message envelopes are JSON over stdio with Content-Length headers (LSP-style framing). The implementation uses stdlib `json` + manual stdin/stdout handling per `AGENTS.md` § STDLIB-FIRST DOCTRINE; no JSON-RPC library dependency.
3. REQUIREMENT: The JSON Schema at `src/gzkit/schemas/authoring_guide_protocol.json` defines: each message envelope has a required `id`, `method`, and `params` field; the response envelope has `id` (matching the request) and `result` or `error`; the `analyze` method's `params` validate to `{file_path: str, cursor_position: int | None}`; the `analyze` method's `result` validates to `{hints: list[AuthoringHint]}`.
4. REQUIREMENT: The specification document at `docs/governance/complexity/authoring-guide-protocol.md` is editor-author-facing prose: it documents the message envelopes, the lifecycle (initialize → analyze* → shutdown), the version-handshake semantics, the error codes, and provides at least three worked examples (initialize handshake, analyze request + response, error response). The document is the canonical reference editor authors consume.
5. REQUIREMENT: Protocol versioning follows semver-style major.minor: minor versions are additive (new optional methods, new optional fields) and clients of older minor versions remain compatible; major versions are breaking and require coordinated client updates. Initial version is `1.0`. The version is declared in the `initialize` handshake.
6. REQUIREMENT: The protocol server is invoked via `gz complexity guide --server` (a flag on the CLI verb, additive amendment to OBPI-01's contract — handled by adding the flag in this OBPI's CLI patch, allowed because OBPI-01's denied-paths list does NOT exclude additive flag amendments). Editor authors invoke this command and communicate via stdio.
7. REQUIREMENT: Tests cover: handshake exchange (client sends initialize, server responds with version + capabilities); analyze request + response with a fixture file; analyze with empty results (clean file); error response on malformed request; shutdown clean exit; protocol version mismatch produces a named error; JSON Schema validates well-formed envelopes; JSON Schema rejects malformed envelopes. Each test decorated with `@covers(REQ-0.0.30-04-NN)`.
8. REQUIREMENT: A behave scenario at `features/authoring_guide_protocol.feature` tagged `@REQ-0.0.30-04-{01,02,03}` covers handshake → analyze → shutdown end-to-end against a synthetic editor client.
9. REQUIREMENT: The advisory-rules-audit scorecard entry classifies the protocol surface as Mechanical (the JSON Schema is the mechanical enforcement artifact).
10. REQUIREMENT: Function-size discipline; the protocol server decomposes into named helpers (envelope read, envelope write, dispatch, error handling).
11. REQUIREMENT: Cross-platform per `.claude/rules/cross-platform.md` — stdin/stdout reconfigured to UTF-8 at server startup; no Windows-vs-POSIX divergence in protocol semantics.
12. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulate editor-client invocation.
13. REQUIREMENT: NEVER include the operator's personal email in code, specification, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-03's `AuthoringHint` model and engine are not landed, STOP — the protocol's `analyze` method depends on them.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.30-03 (`AuthoringHint` model + engine) is `Completed`; `src/gzkit/complexity/authoring/{hint.py,engine.py}` are landed and the projection from `AdvisorDiagnosis` returns advise-band hints only.
- [x] OBPI-0.0.30-01 (`gz complexity guide` CLI verb) is `Completed`; this OBPI extends the verb with an additive `--server` flag per REQ-6 (allowed: OBPI-01's denied-paths list does not exclude additive flag amendments).
- [x] Parent ADR-0.0.30 § Decision rationale #4 binds the protocol substrate to JSON-over-stdio (NOT TCP/HTTP) for security-surface containment.
- [x] AGENTS.md § STDLIB-FIRST DOCTRINE binds: stdlib `json` + manual Content-Length framing; no `jsonrpc` library dependency added.
- [x] `.claude/rules/cross-platform.md` binds: stdin/stdout reconfigured to binary mode at server startup; Windows CRT O_TEXT mode would corrupt `\r\n` framing.

**Existing Code**

- [x] `src/gzkit/complexity/authoring/hint.py` — `AuthoringHint` Pydantic model (consumed read-only).
- [x] `src/gzkit/complexity/authoring/engine.py` — `analyze(path)` API returning tuple of `AuthoringHint` (consumed read-only).
- [x] `src/gzkit/complexity/advisor/engine.py` — `DiagnosisEngine` upstream of OBPI-03 (transitive dependency; not directly consumed by protocol).
- [x] `src/gzkit/commands/complexity_guide.py` — OBPI-01 CLI handler (extended with additive `--server` flag).
- [x] `src/gzkit/cli/parser_artifacts.py` — `complexity-guide` subparser registration (extended with `--server` flag).
- [x] `src/gzkit/schemas/authoring_hint.json` — JSON Schema for AuthoringHint (cross-referenced by the new protocol schema via `$ref`).

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Specification document lands at `docs/governance/complexity/authoring-guide-protocol.md`

### Gate 4: BDD (Heavy)
- [ ] Behave scenario covers handshake → analyze → shutdown

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/authoring/test_protocol.py -v
uv run -m behave features/authoring_guide_protocol.feature
```

## Demo

The protocol is a JSON-over-stdio LSP-style server consumed by editor authors — there is no end-user CLI. Demo proves the server speaks the documented envelope (initialize → analyze → shutdown).

```bash
# 1. Server starts and responds to initialize (printf feeds one JSON-RPC envelope
#    on stdin; pipe ends so the server exits after responding).
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientVersion":"1.0"}}' \
  | uv run gz complexity guide --server | head -1

# 2. Specification document landed (Gate 3 evidence).
ls docs/governance/complexity/authoring-guide-protocol.md
ls src/gzkit/schemas/authoring_guide_protocol.json

# 3. Behave handshake → analyze → shutdown scenario (REQ-04-01..06).
uv run -m behave features/authoring_guide_protocol.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.30-04-01: Given a synthetic editor client sending an `initialize` request, when the server responds, then the response carries the server version (`1.0`) and a capabilities object listing the supported methods.
- [ ] REQ-0.0.30-04-02: Given an `analyze` request with a fixture file containing advise-band crossings, when the server responds, then the response's `result.hints` is a non-empty list of `AuthoringHint` validating against the JSON Schema.
- [ ] REQ-0.0.30-04-03: Given an `analyze` request with a clean file, when the server responds, then `result.hints` is an empty list.
- [ ] REQ-0.0.30-04-04: Given a malformed request envelope, when the server processes it, then an error response with a named code is returned (envelope validation does not crash the server).
- [ ] REQ-0.0.30-04-05: Given a `shutdown` request, when the server processes it, then it exits 0 cleanly.
- [ ] REQ-0.0.30-04-06: Given an `initialize` request declaring a major-version mismatch, when the server processes it, then a named version-mismatch error is returned.
- [ ] REQ-0.0.30-04-07: Given the specification document, when read, then the message envelopes, lifecycle, error codes, and at least three worked examples are present.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: mkdocs --strict + spec document lands
- [ ] Gate 4: behave scenario passes
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + spec document diff
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof


End-to-end protocol exchange verified by both unittest and behave. ARB receipts: `arb-ruff-1ff2f7139f1e48f0a7011fffa75b1474` (lint clean), `arb-step-typecheck-e72ce5f6fe5d4afcba3717a3fff8a2c7` (ty check clean), `arb-step-unittest-d99178e53ec64bce80642e58a2f6dfa0` (full unittest suite green — 9/9 OBPI-04 protocol tests included), `arb-step-mkdocs-ac1f89ca6d6841deb15f785fb21f2513` (mkdocs build --strict clean), `arb-step-behave-84341b3d122b492bae540aec61b92fda` (4/4 BDD scenarios pass with REQ tags). REQ→@covers parity gate: `uncovered_reqs=0` for all 7 acceptance criteria. Pre-flight `gz obpi precomplete`: 7/7 preconditions met (READY).

### Implementation Summary


- Files created: `src/gzkit/complexity/authoring/protocol.py` (JSON-over-stdio LSP-style server, 225 lines, stdlib-only); `src/gzkit/schemas/authoring_guide_protocol.json` (envelope JSON Schema); `tests/complexity/authoring/test_protocol.py` (9 unit tests with @covers for all 7 acceptance REQs); `features/authoring_guide_protocol.feature` + `features/steps/authoring_guide_protocol_steps.py` (4 BDD scenarios covering all 7 REQs); `docs/governance/complexity/authoring-guide-protocol.md` (editor-author specification with three worked examples).
- Files modified: `src/gzkit/commands/complexity_guide.py` (additive `--server` flag dispatching to `protocol.run_server()`); `src/gzkit/cli/parser_artifacts.py` (registers `--server` flag); `docs/user/manpages/complexity-guide.md` (manpage sync per CLI rule); `docs/user/runbook.md` (protocol server entry); `docs/governance/advisory-rules-audit.md` (Mechanical scorecard entry); brief Allowed Paths corrected (REQ-6 carve-out for `complexity_guide.py` + `parser_artifacts.py`).
- Tests added: 9 unittest cases across 7 test classes; 4 behave scenarios covering REQs 01-07.
- Date completed: 2026-05-10
- Attestation status: Operator attested "attest completed" via Stage 4 ceremony.
- Defects noted: none in scope; one brief authorship gap caught and fixed during plan-audit (Allowed Paths missing `complexity_guide.py` + `parser_artifacts.py` for REQ-6 — corrected before Stage 2).

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.30-04 ships the JSON-over-stdio LSP-style protocol server (`gz complexity guide --server`) plus its editor-author specification document. Verified by ARB receipts arb-ruff-1ff2f7139f1e48f0a7011fffa75b1474 (lint), arb-step-typecheck-e72ce5f6fe5d4afcba3717a3fff8a2c7 (typecheck), arb-step-unittest-d99178e53ec64bce80642e58a2f6dfa0 (full suite green), arb-step-mkdocs-ac1f89ca6d6841deb15f785fb21f2513 (mkdocs strict), arb-step-behave-84341b3d122b492bae540aec61b92fda (4/4 BDD). 7/7 acceptance REQs covered (gz covers uncovered_reqs=0). 7/7 preconditions met (gz obpi precomplete READY).
- Date: 2026-05-10

---

**Brief Status:** Completed

**Date Completed:** 2026-05-10

**Evidence Hash:** -
