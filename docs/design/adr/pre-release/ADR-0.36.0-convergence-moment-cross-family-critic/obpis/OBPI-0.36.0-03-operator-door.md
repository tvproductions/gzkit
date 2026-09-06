---
id: OBPI-0.36.0-03-operator-door
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 3
lane: Heavy
status: Draft
allowlist:
  - .gzkit/skills/second-opinion/
  - src/gzkit/second_opinion_door.py
  - tests/governance/test_second_opinion_operator_door.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-03-01
  - REQ-0.36.0-03-02
  - REQ-0.36.0-03-03
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_operator_door -v
  - uv run gz skill list
---

# OBPI-0.36.0-03-operator-door: Operator Door

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #3 - "OBPI-0.36.0-03: **operator-door** — The operator-invoked door: the `second-opinion` slash command, callable on any decision at any moment"

**Status:** Draft

## Objective

Make `/second-opinion` callable by the operator on **any decision, at any
moment**, with **no governance artifact required in scope** — no active OBPI, no
active ADR, no pipeline stage.

That last clause is the whole substance and the reason this is not Step 4b.
Step 4b's adversarial gate is OBPI-scoped by construction: it fires inside a
completion ceremony and needs a brief to attach to. The operator's stated need is
the opposite — *"a permanent '2nd opinion' process where, each and everytime you
provided a critical analysis that leads to my decision making"* — which includes
the many moments when no OBPI is open at all. A door that quietly required
governance context would be Step 4b with a new name, and would silently not fire
in exactly the ad-hoc moments the ADR was written for.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/skills/second-opinion/` — the canonical skill gains its operator-invocation contract. Verified convention: canonical skills live at `.gzkit/skills/<slug>/SKILL.md` and are mirrored by `gz agent sync control-surfaces`.
- `src/gzkit/second_opinion_door.py` — shared door-entry logic (decision capture, verdict rendering) used by this door and OBPI-04's. Verified convention: flat modules under `src/gzkit/`.
- `tests/governance/test_second_opinion_operator_door.py` — covering tests.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `.claude/skills/**`, `.agents/skills/**`, `.github/skills/**`, `src/gzkit/skills/**` — generated mirrors (`.gzkit/rules/skill-surface-sync.md` #4/#5). Edit canonical, then sync.
- `.claude/commands/**` — verified hand-maintained and outside the sync manifest. A second, unsynced operator surface would drift from the skill; the skill IS the door.
- `src/gzkit/cli/**` — Boundary Invariant #2, no new `gz` verb.
- `src/gzkit/commands/obpi_complete_adversarial.py` — Boundary Invariant #1.
- `.claude/hooks/**`, `.claude/settings.json` — OBPI-09.

## Requirements (FAIL-CLOSED)

1. ALWAYS: The door MUST function with no active OBPI, no active ADR, and no pipeline stage. A door that requires governance context is Step 4b renamed.
2. NEVER: Require the operator to name an artifact ID. The decision under review is supplied as free text or a path; the operator's cost of invoking must stay near zero (`AGENTS.md` § OPERATOR ECONOMY OF EFFORT).
3. ALWAYS: Render the critic's verdict to the operator **unedited**, including the UNASKED (scope-challenge) line. The rendering may add structure; it may never summarize, soften, or drop a field.
4. NEVER: Let the primary agent's summary of the verdict substitute for the verdict. The ADR's persona names this as the failure *"an agent building it is most likely to commit."*
5. ALWAYS: Reuse OBPI-02's transport and OBPI-01's schema. This door is an entry point, not a second implementation.
6. NEVER: Add a `gz` verb, edit a generated mirror, or wire a hook.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Target Scope — R2's ruling that the unit is one skill with three doors.
- [ ] Parent ADR § Boundary Invariants #2 — no new `gz` verb.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § OPERATOR ECONOMY OF EFFORT — the operator's typing budget is the scarce resource; the door must be cheap to invoke.
- [ ] `AGENTS.md` § Attestation — the passthrough discipline this door's rendering mirrors: operator words pass unchanged.
- [ ] `.gzkit/rules/skill-surface-sync.md` — canonical-first editing plus the mandatory sync step.

**Context:**

- [ ] OBPI-0.36.0-01 — the skill and verdict schema this door dispatches.
- [ ] OBPI-0.36.0-02 — the transport this door calls.
- [ ] OBPI-0.36.0-04 — the agent door, which shares `second_opinion_door.py`.

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/skills/` exists with at least one `<slug>/SKILL.md` — verified: `.gzkit/skills/gz-arb/SKILL.md`.
- [ ] `uv run gz skill list` prints the active catalog — verified.
- [ ] `.claude/commands/` is hand-maintained and NOT in the sync manifest — verified; this is why the skill rather than a command file is the door.
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/skills/second-opinion/`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_door.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_operator_door.py`

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/git-sync/SKILL.md` — read the `disable-model-invocation: true` frontmatter key, which is how a skill is made operator-only. This door must NOT set it: OBPI-04 needs the same skill agent-invocable.
- [ ] `.gzkit/skills/gz-arb/SKILL.md` — read for the standard frontmatter block and Output Contract shape.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py::_enforce_adversarial_validation` — read to see precisely what OBPI-scoped coupling this door must NOT inherit.

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

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_second_opinion_operator_door -v
uv run gz skill list
uv run gz validate --skill-alignment
uv run gz agent sync control-surfaces
```

## Demo

```bash
# The door is discoverable with no governance artifact in scope
uv run gz skill list

# An ad-hoc decision, no OBPI open, no ADR named
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: healing clipped rulings in place is preferable to authoring a successor handoff."
```

## Acceptance Criteria

- [ ] REQ-0.36.0-03-01 [BEHAVIOR]: Given no active OBPI, no active ADR and no pipeline stage, when the operator door is invoked with a free-text decision, then it dispatches the critic and returns a verdict — governance context is never a precondition.
- [ ] REQ-0.36.0-03-02 [BEHAVIOR]: Given a verdict carrying PREMISE-ATTACK, VERDICT and UNASKED, when the door renders it to the operator, then all three fields appear verbatim — a rendering that drops or paraphrases any field fails.
- [ ] REQ-0.36.0-03-03 [SUPPORT]: `.gzkit/skills/second-opinion/SKILL.md` declares the operator-invocation contract without `disable-model-invocation`, keeping the same skill agent-invocable for OBPI-04. Witnessed by `artifact_edited` citing `.gzkit/skills/second-opinion/SKILL.md` + `gz validate --documents`.

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

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
