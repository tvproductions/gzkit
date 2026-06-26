---
id: OBPI-0.0.74-06-mx-log-auto-assembled
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 6
lane: Heavy
status: Completed
# req_atomic: each REQ is one coherent surface authored in a single TDD
# increment — assembling the log from the ledger+commit window (01), naming
# every fix and the ADRs/OBPIs/REQs touched (02), presenting it for operator
# review before signing (03), and the mx_session_opened/closed event types
# carrying the session window (04, SUPPORT). None decomposes into parallel
# seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-06-01
  - REQ-0.0.74-06-02
  - REQ-0.0.74-06-03
  - REQ-0.0.74-06-04
---

# OBPI-0.0.74-06-mx-log-auto-assembled: Mx Log Auto Assembled

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #6 - "The auto-assembled MX log — built at exit from ledger events + commits between enter/exit, naming fixes and the ADRs/OBPIs/REQs touched; operator reviews before signing; ledger event; unit tests"

**Status:** Completed

## Objective

At exit the MX log is assembled by construction from the ledger events and commits between enter and exit — naming every fix and the ADRs/OBPIs/REQs it touched, so it cannot be hand-narrated or forgotten — and is presented for operator review before signing, backed by `mx_session_opened`/`mx_session_closed` event types that carry the session window.

## Lane

**Heavy** - This OBPI adds the `mx_session_opened`/`mx_session_closed` ledger event types (a schema/runtime-contract surface) that the close ceremony reads.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/mx/log.py` **CREATE** — assembles the MX log from the ledger events + commits in the enter→exit window, naming every fix and the ADRs/OBPIs/REQs touched
- `src/gzkit/events.py` — add the `mx_session_opened` / `mx_session_closed` event types carrying the session window (enter/exit anchors)
- `src/gzkit/schemas/ledger.json` — add the paired schema entries for the two new event types (coupled surface: `gz validate --ledger` and `audit_event_schemas` fail closed on a typed event with no schema entry) — amended 2026-06-26 (operator-approved coupled-surface declaration, AGENTS.md DO-IT-RIGHT §1a)
- `src/gzkit/commands/mx_cmd.py` — wire the `assemble_and_render` call into `mx_exit_cmd` before the `mx_session_closed` write (REQ-06-03: the operator reviews the assembled log before signing) — amended 2026-06-26 (operator-approved) per plan-audit gap: REQ-06-03 requires a call site, and the exit command is the only surface that runs "at exit"
- `tests/mx/test_mx_log.py` **CREATE** — unit tests for window assembly, the named-artifacts roll-up, and the event types' window fields
- `tests/test_schemas.py` — register the two new event types in the `_EVENT_MODELS` schema↔model alignment registry (coupled surface: `TestLedgerSchemaAlignment` fails closed on a schema event with no mapped model) — amended 2026-06-26 (operator-approved coupled-surface declaration, AGENTS.md DO-IT-RIGHT §1a; precedent OBPI-0.0.71-01)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-06-mx-log-auto-assembled.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope

> **Security surface:** `src/gzkit/events.py` was checked against
> `data/security_surfaces.json` — it does NOT overlap any registered surface
> (the `ledger_integrity` category names `ledger.py`, `ledger_events.py`,
> `ledger_proof.py`, `ledger_semantics.py`, not `events.py`), so no
> `sensitivity: security` declaration is required.

## Creates These Files

- `src/gzkit/mx/log.py`
- `tests/mx/test_mx_log.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: With an `mx_session_opened` and `mx_session_closed` bounding a session, the log assembler MUST build the log only from the ledger events and commits in that enter→exit window — complete by construction, not hand-supplied (REQ-06-01).
1. REQUIREMENT: The assembled log MUST name every fix and the ADRs/OBPIs/REQs each fix touched, so nothing in the window can be forgotten or narrated away (REQ-06-02).
1. REQUIREMENT: On exit, the assembled log MUST be rendered for operator review before the signature is taken — the operator reviews the complete-by-construction record, never a hand-authored summary (REQ-06-03).
1. REQUIREMENT: The `mx_session_opened` and `mx_session_closed` ledger event types MUST exist and carry the session window (enter/exit anchors) that bounds assembly, proven by `gz validate --ledger` exit 0 and an `artifact_edited` ledger event for `src/gzkit/events.py` (REQ-06-04).
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --ledger

