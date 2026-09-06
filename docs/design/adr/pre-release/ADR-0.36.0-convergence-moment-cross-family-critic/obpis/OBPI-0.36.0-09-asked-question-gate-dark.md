---
id: OBPI-0.36.0-09-asked-question-gate-dark
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 9
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/hooks/scripts/second_opinion.py
  - src/gzkit/hooks/claude.py
  - data/flags.json
  - .claude/hooks/second-opinion-gate.py
  - .claude/settings.json
  - tests/governance/test_second_opinion_gate_dark.py
  - tests/governance/fixtures/askuserquestion_payload.json
  - tests/governance/fixtures/askuserquestion_payload_unknown_shape.json
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-09-01
  - REQ-0.36.0-09-02
  - REQ-0.36.0-09-03
  - REQ-0.36.0-09-04
  - REQ-0.36.0-09-05
  - REQ-0.36.0-09-06
  - REQ-0.36.0-09-07
  - REQ-0.36.0-09-08
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_gate_dark -v
  - uv run gz validate --surfaces
  - uv run gz flags
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-09-asked-question-gate-dark: Asked Question Gate Dark

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #9 - "OBPI-0.36.0-09: **asked-question-gate-dark** — The `PreToolUse` adapter on `AskUserQuestion` — wired, tested, and off by default, lit only by OBPI-08's measured result"

**Status:** Draft

## Objective

Ship the third door — the automatic one — **wired, tested, and off**. § Target
Scope states the unit definition: *"The `PreToolUse` adapter on
`AskUserQuestion`, wired and tested but **off by default**, lit only by a
measured pilot result and never by a promotion narrative."*

This is the door the whole ADR was commissioned for. The operator's trigger
ruling is unambiguous — *"you've achieved convergence, within that session, when
you do so, I need a 2nd opinion in that exact moment"* — and it is precisely
because this door matters most that it ships dark. § Target Scope names what
still perforates: *"the automatic door binds to a UI event that also carries
mandatory clarification, so it can prevent the very question those rules
require."* A door that can suppress a required clarification is worse than no
door, and no amount of design confidence substitutes for the four measurements
OBPI-08 takes.

**This brief may not be the judge of whether it should be on.** § Why nine names
the shape explicitly: merging the pilot into this unit *"makes the gate's own
OBPI the judge of whether it should be on, which is the self-referential shape
`docs/governance/advisory-rules-audit.md` § Self-referential scope domains
names."* Boundary Invariant #3 fences it: *"Neither brief may light it on its own
evidence."* The dark state is therefore not a promise in prose — it is enforced
by the registry model itself. `data/flags.json` is validated by `FlagSpec`
(`src/gzkit/flags/models.py`), whose `development` category **raises on
`default: true`**: *"Development flags must default to false."* A future edit
flipping this flag's default is rejected at load, not caught at review.

**The trigger signature is borrowed, and the brief says so.** § The trigger
signature is a Claude Code product affordance, not a gzkit one records the
operator identifying the observable signature — *"which is surely product-driven
(claude code product level) because you offer the same choice mechanic enery time
[choices|direct entry|discuss]"* — and the ADR draws the consequence: *"it is a
**portability liability** — the signature belongs to Claude Code and will move
when the product moves."* This brief owns that liability rather than deferring
it. `AskUserQuestion` and `PreToolUse` are harness surfaces gzkit does not
control; the adapter therefore degrades to an inert pass-through when the payload
is not the shape it expects, and never wedges a turn on a product change. The
recurring survey of which hook doors exist, changed, or closed is chore-shaped
and routed separately (§ Derived work: hook-surface currency) — do not absorb it
here.

Both sides of the surface are in scope, because in this repo a hook has two
sides: the generator (`src/gzkit/hooks/scripts/`, emitted by
`src/gzkit/hooks/claude.py`) and the generated artifact (`.claude/hooks/`,
`.claude/settings.json`). Editing only the generated side is overwritten by the
next `gz agent sync control-surfaces`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/hooks/scripts/second_opinion.py` — the hook-script **generator**: a function returning the adapter's source as a `dedent`ed string. Verified convention: `src/gzkit/hooks/scripts/` holds per-category generator modules (`pipeline.py`, `routing.py`, `quality.py`, `validation.py`, `ghi.py`, `mx.py`, `session_exit.py`), each returning script text.
- `src/gzkit/hooks/claude.py` — the emitter and the registration. Verified: `_write_hook_file(hooks_path / "<name>.py", _<name>_script(), executable=True)` writes each hook (see the `plan-audit-gate.py` block at ~line 520), and `generate_claude_settings()` at line 208 builds the `PreToolUse` matcher list that becomes `.claude/settings.json`. Both halves live in this one file.
- `data/flags.json` — the dark switch, registered under the `development` category so `FlagSpec` mechanically refuses a `true` default. Verified convention: `data/flags.json` is the flag registry read by `src/gzkit/flags/registry.py::load_registry`; the shipped entry `ops.product_proof` is the shape to follow.
- `.claude/hooks/second-opinion-gate.py` — the generated adapter. Verified: a **sync output**, written by `setup_claude_hooks`/`sync` from the generator above; it is committed but never hand-edited.
- `.claude/settings.json` — the generated registration. Verified: written by `sync_claude_settings` (`src/gzkit/sync_surfaces.py:448`) via `merge_settings`, and drift-checked by `detect_claude_settings_drift`. Also a sync output; never hand-edited.
- `tests/governance/test_second_opinion_gate_dark.py` — covering tests. Verified convention: `tests/governance/test_*.py`.
- `tests/governance/fixtures/askuserquestion_payload.json` and `tests/governance/fixtures/askuserquestion_payload_unknown_shape.json` — the recorded hook payloads the dark, lit, and unknown-shape paths are exercised against. Verified convention: `tests/governance/fixtures/` exists and holds `.json` fixtures (`foundation_grandfather_golden.json`). Record them from a real harness invocation; do not hand-compose a payload from memory of the event's shape.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

> **Both generated entries are produced by `uv run gz agent sync control-surfaces`, not by an editor.** Edit the generator, run sync, commit the result. A hand-edit to either is reverted by the next sync and flagged by `gz validate --surfaces` sync-parity in the meantime.

## Denied Paths

- `src/gzkit/second_opinion_pilot.py`, `docs/governance/second-opinion-pilot.md` — **Boundary Invariant #3.** OBPI-08 owns the measurements. This brief must not author, adjust, or pre-satisfy the evidence that would light it; that is the self-referential shape § Why nine split these two units to prevent.
- `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, any Step-4b gate — **Boundary Invariant #1**, verbatim operator canon: *"we will NOT alter the OBPI process, at all!"* This adapter binds a `PreToolUse` event directly and routes through no pipeline mechanism.
- `src/gzkit/hooks/scripts/quality.py`, `src/gzkit/hooks/guards.py` — registered security surfaces (`data/security_surfaces.json`, category `subprocess_user_input`). Touching either would make this brief `sensitivity: security` for no gain; the new adapter lives in its own generator module.
- `src/gzkit/second_opinion.py`, `src/gzkit/second_opinion_transport.py`, `src/gzkit/second_opinion_door.py`, `src/gzkit/second_opinion_tiering.py`, `src/gzkit/second_opinion_envelope.py`, `src/gzkit/second_opinion_resolution.py` — OBPI-01/02/03/04/05/06/07. This door is an **adapter**: it translates a hook payload into a call on surfaces that already exist and re-implements none of them.
- `src/gzkit/cli/**` — no new `gz` verb. The adapter is dispatched by the harness, not by a registered verb.
- `.claude/skills/**`, `.agents/skills/**`, `.github/skills/**`, `src/gzkit/skills/**` — generated mirrors (`.gzkit/rules/skill-surface-sync.md` #4/#5).
- Paths not listed in Allowed Paths
- New dependencies — the generated hook script is stdlib-only (`json`, `os`, `sys`, `pathlib`), matching every existing hook in `src/gzkit/hooks/scripts/`.
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. ALWAYS: Ship the adapter **off**. Register its flag in `data/flags.json` under the `development` category, whose `FlagSpec` validator raises on `default: true` — so the dark state is a load-time property of the registry, not a convention someone remembers. § Target Scope: *"off by default, lit only by a measured pilot result and never by a promotion narrative."*
2. NEVER: Light this door on evidence produced inside this brief. Boundary Invariant #3. Only OBPI-08's four measurements plus an operator ruling may flip it, and neither is authored here.
3. ALWAYS: Pass the tool payload through **untouched** when the flag is off — no `updatedInput`, no critic dispatch, no added latency, exit 0. Dark must be indistinguishable from absent.
4. ALWAYS: Exit 0 as a no-op when the payload is not the `AskUserQuestion` shape the adapter expects — a renamed field, a changed event, a missing key. The trigger signature is a Claude Code product affordance (§ The trigger signature), so the product **will** move; the adapter's failure mode on that day must be inert, never a wedged turn. NEVER raise, block, or emit a permission decision on an unrecognized payload.
5. ALWAYS: When lit, take the firing decision from OBPI-06's tier resolver and the verdict from OBPI-02's transport through OBPI-01's schema. NEVER inline a threshold, a prompt, or a verdict parser here.
6. ALWAYS: Preserve the base question's options when injecting. § Mechanics fixes the injection shape: preamble **always**, plus one appended option only when the base question carries ≤3 options. NEVER drop, reorder, or rewrite an operator-facing option.
7. ALWAYS: Carry the critic's verdict **unedited** through `updatedInput`, including the UNASKED line — operator verbatim: *"yes, it is a 2nd opinion, not a usurped opinion … I re-pose the question carrying the critic's verdict unedited."*
8. ALWAYS: Edit the generator (`src/gzkit/hooks/scripts/second_opinion.py`, `src/gzkit/hooks/claude.py`) and regenerate; NEVER hand-edit `.claude/hooks/second-opinion-gate.py` or `.claude/settings.json`. Run `uv run gz agent sync control-surfaces` before completion.
9. NEVER: Add a `gz` verb, edit Step 4b, or narrate this OBPI's completion as "the critic shipped" without the qualifier § Target Scope requires: *"Until that door lights, this ADR does not deliver a second opinion at every structured choice."*

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent and § The trigger — the convergence moment, in the operator's words, and why this event was chosen.
- [ ] Parent ADR § The trigger signature is a Claude Code product affordance, not a gzkit one — read in full. It is the source of requirement #4 and of this brief's portability posture.
- [ ] Parent ADR § Mechanics (measured, not assumed) — the Trigger, Transport, Injection shape, and Passthrough rows. Note that the harness **enforces** the `updatedInput` passthrough, *"stronger than the ruling required"*.
- [ ] Parent ADR § Target Scope — the `asked-question-gate-dark` definition and the staging paragraph, including what still perforates about this door specifically.
- [ ] Parent ADR § Why nine — the **Testability Ceiling** bullet; it is the reason this brief cannot judge itself.
- [ ] Parent ADR § Boundary Invariants #1 and #3 — this brief is fenced by both, and they are the proof channels for REQ-0.36.0-09-07 and REQ-0.36.0-09-08.
- [ ] Parent ADR § Notes — Derived work: hook-surface currency — the recurring door survey. Chore-shaped and routed separately; do not absorb it into this brief.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/advisory-rules-audit.md` § Self-referential scope domains — the named failure this brief's separation from OBPI-08 avoids.
- [ ] `.gzkit/rules/skill-surface-sync.md` #4/#5 — canonical-first editing and the never-edit-generated rule that requirement #8 applies to the hook surface.
- [ ] `AGENTS.md` § Behavior Rules — Never #6 — *"Do not work around hook blocks."* This brief authors a hook; the same discipline applies to how it behaves toward the agent it wraps.
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — this brief carries BEHAVIOR, SUPPORT and two STRUCTURAL-FENCE REQs; read the proof-channel matrix and do NOT author `@covers` tests for the fences.

**Context:**

- [ ] OBPI-0.36.0-01 — the verdict schema this adapter renders. The UNASKED line must be a discrete field precisely because requirement #6 renders it as a separate appended option and cannot parse it out of prose (OBPI-01's requirement #6).
- [ ] OBPI-0.36.0-02 — the transport. Latency measured at 11.62–19.62s is inside a synchronous hook budget per § Mechanics; no escalation ladder, no lag-by-one.
- [ ] OBPI-0.36.0-03 and OBPI-0.36.0-04 — the operator and agent doors. Their verdict rendering is the contract this third door matches; a door that softens what the others preserve is the failure OBPI-04's requirement #3 names.
- [ ] OBPI-0.36.0-06 — the tier resolver this adapter calls when lit (requirement #5).
- [ ] OBPI-0.36.0-08 — the only evidence that may light this door, and the brief this one may not touch.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/hooks/scripts/` exists and holds generator modules — verified: `pipeline.py`, `routing.py`, `quality.py`, `validation.py`, `ghi.py`, `mx.py`, `session_exit.py`.
- [ ] `src/gzkit/hooks/claude.py` exists, exposes `generate_claude_settings` (line 208) and writes hooks via `_write_hook_file` (~line 520) — verified.
- [ ] `.claude/hooks/` exists and holds generated `*.py` hooks — verified: `plan-audit-gate.py`, `pipeline-gate.py`, `verifier-pipe-gate.py` among 16.
- [ ] `data/flags.json` loads clean and `uv run gz flags` prints the table — verified; the registry currently holds exactly one flag (`ops.product_proof`).
- [ ] `src/gzkit/second_opinion_tiering.py` (OBPI-06) and `src/gzkit/second_opinion_transport.py` (OBPI-02) exist — STOP if missing: requirement #5 forbids inlining either, so there is nothing for the lit path to call.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/hooks/scripts/second_opinion.py`
- [ ] Required path exists or is intentionally created in this OBPI: `.claude/hooks/second-opinion-gate.py` (generated by sync)
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_gate_dark.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/fixtures/askuserquestion_payload.json`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/fixtures/askuserquestion_payload_unknown_shape.json`

**Existing Code (understand current state):**

- [ ] `src/gzkit/hooks/scripts/pipeline.py::_pipeline_completion_reminder_script` — read one generator end to end: a `dedent`ed script string with a docstring that states its event and its exit codes. That is the house shape.
- [ ] `src/gzkit/hooks/claude.py:208-260` — `generate_claude_settings`, specifically the `PreToolUse` matcher entries. Read how `matcher` and `_hook_command(hooks_dir, ...)` compose before adding an `AskUserQuestion` matcher.
- [ ] `src/gzkit/hooks/claude.py:500-545` — the `_write_hook_file` sequence. Every hook is written here; an unregistered generator produces no file.
- [ ] `src/gzkit/sync_surfaces.py:448-535` — `sync_claude_settings`, `merge_settings`, and `detect_claude_settings_drift`. Read why the merge cannot be skipped (the GHI #326/#329 orientation-hook precedent) before touching the settings generator.
- [ ] `src/gzkit/flags/models.py::FlagSpec._enforce_category_rules` — the `development` branch that raises *"Development flags must default to false"*. This is requirement #1's mechanism; read it, do not re-derive it.
- [ ] `src/gzkit/flags/service.py::FlagService` — the five-layer precedence chain. Local pilot enablement is layer 2, the `GZKIT_FLAG_<KEY>` environment variable, read live on every call — a deliberate per-invocation act, never a committed default.
- [ ] `.claude/hooks/verifier-pipe-gate.py` — read a live `PreToolUse` gate's stdin/stdout contract and its exit-code discipline before writing a new one.

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
uv run -m unittest tests.governance.test_second_opinion_gate_dark -v
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
uv run gz flags
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
# The door is registered and dark. The registry is the witness, not prose.
uv run gz flags
uv run gz flag explain development.second_opinion_asked_question_gate

# The adapter is wired: generated from src/gzkit/hooks/claude.py and registered
# as a PreToolUse matcher on AskUserQuestion.
uv run gz agent sync control-surfaces
uv run gz validate --surfaces

# Dark behaviour, observed rather than asserted: feed the hook a real
# AskUserQuestion payload with the flag at its default. Passes through, exit 0,
# no updatedInput, no critic dispatched.
uv run python .claude/hooks/second-opinion-gate.py < tests/governance/fixtures/askuserquestion_payload.json

# Lit behaviour, opted into for one invocation via the precedence-layer-2 env
# var — never a committed default.
GZKIT_FLAG_DEVELOPMENT_SECOND_OPINION_ASKED_QUESTION_GATE=true uv run python .claude/hooks/second-opinion-gate.py < tests/governance/fixtures/askuserquestion_payload.json

# Portability: a payload from a renamed or changed product event is inert, not
# fatal (REQ-09-04).
uv run python .claude/hooks/second-opinion-gate.py < tests/governance/fixtures/askuserquestion_payload_unknown_shape.json

# The verdict the lit path would carry, dispatched cross-family and unedited.
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: an AskUserQuestion PreToolUse adapter can be enabled by default before a calibrated pilot has measured false blocks."
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.36.0-09-01 [BEHAVIOR]: Given the flag at its registry default, when the adapter receives a well-formed `AskUserQuestion` `PreToolUse` payload, then it exits 0 having emitted no `updatedInput` and dispatched no critic — dark is indistinguishable from absent.
- [ ] REQ-0.36.0-09-02 [BEHAVIOR]: Given the flag enabled through its `GZKIT_FLAG_` environment variable, when the same payload arrives, then the firing decision is taken by OBPI-06's tier resolver, the verdict is rendered through OBPI-01's schema, and `updatedInput` carries every field verbatim — a rendering that summarizes any field fails.
- [ ] REQ-0.36.0-09-03 [BEHAVIOR]: Given a `data/second_opinion` flag entry in the `development` category declaring `default: true`, when the registry is loaded, then the load raises — the dark state is refused at load rather than caught at review.
- [ ] REQ-0.36.0-09-04 [BEHAVIOR]: Given a payload that is not the expected `AskUserQuestion` shape — renamed field, changed event name, missing key — when the adapter runs, then it exits 0 as a no-op, emits no permission decision, and raises nothing; the borrowed product signature degrades to inert, never to a wedged turn.
- [ ] REQ-0.36.0-09-05 [BEHAVIOR]: Given the base question carries more than three options, when the lit adapter injects, then only the preamble is added and no option is appended; given three or fewer, then exactly one option is appended and every original option is preserved in order.
- [ ] REQ-0.36.0-09-06 [SUPPORT]: `.claude/settings.json` carries the adapter as a `PreToolUse` matcher on `AskUserQuestion`, regenerated from `src/gzkit/hooks/claude.py` rather than hand-edited, so the door is genuinely wired while dark. Witnessed by `artifact_edited` citing `src/gzkit/hooks/claude.py` + `gz validate --surfaces`.
- [ ] REQ-0.36.0-09-07 [STRUCTURAL-FENCE]: Across the delivered set, `src/gzkit/commands/obpi_complete_adversarial.py`, the `gz obpi` parser surface, and every Step-4b gate are unchanged — this adapter binds a `PreToolUse` event and routes through no pipeline mechanism — parent ADR § Boundary Invariants #1 (OBPI-07, OBPI-09).
- [ ] REQ-0.36.0-09-08 [STRUCTURAL-FENCE]: Across the delivered set, the door's registry entry is at its dark default and no artifact of this unit supplies the evidence that would light it — only OBPI-08's four measurements and an operator ruling can — parent ADR § Boundary Invariants #3 (OBPI-08, OBPI-09).

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
