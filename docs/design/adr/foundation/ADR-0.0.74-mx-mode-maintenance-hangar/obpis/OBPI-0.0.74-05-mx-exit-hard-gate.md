---
id: OBPI-0.0.74-05-mx-exit-hard-gate
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 5
lane: Heavy
status: Draft
# req_atomic: each REQ is one coherent surface authored in a single TDD
# increment — the full-strength re-run against the enter-time scope (01), the
# hard-refuse / no-force / no-narrowing fail-close (02), the operator-signs +
# write-close + clear-marker green path (03), the manpage + cli-audit doc
# deliverable (04), and the exit-only-clears boundary fence (05). None
# decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope
# exemption).
req_atomic:
  - REQ-0.0.74-05-01
  - REQ-0.0.74-05-02
  - REQ-0.0.74-05-03
  - REQ-0.0.74-05-04
  - REQ-0.0.74-05-05
---

# OBPI-0.0.74-05-mx-exit-hard-gate: Mx Exit Hard Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #5 - "gz mx exit — hard gate: re-run all guards full strength against the enter-time scope, green-or-grounded, no --force; operator signs; writes mx_session_closed and removes marker; exit is the only clearing path; manpage + gz cli audit green; unit tests"

**Status:** Draft

## Objective

<!-- gz-validate-skip: command-shape -->
The `gz mx exit --attestor <name>` hard gate lands: it re-runs every guard at full strength against the enter-time inspection scope, hard-refuses on any red (exit 3, no `--force`, no narrowing your way out), and only on all-green lets the operator sign — writing `mx_session_closed` and removing the marker, the one and only path that clears it.

## Lane

**Heavy** - This OBPI adds a new gz mx exit CLI subcommand (a command/runtime-contract surface) and a new ledger event type.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- gz-validate-skip: command-shape -->
- `src/gzkit/commands/mx_cmd.py` — add the `exit` handler to the `gz mx` command group (full-strength re-run, hard refuse, write `mx_session_closed`, remove marker)
- `docs/user/manpages/mx.md` — extend the `mx` manpage with the `exit` verb (Heavy-lane docs gate)
- `tests/commands/test_mx_exit.py` **CREATE** — unit tests for the re-run, the hard-refuse fail-close, the green-path close, and exit-only-clears
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-05-mx-exit-hard-gate.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope

## Creates These Files

- `src/gzkit/commands/mx_cmd.py`
- `docs/user/manpages/mx.md`
- `tests/commands/test_mx_exit.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: gz mx exit — hard gate: re-run all guards full strength against the enter-time scope, green-or-grounded, no --force; operator signs; writes mx_session_closed and removes marker; exit is the only clearing path; manpage + gz cli audit green; unit tests.
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
test -f tests/commands/test_mx_exit.py
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Re-run every guard at full strength against the enter-time scope; the operator signs only on all-green.
uv run gz mx exit --attestor g0
```

## Acceptance Criteria

<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-05-01 [behavior]: Given an open MX session, when `gz mx exit` runs, then it re-runs every guard at full strength against the inspection scope captured at enter time (not a narrowed subset). (@covers test in `tests/commands/test_mx_exit.py`)
- [ ] REQ-0.0.74-05-02 [behavior]: Given any guard reporting red on the re-run, when exit completes, then it hard-refuses with exit 3, leaves the marker in place, and writes no `mx_session_closed` — there is no `--force` flag and no way to narrow the scope out of the check. (@covers test in `tests/commands/test_mx_exit.py`)
- [ ] REQ-0.0.74-05-03 [behavior]: Given an all-green re-run and an operator `--attestor`, when exit completes, then the operator signs, the tool writes one `mx_session_closed` event, and the marker is removed; an empty `--attestor` fails closed with exit 1 and no clear. (@covers test in `tests/commands/test_mx_exit.py`)
- [ ] REQ-0.0.74-05-04 [support]: The new `mx exit` verb is documented (manpage + command doc + index). Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/mx.md`.
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.74-05-05 [structural-fence]: `gz mx exit` writing `mx_session_closed` is the ONLY path that clears the marker; a marker cleared without a matching `mx_session_closed` event is a detected dangling state (parent ADR § Boundary Invariants).

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