# Specific verification for this OBPI
test -f src/gzkit/mx/log.py
test -f tests/mx/test_mx_log.py
```

## Demo

```bash
# Assemble the MX log for an enter→exit window and show it names every fix + the ADRs/OBPIs/REQs touched.
uv run -m unittest tests.mx.test_mx_log -v
```

## Acceptance Criteria

- [ ] REQ-0.0.74-06-01 [behavior]: Given an `mx_session_opened` and `mx_session_closed` bounding a session, when the log assembler runs, then the log is built only from the ledger events and commits in that enter→exit window — complete by construction, not hand-supplied. (@covers test in `tests/mx/test_mx_log.py`)
- [ ] REQ-0.0.74-06-02 [behavior]: Given the events and commits in the window, when the log assembles, then it names every fix and the ADRs/OBPIs/REQs each fix touched, so nothing in the window can be forgotten or narrated away. (@covers test in `tests/mx/test_mx_log.py`)
- [ ] REQ-0.0.74-06-03 [behavior]: Given an assembled log, when exit runs, then the log is rendered for operator review before the signature is taken — the operator reviews the complete-by-construction record, never a hand-authored summary. (@covers test in `tests/mx/test_mx_log.py`)
- [ ] REQ-0.0.74-06-04 [support]: The `mx_session_opened` and `mx_session_closed` ledger event types exist and carry the session window (enter/exit anchors) that bounds assembly. Proof: `gz validate --ledger` exit 0 + `artifact_edited` ledger event for `src/gzkit/events.py`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

### Key Proof


REQ-06-03 (render-before-signature) ordering proof:

  uv run -m unittest tests.mx.test_mx_log.TestExitRendersLogBeforeSigning -v

A spy records the count of mx_session_closed ledger events at the moment assemble_and_render is called; asserts [0] (log reviewed before signature) and exactly 1 close event after exit. The independent adversary inverted the order in mx_exit_cmd and the test went RED ([1] != [0]) — a genuine ordering proof, not a tautology. Full suite: 6521/6521 (receipt arb-step-unittest-891fad1a279e4e16a939bafdf5c23ff3, exit_status 0).

### Implementation Summary


- Files created: src/gzkit/mx/log.py (enter→exit window assembler: assemble_window, parse_artifacts, render, assemble_and_render); tests/mx/test_mx_log.py (8 unit tests, @covers all 4 REQs)
- Files modified: src/gzkit/events.py (MxSessionOpenedEvent/MxSessionClosedEvent typed classes added to TypedLedgerEvent union); src/gzkit/commands/mx_cmd.py (log.assemble_and_render wired into mx_exit_cmd before the mx_session_closed write); src/gzkit/schemas/ledger.json (paired schema entries — coupled surface); tests/test_schemas.py (_EVENT_MODELS registry — coupled surface)
- Tests added: 8 (TestAssembleWindow, TestParseArtifacts, TestRender, TestExitRendersLogBeforeSigning, TestMxSessionEventTypes)
- Date completed: 2026-06-26
- Attestation status: operator-verbatim "attest completed" (attestor g0)
- Defects noted: none in deliverable. Two coupled-surface side-fixes landed (GHI #645 reconcile @covers false-positive; GHI #646 pipeline status-flip — found post-merge to conflict with frontmatter-reconcile, follow-up flagged to operator)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-06 mx-log-auto-assembled (ADR-0.0.74 Decision #6, Heavy lane): the auto-assembled MX log assembles by construction from the ledger events + git commits in the enter→exit window, names every fix and the ADRs/OBPIs/REQs each touched, and renders for operator review before the mx_session_closed signature; MxSessionOpenedEvent/MxSessionClosedEvent typed event types carry the session window. All-green: unittest 6521/6521 (arb-step-unittest-891fad1a279e4e16a939bafdf5c23ff3), ruff (arb-ruff-e5071f4e47b84810abc10a88a5e458d0), typecheck (arb-step-typecheck-07c90783df5a48a5bacee25ce8c6563e), mkdocs --strict (arb-step-mkdocs-5e84d0e2f63d4cd084aa2af960f9ce26); REQ parity 4/4; independent adversary NOT-REFUTED-WITH-CAVEATS with the one tautological-render caveat fixed and re-validated RED-under-mutation.
- Date: 2026-06-26

---

**Date Completed:** 2026-06-26

**Evidence Hash:** -
