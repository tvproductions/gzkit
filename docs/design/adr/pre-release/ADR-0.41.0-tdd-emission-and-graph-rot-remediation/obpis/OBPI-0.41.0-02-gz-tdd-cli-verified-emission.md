---
id: OBPI-0.41.0-02-gz-tdd-cli-verified-emission
parent: ADR-0.41.0
item: 2
lane: Heavy
status: pending
---

# OBPI-0.41.0-02: `gz tdd` CLI with Verified Emission

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md`
- **Checklist Item:** #2 — "gz tdd red/green/chain CLI commands with verified emission semantics"

**Status:** Draft

## Objective

Implement `gz tdd` as a new top-level subcommand family (`red`, `green`, `chain`) that verifies TDD cycle claims by running the test target as a subprocess, classifying the output, and emitting the typed events from OBPI-01. This OBPI is the *verification* layer — without it, OBPI-01's event types are inert.

## Lane

**Heavy** — new top-level CLI subcommand, new user-facing contract with exit codes 0/1/2/3, new verification semantics that can block agent workflows.

## Allowed Paths

- `src/gzkit/commands/tdd.py` — new command implementation
- `src/gzkit/tdd_verifier.py` — verification logic (subprocess runner, output classification)
- `src/gzkit/cli/parser_maintenance.py` — register `tdd` subparser
- `tests/test_tdd_verifier.py` — verification logic unit tests
- `tests/commands/test_tdd_cmds.py` — CLI integration tests
- `features/tdd_emission.feature` — BDD scenarios
- `features/steps/tdd_steps.py` — BDD step definitions
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/obpis/OBPI-0.41.0-02-gz-tdd-cli-verified-emission.md` — this brief

## Denied Paths

- `src/gzkit/events.py` — event types live in OBPI-01's scope
- `data/schemas/tdd_event.schema.json` — schema lives in OBPI-01
- `.gzkit/rules/` — rule integration is OBPI-03
- `docs/user/commands/tdd.md` — manpage is OBPI-04
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. `gz tdd red <test-target> --req REQ-X.Y.Z-NN-MM` runs the test target via subprocess, captures stdout + stderr + exit code.
2. `gz tdd red` verifies exit code is non-zero. If exit code is zero, it exits with code 1 ("verification failed — test passed when RED required").
3. `gz tdd red` parses the captured output to classify the failure into one of: `assertion`, `missing_attribute`, `missing_module`, `name_error`, `type_error`, `collection_error`.
4. `gz tdd red` rejects `collection_error` as invalid RED (exit 1) because the test infrastructure is broken, not the behavior.
5. `gz tdd red` rejects failures whose top stack frame is NOT in a file under `tests/` (exit 1) because the failure is in production code, not the test — this closes the 18-month pre-mortem gap where an agent could fake RED by raising an error in the code-under-test.
6. `gz tdd red` emits a `TddRedObservedEvent` to the ledger via `Ledger.append()` on success.
7. `gz tdd green <test-target> --req REQ-X.Y.Z-NN-MM [--red-ref <event-id>]` runs the test target, verifies exit code is zero, extracts test count, and emits `TddGreenObservedEvent`.
8. `gz tdd chain <req-id>` reads the ledger and prints the RED → GREEN history for the REQ in timestamp order, highlighting gaps (RED without GREEN, GREEN without RED).
9. Exit codes: 0 = emission recorded, 1 = verification failed, 2 = subprocess/IO error, 3 = REQ not found in coverage graph.
10. All three subcommands support `--json` for machine-readable output.
11. All three subcommands document themselves via `--help` and match CLI doctrine (epilog with examples, exit code table).
12. The verifier module (`tdd_verifier.py`) is importable and unit-testable independently of the CLI.

## Discovery Checklist

**Governance:**

- [ ] `AGENTS.md` — DO IT RIGHT section, TASK-driven workflow
- [ ] `.gzkit/rules/tests.md` — TDD discipline (Red-Green-Refactor section)
- [ ] `.gzkit/rules/cli.md` — CLI contract doctrine (exit codes, flags)

**Context:**

- [ ] OBPI-0.41.0-01 event types — must be complete and merged before this OBPI begins
- [ ] `src/gzkit/commands/task.py` — existing subcommand family with ledger-emission pattern (precedent)
- [ ] `src/gzkit/commands/arb.py` — existing wrapper-with-subprocess pattern
- [ ] `src/gzkit/cli/parser_maintenance.py` — subparser registration pattern

**Prerequisites:**

