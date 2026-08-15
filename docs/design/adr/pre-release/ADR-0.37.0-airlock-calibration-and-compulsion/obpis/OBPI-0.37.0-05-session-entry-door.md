---
id: OBPI-0.37.0-05-session-entry-door
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 5
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-05-session-entry-door.md
  - src/gzkit/hooks/claude.py
  - src/gzkit/hooks/scripts/handoff.py
  - src/gzkit/handoff_resume_gate.py
  - tests/test_session_entry_door.py
  - tests/governance/test_handoff_resume_gate.py
reqs:
  - REQ-0.37.0-05-01
  - REQ-0.37.0-05-02
  - REQ-0.37.0-05-03
  - REQ-0.37.0-05-04
verification:
  - uv run -m unittest tests.test_session_entry_door -q
---

# OBPI-0.37.0-05-session-entry-door: Session Entry Door

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #5 - "OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it"

**Status:** Draft

## Objective

OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-05-session-entry-door.md` — this brief
- `src/gzkit/hooks/claude.py` — generates the SessionStart hook; gains the airlock-IN call
- `src/gzkit/hooks/scripts/handoff.py` — the resume-gate template whose `Write|Edit|NotebookEdit` arm retires here
- `src/gzkit/handoff_resume_gate.py` — the gate module backing that arm
- `tests/test_session_entry_door.py` — new covering tests (flat convention) **CREATE**
- `tests/governance/test_handoff_resume_gate.py` — existing 49-test suite, updated as the arm retires
## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** pull edges for this brief are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The scaffold carried the parent ADR and a `…/**` glob in its allowlist; removed 2026-08-15.)
- Retiring the `Write|Edit|NotebookEdit` arm BEFORE the session-entry door is live. Removing it first opens a gap in front of the door; the improvisation and the hole close in ONE move or not at all.
- `gz git-sync` — exempt unconditionally (parent ADR § Boundary Invariants #5).
- Any local weight, profile, or decision grammar. The door CALLS `gzkit.airlock.enter.airlock_enter` (§ Boundary Invariants #2).
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/hooks/claude.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/hooks/scripts/handoff.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/handoff_resume_gate.py`
- [ ] Parent ADR § Boundary Invariants parses and each invariant carries an `(OBPI-NN)` binding token
- [ ] Parent ADR § Flip Criteria baselines re-measured rather than transcribed from this brief
**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_session_entry_door -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Session entry is now a transit: the airlock fires and the encounter reaches L2.
uv run python scripts/session_orientation.py

# The transit is readable from the ledger, not from agent narrative.
uv run gz state --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-05-01 [BEHAVIOR]: Given a session entering the project, when SessionStart runs, then airlock-IN fires and the encounter is booked to L2. Evidence the gap is real and this is its closure: the 2026-07-18 session ran a full corpus survey, filed 2 GHIs, changed 3 source files and rewrote the campaign plan across ZERO transits.
- [ ] REQ-0.37.0-05-02 [BEHAVIOR]: Given the session-entry door is live, when it decides, then it is the ONLY session-entry mechanism — no second, forked entry gate exists alongside it. **AMENDED 2026-08-15 (operator ruling).** This REQ read: *"when the handoff-resume-gate's `Write|Edit|NotebookEdit` arm is retired, then no window exists in which neither mechanism is active. The two changes land together; a retirement that precedes the door is a regression, not an increment."* The operator retired that arm ahead of the door — verbatim: *"the handoff should be an advisor, not a gate-keeping nanny"* — so the coupling it required cannot be satisfied and the window it forbade is already open. Recorded rather than silently contradicted. The premise (*"Given the session-entry door is live"*) was unmet and unscheduled at the ruling: ADR-0.37.0 was `Pending` at 0/6 with no implementation, while the arm's measured lifetime was 9 lifts to 1 block over the single day refusal-recording existed. What the door must still not do is re-create a forked entry gate, which is what the retired arm was; that duty survives here and in the sibling criterion below requiring it to consume `airlock_enter` and define no local decision grammar.
- [ ] REQ-0.37.0-05-03 [BEHAVIOR]: Given the session-entry door, when it decides, then it consumes `gzkit.airlock.enter.airlock_enter` and defines no local weight, profile, or decision grammar of its own. The arm it retires WAS a forked variant; retiring it must not create a second one.
- [ ] REQ-0.37.0-05-04 [STRUCTURAL-FENCE]: The session-entry door requires no TTY, PTY, or interactive terminal, and its acknowledge-and-decide outcome is never recorded, rendered, or counted as a Gate-5 completion attestation. Proof channel is the parent ADR's `## Boundary Invariants` #6 and #8, both of which name OBPI-05; audited at ADR closeout.
## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
