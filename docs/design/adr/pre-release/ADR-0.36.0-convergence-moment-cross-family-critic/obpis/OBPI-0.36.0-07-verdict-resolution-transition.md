---
id: OBPI-0.36.0-07-verdict-resolution-transition
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 7
lane: Heavy
sensitivity: security
status: Draft
allowlist:
  - src/gzkit/second_opinion_resolution.py
  - src/gzkit/events.py
  - src/gzkit/ledger_events.py
  - src/gzkit/schemas/ledger.json
  - src/gzkit/governance/trust_audits/events.py
  - tests/governance/test_second_opinion_resolution.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-07-01
  - REQ-0.36.0-07-02
  - REQ-0.36.0-07-03
  - REQ-0.36.0-07-04
  - REQ-0.36.0-07-05
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_resolution -v
  - uv run gz validate --event-schemas
  - uv run gz validate --event-handlers
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-07-verdict-resolution-transition: Verdict Resolution Transition

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #7 - "OBPI-0.36.0-07: **verdict-resolution-transition** — Step 4b's resolution shape generalized without touching 4b — a refuted verdict with no recorded resolution blocks, and the resolution names what was fixed and how the critic's check was re-run"

**Status:** Draft

## Objective

Answer the question Step 4b already answers, for decisions Step 4b never sees:
**what happens after a critic says no.** § Target Scope states the unit
definition: *"Step 4b's resolution shape generalized without touching 4b: a
`refuted` verdict with no recorded resolution blocks, and the resolution must
state both what was fixed and how the critic's own check was re-run, durable in
the ledger rather than in a transcript."*

Every word of that is already implemented once, forty lines of one file away, and
that file is the one this brief may not touch. Read it and generalize from it:

- The verdict vocabulary is `ADVERSARY_VERDICTS` at
  `src/gzkit/commands/obpi_complete_adversarial.py:47` —
  `refuted | not-refuted | refuted-with-caveats | degraded-human-only`.
- The blocking rule is `_enforce_adversarial_validation` at line 282:
  `if verdict == "refuted" and not resolution:` → fail, with the message
  *"A known refutation must never be handed to the operator dressed as clean."*
- The durability channel is `_build_adversarial_event` at line 137, which writes
  `resolution` onto an `adversarial_validation` ledger event rather than leaving
  it in a transcript. The docstring for the enforcement names why: without it,
  *"one that skipped 4b and one that was refuted and attested anyway left
  indistinguishable durable records — the verdict lived only in a transcript or
  a vendor cache."*

**One thing is deliberately not copied.** 4b takes the resolution as a single
free-text string whose placeholder demands two facts at once:
`--adversary-resolution '<what was fixed and how the adversary's check was
re-run>'`. A single string asked for two facts is answered with one — the
cheaper one, the fix, with the re-run silently unaccounted. The ADR's Target
Scope says the resolution *"must state **both** what was fixed **and** how the
critic's own check was re-run"*; this brief makes that structural by taking two
required fields instead of one. That is generalization in the direction the ADR
points, and it is the difference between a rule and a rule that holds.

**The boundary is the point of the unit, not an aside.** Boundary Invariant #1
fences this brief by name. Operator canon, verbatim: *"we will NOT alter the OBPI
process, at all!"* and *"I am hesitant to alter anything about the obpi pipeline
as it is the most enduringly stable part of gzkit."* A brief that edits 4b to
make its own claim pass has inverted the ADR — the parent states exactly that.
Read 4b. Import its vocabulary so the two cannot drift. Change nothing in it.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Sensitivity

**`security`** — declared, not inherited. This brief writes a new event type into
`src/gzkit/ledger_events.py`, which `data/security_surfaces.json` registers under
category `ledger_integrity`: *"the ledger is gzkit's system-of-record and any
non-monotonic write corrupts every downstream audit."* The auto-detect floor in
`.gzkit/rules/security-sensitivity.md` fails closed on an omitted declaration over
a registered overlap, and this overlap is real rather than incidental — the whole
point of the unit is that the resolution is durable in the ledger. Gate 5 fires
the heightened walkthrough, including the `arb-step-security-scan-*` receipt.

## Allowed Paths

- `src/gzkit/second_opinion_resolution.py` — the transition gate: verdict in, blocked-or-cleared out, with the two-field resolution contract. Verified convention: flat modules under `src/gzkit/`; siblings in this ADR are `second_opinion.py`, `second_opinion_transport.py`, `second_opinion_door.py`, `second_opinion_envelope.py`, `second_opinion_tiering.py`.
- `src/gzkit/events.py` — the typed `TypedLedgerEvent` union member for the resolution event. Required, not optional: `req_kind_support._derive_typed_event_types()` walks that union to decide which event names a SUPPORT REQ may cite, so an event absent from it is uncitable anywhere in the repo.
- `src/gzkit/ledger_events.py` — the event factory. Verified convention: every event has a `*_event()` factory here (`obpi_created_event`, `obpi_withdrawn_event`); `audit_event_handlers` parses this exact file for emitted types.
- `src/gzkit/schemas/ledger.json` — the paired schema entry. Verified requirement: `audit_event_schemas` compares emitted types against `schema["events"].keys()`, and a missing entry makes `gz validate --ledger` fail with `Unknown event type` the moment the event lands.
- `src/gzkit/governance/trust_audits/events.py` — the `_NO_GRAPH_IMPACT` waiver entry with its rationale. Verified location: the dict is at line 21 of that module, **not** in the test file its own error message names.
- `tests/governance/test_second_opinion_resolution.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `src/gzkit/commands/obpi_complete_adversarial.py` — **Boundary Invariant #1**, the fence this brief is named in. Read-only: quote it, import from it, never edit it. Operator canon, verbatim: *"we will NOT alter the OBPI process, at all!"*
- The `gz obpi` parser surface (`src/gzkit/cli/**`, `src/gzkit/commands/obpi_cmd.py`) and any Step-4b gate — same invariant. `obpi_cmd.py` and `obpi_complete.py` are additionally registered security surfaces (`auth_boundaries`), so an edit here would be both a boundary breach and an undeclared sensitivity escalation.
- `src/gzkit/ledger.py` — the graph writer, and a registered `ledger_integrity` surface. A second-opinion resolution is not a governance-graph node; it is recorded via the `_NO_GRAPH_IMPACT` waiver with a written rationale rather than by drawing a false lineage edge.
- `.gzkit/ledger.jsonl` — never hand-edited (`AGENTS.md` § Behavior Rules — Never #2).
- `data/flags.json` — OBPI-09's dark-door switch (Boundary Invariant #3).
- `src/gzkit/second_opinion_door.py`, `src/gzkit/second_opinion_tiering.py`, `src/gzkit/second_opinion_envelope.py` — OBPI-03/04, OBPI-06, OBPI-05. This gate consumes an envelope id and a verdict; it authors neither.
- `.claude/hooks/**`, `.claude/settings.json`, `src/gzkit/hooks/**` — OBPI-09.
- New `gz` verb — the gate is a library surface called by the doors.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. NEVER: Edit `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, or any Step-4b gate. Boundary Invariant #1. If a claim in this brief can only be made true by editing 4b, the claim is wrong, not 4b.
2. ALWAYS: Block on a `refuted` verdict with no recorded resolution. This is 4b's rule at `obpi_complete_adversarial.py:282` generalized to any decision, and it carries 4b's reason unchanged: *"A known refutation must never be handed to the operator dressed as clean."*
3. ALWAYS: Require the resolution as **two distinct non-empty fields** — what was fixed, and how the critic's own check was re-run. NEVER accept one free-text blob for both. A single field asked for two facts is answered with the cheaper one.
4. ALWAYS: Write the resolution to the ledger as a typed event before the decision proceeds. NEVER let a transcript, a chat message, or an in-memory object stand as the record. § The operator predicted this exact loss is the standing evidence: *"multiple audio tape recordings of audio tape recordings."*
5. ALWAYS: Source the verdict vocabulary from the single existing definition (`ADVERSARY_VERDICTS`) rather than restating the four tokens. A second, differently-spelled vocabulary for the same concept is the failure OBPI-01's REQ-0.36.0-01-04 already fences on the schema side.
6. ALWAYS: Bind the resolution to the OBPI-05 envelope id of the decision it resolves. A resolution that names no subject cannot be checked against the decision the operator actually saw.
7. ALWAYS: Land the event on all four coupled surfaces in the same change — typed model, factory, `schemas/ledger.json` entry, and either a graph handler or a written `_NO_GRAPH_IMPACT` rationale (`AGENTS.md` § DO IT RIGHT 1a, coupled-surface coherence). Landing three of four leaves `gz validate --ledger` failing on the first real event.
8. NEVER: Add a `gz` verb, wire a hook, or edit a generated mirror.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — the `verdict-resolution-transition` one-line definition, including *"both"* and *"durable in the ledger rather than in a transcript"*.
- [ ] Parent ADR § Boundary — the OBPI pipeline is untouched — the two verbatim operator quotes, and the recorded casualty of ignoring the boundary once (*"a 7-to-8-minute latency figure imported from OBPI-pipeline mechanism was ~20x high"*).
- [ ] Parent ADR § Boundary Invariants #1 — this brief is one of the two units it fences; it is the proof channel for REQ-0.36.0-07-05.
- [ ] Parent ADR § Persona — *"An agent working this ADR treats a critique as something to **carry**, not to absorb."* A resolution field is where absorption becomes visible.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/security-sensitivity.md` — the auto-detect floor, why this brief declares `sensitivity: security`, and the heightened Gate-5 walkthrough it triggers (`arb-step-security-scan-*` receipt; scanner-unavailable is fail-closed, no degradation).
- [ ] `.claude/rules/task-discovery.md` § Convention: Ledger `task_id` — the optional `task_id` field on worklog event types, so the new event follows the established envelope rather than inventing one.
- [ ] `AGENTS.md` § DO IT RIGHT 1a — coupled-surface coherence. Four surfaces move together here; requirement #7 is that rule applied.
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — this brief carries BEHAVIOR, SUPPORT and STRUCTURAL-FENCE REQs. Read the proof-channel matrix: the SUPPORT REQ proves by ledger event **citing its path** plus a structural validator, and the fence proves only by the parent ADR's § Boundary Invariants anchor. Do NOT author a `@covers` test for either.

**Context:**

- [ ] OBPI-0.36.0-01 — REQ-0.36.0-01-04 already pins the verdict vocabulary to `events.py::adversarial_validation`. Requirement #5 is the same fence on the resolution side; the two must agree.
- [ ] OBPI-0.36.0-05 — the envelope id this resolution binds to (requirement #6).
- [ ] OBPI-0.36.0-08 — the pilot reads these resolution events to derive *false blocks*. A resolution shape that cannot be aggregated is a measurement the ADR cannot take.
- [ ] OBPI-0.36.0-09 — the other unit Boundary Invariant #1 fences. Both briefs must be diffable against the 4b path at closeout and show no change.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/obpi_complete_adversarial.py` exists and is readable — verified, 387 lines. STOP if missing: there is no shape to generalize from, and inventing one would be the fabrication this ADR was written against.
- [ ] `src/gzkit/events.py`, `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` all exist — verified; `audit_event_schemas` returns empty (silently passing) if any is absent, so their presence is a precondition for the checks in Verification to mean anything.
- [ ] `src/gzkit/governance/trust_audits/events.py::_NO_GRAPH_IMPACT` exists — verified at line 21, a `dict[str, str]` of event name to rationale.
- [ ] `src/gzkit/second_opinion_envelope.py` exists (created by OBPI-05) — STOP if missing: requirement #6 has no subject to bind to.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_resolution.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_resolution.py`

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:47-52` — `ADVERSARY_VERDICTS`. Read the four tokens and import them; do not retype them (requirement #5).
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:238-292` — `_enforce_adversarial_validation`, including the docstring's account of why an unrecorded verdict is indistinguishable from a skipped one, and the `verdict == "refuted" and not resolution` block at line 282 with its exact operator-facing message.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:137-176` — `_build_adversarial_event`. Note the optional-field pattern (`if value:` — omitted rather than emitted as null, *"matching `_EventBase._serialize`"*); the new event follows it.
- [ ] `src/gzkit/ledger_events.py::obpi_withdrawn_event` — read one factory end to end for the house shape before adding another.
- [ ] `src/gzkit/events.py::_EventBase` — the frozen, `extra="forbid"` base and the `schema`/`schema_` mapping every typed event inherits.
- [ ] `src/gzkit/governance/trust_audits/events.py:21-60` — read two existing `_NO_GRAPH_IMPACT` rationales (`surface_weight_recalibrated`, `session_exit_bookmark_skipped`). Both argue *why the event has no graph node*, at length. Match that standard or add a real handler instead.
- [ ] `src/gzkit/schemas/ledger.json` — find the `artifact_edited` entry (line 58) and mirror its shape for the new event.

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
uv run -m unittest tests.governance.test_second_opinion_resolution -v
uv run gz validate --event-schemas
uv run gz validate --event-handlers
uv run gz validate --ledger
uv run gz validate --sensitivity
uv run gz validate --req-kind-discipline
uv run gz covers
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# A refuted verdict with no resolution is blocked. Non-zero exit, and the
# message names both missing halves.
uv run python -m gzkit.second_opinion_resolution close --envelope-id 3f2b91c07d4e5a68 --verdict refuted

# Half a resolution is still blocked: what was fixed, with no account of the
# re-run, is the cheaper answer requirement #3 refuses.
uv run python -m gzkit.second_opinion_resolution close --envelope-id 3f2b91c07d4e5a68 --verdict refuted --fixed "Narrowed the envelope store root to the configured receipts pattern."

# Both halves supplied: the transition clears and the resolution is written to
# the ledger, not to this terminal.
uv run python -m gzkit.second_opinion_resolution close --envelope-id 3f2b91c07d4e5a68 --verdict refuted --fixed "Narrowed the envelope store root to the configured receipts pattern." --recheck "Re-ran the critic's own check: codex exec --sandbox read-only against src/gzkit/arb/paths.py; it returned not-refuted."

# The record survives the process. Read it back from the system-of-record.
uv run gz state --json

# The ledger still validates with the new event type present.
uv run gz validate --ledger

# The 4b path this brief generalized from is byte-unchanged (Boundary Invariant #1).
uv run git diff --stat HEAD -- src/gzkit/commands/obpi_complete_adversarial.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.36.0-07-01 [BEHAVIOR]: Given a `refuted` verdict with no recorded resolution, when the transition is attempted, then it is blocked and nothing is written — and given the same verdict with a complete resolution, then it clears. A `not-refuted` verdict clears without a resolution.
- [ ] REQ-0.36.0-07-02 [BEHAVIOR]: Given a resolution supplying only what was fixed, or only how the critic's check was re-run, when the transition is attempted, then it is blocked naming the missing half — a single combined free-text string does not satisfy the contract.
- [ ] REQ-0.36.0-07-03 [BEHAVIOR]: Given a cleared refuted verdict, when the process has exited, then the ledger carries a typed resolution event holding both fields and the OBPI-05 envelope id, parseable through the `TypedLedgerEvent` union — an in-memory or transcript-only record fails this criterion.
- [ ] REQ-0.36.0-07-04 [SUPPORT]: `src/gzkit/schemas/ledger.json` carries the resolution event entry paired with its factory in `src/gzkit/ledger_events.py`, so the ledger validator admits the event rather than rejecting it as unknown. Witnessed by `artifact_edited` citing `src/gzkit/schemas/ledger.json` + `gz validate --event-schemas`.
- [ ] REQ-0.36.0-07-05 [STRUCTURAL-FENCE]: Across the delivered set, `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, and every Step-4b gate are unchanged — this unit reads 4b's resolution shape and generalizes it without editing 4b — parent ADR § Boundary Invariants #1 (OBPI-07, OBPI-09).

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