- [ ] OBPI-0.41.0-01 is Completed (event types + schema merged)
- [ ] `uv run gz task list OBPI-0.41.0-01` shows all TASKs completed

**Existing code:**

- [ ] `gz task start` / `gz task complete` in `src/gzkit/commands/task.py` is the nearest structural precedent — read it before authoring.
- [ ] `gz arb step` in `src/gzkit/commands/arb.py` is the nearest subprocess+wrap precedent.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded

### Gate 2: TDD

- [ ] Per-REQ TDD cycle followed — each REQ gets its own Red → Green
- [ ] Once OBPI-01 is complete, this OBPI's own TDD cycle is meta: `gz tdd red` and `gz tdd green` events will be emitted for OBPI-02's REQs as the commands come online (bootstrap: the first REQ is emitted via OBPI-01's typed event constructors directly, subsequent REQs use `gz tdd` itself).

### Gate 3: Docs (Heavy)

- [ ] Docs build passes (manpage lives in OBPI-04 but Rich help text is authored here)

### Gate 4: BDD (Heavy)

- [ ] `features/tdd_emission.feature` scenarios pass

### Gate 5: Human (Heavy)

- [ ] Human attestation at ADR closeout

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_tdd_verifier tests.commands.test_tdd_cmds -v
uv run -m behave features/tdd_emission.feature

# End-to-end proof
uv run gz tdd red tests.test_tdd_verifier.TestVerifyRed.test_classifies_assertion --req REQ-0.41.0-02-01
uv run gz tdd chain REQ-0.41.0-02-01
```

## Acceptance Criteria

- [ ] REQ-0.41.0-02-01: Given a failing assertion test, when `gz tdd red --req REQ-X` runs, then exit code is 0, failure_kind is `assertion`, and a `tdd_red_observed` event is appended to the ledger.
- [ ] REQ-0.41.0-02-02: Given a passing test, when `gz tdd red` runs, then exit code is 1 with message "verification failed — test passed when RED required" and no event is emitted.
- [ ] REQ-0.41.0-02-03: Given a test whose top failure frame is in production code (`src/`), when `gz tdd red` runs, then exit code is 1 and the RED is rejected as invalid (failure originated outside the test).
- [ ] REQ-0.41.0-02-04: Given a test that fails with `ImportError`/`ModuleNotFoundError` on collection, when `gz tdd red` runs, then exit code is 1 and classification is `collection_error` (invalid RED).
- [ ] REQ-0.41.0-02-05: Given a passing test, when `gz tdd green --req REQ-X` runs, then exit code is 0, test count is extracted, and a `tdd_green_observed` event is appended.
- [ ] REQ-0.41.0-02-06: Given `gz tdd green --red-ref <event-id>`, when invoked, then the emitted event's `red_event_ref` field contains the referenced event ID.
- [ ] REQ-0.41.0-02-07: Given a REQ with a RED event followed by a GREEN event, when `gz tdd chain REQ-X` runs, then the output lists the RED and GREEN events in timestamp order.
- [ ] REQ-0.41.0-02-08: Given a REQ with a RED event and no matching GREEN, when `gz tdd chain REQ-X` runs, then the output flags the gap.
- [ ] REQ-0.41.0-02-09: Given `gz tdd red --help`, when invoked, then help text shows usage, description, example, and exit code table per CLI doctrine.
- [ ] REQ-0.41.0-02-10: Given `gz tdd red --json`, when invoked, then output is valid JSON containing the event ID and classification.

## Completion Checklist

- [ ] Gate 1: ADR intent recorded
- [ ] Gate 2: TDD RGR per REQ
- [ ] Code Quality clean
- [ ] Value Narrative documented
- [ ] Key Proof included
- [ ] Evidence recorded

## Evidence

### Gate 2 (TDD)

```text
# Paste test output
```

### Value Narrative

Before this OBPI: TDD cycle claims were prose. Agents could write "I did RED, then GREEN" in a commit message with no verification. After this OBPI: the verifier runs the test, inspects the real stack frame, classifies the failure, and emits a typed ledger event only when the RED is genuinely correct. The event is the proof.

### Key Proof

```bash
$ uv run gz tdd red tests.test_tdd_verifier.TestVerifyRed.test_classifies_assertion --req REQ-0.41.0-02-01
RED verified: assertion failure in tests/test_tdd_verifier.py:42
Event: tdd-red-2026-04-16T09-00-00
Ledger: appended to .gzkit/ledger.jsonl
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: at ADR closeout
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -
