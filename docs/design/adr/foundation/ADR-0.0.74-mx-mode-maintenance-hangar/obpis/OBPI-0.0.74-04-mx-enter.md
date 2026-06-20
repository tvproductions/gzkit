---
id: OBPI-0.0.74-04-mx-enter
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 4
lane: Heavy
status: Draft
# req_atomic: each REQ is one coherent surface authored in a single TDD
# increment — the enter handler that sets the marker + writes the event +
# captures scope (01), the operator-only door (02), the empty-input fail-close
# (03), the lock_manager/token rail (04), and the manpage + cli-audit doc
# deliverable (05). None decomposes into parallel seq=02+ sub-tasks
# (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-04-01
  - REQ-0.0.74-04-02
  - REQ-0.0.74-04-03
  - REQ-0.0.74-04-04
  - REQ-0.0.74-04-05
---

# OBPI-0.0.74-04-mx-enter: Mx Enter

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #4 - "gz mx enter — operator opens the door (reason + attestor); sets marker, writes mx_session_opened, captures inspection scope; token-rail/lock_manager; manpage + gz cli audit green; unit tests"

**Status:** Draft

## Objective

<!-- gz-validate-skip: command-shape -->
The `gz mx enter --reason <text> --attestor <name>` command lands so the operator opens the hangar door — the tool sets the marker, writes the `mx_session_opened` ledger event, and captures the inspection scope — while the agent can never open the door on its own and an empty reason or attestor fails closed.

## Lane

**Heavy** - This OBPI adds a new gz mx enter CLI subcommand (a command/runtime-contract surface) and a new ledger event type.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- gz-validate-skip: command-shape -->
- `src/gzkit/commands/mx_cmd.py` **CREATE** — the `gz mx` command group with the `enter` handler (sets marker, writes `mx_session_opened`, captures inspection scope)
- `src/gzkit/cli/parser_governance.py` — register the `mx enter` verb on the parser
- `docs/user/manpages/mx.md` **CREATE** — manpage for the `mx` verb group (Heavy-lane docs gate)
- `tests/commands/test_mx_enter.py` **CREATE** — unit tests for the enter handler, the operator-only door, and the empty-input fail-close
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-04-mx-enter.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope

## Creates These Files

- `src/gzkit/commands/mx_cmd.py`
- `docs/user/manpages/mx.md`
- `tests/commands/test_mx_enter.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: gz mx enter — operator opens the door (reason + attestor); sets marker, writes mx_session_opened, captures inspection scope; token-rail/lock_manager; manpage + gz cli audit green; unit tests.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
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
uv run gz cli audit

# Specific verification for this OBPI
test -f src/gzkit/commands/mx_cmd.py
test -f docs/user/manpages/mx.md
test -f tests/commands/test_mx_enter.py
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# The operator opens the hangar door; the tool sets the marker and writes mx_session_opened.
uv run gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0
```

## Acceptance Criteria

<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-04-01 [behavior]: Given `gz mx enter --reason <text> --attestor <name>`, when it runs outside the hangar, then it sets the marker, writes one `mx_session_opened` ledger event, and captures the inspection scope on that event. (@covers test in `tests/commands/test_mx_enter.py`)
- [ ] REQ-0.0.74-04-02 [behavior]: Given the enter command, when no `--attestor` is supplied, then the door does not open — there is no agent-autonomous entry path; only an operator-supplied attestor opens the hangar. (@covers test in `tests/commands/test_mx_enter.py`)
- [ ] REQ-0.0.74-04-03 [behavior]: Given an empty `--reason` or empty `--attestor`, when enter runs, then it fails closed with exit 1, sets no marker, and writes no ledger event. (@covers test in `tests/commands/test_mx_enter.py`)
- [ ] REQ-0.0.74-04-04 [behavior]: Given the enter command, when it opens the hangar, then it acquires the session through the `lock_manager`/token rail (not a hand-rolled lock), so concurrent entry is serialized on the existing rail. (@covers test in `tests/commands/test_mx_enter.py`)
- [ ] REQ-0.0.74-04-05 [support]: The new `mx` verb is documented (manpage + command doc + index). Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/mx.md`.

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

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
